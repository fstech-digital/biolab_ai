"""
Módulo de geração de embeddings para RAG
Responsável por converter dados de exames em vetores para busca semântica
"""

import os
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dotenv import load_dotenv
import openai

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Classe para geração de embeddings para dados de exames
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        Inicializa o gerador de embeddings
        
        Args:
            model: Nome do modelo de embedding a ser usado
        """
        self.model = model or EMBEDDING_MODEL
        
        # Validar API key
        if not openai.api_key:
            logger.warning("API key da OpenAI não encontrada. Configure a variável OPENAI_API_KEY no .env")
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Gera embeddings para uma lista de chunks de texto
        
        Args:
            chunks: Lista de chunks com texto e metadados
            
        Returns:
            Lista de chunks com embeddings adicionados
        """
        # Verificar se temos API key
        if not openai.api_key:
            logger.error("API key da OpenAI não configurada. Embeddings não serão gerados.")
            # Adicionar campo vazio para manter estrutura
            for chunk in chunks:
                chunk['embedding'] = []
            return chunks
        
        try:
            # Extrair textos para gerar embeddings
            texts = [chunk.get('text', '') for chunk in chunks]
            
            # Gerar embeddings em lote
            response = openai.embeddings.create(
                input=texts,
                model=self.model
            )
            
            # Extrair embeddings da resposta
            embeddings = [item.embedding for item in response.data]
            
            # Adicionar embeddings aos chunks
            for i, embedding in enumerate(embeddings):
                chunks[i]['embedding'] = embedding
            
            logger.info(f"Gerados {len(embeddings)} embeddings usando o modelo {self.model}")
            
            return chunks
        
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            # Em caso de erro, adicionar campo vazio para manter estrutura
            for chunk in chunks:
                chunk['embedding'] = []
            return chunks
    
    def generate_embedding_single(self, text: str) -> List[float]:
        """
        Gera embedding para um único texto
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de valores do embedding
        """
        # Verificar se temos API key
        if not openai.api_key:
            logger.error("API key da OpenAI não configurada. Embedding não será gerado.")
            return []
        
        try:
            response = openai.embeddings.create(
                input=[text],
                model=self.model
            )
            
            # Extrair embedding da resposta
            embedding = response.data[0].embedding
            
            return embedding
        
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calcula a similaridade de cosseno entre dois embeddings
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Valor de similaridade (0 a 1)
        """
        # Converter para arrays numpy
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calcular similaridade de cosseno
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        similarity = dot_product / (norm1 * norm2)
        
        return float(similarity)