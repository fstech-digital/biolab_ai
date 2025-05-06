#!/usr/bin/env python
"""
Script para listar todos os documentos armazenados no Supabase
"""

import os
import sys
import json
from dotenv import load_dotenv

# Adicionar diretório pai ao path para importar módulos do projeto
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from app.services.vector_db.supabase_client import supabase

# Carregar variáveis de ambiente
load_dotenv()

def list_documents():
    """Lista todos os documentos no Supabase"""
    try:
        # Buscar documentos
        response = supabase.table("documents").select("*").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Erro ao buscar documentos: {response.error}")
            return
        
        if hasattr(response, 'data') and response.data:
            print(f"\n===== DOCUMENTOS ({len(response.data)}) =====")
            for i, doc in enumerate(response.data, 1):
                doc_id = doc.get('id', 'N/A')
                metadata = doc.get('metadata', {})
                filename = metadata.get('filename', 'desconhecido')
                name = metadata.get('name', '')
                date = metadata.get('date_reported', '')
                
                print(f"{i}. ID: {doc_id[:8]}... | Arquivo: {filename}")
                if name:
                    print(f"   Nome: {name}")
                if date:
                    print(f"   Data: {date}")
                
                # Tentar buscar exames associados a este documento
                try:
                    exam_response = supabase.table("exam_vectors").select("*").filter("document_id", "eq", doc_id).execute()
                    if hasattr(exam_response, 'data') and exam_response.data:
                        print(f"   Exames associados: {len(exam_response.data)}")
                        for j, exam in enumerate(exam_response.data[:3], 1):  # Mostrar apenas os 3 primeiros
                            exam_name = exam.get('exam_name', 'N/A')
                            exam_value = exam.get('exam_value', 'N/A')
                            exam_unit = exam.get('exam_unit', '')
                            
                            print(f"     {j}. {exam_name}: {exam_value} {exam_unit}")
                        
                        if len(exam_response.data) > 3:
                            print(f"     ... e mais {len(exam_response.data) - 3} exames")
                except Exception as e:
                    print(f"   Erro ao buscar exames: {str(e)}")
                
                print()  # Linha em branco entre documentos
        else:
            print("Nenhum documento encontrado.")
    
    except Exception as e:
        print(f"Erro: {str(e)}")

def list_exams():
    """Lista todos os exames no Supabase"""
    try:
        # Buscar exames
        response = supabase.table("exam_vectors").select("*").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Erro ao buscar exames: {response.error}")
            return
        
        if hasattr(response, 'data') and response.data:
            # Agrupar exames por documento
            exams_by_doc = {}
            for exam in response.data:
                doc_id = exam.get('document_id', 'desconhecido')
                if doc_id not in exams_by_doc:
                    exams_by_doc[doc_id] = []
                exams_by_doc[doc_id].append(exam)
            
            print(f"\n===== EXAMES POR DOCUMENTO ({len(exams_by_doc)}) =====")
            for i, (doc_id, exams) in enumerate(exams_by_doc.items(), 1):
                print(f"{i}. Documento ID: {doc_id[:8]}... | Total exames: {len(exams)}")
                
                # Buscar metadados do documento
                try:
                    doc_response = supabase.table("documents").select("*").filter("id", "eq", doc_id).execute()
                    if hasattr(doc_response, 'data') and doc_response.data:
                        metadata = doc_response.data[0].get('metadata', {})
                        filename = metadata.get('filename', 'desconhecido')
                        name = metadata.get('name', '')
                        
                        print(f"   Arquivo: {filename}")
                        if name:
                            print(f"   Nome: {name}")
                except Exception as e:
                    print(f"   Erro ao buscar documento: {str(e)}")
                
                # Mostrar primeiros 5 exames
                for j, exam in enumerate(exams[:5], 1):
                    exam_name = exam.get('exam_name', 'N/A')
                    exam_value = exam.get('exam_value', 'N/A')
                    exam_unit = exam.get('exam_unit', '')
                    exam_reference = exam.get('reference_range', '')
                    
                    print(f"   {j}. {exam_name}: {exam_value} {exam_unit}")
                    if exam_reference:
                        print(f"      Referência: {exam_reference}")
                
                if len(exams) > 5:
                    print(f"   ... e mais {len(exams) - 5} exames")
                
                print()  # Linha em branco entre documentos
        else:
            print("Nenhum exame encontrado.")
    
    except Exception as e:
        print(f"Erro: {str(e)}")

