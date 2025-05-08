"""
Módulo para indexação de documentos no Supabase
Responsável por armazenar chunks processados no banco vetorial
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseIndexer:
    """
    Classe para indexação de chunks no Supabase
    """
    
    def __init__(self):
        """
        Inicializa o indexador com configurações do Supabase
        """
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.vector_collection = os.getenv("VECTOR_COLLECTION", "biolab_documents")
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("SUPABASE_URL e SUPABASE_KEY devem ser definidos no .env")
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no .env")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def index_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Indexa uma lista de chunks no Supabase
        
        Args:
            chunks: Lista de chunks processados com embeddings
            
        Returns:
            Lista de respostas da inserção
        """
        responses = []
        
        for chunk in chunks:
            # Verificar se tem embedding
            if 'embedding' not in chunk or not chunk['embedding']:
                logger.warning(f"Chunk sem embedding. Pulando...")
                continue
            
            try:
                # Preparar dados para inserção
                data = {
                    "content": chunk.get('text', ''),
                    "embedding": chunk.get('embedding', []),
                    "metadata": chunk.get('metadata', {}),
                    "chunk_type": chunk.get('chunk_type', 'unknown')
                }
                
                # Inserir no Supabase
                response = self.client.table(self.vector_collection).insert(data).execute()
                responses.append(response.data)
                
                logger.info(f"Chunk indexado com sucesso: {response.data[0].get('id')}")
                
            except Exception as e:
                logger.error(f"Erro ao indexar chunk: {e}")
        
        logger.info(f"Indexação concluída. {len(responses)} de {len(chunks)} chunks indexados.")
        
        return responses
    
    def index_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Indexa chunks a partir de um arquivo JSON
        
        Args:
            file_path: Caminho para o arquivo JSON com chunks
            
        Returns:
            Lista de respostas da inserção
        """
        # Validar existência do arquivo
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Carregar chunks do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        # Verificar se é uma lista
        if not isinstance(chunks, list):
            raise ValueError(f"O arquivo deve conter uma lista de chunks: {file_path}")
        
        # Indexar chunks
        logger.info(f"Indexando {len(chunks)} chunks de {file_path}")
        return self.index_chunks(chunks)
    
    def index_directory(self, dir_path: str, file_pattern: str = "*_rag.json") -> Dict[str, List[Dict[str, Any]]]:
        """
        Indexa todos os arquivos de chunks em um diretório
        
        Args:
            dir_path: Caminho para o diretório
            file_pattern: Padrão para filtrar arquivos
            
        Returns:
            Dicionário com resultados da indexação por arquivo
        """
        from pathlib import Path
        
        # Validar diretório
        if not os.path.isdir(dir_path):
            raise NotADirectoryError(f"Diretório não encontrado: {dir_path}")
        
        # Listar arquivos JSON no diretório
        json_files = list(Path(dir_path).glob(file_pattern))
        
        if not json_files:
            logger.warning(f"Nenhum arquivo correspondente ao padrão '{file_pattern}' encontrado em: {dir_path}")
            return {}
        
        # Processar cada arquivo
        results = {}
        for json_file in json_files:
            try:
                file_path = str(json_file)
                responses = self.index_from_file(file_path)
                results[file_path] = responses
            except Exception as e:
                logger.error(f"Erro ao indexar arquivo {json_file}: {e}")
                results[str(json_file)] = []
        
        return results