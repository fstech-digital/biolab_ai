"""
Módulo principal para extração de dados de PDFs de exames médicos
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Classe base para extração de dados de PDFs de exames médicos
    """
    
    def __init__(self, pdf_path: str):
        """
        Inicializa o extrator com o caminho para o PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
        """
        self.pdf_path = pdf_path
        self.text = ""
        self.extracted_data = {}
        
        # Validar existência do arquivo
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
    
    def extract_text_pymupdf(self) -> str:
        """
        Extrai texto do PDF usando PyMuPDF (mais rápido)
        
        Returns:
            Texto completo extraído do PDF
        """
        text = ""
        try:
            doc = fitz.open(self.pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            logger.error(f"Erro ao extrair texto com PyMuPDF: {e}")
        
        return text
    
    def extract_text_pdfplumber(self) -> str:
        """
        Extrai texto do PDF usando pdfplumber (mais preciso para tabelas)
        
        Returns:
            Texto completo extraído do PDF
        """
        text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            logger.error(f"Erro ao extrair texto com pdfplumber: {e}")
        
        return text
    
    def extract_tables_pdfplumber(self) -> List[List[List[str]]]:
        """
        Extrai tabelas do PDF usando pdfplumber
        
        Returns:
            Lista de tabelas, onde cada tabela é uma lista de linhas, e cada linha é uma lista de células
        """
        tables = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except Exception as e:
            logger.error(f"Erro ao extrair tabelas com pdfplumber: {e}")
        
        return tables
    
    def extract_all(self) -> Dict[str, Any]:
        """
        Extrai todos os dados do PDF
        
        Returns:
            Dicionário com todos os dados extraídos
        """
        # Extrair texto usando múltiplos métodos para maior precisão
        text_pymupdf = self.extract_text_pymupdf()
        text_pdfplumber = self.extract_text_pdfplumber()
        
        # Usar o texto que parece mais completo/preciso
        if len(text_pdfplumber) > len(text_pymupdf):
            self.text = text_pdfplumber
        else:
            self.text = text_pymupdf
        
        # Extrair tabelas
        tables = self.extract_tables_pdfplumber()
        
        # Extrair metadados do PDF
        metadata = self.extract_pdf_metadata()
        
        # Extrair dados do paciente
        patient_data = self.extract_patient_data()
        
        # Extrair dados de exames
        exam_data = self.extract_exam_data()
        
        # Consolidar todos os dados extraídos
        self.extracted_data = {
            "metadata": metadata,
            "patient": patient_data,
            "exams": exam_data,
            "raw_text": self.text,
            "tables": tables,
            "extraction_date": datetime.now().isoformat()
        }
        
        return self.extracted_data
    
    def extract_pdf_metadata(self) -> Dict[str, Any]:
        """
        Extrai metadados do arquivo PDF
        
        Returns:
            Dicionário com metadados do PDF
        """
        metadata = {
            "filename": os.path.basename(self.pdf_path),
            "filesize": os.path.getsize(self.pdf_path),
            "created": None,
            "modified": None,
            "title": None,
            "author": None,
            "producer": None
        }
        
        try:
            doc = fitz.open(self.pdf_path)
            pdf_metadata = doc.metadata
            if pdf_metadata:
                metadata["title"] = pdf_metadata.get("title")
                metadata["author"] = pdf_metadata.get("author")
                metadata["producer"] = pdf_metadata.get("producer")
                
                # Tentar extrair datas
                if "creationDate" in pdf_metadata:
                    try:
                        # Formato comum: "D:20240506123456+02'00'"
                        date_str = pdf_metadata["creationDate"].strip("D:").split("+")[0]
                        metadata["created"] = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S").isoformat()
                    except:
                        pass
                
                if "modDate" in pdf_metadata:
                    try:
                        date_str = pdf_metadata["modDate"].strip("D:").split("+")[0]
                        metadata["modified"] = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S").isoformat()
                    except:
                        pass
            
            doc.close()
        except Exception as e:
            logger.error(f"Erro ao extrair metadados do PDF: {e}")
        
        return metadata
    
    def extract_patient_data(self) -> Dict[str, Any]:
        """
        Extrai dados do paciente do texto do PDF
        
        Returns:
            Dicionário com dados do paciente
        """
        # Implementação básica - será especializada por subclasses
        patient_data = {
            "name": None,
            "age": None,
            "gender": None,
            "date_of_birth": None,
            "document": None,
            "exam_date": None
        }
        
        # Tentar extrair nome do paciente com padrões comuns
        name_patterns = [
            r"(?:Paciente|Nome)[\s:]+([\w\s]+?)(?:\n|\r|,|Idade)",
            r"(?:PACIENTE|NOME)[\s:]+([\w\s]+?)(?:\n|\r|,|IDADE)",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, self.text)
            if match:
                patient_data["name"] = match.group(1).strip()
                break
        
        # Tentar extrair idade
        age_patterns = [
            r"(?:Idade|Age)[\s:]+(\d+)",
            r"(?:IDADE|AGE)[\s:]+(\d+)",
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, self.text)
            if match:
                try:
                    patient_data["age"] = int(match.group(1))
                except:
                    pass
                break
        
        # Tentar extrair gênero
        gender_patterns = [
            r"(?:Sexo|Gênero)[\s:]+(M|F|Masculino|Feminino)",
            r"(?:SEXO|GÊNERO)[\s:]+(M|F|MASCULINO|FEMININO)",
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, self.text)
            if match:
                gender = match.group(1).upper()
                if gender in ("M", "MASCULINO"):
                    patient_data["gender"] = "M"
                elif gender in ("F", "FEMININO"):
                    patient_data["gender"] = "F"
                break
        
        # Tentar extrair data do exame
        date_patterns = [
            r"(?:Data|Date|Data da Coleta)[\s:]+(\d{2}/\d{2}/\d{4})",
            r"(?:DATA|DATE|DATA DA COLETA)[\s:]+(\d{2}/\d{2}/\d{4})",
            r"(?:Data|Date|Data da Coleta)[\s:]+(\d{2}-\d{2}-\d{4})",
            r"(?:DATA|DATE|DATA DA COLETA)[\s:]+(\d{2}-\d{2}-\d{4})",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, self.text)
            if match:
                patient_data["exam_date"] = match.group(1)
                break
        
        return patient_data
    
    def extract_exam_data(self) -> List[Dict[str, Any]]:
        """
        Extrai dados dos exames do texto do PDF
        
        Returns:
            Lista de dicionários com dados dos exames
        """
        # Implementação básica - será especializada por subclasses
        return []
    
    def save_to_json(self, output_path: Optional[str] = None) -> str:
        """
        Salva os dados extraídos em um arquivo JSON
        
        Args:
            output_path: Caminho para o arquivo de saída. Se não fornecido,
                         será gerado a partir do nome do PDF
        
        Returns:
            Caminho para o arquivo JSON gerado
        """
        if not self.extracted_data:
            self.extract_all()
        
        if output_path is None:
            # Gerar nome de arquivo baseado no original
            pdf_filename = os.path.basename(self.pdf_path)
            pdf_name = os.path.splitext(pdf_filename)[0]
            output_dir = os.path.dirname(self.pdf_path)
            output_path = os.path.join(output_dir, f"{pdf_name}_extracted.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dados extraídos salvos em {output_path}")
        return output_path