"""
Módulo principal para execução do pré-processamento RAG
"""

import os
import argparse
import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from .processor import RAGProcessor

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_json_file(json_path: str, 
                     output_dir: Optional[str] = None,
                     chunk_size: int = 1000,
                     chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Processa um arquivo JSON com dados extraídos de exame
    
    Args:
        json_path: Caminho para o arquivo JSON
        output_dir: Diretório para os arquivos de saída (opcional)
        chunk_size: Tamanho máximo de cada chunk em caracteres
        chunk_overlap: Sobreposição entre chunks em caracteres
        
    Returns:
        Lista de chunks prontos para indexação
    """
    # Validar caminhos
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Arquivo JSON não encontrado: {json_path}")
    
    # Criar processador RAG
    processor = RAGProcessor(chunk_size, chunk_overlap)
    
    # Processar arquivo
    chunks = processor.process_exam_file(json_path)
    
    # Salvar em diretório específico, se fornecido
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(json_path).replace('.json', '_rag.json')
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Chunks RAG salvos em: {output_path}")
    
    return chunks

def process_directory(dir_path: str, 
                     output_dir: Optional[str] = None,
                     file_pattern: str = "*_extracted.json",
                     chunk_size: int = 1000,
                     chunk_overlap: int = 200) -> List[List[Dict[str, Any]]]:
    """
    Processa todos os arquivos JSON em um diretório
    
    Args:
        dir_path: Caminho para o diretório
        output_dir: Diretório para os arquivos de saída (opcional)
        file_pattern: Padrão para filtrar arquivos
        chunk_size: Tamanho máximo de cada chunk em caracteres
        chunk_overlap: Sobreposição entre chunks em caracteres
        
    Returns:
        Lista de listas de chunks prontos para indexação
    """
    # Validar diretório
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Diretório não encontrado: {dir_path}")
    
    # Criar processador RAG
    processor = RAGProcessor(chunk_size, chunk_overlap)
    
    # Processar diretório
    return processor.process_directory(dir_path, file_pattern)

def main():
    """Função principal para execução via linha de comando"""
    
    parser = argparse.ArgumentParser(description="Pré-processador RAG para exames médicos")
    
    # Argumentos para modo de operação
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", type=str, help="Caminho para um único arquivo JSON")
    group.add_argument("--dir", type=str, help="Caminho para diretório com JSONs")
    
    # Argumentos opcionais
    parser.add_argument("--output", type=str, help="Diretório para arquivos de saída")
    parser.add_argument("--pattern", type=str, default="*_extracted.json", help="Padrão para filtrar arquivos (para --dir)")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Tamanho máximo de cada chunk em caracteres")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Sobreposição entre chunks em caracteres")
    
    args = parser.parse_args()
    
    try:
        if args.json:
            # Processar um único JSON
            process_json_file(
                args.json,
                output_dir=args.output,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
        else:
            # Processar diretório
            process_directory(
                args.dir,
                output_dir=args.output,
                file_pattern=args.pattern,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()