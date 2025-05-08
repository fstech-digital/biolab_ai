"""
Módulo principal para processamento de PDFs de exames
"""

import os
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .specialized_extractors import ExtractorFactory
from .excel_reference import ExcelReferenceProcessor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf_file(pdf_path: str, 
                    reference_path: Optional[str] = None,
                    output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Processa um arquivo PDF de exame
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        reference_path: Caminho para a planilha de referência (opcional)
        output_dir: Diretório para os arquivos de saída (opcional)
        
    Returns:
        Dicionário com os dados extraídos
    """
    # Validar caminhos
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
    
    if reference_path and not os.path.exists(reference_path):
        logger.warning(f"Planilha de referência não encontrada: {reference_path}")
        reference_path = None
    
    # Definir diretório de saída
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(pdf_path)
    
    # Criar extrator apropriado para o formato do PDF
    extractor = ExtractorFactory.create_extractor(pdf_path)
    
    # Extrair dados do PDF
    logger.info(f"Extraindo dados do PDF: {pdf_path}")
    extracted_data = extractor.extract_all()
    
    # Salvar dados extraídos
    pdf_name = Path(pdf_path).stem
    output_json_path = os.path.join(output_dir, f"{pdf_name}_extracted.json")
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Dados extraídos salvos em: {output_json_path}")
    
    # Enriquecer com valores de referência, se disponível
    if reference_path and extracted_data.get('exams'):
        try:
            # Carregar processador de referências
            logger.info(f"Carregando valores de referência da planilha: {reference_path}")
            reference_processor = ExcelReferenceProcessor(reference_path)
            reference_processor.load_reference_data()
            
            # Dados do paciente para filtros
            patient = extracted_data.get('patient', {})
            sex = patient.get('gender')
            age = patient.get('age')
            
            # Enriquecer cada exame com valores de referência
            for exam in extracted_data['exams']:
                exam_name = exam.get('name', '')
                if not exam_name:
                    continue
                
                # Obter referências para este exame
                ref_data = reference_processor.get_reference_for_exam(exam_name, sex, age)
                
                # Adicionar dados de referência ao exame
                if 'error' not in ref_data:
                    exam['reference_data'] = ref_data
            
            # Salvar dados enriquecidos
            output_enriched_path = os.path.join(output_dir, f"{pdf_name}_enriched.json")
            
            with open(output_enriched_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados enriquecidos salvos em: {output_enriched_path}")
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer dados com valores de referência: {e}")
    
    return extracted_data

def process_directory(dir_path: str, 
                     reference_path: Optional[str] = None,
                     output_dir: Optional[str] = None,
                     file_pattern: str = "*.pdf") -> List[Dict[str, Any]]:
    """
    Processa todos os PDFs em um diretório
    
    Args:
        dir_path: Caminho para o diretório com PDFs
        reference_path: Caminho para a planilha de referência (opcional)
        output_dir: Diretório para os arquivos de saída (opcional)
        file_pattern: Padrão para filtrar arquivos
        
    Returns:
        Lista de dicionários com os dados extraídos de cada PDF
    """
    # Validar caminhos
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Diretório não encontrado: {dir_path}")
    
    # Listar arquivos PDF no diretório
    pdf_files = list(Path(dir_path).glob(file_pattern))
    
    if not pdf_files:
        logger.warning(f"Nenhum arquivo correspondente ao padrão '{file_pattern}' encontrado em: {dir_path}")
        return []
    
    # Processar cada arquivo
    results = []
    for pdf_file in pdf_files:
        try:
            data = process_pdf_file(
                str(pdf_file), 
                reference_path=reference_path,
                output_dir=output_dir
            )
            results.append(data)
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {pdf_file}: {e}")
    
    return results

def main():
    """Função principal para execução via linha de comando"""
    
    parser = argparse.ArgumentParser(description="Processador de PDFs de exames médicos")
    
    # Argumentos para modo de operação
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf", type=str, help="Caminho para um único arquivo PDF")
    group.add_argument("--dir", type=str, help="Caminho para diretório com PDFs")
    
    # Argumentos opcionais
    parser.add_argument("--reference", type=str, help="Caminho para planilha de referência")
    parser.add_argument("--output", type=str, help="Diretório para arquivos de saída")
    parser.add_argument("--pattern", type=str, default="*.pdf", help="Padrão para filtrar arquivos (para --dir)")
    
    args = parser.parse_args()
    
    try:
        if args.pdf:
            # Processar um único PDF
            process_pdf_file(
                args.pdf,
                reference_path=args.reference,
                output_dir=args.output
            )
        else:
            # Processar diretório
            process_directory(
                args.dir,
                reference_path=args.reference,
                output_dir=args.output,
                file_pattern=args.pattern
            )
    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()