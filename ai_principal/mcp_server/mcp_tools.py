"""
Ferramentas MCP para BioLab.Ai

Define as ferramentas disponíveis pelo servidor MCP para integração com LLMs.
Cada ferramenta implementa uma função específica que pode ser chamada por LLMs
através do protocolo MCP.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from .supabase_client import SupabaseVectorStore

# Modelos de dados para as ferramentas MCP

class PatientExamSearchRequest(BaseModel):
    """Modelo para busca de exames por nome do paciente"""
    patient_name: str = Field(..., description="Nome do paciente para busca de exames")

class ExamDateSearchRequest(BaseModel):
    """Modelo para busca de exames por intervalo de data"""
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")

class ExamTypeSearchRequest(BaseModel):
    """Modelo para busca de exames por tipo"""
    exam_type: str = Field(..., description="Tipo de exame a ser buscado")

class ReferenceValueRequest(BaseModel):
    """Modelo para obtenção de valores de referência"""
    exam_code: str = Field(..., description="Código do exame")
    age: int = Field(..., description="Idade do paciente")
    gender: str = Field(..., description="Gênero do paciente (M/F)")

# Implementação das ferramentas MCP

class MCPTools:
    """Classe que implementa as ferramentas MCP para o BioLab.Ai"""
    
    def __init__(self):
        """Inicializa as ferramentas MCP"""
        self.vector_store = SupabaseVectorStore()
    
    def buscar_exames_paciente(self, request: PatientExamSearchRequest) -> List[Dict[str, Any]]:
        """
        Busca exames por nome do paciente
        
        Args:
            request: Objeto com nome do paciente
            
        Returns:
            Lista de exames do paciente
        """
        return self.vector_store.search_patient_exams(request.patient_name)
    
    def buscar_exames_data(self, request: ExamDateSearchRequest) -> List[Dict[str, Any]]:
        """
        Busca exames por intervalo de data
        
        Args:
            request: Objeto com intervalo de datas
            
        Returns:
            Lista de exames no período
        """
        # Implementação a ser concluída
        metadata_filters = {
            "exam_date_range": [request.start_date, request.end_date]
        }
        return self.vector_store.search_by_metadata(metadata_filters)
    
    def buscar_exames_tipo(self, request: ExamTypeSearchRequest) -> List[Dict[str, Any]]:
        """
        Busca exames por tipo
        
        Args:
            request: Objeto com tipo de exame
            
        Returns:
            Lista de exames do tipo especificado
        """
        # Implementação a ser concluída
        metadata_filters = {
            "exam_type": request.exam_type
        }
        return self.vector_store.search_by_metadata(metadata_filters)
    
    def obter_valores_referencia(self, request: ReferenceValueRequest) -> Dict[str, Any]:
        """
        Obtém valores de referência para um exame
        
        Args:
            request: Objeto com código do exame, idade e gênero
            
        Returns:
            Valores de referência para o exame
        """
        # Implementação a ser concluída - buscar valores na base
        # Por enquanto retornamos valores estáticos para teste
        return {
            "exam_code": request.exam_code,
            "min_value": 3.5,
            "max_value": 5.0,
            "unit": "g/dL",
            "age_range": f"{request.age-5}-{request.age+5}",
            "gender": request.gender
        }