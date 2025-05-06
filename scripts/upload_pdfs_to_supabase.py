import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from app.services.vector_db.supabase_client import store_document_vectors
from app.services.pdf_extraction.extractor import extract_exam_data

PDFS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'pdfs')
USER_ID = 'mock_user'  # Para MVP

async def upload_all_pdfs():
    files = [f for f in os.listdir(PDFS_DIR) if f.lower().endswith('.pdf')]
    print(f"Encontrados {len(files)} arquivos PDF em {PDFS_DIR}\n")
    for filename in files:
        file_path = os.path.join(PDFS_DIR, filename)
        print(f"Processando: {filename}")
        try:
            doc_data = await extract_exam_data(file_path)
            doc_id = await store_document_vectors(doc_data, filename, USER_ID)
            print(f"  ✔️ Enviado para o Supabase com ID: {doc_id}\n")
        except Exception as e:
            print(f"  ❌ Erro ao processar/enviar {filename}: {e}\n")

if __name__ == "__main__":
    asyncio.run(upload_all_pdfs())
