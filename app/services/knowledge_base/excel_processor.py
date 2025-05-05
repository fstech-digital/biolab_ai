"""
Módulo para processar planilhas Excel e transformá-las em conhecimento vetorial
para o sistema BioLab.Ai.

Este módulo lê planilhas Excel específicas, processa seu conteúdo e armazena
os dados como embeddings no banco de dados vetorial do Supabase.
"""
import os
import uuid
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import asyncio
from app.services.llm.openai_client import get_embeddings
from app.services.vector_db.supabase_client import supabase

# Tamanho do chunk para processamento
CHUNK_SIZE = 1000

async def process_excel_file(
    file_path: str,
    collection_name: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Processa um arquivo Excel, extraindo seu conteúdo e gerando embeddings
    para armazenamento no Supabase.
    
    Args:
        file_path: Caminho do arquivo Excel
        collection_name: Nome da coleção para armazenar no banco
        description: Descrição da planilha
        
    Returns:
        Informações sobre o processamento
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Ler planilha Excel
        df = pd.read_excel(file_path)
        
        # Informações básicas
        file_name = os.path.basename(file_path)
        sheet_count = len(pd.ExcelFile(file_path).sheet_names)
        row_count = df.shape[0]
        col_count = df.shape[1]
        
        # Criar ID para a planilha
        sheet_id = str(uuid.uuid4())
        
        # Processar conteúdo
        chunks = await extract_chunks_from_excel(df)
        
        # Gerar embeddings e armazenar no banco
        stored_count = 0
        for chunk in chunks:
            try:
                # Log para debug do conteúdo que está sendo processado
                print(f"[DEBUG] Processando chunk {stored_count+1}/{len(chunks)} - Tamanho do conteúdo: {len(chunk['content'])} caracteres")
                
                # Verificar se o conteúdo é válido para evitar requisições inválidas
                if not chunk['content'] or len(chunk['content'].strip()) < 10:
                    print(f"[AVISO] Conteúdo muito curto ou vazio, pulando: {chunk['content']}")
                    continue
                
                # Gerar embedding para o conteúdo
                try:
                    embedding = await get_embeddings(chunk['content'])
                    # Verificar se o embedding foi gerado corretamente
                    if not embedding or len(embedding) == 0:
                        print(f"[ERRO] Embedding não gerado corretamente: {embedding}")
                        continue
                    
                    print(f"[DEBUG] Embedding gerado com sucesso: {len(embedding)} dimensões")
                except Exception as e:
                    print(f"[ERRO] Falha ao gerar embedding: {repr(e)}")
                    # Esperar um pouco antes de tentar o próximo para evitar sobrecarga da API
                    await asyncio.sleep(2)
                    continue
                
                # Armazenar no banco vetorial
                result = await store_knowledge_vector(
                    sheet_id=sheet_id,
                    collection_name=collection_name,
                    content=chunk['content'],
                    metadata=chunk['metadata'],
                    embedding=embedding
                )
                
                if result:
                    stored_count += 1
                    print(f"[INFO] Vetor {stored_count} armazenado com sucesso!")
                else:
                    print(f"[ALERTA] Falha ao armazenar vetor {stored_count+1}")
                
                # Pequena pausa entre processamentos para evitar sobrecarga da API
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[ERRO] Erro não tratado no processamento do chunk: {repr(e)}")
        
        # Retornar informações sobre o processamento
        return {
            "sheet_id": sheet_id,
            "file_name": file_name,
            "collection_name": collection_name,
            "description": description,
            "sheet_count": sheet_count,
            "row_count": row_count,
            "col_count": col_count,
            "chunks_processed": len(chunks),
            "chunks_stored": stored_count,
            "status": "success"
        }
        
    except Exception as e:
        # Logar e retornar erro
        print(f"Erro ao processar planilha: {str(e)}")
        return {
            "file_name": os.path.basename(file_path) if file_path else "",
            "collection_name": collection_name,
            "status": "error",
            "error": str(e)
        }

async def extract_chunks_from_excel(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extrai chunks de conteúdo de uma planilha Excel.
    
    Args:
        df: DataFrame do pandas
        
    Returns:
        Lista de chunks com conteúdo e metadados
    """
    chunks = []
    
    # Estratégia 1: Por colunas como propriedades
    # Esta é a melhor abordagem para dados estruturados
    col_names = df.columns.tolist()
    
    # Processar linha por linha
    for i, row in df.iterrows():
        content = f"Informação de exame/análise:\n"
        row_data = {}
        
        # Adicionar cada coluna ao conteúdo
        for col in col_names:
            value = row[col]
            # Ignorar valores nulos
            if pd.isna(value) or value == "" or value is None:
                continue
                
            content += f"{col}: {value}\n"
            row_data[col] = str(value)
        
        if len(content) > 0:
            chunks.append({
                "content": content,
                "metadata": {
                    "row": i,
                    "data": row_data
                }
            })
    
    # Estratégia 2: Por grupos de linhas
    # Combinar múltiplas linhas em um único chunk
    row_buffer = []
    buffer_size = 0
    
    for i, row in df.iterrows():
        row_content = " | ".join([f"{col}: {val}" for col, val in row.items() if not pd.isna(val)])
        row_size = len(row_content)
        
        # Se o buffer estiver vazio ou não estourar o limite, adicionar ao buffer
        if buffer_size == 0 or buffer_size + row_size <= CHUNK_SIZE:
            row_buffer.append((i, row_content))
            buffer_size += row_size
        else:
            # Processar buffer atual e criar novo chunk
            if row_buffer:
                content = "\n".join([content for _, content in row_buffer])
                rows = [idx for idx, _ in row_buffer]
                chunks.append({
                    "content": content,
                    "metadata": {
                        "rows": rows,
                        "strategy": "group_rows"
                    }
                })
            
            # Reiniciar buffer
            row_buffer = [(i, row_content)]
            buffer_size = row_size
    
    # Processar buffer restante
    if row_buffer:
        content = "\n".join([content for _, content in row_buffer])
        rows = [idx for idx, _ in row_buffer]
        chunks.append({
            "content": content,
            "metadata": {
                "rows": rows,
                "strategy": "group_rows"
            }
        })
    
    return chunks

async def store_knowledge_vector(
    sheet_id: str,
    collection_name: str,
    content: str,
    metadata: Dict[str, Any],
    embedding: List[float]
) -> bool:
    """
    Armazena um vetor de conhecimento no Supabase.
    
    Args:
        sheet_id: ID da planilha
        collection_name: Nome da coleção
        content: Conteúdo textual
        metadata: Metadados adicionales
        embedding: Vetor de embedding
        
    Returns:
        True se armazenado com sucesso, False caso contrário
    """
    try:
        # Validação dos parâmetros antes de inserir
        if not sheet_id or not collection_name or not content or not embedding:
            print(f"[ERRO] Parâmetros inválidos para inserção no Supabase:")
            print(f"  - sheet_id: {sheet_id}")
            print(f"  - collection_name: {collection_name}")
            print(f"  - content: {'Presente' if content else 'Ausente'} (tamanho: {len(content) if content else 0})")
            print(f"  - metadata: {metadata}")
            print(f"  - embedding: {'Presente' if embedding else 'Ausente'} (tamanho: {len(embedding) if embedding else 0})")
            return False
            
        # Verificar se embedding é válido
        if not isinstance(embedding, list) or len(embedding) == 0:
            print(f"[ERRO] Embedding inválido: {type(embedding)}, {embedding}")
            return False
            
        print(f"[DEBUG] Dados para inserção no Supabase:")
        print(f"  - ID gerado: {str(uuid.uuid4())[0:8]}...")
        print(f"  - sheet_id: {sheet_id}")
        print(f"  - collection_name: {collection_name}")
        print(f"  - content (tamanho): {len(content)} caracteres")
        print(f"  - embedding: {type(embedding)} com {len(embedding)} dimensões")
        
        # Inserir no banco de dados
        record_id = str(uuid.uuid4())
        response = supabase.table("knowledge_vectors").insert({
            "id": record_id,
            "sheet_id": sheet_id,
            "collection_name": collection_name,
            "content": content,
            "metadata": metadata,
            "embedding": embedding
        }).execute()

        # Logging detalhado do response
        print(f"[DEBUG] Supabase insert response para ID {record_id[0:8]}...")
        if hasattr(response, 'error'):
            print("[DEBUG] response.error:", response.error)
        if hasattr(response, 'data'):
            print("[DEBUG] response.data:", response.data)
        if hasattr(response, 'status_code'):
            print("[DEBUG] response.status_code:", response.status_code)
        
        # Transformar para dict se possível para facilitar inspeção
        response_dict = {}
        try:
            if hasattr(response, 'json'):
                response_dict = response.json()
                print("[DEBUG] response.json:", response_dict)
        except Exception as e:
            print(f"[DEBUG] Não foi possível converter response para JSON: {repr(e)}")
            
        if isinstance(response, dict):
            response_dict = response
            print("[DEBUG] response (dict):", response_dict)

        # Verificar se houve erro
        # Para objetos do supabase-py, normalmente há um atributo .error
        if hasattr(response, 'error') and response.error:
            print(f"[ERRO] Erro ao armazenar vetor (Supabase): {response.error}")
            return False
        if isinstance(response, dict) and 'error' in response and response['error']:
            print(f"[ERRO] Erro ao armazenar vetor (Supabase dict): {response['error']}")
            return False
        
        # Verificar o atributo 'data' da resposta para confirmação
        if hasattr(response, 'data') and response.data:
            print(f"[DEBUG] Inserção confirmada com dados retornados: {response.data}")
        else:
            print(f"[AVISO] Inserção parece ter sucesso, mas sem dados retornados")
            
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao armazenar vetor (Exception): {repr(e)}")
        import traceback
        print(f"[ERRO] Traceback: {traceback.format_exc()}")
        return False

async def search_knowledge_base(
    query: str,
    collection_name: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Busca na base de conhecimento usando embeddings.
    
    Args:
        query: Consulta de busca
        collection_name: Nome da coleção para filtrar (opcional)
        limit: Número máximo de resultados
        
    Returns:
        Lista de documentos relevantes
    """
    try:
        # Gerar embedding para a consulta
        query_embedding = await get_embeddings(query)
        
        # Construir consulta base
        base_query = supabase.table("knowledge_vectors").select("*")
        
        # Filtrar por coleção, se fornecida
        if collection_name:
            base_query = base_query.filter("collection_name", "eq", collection_name)
        
        # Executar busca vetorial
        response = (
            base_query
            .order("embedding", query_embedding, ascending=False)
            .limit(limit)
            .execute()
        )
        
        # Verificar se houve erro
        if "error" in response:
            print(f"Erro na busca: {response['error']}")
            return []
        
        return response.data
        
    except Exception as e:
        print(f"Erro na busca de conhecimento: {str(e)}")
        return []
