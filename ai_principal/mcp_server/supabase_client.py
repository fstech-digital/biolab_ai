"""
Módulo Supabase Client para MCP Server BioLab.Ai
Cliente para acesso ao banco de dados Supabase utilizado pelo BioLab.Ai.
Export todas as funções necessárias para as ferramentas MCP.
"""
import os
import datetime
from typing import Dict, List, Any, Optional, Union
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializa o cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_exames_paciente(patient_name: str) -> List[Dict[str, Any]]:
    """
    Busca exames no banco vetorial pelo nome do paciente (case-insensitive, substring).
    Args:
        patient_name: Nome ou parte do nome do paciente
    Returns:
        Lista de exames (dicts)
    """
    if not patient_name:
        return []
    # Busca usando ilike para substring case-insensitive
    response = supabase.table("exam_vectors") \
        .select("*") \
        .ilike("patient_name", f"%{patient_name}%") \
        .execute()
    exames = response.data if hasattr(response, 'data') else response.get('data', [])
    return exames

def buscar_exames_por_data(start_date: str, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Busca exames no banco vetorial por intervalo de data de coleta.
    Args:
        start_date: Data inicial no formato DD/MM/AAAA
        end_date: Data final (opcional) no formato DD/MM/AAAA
    Returns:
        Lista de exames (dicts)
    """
    if not start_date:
        return []
    
    # Se end_date não for fornecido, usa start_date como end_date também
    if not end_date:
        end_date = start_date
    
    # Busca usando between para intervalo de datas
    query = supabase.table("exam_vectors").select("*")
    
    # Filtra por data entre start_date e end_date (inclusive)
    query = query.gte("date_collected", start_date)
    query = query.lte("date_collected", end_date)
    
    response = query.execute()
    exames = response.data if hasattr(response, 'data') else response.get('data', [])
    return exames

def buscar_exames_por_tipo(exam_type: str) -> List[Dict[str, Any]]:
    """
    Busca exames no banco vetorial por tipo de exame.
    Args:
        exam_type: Tipo ou nome do exame (ex: hemoglobina, glicose)
    Returns:
        Lista de exames (dicts)
    """
    if not exam_type:
        return []
    
    # Busca usando ilike para substring case-insensitive no nome do exame
    response = supabase.table("exam_vectors") \
        .select("*") \
        .ilike("exam_name", f"%{exam_type}%") \
        .execute()
    exames = response.data if hasattr(response, 'data') else response.get('data', [])
    return exames

def obter_valores_referencia(exam_code: str, age: Optional[int] = None, gender: Optional[str] = None) -> Dict[str, Any]:
    """
    Obtém valores de referência para um exame específico, considerando idade e sexo.
    Args:
        exam_code: Código ou nome do exame
        age: Idade do paciente (opcional)
        gender: Sexo do paciente (opcional, 'Masculino' ou 'Feminino')
    Returns:
        Dicionário com valores de referência
    """
    if not exam_code:
        return {"min": None, "max": None, "text": ""}
    
    # Busca um exemplo deste exame no banco para obter valores de referência
    query = supabase.table("exam_vectors").select("*")
    query = query.ilike("exam_name", f"%{exam_code}%")
    
    # Se idade for fornecida, priorizar exames de pacientes com idade semelhante
    if age is not None:
        # Poderia implementar uma lógica mais complexa aqui para matching por idade
        pass
        
    # Se sexo for fornecido, filtrar por sexo
    if gender:
        query = query.eq("patient_gender", gender)
    
    # Limitar a 1 resultado apenas para pegar valores de referência
    query = query.limit(1)
    
    response = query.execute()
    exames = response.data if hasattr(response, 'data') else response.get('data', [])
    
    if not exames:
        return {"min": None, "max": None, "text": ""}
    
    # Retorna os valores de referência do primeiro exame encontrado
    exame = exames[0]
    return {
        "min": exame.get("reference_min"),
        "max": exame.get("reference_max"),
        "text": exame.get("reference_text", ""),
        "unit": exame.get("exam_unit", "")
    }
