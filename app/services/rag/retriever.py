from typing import Dict, List, Any
import re
from app.services.vector_db.supabase_client import search_similar_exams, search_knowledge_vectors
from app.services.llm.openai_client import get_embeddings

async def get_relevant_context(query: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Obtém contexto relevante para a consulta do usuário, focando nos exames específicos.
    
    Versão simplificada para MVP que prioriza exames diretamente relacionados à consulta do usuário.
    
    Args:
        query: Consulta do usuário
        user_id: ID do usuário
        
    Returns:
        Lista de documentos relevantes
    """
    # Detectar se é uma saudação ou mensagem muito curta/genérica
    if is_greeting_or_simple_query(query):
        return []
    
    context = []
    
    # Buscar exames específicos do usuário relacionados à consulta
    exams_context = await search_similar_exams(query, user_id)
    
    # Se encontramos exames específicos, retorná-los diretamente
    if exams_context:
        return exams_context[:5]  # Limitamos a 5 resultados para manter o contexto conciso
    
    # Caso não encontre exames específicos, buscar conhecimento básico
    # apenas sobre os termos mencionados na consulta (simplificado)
    knowledge_context = await search_knowledge_vectors(query, limit=3)
    
    return knowledge_context

def is_greeting_or_simple_query(query: str) -> bool:
    """
    Verifica se a consulta é uma saudação ou mensagem muito curta/genérica.
    
    Args:
        query: Consulta do usuário
        
    Returns:
        True se a consulta é uma saudação ou muito curta, False caso contrário
    """
    # Lista de saudações e mensagens genéricas que não precisam de contexto
    greetings = [
        "oi", "olá", "ola", "hi", "hello", "hey", "bom dia", "boa tarde", "boa noite",
        "como vai", "tudo bem", "como você está", "como voce esta"
    ]
    
    query_lower = query.lower().strip()
    
    # Verificar se a consulta é apenas uma saudação ou muito curta
    if any(greeting == query_lower for greeting in greetings) or len(query_lower.split()) <= 2:
        return True
    
    return False

def extract_exam_codes(query: str) -> List[str]:
    """
    Extrai possíveis códigos de exames mencionados na consulta.
    
    Args:
        query: Consulta do usuário
        
    Returns:
        Lista de códigos de exames identificados
    """
    # Lista de códigos de exames comuns
    common_exam_codes = [
        "HEMOGLOBINA", "HEMATOCRITO", "LEUCOCITOS", "PLAQUETAS",
        "COLESTEROL_TOTAL", "HDL", "LDL", "TRIGLICERIDEOS",
        "CREATININA", "UREIA", "GLICOSE",
        "ALT", "AST", "FOSFATASE_ALCALINA", "GAMA_GT"
    ]
    
    # Versões normalizadas com espaços e sem underscore
    normalized_codes = {code.replace("_", " "): code for code in common_exam_codes}
    
    # Verificar menções diretas de códigos de exames
    found_codes = []
    query_upper = query.upper()
    
    # Verificar códigos exatos
    for code in common_exam_codes:
        if code in query_upper:
            found_codes.append(code)
    
    # Verificar versões normalizadas
    for normalized, code in normalized_codes.items():
        if normalized.upper() in query_upper and code not in found_codes:
            found_codes.append(code)
    
    # Buscar por padrões de termos comuns de exames
    exam_patterns = {
        r'\b(HEMOGLOBINA|HB|HGB)\b': 'HEMOGLOBINA',
        r'\b(HEMATOCRITO|HCT|HT)\b': 'HEMATOCRITO',
        r'\b(LEUCOCITOS|LEUCÓCITOS|WBC|GLOBULOS BRANCOS)\b': 'LEUCOCITOS',
        r'\b(PLAQUETAS|PLT)\b': 'PLAQUETAS',
        r'\b(COLESTEROL TOTAL|CT)\b': 'COLESTEROL_TOTAL',
        r'\b(TRIGLICERIDEOS|TRIGLICERÍDEOS|TG)\b': 'TRIGLICERIDEOS',
        r'\b(GLICOSE|GLICEMIA|GLI)\b': 'GLICOSE'
    }
    
    for pattern, code in exam_patterns.items():
        if re.search(pattern, query_upper) and code not in found_codes:
            found_codes.append(code)
    
    return found_codes

async def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Reordena os resultados com base na relevância para a consulta.
    
    Args:
        query: Consulta do usuário
        results: Lista de resultados a serem reordenados
        top_k: Número de resultados a retornar
        
    Returns:
        Lista reordenada de resultados
    """
    if not results or len(results) <= 1:
        return results
    
    # Para MVP, vamos assumir que a ordem já está correta
    # Em implementações futuras, podemos usar um modelo específico para reranking
    
    return results[:top_k]
