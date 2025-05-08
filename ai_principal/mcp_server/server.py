"""
Implementação do Servidor MCP para BioLab.Ai

Este módulo implementa o protocolo MCP (Model Context Protocol) para permitir 
que LLMs interajam com as ferramentas do BioLab.Ai de forma padronizada.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from pydantic import BaseModel, Field, create_model

from .mcp_tools import (
    MCPTools, 
    PatientExamSearchRequest,
    ExamDateSearchRequest,
    ExamTypeSearchRequest,
    ReferenceValueRequest
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    """Modelo para requisições MCP"""
    tool_name: str = Field(..., description="Nome da ferramenta a ser chamada")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parâmetros para a ferramenta")

class MCPResponse(BaseModel):
    """Modelo para respostas MCP"""
    status: str = Field(..., description="Status da requisição (success/error)")
    data: Optional[Any] = Field(None, description="Dados retornados pela ferramenta")
    error: Optional[str] = Field(None, description="Mensagem de erro, se houver")

class MCPServer:
    """Servidor MCP para BioLab.Ai"""
    
    def __init__(self):
        """Inicializa o servidor MCP"""
        self.tools = MCPTools()
        self.registered_tools: Dict[str, Callable] = {
            "buscar_exames_paciente": (self.tools.buscar_exames_paciente, PatientExamSearchRequest),
            "buscar_exames_data": (self.tools.buscar_exames_data, ExamDateSearchRequest),
            "buscar_exames_tipo": (self.tools.buscar_exames_tipo, ExamTypeSearchRequest),
            "obter_valores_referencia": (self.tools.obter_valores_referencia, ReferenceValueRequest)
        }
    
    def handle_request(self, request_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa uma requisição MCP
        
        Args:
            request_data: Dados da requisição (JSON string ou dicionário)
            
        Returns:
            Resposta formatada segundo protocolo MCP
        """
        try:
            # Converter string JSON para dicionário, se necessário
            if isinstance(request_data, str):
                request_data = json.loads(request_data)
            
            # Validar requisição
            request = MCPRequest(**request_data)
            
            # Verificar se a ferramenta existe
            if request.tool_name not in self.registered_tools:
                return MCPResponse(
                    status="error",
                    error=f"Ferramenta '{request.tool_name}' não encontrada"
                ).dict()
            
            # Obter função e modelo de parâmetros
            tool_func, param_model = self.registered_tools[request.tool_name]
            
            # Validar parâmetros
            params = param_model(**request.parameters)
            
            # Executar ferramenta
            result = tool_func(params)
            
            # Retornar resposta bem-sucedida
            return MCPResponse(
                status="success",
                data=result
            ).dict()
            
        except Exception as e:
            logger.exception(f"Erro ao processar requisição MCP: {e}")
            return MCPResponse(
                status="error",
                error=str(e)
            ).dict()
    
    def get_tool_schemas(self) -> Dict[str, Any]:
        """
        Retorna schema de todas as ferramentas disponíveis
        
        Returns:
            Dicionário com schema de ferramentas
        """
        schemas = {}
        
        for tool_name, (_, param_model) in self.registered_tools.items():
            schema = param_model.schema()
            schemas[tool_name] = {
                "name": tool_name,
                "description": schema.get("description", ""),
                "parameters": schema
            }
        
        return schemas