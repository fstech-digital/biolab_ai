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
    try:
        # Validações básicas
        if not document_data:
            raise ValueError("Dados do documento são inválidos ou vazios")
            
        if not isinstance(document_data, dict):
            raise TypeError(f"Dados do documento devem ser um dicionário, recebido: {type(document_data)}")
            
        print(f"[INFO] Iniciando armazenamento do documento no banco de dados. Filename: {filename}")
        
        # Gerar UUID para o documento
        document_id = str(uuid.uuid4())
        print(f"[INFO] Document ID gerado: {document_id}")
        
        # Preparar metadados do documento
        metadata = document_data.get("metadata", {})
        if not metadata:
            print("[AVISO] Metadados vazios, criando estrutura básica")
            metadata = {}
            
        metadata.update({
            "filename": filename,
            "user_id": user_id,
            "document_id": document_id
        })
        
        print(f"[INFO] Metadados preparados: {metadata}")
        
        # Armazenar documento na tabela de documentos
        print("[INFO] Armazenando metadados do documento...")
        await store_document_metadata(document_id, metadata)
        print("[INFO] Metadados armazenados com sucesso")
        
        # Processar e armazenar exames individuais como vetores
        exams = document_data.get("exams", [])
        print(f"[INFO] Total de exames encontrados: {len(exams)}")
        
        if not exams:
            print("[AVISO] Nenhum exame encontrado no documento")
            return document_id
        
        # Propagar campos essenciais dos metadados para cada exame
        print(f"[DEBUG] Exemplo de exame antes da propagação: {exams[0] if exams else None}")
        
        # Mapeamento explícito dos campos essenciais para garantir preenchimento correto
        for i, exam in enumerate(exams):
            try:
                # Nome do paciente (campo crítico para as buscas)
                exam["patient_name"] = metadata.get("name", "")
                if not exam.get("patient_name"):
                    print(f"[AVISO] Nome do paciente não encontrado nos metadados. Usando valor padrão.")
                    exam["patient_name"] = "Paciente"
                    
                # Idade
                exam["patient_age"] = metadata.get("age", None)
                # Sexo
                exam["patient_gender"] = metadata.get("gender", "")
                # Datas
                exam["date_collected"] = metadata.get("date_collected", "")
                exam["date_reported"] = metadata.get("date_reported", "")
                # Outros campos úteis
                exam["filename"] = metadata.get("filename", "")
                exam["user_id"] = metadata.get("user_id", "")
                exam["document_id"] = metadata.get("document_id", "")
                
                if i == 0:  # Apenas mostra o primeiro para não poluir o log
                    print(f"[DEBUG] Primeiro exame após propagação: {exam}")
                    
                # Armazenar exame no banco de dados
                print(f"[INFO] Armazenando exame {i+1}/{len(exams)}: {exam.get('name', 'Desconhecido')}")
                await store_exam_vector(exam, document_id, user_id)
                
            except Exception as e:
                print(f"[ERRO] Falha ao processar exame {i+1}: {str(e)}")
                # Continuar com os próximos exames mesmo se um falhar
        
        print(f"[INFO] Documento armazenado com sucesso. ID: {document_id}")
        return document_id
        
    except Exception as e:
        print(f"[ERRO] Falha ao armazenar documento: {str(e)}")
        # Repassar a exceção para ser tratada no nível superior
        raise

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
        "patient_name": exam.get("patient_name", ""),
        "patient_age": exam.get("patient_age", None),
        "patient_gender": exam.get("patient_gender", ""),
        "date_collected": exam.get("date_collected", ""),
        "date_reported": exam.get("date_reported", ""),
        "filename": exam.get("filename", ""),
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
    Busca simplificada para documentos na base de conhecimento relacionados à consulta.
    Versão MVP focada em eficiência e simplicidade.
    
    Args:
        query: Consulta do usuário
        limit: Número máximo de resultados
        collection_name: Nome da coleção específica para filtrar (opcional)
        
    Returns:
        Lista de documentos de conhecimento relevantes
    """
    try:
        # Abordagem mais simples: busca por palavras-chave diretamente
        # Extrair palavras-chave da consulta (palavras com mais de 3 caracteres)
        keywords = [k.strip().lower() for k in query.split() if len(k.strip()) > 3]
        
        if not keywords:
            # Consulta muito curta, retornar lista vazia
            print("Consulta sem palavras-chave significativas, pulando busca de conhecimento")
            return []
        
        print(f"Buscando conhecimento com palavras-chave: {keywords}")
        
        # Construir consulta básica
        search_query = supabase.table("knowledge_vectors").select("*")
        
        # Aplicar filtro para a primeira palavra-chave
        first_keyword = keywords[0]
        search_query = search_query.filter("content", "ilike", f"%{first_keyword}%")
        
        # Adicionar outras palavras-chave se houver (até 2 para simplicidade)
        if len(keywords) > 1:
            for keyword in keywords[1:3]:  # Limitamos a 3 palavras-chave no total
                # Usar or_ para buscar documentos que contenham qualquer uma das palavras
                search_query = search_query.or_(f"content.ilike.%{keyword}%")
        
        # Aplicar filtro de coleção se fornecido
        if collection_name:
            search_query = search_query.filter("collection_name", "eq", collection_name)
        
        # Executar a consulta com limite
        result = search_query.limit(limit).execute()
        
        # Verificar resultados
        if hasattr(result, 'data') and result.data:
            docs = result.data
            print(f"Encontrados {len(docs)} documentos relevantes para a consulta.")
            
            # Identificar fonte para cada resultado (simplificado)
            for i, item in enumerate(docs, 1):
                collection = item.get("collection_name", "desconhecida")
                print(f"  {i}. Base de conhecimento: {collection}")
            
            return docs
            
        # Se não encontrou resultados, retornar lista vazia
        print("Nenhum documento de conhecimento encontrado para a consulta")
        return []
        
    except Exception as e:
        # Em caso de erro, logar e retornar lista vazia
        print(f"Erro na busca de conhecimento: {str(e)}")
        return []

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
