"""
Módulo de integração com Supabase
Fornece conexão e operações básicas com o banco vetorial Supabase
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseVectorStore:
    """Cliente para interação com o banco vetorial Supabase"""
    
    def __init__(self):
        """Inicializa a conexão com o Supabase"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.vector_collection = os.getenv("VECTOR_COLLECTION", "biolab_documents")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no .env")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def store_document(self, document_data: Dict[str, Any], embeddings: List[float]) -> Dict[str, Any]:
        """
        Armazena um documento no banco vetorial
        
        Args:
            document_data: Dicionário com metadados do documento
            embeddings: Lista de embeddings do documento
        
        Returns:
            Resposta da inserção no Supabase
        """
        data = {
            **document_data,
            "embedding": embeddings
        }
        
        response = self.client.table(self.vector_collection).insert(data).execute()
        return response.data
    
    def search_similar(self, query_embedding: List[float], match_threshold: float = 0.7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Realiza busca semântica por similaridade de embeddings
        
        Args:
            query_embedding: Embedding da consulta
            match_threshold: Limiar mínimo de similaridade (0.0 a 1.0)
            limit: Número máximo de resultados
            
        Returns:
            Lista de documentos similares
        """
        response = (
            self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": limit
                }
            ).execute()
        )
        
        return response.data
    
    def search_by_metadata(self, metadata_filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca documentos com base em metadados específicos
        
        Args:
            metadata_filters: Dicionário com filtros a serem aplicados
            limit: Número máximo de resultados
            
        Returns:
            Lista de documentos que correspondem aos filtros
        """
        query = self.client.table(self.vector_collection).select("*")
        
        # Aplicar filtros
        for key, value in metadata_filters.items():
            query = query.eq(key, value)
            
        response = query.limit(limit).execute()
        return response.data
    
    def search_patient_exams(self, patient_name: str) -> List[Dict[str, Any]]:
        """
        Busca exames específicos de um paciente
        
        Args:
            patient_name: Nome do paciente
            
        Returns:
            Lista de exames do paciente
        """
        # Primeiro tenta busca exata
        response = (
            self.client.table(self.vector_collection)
            .select("*")
            .eq("patient_name", patient_name)
            .execute()
        )
        
        results = response.data
        
        # Se não encontrar resultados, tenta busca parcial (contém)
        if not results:
            response = (
                self.client.table(self.vector_collection)
                .select("*")
                .ilike("patient_name", f"%{patient_name}%")
                .execute()
            )
            results = response.data
        
        return results