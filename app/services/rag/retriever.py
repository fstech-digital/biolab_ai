from typing import Dict, List, Any
import re
from app.services.vector_db.supabase_client import search_similar_exams
from app.services.llm.openai_client import get_embeddings

async def get_relevant_context(
    query: str,
    user_id: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Recupera contexto relevante com base na consulta do usuário.
    
    Args:
        query: Consulta do usuário
        user_id: ID do usuário
        limit: Número máximo de documentos a retornar
        
    Returns:
        Lista de documentos relevantes para a consulta
    """
    # Extrair códigos de exames específicos mencionados na consulta
    exam_codes = extract_exam_codes(query)
    
    # Se temos códigos específicos mencionados, buscar por eles
    context_docs = []
    
    if exam_codes:
        # Buscar para cada código específico
        for exam_code in exam_codes:
            specific_docs = await search_similar_exams(
                query=query,
                user_id=user_id,
                limit=2,  # Limitado por código específico
                exam_code=exam_code
            )
            context_docs.extend(specific_docs)
    
    # Se não encontramos documentos específicos ou queremos adicionar mais contexto
    if not context_docs or len(context_docs) < limit:
        remaining_limit = limit - len(context_docs)
        
        # Busca semântica geral
        general_docs = await search_similar_exams(
            query=query,
            user_id=user_id,
            limit=remaining_limit
        )
        
        # Adicionar à lista de contexto, evitando duplicatas
        existing_ids = {doc.get("id") for doc in context_docs if "id" in doc}
        for doc in general_docs:
            if doc.get("id") not in existing_ids:
                context_docs.append(doc)
                existing_ids.add(doc.get("id"))
    
    # Limitar ao número máximo de documentos
    context_docs = context_docs[:limit]
    
    # Ordenar por relevância (assumindo que os documentos já vêm ordenados)
    return context_docs

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
