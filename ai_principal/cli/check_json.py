"""
Script para verificar a estrutura dos arquivos JSON gerados
"""

import json
import sys
import os

def show_file_content(file_path):
    """Mostra o conteúdo de um arquivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n=== Conteúdo do arquivo: {os.path.basename(file_path)} ===\n")
        
        # Processamento específico para diferentes tipos de arquivo
        if "_extracted.json" in file_path:
            # Arquivo de extração de PDF
            print("Tipo: Dados extraídos de PDF")
            
            # Mostrar metadados
            if "metadata" in data:
                print("\nMetadados do PDF:")
                print(json.dumps(data["metadata"], indent=2, ensure_ascii=False))
            
            # Mostrar dados do paciente
            if "patient" in data:
                print("\nDados do Paciente:")
                print(json.dumps(data["patient"], indent=2, ensure_ascii=False))
            
            # Mostrar exames
            if "exams" in data:
                print(f"\nExames ({len(data['exams'])}):")
                for i, exam in enumerate(data["exams"], 1):
                    print(f"\n  Exame {i}:")
                    print(f"  Nome: {exam.get('name', 'N/A')}")
                    print(f"  Resultado: {exam.get('result', 'N/A')} {exam.get('unit', '')}")
                    print(f"  Referência: {exam.get('reference', 'N/A')}")
        
        elif "_rag.json" in file_path:
            # Arquivo de processamento RAG
            print("Tipo: Chunks para RAG")
            print(f"Total de chunks: {len(data)}")
            
            for i, chunk in enumerate(data, 1):
                print(f"\nChunk {i} (tipo: {chunk.get('chunk_type', 'desconhecido')}):")
                
                # Mostrar texto truncado
                text = chunk.get("text", "")
                print(f"Texto ({len(text)} caracteres): {text[:100]}...")
                
                # Mostrar metadados
                if "metadata" in chunk:
                    print("\nMetadados:")
                    print(json.dumps(chunk["metadata"], indent=2, ensure_ascii=False))
                
                # Verificar se há embedding
                if "embedding" in chunk:
                    embedding = chunk["embedding"]
                    print(f"Embedding: {type(embedding)} com {len(embedding) if isinstance(embedding, list) else 'N/A'} dimensões")
                
                # Limite de exibição
                if i >= 3:
                    print("\n... mais chunks omitidos ...")
                    break
        else:
            # Genérico
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
            if len(json.dumps(data)) > 2000:
                print("\n... (truncado) ...")
    
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python check_json.py arquivo1.json [arquivo2.json ...]")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        show_file_content(file_path)