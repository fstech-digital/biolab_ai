"""
Módulo principal de processamento RAG
Coordena os passos de pré-processamento para RAG
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from .chunking import ExamChunker
from .normalizer import ExamNormalizer
from .embeddings import EmbeddingGenerator

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGProcessor:
    """
    Processador completo para RAG
    Coordena normalização, chunking e geração de embeddings
    """
    
    def __init__(self, 
                chunk_size: int = 1000, 
                chunk_overlap: int = 200,
                embedding_model: Optional[str] = None,
                normalization_rules: Optional[Dict[str, Any]] = None):
        """
        Inicializa o processador RAG com configurações
        
        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres
            chunk_overlap: Sobreposição entre chunks em caracteres
            embedding_model: Nome do modelo de embedding a ser usado
            normalization_rules: Regras de normalização para exames
        """
        self.normalizer = ExamNormalizer(normalization_rules)
        self.chunker = ExamChunker(chunk_size, chunk_overlap)
        self.embedding_generator = EmbeddingGenerator(embedding_model)
    
    def process_exam_data(self, exam_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executa o pipeline completo de pré-processamento RAG
        
        Args:
            exam_data: Dados do exame extraídos do PDF
            
        Returns:
            Lista de chunks prontos para indexação
        """
        # 1. Normalização
        logger.info("Normalizando dados do exame...")
        normalized_data = self.normalizer.normalize_exam_data(exam_data)
        
        # 2. Chunking
        logger.info("Dividindo dados em chunks significativos...")
        chunks = self.chunker.chunk_exam_data(normalized_data)
        
        # 3. Geração de embeddings
        logger.info("Gerando embeddings para os chunks...")
        chunks_with_embeddings = self.embedding_generator.generate_embeddings(chunks)
        
        logger.info(f"Processamento RAG concluído. Gerados {len(chunks_with_embeddings)} chunks.")
        
        return chunks_with_embeddings
    
    def process_exam_file(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        Processa um arquivo JSON com dados extraídos de exame
        
        Args:
            json_file_path: Caminho para o arquivo JSON
            
        Returns:
            Lista de chunks prontos para indexação
        """
        # Validar existência do arquivo
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {json_file_path}")
        
        # Carregar dados do arquivo
        with open(json_file_path, 'r', encoding='utf-8') as f:
            exam_data = json.load(f)
        
        # Processar dados
        logger.info(f"Processando arquivo: {json_file_path}")
        chunks = self.process_exam_data(exam_data)
        
        # Salvar chunks em arquivo
        output_path = json_file_path.replace('.json', '_rag.json')
        if json_file_path == output_path:
            output_path = json_file_path.replace('.json', '_processed_rag.json')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Chunks RAG salvos em: {output_path}")
        
        return chunks
    
    def process_directory(self, dir_path: str, file_pattern: str = "*_extracted.json") -> List[List[Dict[str, Any]]]:
        """
        Processa todos os arquivos JSON em um diretório
        
        Args:
            dir_path: Caminho para o diretório
            file_pattern: Padrão para filtrar arquivos
            
        Returns:
            Lista de listas de chunks prontos para indexação
        """
        # Validar diretório
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"Diretório não encontrado: {dir_path}")
        
        # Listar arquivos JSON no diretório
        json_files = list(Path(dir_path).glob(file_pattern))
        
        if not json_files:
            logger.warning(f"Nenhum arquivo correspondente ao padrão '{file_pattern}' encontrado em: {dir_path}")
            return []
        
        # Processar cada arquivo
        results = []
        for json_file in json_files:
            try:
                chunks = self.process_exam_file(str(json_file))
                results.append(chunks)
            except Exception as e:
                logger.error(f"Erro ao processar arquivo {json_file}: {e}")
        
        return results