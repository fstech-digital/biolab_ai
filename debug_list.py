#!/usr/bin/env python
"""
Script simplificado para depurar a conexão com o Supabase
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
    """Função simplificada para listar documentos no Supabase"""
    print("\n===== DEPURAÇÃO SUPABASE =====\n")
    
    try:
        # Buscar todos os documentos
        print("Buscando documentos...")
        response = supabase.table("documents").select("*").execute()
        
        print(f"Tipo da resposta: {type(response)}")
        print(f"Atributos da resposta: {dir(response)}")
        
        if hasattr(response, 'data'):
            print(f"\nTipo de response.data: {type(response.data)}")
            print(f"Número de documentos: {len(response.data)}")
            
            if response.data:
                print("\nPrimeiro documento:")
                first_doc = response.data[0]
                print(f"Tipo do primeiro documento: {type(first_doc)}")
                print(f"Chaves do primeiro documento: {first_doc.keys() if hasattr(first_doc, 'keys') else 'Não tem método keys()'}")
                
                for key, value in first_doc.items():
                    print(f"- {key}: {type(value)} = {value}")
        
        # Buscar metadados de documentos
        print("\nBuscando documentos com select específico...")
        meta_response = supabase.table("documents").select("id,metadata").execute()
        
        if hasattr(meta_response, 'data') and meta_response.data:
            print(f"Número de documentos (select específico): {len(meta_response.data)}")
            
            print("\nPercorrendo documentos:")
            for i, doc in enumerate(meta_response.data[:3]):  # Mostrar apenas 3 primeiros
                print(f"\nDocumento {i+1}:")
                for key, value in doc.items():
                    if key == "metadata":
                        print(f"- {key} (tipo: {type(value)}):")
                        
                        if isinstance(value, dict):
                            for meta_key, meta_value in value.items():
                                print(f"  - {meta_key}: {meta_value}")
                        else:
                            print(f"  Valor não é dict: {value}")
                    else:
                        print(f"- {key}: {value}")
        
        # Buscar exames
        print("\nBuscando exames...")
        exam_response = supabase.table("exam_vectors").select("*").limit(5).execute()
        
        if hasattr(exam_response, 'data'):
            print(f"Número de exames encontrados: {len(exam_response.data)}")
            
            if exam_response.data:
                print("\nPrimeiro exame:")
                first_exam = exam_response.data[0]
                
                for key, value in first_exam.items():
                    print(f"- {key}: {value}")
                
    except Exception as e:
        print(f"Erro ao consultar Supabase: {str(e)}")

if __name__ == "__main__":
    main()
