"""
Ferramentas MCP para o BioLab.Ai
Este módulo define as funções MCP que podem ser expostas
pelo servidor para uso por LLMs e aplicações cliente.
"""
import os
import json
import datetime
from typing import Dict, List, Any, Optional
# Import absoluto para execução direta
try:
    from supabase_client import (
        buscar_exames_paciente,
        buscar_exames_por_data,
        buscar_exames_por_tipo,
        obter_valores_referencia
    )
except ImportError:
    # Fallback para import relativo quando usado como módulo
    from .supabase_client import (
        buscar_exames_paciente,
        buscar_exames_por_data,
        buscar_exames_por_tipo,
        obter_valores_referencia
    )

# Schema em formato MCP
SCHEMAS = {
    "buscar_exames_paciente": {
        "name": "buscar_exames_paciente",
        "description": "Busca exames laboratoriais de um paciente pelo nome.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {
                    "type": "string", 
                    "description": "Nome do paciente a ser buscado."
                }
            },
            "required": ["patient_name"]
        }
    },
    "buscar_exames_por_data": {
        "name": "buscar_exames_por_data",
        "description": "Busca exames laboratoriais por período de data.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string", 
                    "description": "Data inicial no formato DD/MM/AAAA"
                },
                "end_date": {
                    "type": "string", 
                    "description": "Data final no formato DD/MM/AAAA"
                }
            },
            "required": ["start_date"]
        }
    },
    "buscar_exames_por_tipo": {
        "name": "buscar_exames_por_tipo",
        "description": "Busca exames por tipo específico (ex: hemograma, glicose).",
        "parameters": {
            "type": "object",
            "properties": {
                "exam_type": {
                    "type": "string", 
                    "description": "Tipo de exame (ex: hemoglobina, leucocitos, etc.)"
                }
            },
            "required": ["exam_type"]
        }
    },
    "obter_valores_referencia": {
        "name": "obter_valores_referencia",
        "description": "Obtém valores de referência para um tipo de exame, considerando idade e sexo.",
        "parameters": {
            "type": "object",
            "properties": {
                "exam_code": {
                    "type": "string", 
                    "description": "Código do exame (ex: hemoglobina, glicose)"
                },
                "age": {
                    "type": "integer", 
                    "description": "Idade do paciente"
                },
                "gender": {
                    "type": "string", 
                    "description": "Sexo do paciente (Masculino/Feminino)"
                }
            },
            "required": ["exam_code"]
        }
    }
}

# Funções MCP
def mcp_buscar_exames_paciente(params: Dict[str, Any]) -> Dict[str, Any]:
    """Ferramenta MCP para buscar exames por nome de paciente"""
    patient_name = params.get("patient_name", "")
    exames = buscar_exames_paciente(patient_name)
    return {
        "exames": exames,
        "total": len(exames),
        "query": patient_name
    }

def mcp_buscar_exames_por_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """Ferramenta MCP para buscar exames por intervalo de data"""
    start_date = params.get("start_date", "")
    end_date = params.get("end_date", "")
    exames = buscar_exames_por_data(start_date, end_date)
    return {
        "exames": exames,
        "total": len(exames),
        "periodo": {
            "inicio": start_date,
            "fim": end_date if end_date else start_date
        }
    }

def mcp_buscar_exames_por_tipo(params: Dict[str, Any]) -> Dict[str, Any]:
    """Ferramenta MCP para buscar exames por tipo específico"""
    exam_type = params.get("exam_type", "")
    exames = buscar_exames_por_tipo(exam_type)
    return {
        "exames": exames,
        "total": len(exames),
        "tipo": exam_type
    }

def mcp_obter_valores_referencia(params: Dict[str, Any]) -> Dict[str, Any]:
    """Ferramenta MCP para obter valores de referência de um exame"""
    exam_code = params.get("exam_code", "")
    age = params.get("age")
    gender = params.get("gender", "")
    referencia = obter_valores_referencia(exam_code, age, gender)
    return {
        "exame": exam_code,
        "valores_referencia": referencia,
        "perfil": {
            "idade": age,
            "sexo": gender
        }
    }

# Mapeamento de nome da ferramenta para função
MCP_TOOLS = {
    "buscar_exames_paciente": mcp_buscar_exames_paciente,
    "buscar_exames_por_data": mcp_buscar_exames_por_data,
    "buscar_exames_por_tipo": mcp_buscar_exames_por_tipo,
    "obter_valores_referencia": mcp_obter_valores_referencia
}

def get_available_tools() -> List[Dict[str, Any]]:
    """Retorna a lista de todas as ferramentas MCP disponíveis com seus schemas"""
    return list(SCHEMAS.values())

def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Executa uma ferramenta MCP pelo nome"""
    if tool_name not in MCP_TOOLS:
        return {"error": f"Ferramenta '{tool_name}' não encontrada"}
    
    try:
        result = MCP_TOOLS[tool_name](params)
        return result
    except Exception as e:
        return {
            "error": f"Erro ao executar ferramenta: {str(e)}",
            "tool": tool_name,
            "params": params
        }
