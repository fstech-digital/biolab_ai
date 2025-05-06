"""
Servidor HTTP para MCP Server BioLab.Ai
Expõe as mesmas ferramentas MCP como endpoints REST.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Adicionar diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Importar ferramentas MCP
try:
    # Import absoluto para execução direta
    from mcp_tools import (
        mcp_buscar_exames_paciente,
        mcp_buscar_exames_por_data,
        mcp_buscar_exames_por_tipo,
        mcp_obter_valores_referencia
    )
except ImportError:
    # Fallback para import relativo quando usado como módulo
    from .mcp_tools import (
        mcp_buscar_exames_paciente,
        mcp_buscar_exames_por_data,
        mcp_buscar_exames_por_tipo,
        mcp_obter_valores_referencia
    )

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("biolab_mcp_http")

# Criar aplicação FastAPI
app = FastAPI(
    title="BioLab.Ai MCP HTTP API",
    description="API REST para as ferramentas MCP do BioLab.Ai",
    version="0.1.0",
)

# Configurar CORS para permitir acesso de frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, limitar para domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para validação dos dados
class BuscaPacienteRequest(BaseModel):
    patient_name: str = Field(..., description="Nome ou parte do nome do paciente")

class BuscaDataRequest(BaseModel):
    start_date: str = Field(..., description="Data inicial no formato DD/MM/AAAA")
    end_date: Optional[str] = Field(None, description="Data final no formato DD/MM/AAAA (opcional)")

class BuscaTipoRequest(BaseModel):
    exam_type: str = Field(..., description="Tipo ou nome do exame (ex: hemoglobina)")

class ValoresReferenciaRequest(BaseModel):
    exam_code: str = Field(..., description="Código ou nome do exame")
    age: Optional[int] = Field(None, description="Idade do paciente (opcional)")
    gender: Optional[str] = Field(None, description="Sexo do paciente (Masculino ou Feminino)")

# Endpoints da API
@app.get("/")
async def root():
    """Endpoint raiz com informações sobre a API"""
    return {
        "name": "BioLab.Ai MCP HTTP API",
        "version": "0.1.0",
        "description": "API REST para as ferramentas MCP do BioLab.Ai",
        "endpoints": [
            {"path": "/api/exames/paciente", "description": "Buscar exames por nome do paciente"},
            {"path": "/api/exames/data", "description": "Buscar exames por intervalo de data"},
            {"path": "/api/exames/tipo", "description": "Buscar exames por tipo"},
            {"path": "/api/exames/referencia", "description": "Obter valores de referência para exame"},
        ],
    }

@app.post("/api/exames/paciente")
async def buscar_por_paciente(request: BuscaPacienteRequest):
    """Buscar exames por nome do paciente"""
    try:
        resultado = mcp_buscar_exames_paciente(request.dict())
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar exames por paciente: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/exames/data")
async def buscar_por_data(request: BuscaDataRequest):
    """Buscar exames por intervalo de data"""
    try:
        resultado = mcp_buscar_exames_por_data(request.dict())
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar exames por data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/exames/tipo")
async def buscar_por_tipo(request: BuscaTipoRequest):
    """Buscar exames por tipo"""
    try:
        resultado = mcp_buscar_exames_por_tipo(request.dict())
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar exames por tipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/exames/referencia")
async def obter_referencia(request: ValoresReferenciaRequest):
    """Obter valores de referência para exame"""
    try:
        resultado = mcp_obter_valores_referencia(request.dict())
        return resultado
    except Exception as e:
        logger.error(f"Erro ao obter valores de referência: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints alternativos usando GET (para facilitar testes)
@app.get("/api/exames/paciente/{patient_name}")
async def buscar_por_paciente_get(patient_name: str):
    """Buscar exames por nome do paciente (GET)"""
    try:
        resultado = mcp_buscar_exames_paciente({"patient_name": patient_name})
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar exames por paciente: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exames/data/")
async def buscar_por_data_get(
    start_date: str = Query(..., description="Data inicial (DD/MM/AAAA)"),
    end_date: Optional[str] = Query(None, description="Data final (DD/MM/AAAA)")
):
    """Buscar exames por intervalo de data (GET)"""
    try:
        resultado = mcp_buscar_exames_por_data({"start_date": start_date, "end_date": end_date})
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar exames por data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exames/tipo/{exam_type}")
async def buscar_por_tipo_get(exam_type: str):
    """Buscar exames por tipo (GET)"""
    try:
        resultado = mcp_buscar_exames_por_tipo({"exam_type": exam_type})
        return resultado
    except Exception as e:
        logger.error(f"Erro ao buscar exames por tipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/exames/referencia/{exam_code}")
async def obter_referencia_get(
    exam_code: str,
    age: Optional[int] = Query(None, description="Idade do paciente"),
    gender: Optional[str] = Query(None, description="Sexo do paciente (Masculino/Feminino)")
):
    """Obter valores de referência para exame (GET)"""
    try:
        resultado = mcp_obter_valores_referencia({
            "exam_code": exam_code,
            "age": age,
            "gender": gender
        })
        return resultado
    except Exception as e:
        logger.error(f"Erro ao obter valores de referência: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def check_env_vars():
    """Verifica se as variáveis de ambiente necessárias estão configuradas"""
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("ERRO: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias")
        sys.exit(1)

def start_server(host="0.0.0.0", port=8000):
    """Inicia o servidor HTTP"""
    check_env_vars()
    uvicorn.run("http_server:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    check_env_vars()
    # Carregar configurações do arquivo .env se existir
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Obter porta do ambiente ou usar 8000 por padrão
    port = int(os.getenv("MCP_HTTP_PORT", 8000))
    
    print(f"Iniciando BioLab.Ai MCP HTTP API na porta {port}...")
    start_server(port=port)
