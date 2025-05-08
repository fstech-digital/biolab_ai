"""
Implementações especializadas de extratores para diferentes formatos de laboratórios
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from .pdf_extractor import PDFExtractor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenericLabExtractor(PDFExtractor):
    """
    Extrator genérico para laboratórios não especificados
    Tenta extrair dados usando heurísticas mais gerais
    """
    
    def extract_exam_data(self) -> List[Dict[str, Any]]:
        """
        Extrai dados dos exames usando padrões genéricos
        
        Returns:
            Lista de dicionários com dados dos exames
        """
        exams = []
        
        # Extrair tabelas primeiro (mais confiável para estrutura)
        tables = self.extract_tables_pdfplumber()
        
        # Processar tabelas que parecem conter resultados de exames
        for table in tables:
            if not table or len(table) <= 1:  # Pular tabelas vazias ou só com cabeçalho
                continue
            
            # Tentar identificar cabeçalho
            header = table[0]
            if not header:
                continue
            
            # Verificar se parece uma tabela de resultados de exames
            # Procurar por cabeçalhos comuns como "Exame", "Resultado", "Valor de Referência"
            exam_col = None
            result_col = None
            reference_col = None
            unit_col = None
            
            header_lower = [h.lower() if h else "" for h in header]
            
            for i, col_name in enumerate(header_lower):
                if col_name and any(term in col_name for term in ["exame", "teste", "análise", "parâmetro"]):
                    exam_col = i
                elif col_name and any(term in col_name for term in ["resultado", "valor", "medida"]):
                    result_col = i
                elif col_name and any(term in col_name for term in ["referência", "referencia", "normal", "intervalo"]):
                    reference_col = i
                elif col_name and any(term in col_name for term in ["unidade", "un"]):
                    unit_col = i
            
            # Se encontramos pelo menos nome do exame e resultado, processamos a tabela
            if exam_col is not None and result_col is not None:
                for row in table[1:]:  # Pular cabeçalho
                    if not row or len(row) <= max(exam_col, result_col):
                        continue
                    
                    exam_name = row[exam_col].strip() if row[exam_col] else ""
                    if not exam_name:
                        continue  # Pular linhas sem nome de exame
                    
                    result_value = row[result_col].strip() if row[result_col] else ""
                    
                    # Extrair unidade e valor de referência se disponíveis
                    unit = row[unit_col].strip() if unit_col is not None and unit_col < len(row) and row[unit_col] else ""
                    reference = row[reference_col].strip() if reference_col is not None and reference_col < len(row) and row[reference_col] else ""
                    
                    # Criar entrada para o exame
                    exam_entry = {
                        "name": exam_name,
                        "result": result_value,
                        "unit": unit,
                        "reference": reference,
                        "source": "table"
                    }
                    
                    exams.append(exam_entry)
        
        # Se não conseguimos extrair das tabelas, tentar extrair do texto
        if not exams:
            # Padrão para capturar exames no formato "NOME DO EXAME: RESULTADO (UNIDADE) Valor de Referência: REF"
            exam_pattern = r"([\w\s-]+?):\s+([\d.,]+)\s*([a-zA-Z%/]+)?\s*(?:Valor\s+de\s+Referência|Referência):\s+([\w\s.,<>-]+)"
            
            matches = re.finditer(exam_pattern, self.text, re.IGNORECASE)
            for match in matches:
                exam_name = match.group(1).strip()
                result_value = match.group(2).strip()
                unit = match.group(3).strip() if match.group(3) else ""
                reference = match.group(4).strip()
                
                exam_entry = {
                    "name": exam_name,
                    "result": result_value,
                    "unit": unit,
                    "reference": reference,
                    "source": "text"
                }
                
                exams.append(exam_entry)
        
        return exams


class RamosMedicinaExtractor(PDFExtractor):
    """
    Extrator especializado para o formato Ramos Medicina
    """
    
    def extract_patient_data(self) -> Dict[str, Any]:
        """
        Extrai dados do paciente específicos para Ramos Medicina
        
        Returns:
            Dicionário com dados do paciente
        """
        # Primeiro tenta extrair usando a implementação genérica
        patient_data = super().extract_patient_data()
        
        # Padrões específicos para Ramos Medicina
        if not patient_data["name"]:
            name_match = re.search(r"Paciente:\s+([\w\s]+)", self.text)
            if name_match:
                patient_data["name"] = name_match.group(1).strip()
        
        # Tenta extrair documento/ID
        doc_match = re.search(r"(CPF|RG|ID):\s+([\w\s./-]+)", self.text)
        if doc_match:
            patient_data["document"] = doc_match.group(2).strip()
        
        return patient_data
    
    def extract_exam_data(self) -> List[Dict[str, Any]]:
        """
        Extrai dados dos exames específicos para Ramos Medicina
        
        Returns:
            Lista de dicionários com dados dos exames
        """
        exams = []
        
        # Tentar localizar a seção de resultados no texto
        results_section_match = re.search(r"RESULTADOS(.*?)(?:OBSERVAÇÕES|$)", self.text, re.DOTALL)
        if not results_section_match:
            # Tentar padrão alternativo
            results_section_match = re.search(r"EXAMES REALIZADOS(.*?)(?:OBSERVAÇÕES|$)", self.text, re.DOTALL)
        
        if results_section_match:
            results_text = results_section_match.group(1)
            
            # Padrão para extrair linhas de exames no formato Ramos Medicina
            # Exemplo: "Hemoglobina: 15.2 g/dL Referência: 13.5 - 17.5"
            exam_pattern = r"([\w\s]+):\s+([\d.,]+)\s+([a-zA-Z%/]+)(?:\s+Referência:\s+([\d.,\s-]+))?"
            
            matches = re.finditer(exam_pattern, results_text)
            for match in matches:
                exam_name = match.group(1).strip()
                result_value = match.group(2).strip()
                unit = match.group(3).strip() if match.group(3) else ""
                reference = match.group(4).strip() if match.group(4) else ""
                
                exam_entry = {
                    "name": exam_name,
                    "result": result_value,
                    "unit": unit,
                    "reference": reference,
                    "source": "text_pattern"
                }
                
                exams.append(exam_entry)
        
        # Se não conseguiu extrair com o padrão específico, tenta o método genérico
        if not exams:
            exams = super().extract_exam_data()
        
        return exams


class ExtractorFactory:
    """
    Fábrica para criar o extrator apropriado com base nas características do PDF
    """
    
    @staticmethod
    def create_extractor(pdf_path: str) -> PDFExtractor:
        """
        Cria o extrator mais apropriado para o PDF fornecido
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Instância do extrator apropriado
        """
        # Instanciar um extrator genérico para extrair texto
        generic = PDFExtractor(pdf_path)
        text = generic.extract_text_pymupdf()
        
        # Verificar padrões para identificar o formato do laboratório
        if "Ramos Medicina" in text:
            logger.info(f"Identificado formato Ramos Medicina para {pdf_path}")
            return RamosMedicinaExtractor(pdf_path)
        
        # Adicionar mais condições para outros laboratórios
        # elif "Outro Laboratório" in text:
        #     return OutroLaboratorioExtractor(pdf_path)
        
        # Se não conseguir identificar formato específico, usa o genérico
        logger.info(f"Usando extrator genérico para {pdf_path}")
        return GenericLabExtractor(pdf_path)