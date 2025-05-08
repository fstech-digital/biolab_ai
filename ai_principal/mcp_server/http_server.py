"""
Servidor HTTP para BioLab.Ai MCP

Este módulo implementa uma API HTTP usando FastAPI para expor as 
funcionalidades do MCP Server para aplicações web e outros clientes.
"""

import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .server import MCPServer, MCPRequest, MCPResponse

# Carregar variáveis de ambiente
load_dotenv()

# Configurar app FastAPI
app = FastAPI(
    title="BioLab.Ai MCP API",
    description="API para interação com as ferramentas do BioLab.Ai via protocolo MCP",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciar servidor MCP
mcp_server = MCPServer()

# Modelos para API
class APIRequest(BaseModel):
    """Modelo para requisição à API HTTP"""
    tool_name: str
    parameters: Dict[str, Any]

class APIResponse(BaseModel):
    """Modelo para resposta da API HTTP"""
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None

# Rotas da API
@app.get("/")
async def read_root():
    """Rota raiz com informações básicas"""
    return {
        "name": "BioLab.Ai MCP API",
        "version": "0.1.0",
        "docs_url": "/docs"
    }

@app.get("/tools")
async def get_tools():
    """Retorna todas as ferramentas disponíveis"""
    return mcp_server.get_tool_schemas()

@app.post("/execute", response_model=APIResponse)
async def execute_tool(request: APIRequest):
    """
    Executa uma ferramenta MCP
    
    Args:
        request: Requisição contendo ferramenta e parâmetros
        
    Returns:
        Resultado da execução da ferramenta
    """
    mcp_request = {
        "tool_name": request.tool_name,
        "parameters": request.parameters
    }
    
    result = mcp_server.handle_request(mcp_request)
    
    if result["status"] == "error":
        # Retornar erro com status HTTP 400, mas manter formato de resposta
        return APIResponse(
            status="error",
            error=result["error"]
        )
    
    return APIResponse(
        status="success",
        data=result["data"]
    )

@app.post("/mcp")
async def mcp_endpoint(request_data: Dict[str, Any] = Body(...)):
    """
    Endpoint compatível com MCP para LLMs
    
    Args:
        request_data: Dados da requisição MCP
        
    Returns:
        Resposta MCP
    """
    return mcp_server.handle_request(request_data)

def start_server(host: str = "0.0.0.0", port: int = None):
    """
    Inicia o servidor HTTP
    
    Args:
        host: Host para o servidor
        port: Porta para o servidor (usa variável PORT do .env se não especificado)
    """
    import uvicorn
    
    if port is None:
        port = int(os.getenv("PORT", 8000))
    
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    uvicorn.run(
        "ai_principal.mcp_server.http_server:app",
        host=host,
        port=port,
        reload=debug
    )