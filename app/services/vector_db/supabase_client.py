from typing import Dict, List, Any
import json
import uuid
from supabase import create_client, Client
from app.core.config import settings
from app.services.llm.openai_client import get_embeddings

# Inicializar cliente Supabase
supabase: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_KEY
)

async def store_document_vectors(
    document_data: Dict[str, Any], 
    filename: str, 
    user_id: str
) -> str:
    """
    Armazena um documento com seus vetores no Supabase.
    
    Args:
        document_data: Dados extraídos do documento
        filename: Nome do arquivo original
        user_id: ID do usuário
        
    Returns:
        ID do documento armazenado
    """
    # Gerar UUID para o documento
    document_id = str(uuid.uuid4())
    
    # Preparar metadados do documento
    metadata = document_data.get("metadata", {})
    metadata.update({
        "filename": filename,
        "user_id": user_id,
        "document_id": document_id
    })
    
    # Armazenar documento na tabela de documentos
    await store_document_metadata(document_id, metadata)
    
    # Processar e armazenar exames individuais como vetores
    exams = document_data.get("exams", [])
    for exam in exams:
        await store_exam_vector(exam, document_id, user_id)
    
    return document_id

async def store_document_metadata(document_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Armazena os metadados do documento.
    
    Args:
        document_id: ID do documento
        metadata: Metadados do documento
        
    Returns:
        Resposta da inserção
    """
    # Inserir na tabela de documentos
    response = supabase.table("documents").insert({
        "id": document_id,
        "metadata": json.dumps(metadata),
        "created_at": metadata.get("processed_at")
    }).execute()
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao armazenar metadados: {response['error']}")
    
    return response.data

async def store_exam_vector(exam: Dict[str, Any], document_id: str, user_id: str) -> Dict[str, Any]:
    """
    Armazena um exame como vetor pesquisável.
    
    Args:
        exam: Dados do exame
        document_id: ID do documento pai
        user_id: ID do usuário
        
    Returns:
        Resposta da inserção
    """
    # Criar texto para embedding
    text_for_embedding = f"""
    Exame: {exam.get('name')}
    Código: {exam.get('code')}
    Valor: {exam.get('value')} {exam.get('unit')}
    Referência: {exam.get('reference_range', {}).get('text', '')}
    """
    
    # Obter embedding do OpenAI
    embedding = await get_embeddings(text_for_embedding)
    
    # Inserir na tabela de vetores
    response = supabase.table("exam_vectors").insert({
        "document_id": document_id,
        "user_id": user_id,
        "exam_code": exam.get("code"),
        "exam_name": exam.get("name"),
        "exam_value": exam.get("value"),
        "exam_unit": exam.get("unit"),
        "reference_min": exam.get("reference_range", {}).get("min"),
        "reference_max": exam.get("reference_range", {}).get("max"),
        "reference_text": exam.get("reference_range", {}).get("text", ""),
        "content": text_for_embedding,
        "embedding": embedding
    }).execute()
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao armazenar vetor: {response['error']}")
    
    return response.data

async def search_similar_exams(
    query: str, 
    user_id: str, 
    limit: int = 5, 
    exam_code: str = None
) -> List[Dict[str, Any]]:
    """
    Busca exames similares à consulta fornecida.
    
    Args:
        query: Consulta para busca
        user_id: ID do usuário
        limit: Número máximo de resultados
        exam_code: Código específico de exame (opcional)
        
    Returns:
        Lista de exames similares
    """
    # Obter embedding da consulta
    query_embedding = await get_embeddings(query)
    
    # Construir query base
    base_query = (
        supabase.table("exam_vectors")
        .select("*")
        .filter("user_id", "eq", user_id)
    )
    
    # Adicionar filtro por código de exame, se fornecido
    if exam_code:
        base_query = base_query.filter("exam_code", "eq", exam_code)
    
    # Executar busca vetorial
    response = (
        base_query
        .order("embedding", query_embedding, ascending=False)
        .limit(limit)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro na busca vetorial: {response['error']}")
    
    return response.data

async def get_document_by_id(document_id: str) -> Dict[str, Any]:
    """
    Recupera um documento pelo seu ID.
    
    Args:
        document_id: ID do documento
        
    Returns:
        Dados do documento
    """
    response = (
        supabase.table("documents")
        .select("*")
        .filter("id", "eq", document_id)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao recuperar documento: {response['error']}")
    
    if not response.data:
        return None
    
    # Converter metadata de JSON para dict
    if "metadata" in response.data[0]:
        try:
            response.data[0]["metadata"] = json.loads(response.data[0]["metadata"])
        except:
            pass
    
    return response.data[0]

async def get_exams_by_document_id(document_id: str) -> List[Dict[str, Any]]:
    """
    Recupera todos os exames de um documento.
    
    Args:
        document_id: ID do documento
        
    Returns:
        Lista de exames
    """
    response = (
        supabase.table("exam_vectors")
        .select("*")
        .filter("document_id", "eq", document_id)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao recuperar exames: {response['error']}")
    
    return response.data