def search_exams_by_name(name_part):
    """Busca exames por parte do nome"""
    try:
        # Buscar exames pelo nome (case insensitive)
        response = supabase.table("exam_vectors").select("*").filter("exam_name", "ilike", f"%{name_part}%").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Erro ao buscar exames: {response.error}")
            return
        
        if hasattr(response, 'data') and response.data:
            print(f"\n===== EXAMES CONTENDO '{name_part}' ({len(response.data)}) =====")
            for i, exam in enumerate(response.data, 1):
                exam_name = exam.get('exam_name', 'N/A')
                exam_value = exam.get('exam_value', 'N/A')
                exam_unit = exam.get('exam_unit', '')
                doc_id = exam.get('document_id', 'desconhecido')
                
                print(f"{i}. {exam_name}: {exam_value} {exam_unit} | Doc ID: {doc_id[:8]}...")
                
                # Buscar metadados do documento
                try:
                    doc_response = supabase.table("documents").select("*").filter("id", "eq", doc_id).execute()
                    if hasattr(doc_response, 'data') and doc_response.data:
                        metadata = doc_response.data[0].get('metadata', {})
                        filename = metadata.get('filename', 'desconhecido')
                        name = metadata.get('name', '')
                        
                        print(f"   Arquivo: {filename}")
                        if name:
                            print(f"   Nome: {name}")
                except Exception as e:
                    print(f"   Erro ao buscar documento: {str(e)}")
                
                print()  # Linha em branco entre exames
        else:
            print(f"Nenhum exame encontrado contendo '{name_part}'.")
    
    except Exception as e:
        print(f"Erro: {str(e)}")

def search_documents_by_name(name_part):
    """Busca documentos por parte do nome no metadata"""
    try:
        # Infelizmente, não podemos filtrar diretamente por um campo dentro do JSONB
        # Vamos obter todos os documentos e filtrar manualmente
        response = supabase.table("documents").select("*").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Erro ao buscar documentos: {response.error}")
            return
        
        matching_docs = []
        name_part = name_part.lower()
        
        if hasattr(response, 'data') and response.data:
            for doc in response.data:
                metadata = doc.get('metadata', {})
                filename = metadata.get('filename', '').lower()
                name = metadata.get('name', '').lower()
                
                if name_part in filename or name_part in name:
                    matching_docs.append(doc)
            
            if matching_docs:
                print(f"\n===== DOCUMENTOS CONTENDO '{name_part}' ({len(matching_docs)}) =====")
                for i, doc in enumerate(matching_docs, 1):
                    doc_id = doc.get('id', 'N/A')
                    metadata = doc.get('metadata', {})
                    filename = metadata.get('filename', 'desconhecido')
                    name = metadata.get('name', '')
                    date = metadata.get('date_reported', '')
                    
                    print(f"{i}. ID: {doc_id[:8]}... | Arquivo: {filename}")
                    if name:
                        print(f"   Nome: {name}")
                    if date:
                        print(f"   Data: {date}")
                    
                    print()  # Linha em branco entre documentos
            else:
                print(f"Nenhum documento encontrado contendo '{name_part}'.")
        else:
            print("Nenhum documento encontrado.")
    
    except Exception as e:
        print(f"Erro: {str(e)}")

def main():
    print("===== Listagem de Documentos e Exames no Supabase =====")
    print("1. Listar todos os documentos")
    print("2. Listar todos os exames agrupados por documento")
    print("3. Buscar exames por nome")
    print("4. Buscar documentos por nome")
    print("5. Sair")
    
    choice = input("\nEscolha uma opção: ")
    
    if choice == "1":
        list_documents()
    elif choice == "2":
        list_exams()
    elif choice == "3":
        name_part = input("Digite parte do nome do exame: ")
        search_exams_by_name(name_part)
    elif choice == "4":
        name_part = input("Digite parte do nome do documento: ")
        search_documents_by_name(name_part)
    elif choice == "5":
        print("Saindo...")
        return
    else:
        print("Opção inválida!")
    
    input("\nPressione Enter para continuar...")
    main()  # Recursão para voltar ao menu

if __name__ == "__main__":
    main()
