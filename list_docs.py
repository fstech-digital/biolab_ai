#!/usr/bin/env python
"""
Script simples para listar documentos e exames no Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar cliente do Supabase
from app.services.vector_db.supabase_client import supabase

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal para listar documentos e exames no Supabase"""
    print("\n===== LISTAGEM DE DOCUMENTOS NO SUPABASE =====\n")
    
    try:
        # Buscar todos os documentos
        doc_response = supabase.table("documents").select("*").execute()
        
        if hasattr(doc_response, 'data') and doc_response.data:
            print(f"Total de documentos: {len(doc_response.data)}")
            print("\nLista de documentos:")
            
            for i, doc in enumerate(doc_response.data, 1):
                doc_id = doc.get('id')
                metadata = doc.get('metadata', {})
                
                filename = metadata.get('filename', 'N/A')
                name = metadata.get('name', 'N/A')
                lab_type = metadata.get('lab_type', 'N/A')
                
                print(f"\n{i}. Document ID: {doc_id[:8]}...")
                print(f"   Filename: {filename}")
                print(f"   Name: {name}")
                print(f"   Lab Type: {lab_type}")
                
                # Buscar exames associados a este documento
                exam_response = supabase.table("exam_vectors").select("*").filter("document_id", "eq", doc_id).execute()
                
                if hasattr(exam_response, 'data') and exam_response.data:
                    exams = exam_response.data
                    print(f"   Total de exames: {len(exams)}")
                    
                    # Mostrar apenas os primeiros 5 exames de cada documento
                    for j, exam in enumerate(exams[:5], 1):
                        exam_name = exam.get('exam_name', 'N/A')
                        exam_value = exam.get('exam_value', 'N/A')
                        exam_unit = exam.get('exam_unit', '')
                        
                        print(f"     {j}. {exam_name}: {exam_value} {exam_unit}")
                    
                    if len(exams) > 5:
                        print(f"     ... e mais {len(exams) - 5} exames")
                else:
                    print("   Nenhum exame encontrado para este documento")
            
            # Buscar exames específicos de eritrócitos e hemoglobina do Altamiro
            print("\n\n===== BUSCANDO EXAMES ESPECÍFICOS =====\n")
            
            # Buscar exames de eritrócitos
            print("Buscando exames de eritrócitos...")
            erit_response = supabase.table("exam_vectors").select("*").filter("exam_name", "ilike", "%eritr%").execute()
            
            if hasattr(erit_response, 'data') and erit_response.data:
                for i, exam in enumerate(erit_response.data, 1):
                    doc_id = exam.get('document_id')
                    exam_name = exam.get('exam_name')
                    exam_value = exam.get('exam_value')
                    exam_unit = exam.get('exam_unit', '')
                    
                    print(f"{i}. Doc ID: {doc_id[:8]}... | {exam_name}: {exam_value} {exam_unit}")
                    
                    # Buscar metadados do documento
                    doc_meta = supabase.table("documents").select("metadata").filter("id", "eq", doc_id).execute()
                    if hasattr(doc_meta, 'data') and doc_meta.data:
                        filename = doc_meta.data[0].get('metadata', {}).get('filename', 'N/A')
                        name = doc_meta.data[0].get('metadata', {}).get('name', 'N/A')
                        print(f"   Arquivo: {filename}")
                        print(f"   Nome: {name}")
            else:
                print("Nenhum exame de eritrócitos encontrado")
            
            # Buscar exames por nome de paciente
            print("\nBuscando documentos relacionados a 'Altamiro'...")
            
            # Infelizmente, não podemos filtrar diretamente por JSONB em Supabase
            # Vamos pegar todos e filtrar manualmente pelo nome
            altamiro_docs = []
            for doc in doc_response.data:
                metadata = doc.get('metadata', {})
                name = metadata.get('name', '')
                filename = metadata.get('filename', '')
                
                if 'altamiro' in name.lower() or 'altamiro' in filename.lower():
                    altamiro_docs.append(doc)
            
            if altamiro_docs:
                print(f"Encontrados {len(altamiro_docs)} documentos relacionados a 'Altamiro':")
                for i, doc in enumerate(altamiro_docs, 1):
                    doc_id = doc.get('id')
                    metadata = doc.get('metadata', {})
                    filename = metadata.get('filename', 'N/A')
                    
                    print(f"{i}. Doc ID: {doc_id[:8]}... | Arquivo: {filename}")
                    
                    # Buscar exames deste documento
                    exam_response = supabase.table("exam_vectors").select("*").filter("document_id", "eq", doc_id).execute()
                    
                    if hasattr(exam_response, 'data') and exam_response.data:
                        print(f"   Total de exames: {len(exam_response.data)}")
                        for j, exam in enumerate(exam_response.data, 1):
                            exam_name = exam.get('exam_name', 'N/A')
                            exam_value = exam.get('exam_value', 'N/A')
                            exam_unit = exam.get('exam_unit', '')
                            
                            print(f"   {j}. {exam_name}: {exam_value} {exam_unit}")
                    else:
                        print("   Nenhum exame encontrado para este documento")
            else:
                print("Nenhum documento encontrado relacionado a 'Altamiro'")
            
        else:
            print("Nenhum documento encontrado no Supabase")
    
    except Exception as e:
        print(f"Erro ao consultar Supabase: {str(e)}")

if __name__ == "__main__":
    main()
