"""
Script para verificar o conteúdo da base de dados
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    vector_collection = os.getenv("VECTOR_COLLECTION", "biolab_documents")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no .env")
    
    client: Client = create_client(supabase_url, supabase_key)
    
    print(f"Conectado ao Supabase: {supabase_url}")
    print(f"Consultando a coleção: {vector_collection}")
    
    # Listar todas as coleções
    print("\n=== Coleções Disponíveis ===")
    try:
        collections = client.table("information_schema.tables").select("table_name").eq("table_schema", "public").execute()
        for table in collections.data:
            print(f"- {table['table_name']}")
    except Exception as e:
        print(f"Erro ao listar coleções: {e}")
    
    # Listar todos os documentos
    print(f"\n=== Documentos em {vector_collection} ===")
    try:
        documents = client.table(vector_collection).select("*").limit(10).execute()
        
        if documents.data:
            print(f"Total de documentos: {len(documents.data)}")
            print("\nPrimeiros 3 documentos (sem embeddings):")
            
            for i, doc in enumerate(documents.data[:3], 1):
                # Remover vetores para facilitar visualização
                doc_display = doc.copy()
                if 'embedding' in doc_display:
                    embedding_len = len(doc_display['embedding']) if isinstance(doc_display['embedding'], list) else 0
                    doc_display['embedding'] = f"[Vector com {embedding_len} dimensões]"
                
                print(f"\nDocumento {i}:")
                print(json.dumps(doc_display, indent=2, ensure_ascii=False))
        else:
            print("Nenhum documento encontrado.")
    except Exception as e:
        print(f"Erro ao listar documentos: {e}")
    
    # Verificar se há documentos com o nome "Lazaro"
    print("\n=== Busca por 'Lazaro' ===")
    try:
        # Tentar buscar em diferentes campos
        lazaro_docs = client.table(vector_collection).select("*").filter("content", "ilike", "%Lazaro%").execute()
        print(f"Documentos com 'Lazaro' no conteúdo: {len(lazaro_docs.data)}")
        
        lazaro_meta_docs = client.table(vector_collection).select("*").filter("metadata::text", "ilike", "%Lazaro%").execute()
        print(f"Documentos com 'Lazaro' nos metadados: {len(lazaro_meta_docs.data)}")
        
        if lazaro_meta_docs.data:
            print("\nExemplo de metadados encontrados:")
            for doc in lazaro_meta_docs.data[:1]:
                if 'metadata' in doc:
                    print(json.dumps(doc['metadata'], indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erro na busca por 'Lazaro': {e}")

if __name__ == "__main__":
    main()