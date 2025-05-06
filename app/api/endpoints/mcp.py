from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.core.security import get_current_user

# Importar as ferramentas MCP
import sys
import os
# Adicionar diretório do MCP server ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai_principal/mcp_server')))

try:
    from mcp_tools import (
        mcp_buscar_exames_paciente,
        mcp_buscar_exames_por_data,
        mcp_buscar_exames_por_tipo,
        mcp_obter_valores_referencia,
        get_available_tools,
        execute_tool
    )
except ImportError:
    # Fallback para imports relativos
    from ai_principal.mcp_server.mcp_tools import (
        mcp_buscar_exames_paciente,
        mcp_buscar_exames_por_data,
        mcp_buscar_exames_por_tipo,
        mcp_obter_valores_referencia,
        get_available_tools,
        execute_tool
    )

router = APIRouter()

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

class ToolRequest(BaseModel):
    tool_name: str = Field(..., description="Nome da ferramenta MCP")
    params: Dict[str, Any] = Field(..., description="Parâmetros para a ferramenta")

# Endpoints da API
@router.get("/tools")
async def list_tools(current_user = Depends(get_current_user)):
    """Lista todas as ferramentas MCP disponíveis"""
    return get_available_tools()

@router.post("/execute")
async def execute_mcp_tool(request: ToolRequest, current_user = Depends(get_current_user)):
    """Executa uma ferramenta MCP pelo nome"""
    result = execute_tool(request.tool_name, request.params)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# Endpoints específicos para cada ferramenta MCP
@router.post("/exames/paciente")
async def buscar_por_paciente(request: BuscaPacienteRequest, current_user = Depends(get_current_user)):
    """Buscar exames por nome do paciente"""
    try:
        resultado = mcp_buscar_exames_paciente(request.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exames/data")
async def buscar_por_data(request: BuscaDataRequest, current_user = Depends(get_current_user)):
    """Buscar exames por intervalo de data"""
    try:
        resultado = mcp_buscar_exames_por_data(request.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exames/tipo")
async def buscar_por_tipo(request: BuscaTipoRequest, current_user = Depends(get_current_user)):
    """Buscar exames por tipo"""
    try:
        resultado = mcp_buscar_exames_por_tipo(request.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exames/referencia")
async def obter_referencia(request: ValoresReferenciaRequest, current_user = Depends(get_current_user)):
    """Obter valores de referência para exame"""
    try:
        resultado = mcp_obter_valores_referencia(request.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints alternativos usando GET (para facilitar testes)
@router.get("/exames/paciente/{patient_name}")
async def buscar_por_paciente_get(patient_name: str, current_user = Depends(get_current_user)):
    """Buscar exames por nome do paciente (GET)"""
    try:
        resultado = mcp_buscar_exames_paciente({"patient_name": patient_name})
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exames/data/")
async def buscar_por_data_get(
    start_date: str = Query(..., description="Data inicial (DD/MM/AAAA)"),
    end_date: Optional[str] = Query(None, description="Data final (DD/MM/AAAA)"),
    current_user = Depends(get_current_user)
):
    """Buscar exames por intervalo de data (GET)"""
    try:
        resultado = mcp_buscar_exames_por_data({"start_date": start_date, "end_date": end_date})
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exames/tipo/{exam_type}")
async def buscar_por_tipo_get(exam_type: str, current_user = Depends(get_current_user)):
    """Buscar exames por tipo (GET)"""
    try:
        resultado = mcp_buscar_exames_por_tipo({"exam_type": exam_type})
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exames/referencia/")
async def obter_referencia_get(
    exam_code: str = Query(..., description="Código ou nome do exame"),
    age: Optional[int] = Query(None, description="Idade do paciente"),
    gender: Optional[str] = Query(None, description="Sexo do paciente (Masculino/Feminino)"),
    current_user = Depends(get_current_user)
):
    """Obter valores de referência para exame (GET)"""
    try:
        resultado = mcp_obter_valores_referencia({"exam_code": exam_code, "age": age, "gender": gender})
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
