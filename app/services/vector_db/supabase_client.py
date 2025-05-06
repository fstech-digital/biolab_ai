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
    
    # Preparar filtros adicionais
    match_filters = {"user_id": user_id}
    
    # Adicionar filtro por código de exame, se fornecido
    if exam_code:
        match_filters["exam_code"] = exam_code
        
    try:
        # Usar função RPC para busca vetorial
        # Esta abordagem é compatível com diferentes versões do supabase-py
        response = (
            supabase.rpc(
                "match_exam_vectors",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,  # Limite de similaridade
                    "match_count": limit,     # Número máximo de resultados
                    "user_filter": user_id    # Filtro por usuário
                }
            ).execute()
        )
        
        # Verificar se houve erro na resposta
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Erro na busca vetorial RPC: {response.error}")
            
        # Garantir que temos dados válidos da resposta
        if hasattr(response, 'data'):
            return response.data
        elif isinstance(response, dict) and 'data' in response:
            return response['data']
        else:
            print("Retornando resposta RPC diretamente")
            return response
            
    except Exception as e:
        # Fallback: Se RPC falhar, tentar consulta simples sem matching vetorial
        print(f"Erro na busca vetorial RPC: {str(e)}")
        print("Usando fallback: consulta simples sem vetores")
        
        try:
            # Construir a consulta de fallback
            query = supabase.table("exam_vectors").select("*").filter("user_id", "eq", user_id)
            
            # Adicionar filtro por código de exame se necessário
            if exam_code:
                query = query.filter("exam_code", "eq", exam_code)
                
            # Adicionar limite e executar
            fallback_response = query.limit(limit).execute()
            
            # Tratar resposta do fallback
            if hasattr(fallback_response, 'data'):
                return fallback_response.data
            elif isinstance(fallback_response, dict) and 'data' in fallback_response:
                return fallback_response['data']
            else:
                return []  # Retornar lista vazia se não conseguir extrair os dados
                
        except Exception as fallback_error:
            print(f"Erro no fallback: {str(fallback_error)}")
            return []  # Retornar lista vazia em caso de erro

async def search_knowledge_vectors(query: str, limit: int = 5, collection_name: str = None) -> List[Dict[str, Any]]:
    """
    Busca vetores na base de conhecimento (planilhas) que são similares à consulta.
    
    Args:
        query: Consulta do usuário
        limit: Número máximo de resultados
        collection_name: Nome da coleção específica para filtrar (opcional)
        
    Returns:
        Lista de vetores de conhecimento similares
    """
    # Obter embedding da consulta
    query_embedding = await get_embeddings(query)
    
    try:
        # Tentar usar função RPC para busca vetorial na base de conhecimento
        params = {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,  # Limite de similaridade
            "match_count": limit     # Número máximo de resultados
        }
        
        # Adicionar filtro por coleção, se fornecido
        if collection_name:
            params["collection_filter"] = collection_name
        
        # Tentar chamar a função RPC
        try:
            response = (
                supabase.rpc(
                    "match_knowledge_vectors",
                    params
                ).execute()
            )
            
            # Verificar se houve erro na resposta
            if hasattr(response, 'error') and response.error:
                raise Exception(f"Erro na busca vetorial RPC: {response.error}")
                
            # Garantir que temos dados válidos da resposta
            if hasattr(response, 'data'):
                return response.data
            elif isinstance(response, dict) and 'data' in response:
                return response['data']
            else:
                print("Retornando resposta RPC diretamente")
                return response
        except Exception as rpc_error:
            # Se falhar na RPC específica, levanta o erro para o fallback
            print(f"Erro específico na função RPC: {str(rpc_error)}")
            raise
            
    except Exception as e:
        # Fallback inteligente: pesquisa baseada no texto usando LIKE ou ILIKE
        print(f"Erro na busca vetorial de conhecimento: {str(e)}")
        print("Usando fallback inteligente baseado em texto")
        
        try:
            # Quebrar a consulta em palavras-chave
            keywords = [k.strip().lower() for k in query.split() if len(k.strip()) > 3]
            
            if not keywords:
                # Se não tiver palavras-chave suficientes, usa termos genéricos relevantes
                print("Consulta muito curta, usando termos gerais")
                results = []
                
                # Tenta fazer uma busca mais básica com o que temos
                fallback_response = supabase.table("knowledge_vectors").select("*").limit(limit).execute()
                
                if hasattr(fallback_response, 'data') and fallback_response.data:
                    # Marca a fonte explícita para o usuário saber que não é altamente relevante
                    for item in fallback_response.data:
                        if 'source' not in item or not item['source']:
                            item['source'] = 'informação geral (fallback)'
                    return fallback_response.data
                return []
            
            print(f"Usando palavras-chave para busca textual: {keywords}")
            
            # Construir consulta para cada palavra-chave com ILIKE 
            query = supabase.table("knowledge_vectors").select("*")
            
            # Adiciona filtro para buscar conteúdo relacionado a qualquer keyword
            # Para simplificar e evitar problemas de sintaxe, vamos usar uma abordagem diferente
            # Com apenas um filtro ILIKE que busca por qualquer uma das palavras-chave
            keyword_pattern = "%" + "%|%".join(keywords[:3]) + "%" # ex: %palavra1%|%palavra2%|%palavra3%
            query = query.filter("content", "ilike", keyword_pattern)
            
            # Adicionar filtro por coleção se necessário
            if collection_name:
                query = query.filter("collection_name", "eq", collection_name)
                
            # Executar a consulta
            fallback_response = query.limit(limit).execute()
            
            # Tratar resposta do fallback
            if hasattr(fallback_response, 'data') and fallback_response.data:
                return fallback_response.data
            elif isinstance(fallback_response, dict) and 'data' in fallback_response:
                return fallback_response['data']
            else:
                # Se não encontrar nada com a busca por keywords, tenta uma última abordagem
                print("Nenhum resultado encontrado com keywords, tentando busca mais ampla")
                final_response = supabase.table("knowledge_vectors").select("*").limit(limit).execute()
                
                if hasattr(final_response, 'data'):
                    return final_response.data
                return []
                
        except Exception as fallback_error:
            print(f"Erro no fallback da base de conhecimento: {str(fallback_error)}")
            return []  # Retornar lista vazia em caso de erro

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
