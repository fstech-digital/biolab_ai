#!/usr/bin/env python
"""
Script para processamento de arquivos PDF de amostra para o BioLab.Ai

Este script processa os arquivos PDF de amostra fornecidos para testes
do sistema BioLab.Ai. Ele utiliza a API de extração de PDF implementada
no projeto para extrair informações e armazená-las no Supabase.

Este script é útil para pré-carregar dados de exames de amostra durante
o desenvolvimento e testes do sistema.
"""

import os
import sys
import asyncio
import argparse
import uuid
import json
from dotenv import load_dotenv

# Adicionar diretório pai ao path para importar módulos do projeto
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app.services.pdf_extraction.extractor import extract_exam_data
from app.services.vector_db.supabase_client import store_document_vectors

# Carregar variáveis de ambiente
load_dotenv()

# Configurações padrão
SAMPLE_PDF_DIR = "docs/pdfs"
UPLOAD_DIR = "tmp/uploads"

async def process_pdf_file(file_path, user_id):
    """
    Processa um arquivo PDF e armazena os dados no Supabase.
    
    Args:
        file_path: Caminho do arquivo PDF
        user_id: ID do usuário para associar ao documento
        
    Returns:
        Resultado do processamento
    """
    try:
        print(f"Processando arquivo: {os.path.basename(file_path)}")
        
        # Extrair dados do PDF
        extracted_data = await extract_exam_data(file_path)
        
        if not extracted_data or "exams" not in extracted_data or not extracted_data["exams"]:
            print(f"Nenhum dado de exame encontrado no arquivo: {file_path}")
            return {
                "file_name": os.path.basename(file_path),
                "status": "error",
                "error": "Nenhum dado de exame encontrado"
            }
        
        # Armazenar no Supabase
        document_id = await store_document_vectors(
            extracted_data,
            os.path.basename(file_path),
            user_id=user_id
        )
        
        return {
            "document_id": document_id,
            "file_name": os.path.basename(file_path),
            "exam_count": len(extracted_data.get("exams", [])),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Erro ao processar arquivo {file_path}: {str(e)}")
        return {
            "file_name": os.path.basename(file_path),
            "status": "error",
            "error": str(e)
        }

async def copy_and_process_pdfs(source_dir, upload_dir, user_id, limit=None):
    """
    Copia PDFs do diretório de origem para o diretório de upload e os processa.
    
    Args:
        source_dir: Diretório contendo os PDFs de amostra
        upload_dir: Diretório de upload do sistema
        user_id: ID do usuário para associar aos documentos
        limit: Número máximo de arquivos a processar (opcional)
        
    Returns:
        Lista de resultados de processamento
    """
    # Verificar se os diretórios existem
    if not os.path.exists(source_dir):
        print(f"Diretório de origem não encontrado: {source_dir}")
        return []
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        print(f"Diretório de upload criado: {upload_dir}")
    
    # Listar arquivos PDF no diretório de origem
    pdf_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')]
    
    if limit and len(pdf_files) > limit:
        pdf_files = pdf_files[:limit]
    
    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado em: {source_dir}")
        return []
    
    print(f"Encontrados {len(pdf_files)} arquivos PDF para processamento")
    
    # Copiar e processar cada arquivo
    results = []
    for pdf_file in pdf_files:
        source_path = os.path.join(source_dir, pdf_file)
        dest_path = os.path.join(upload_dir, pdf_file)
        
        # Copiar arquivo
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            print(f"Arquivo copiado: {source_path} -> {dest_path}")
        except Exception as e:
            print(f"Erro ao copiar arquivo {pdf_file}: {str(e)}")
            continue
        
        # Processar arquivo
        result = await process_pdf_file(dest_path, user_id)
        results.append(result)
    
    return results

async def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Processamento de PDFs de amostra para o BioLab.Ai")
    parser.add_argument("--source", type=str, default=SAMPLE_PDF_DIR,
                        help=f"Diretório contendo os PDFs de amostra (padrão: {SAMPLE_PDF_DIR})")
    parser.add_argument("--upload", type=str, default=UPLOAD_DIR,
                        help=f"Diretório de upload do sistema (padrão: {UPLOAD_DIR})")
    parser.add_argument("--user-id", type=str, required=True,
                        help="ID do usuário para associar aos documentos")
    parser.add_argument("--limit", type=int, default=None,
                        help="Número máximo de arquivos a processar")
    
    args = parser.parse_args()
    
    print("===== Processamento de PDFs de Amostra para o BioLab.Ai =====")
    
    # Validar ID do usuário
    try:
        uuid.UUID(args.user_id)
    except ValueError:
        print(f"ID de usuário inválido: {args.user_id}")
        print("Por favor, forneça um UUID válido")
        return
    
    # Copiar e processar PDFs
    results = await copy_and_process_pdfs(args.source, args.upload, args.user_id, args.limit)
    
    # Exibir resumo
    print("\n===== Resumo do Processamento =====")
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]
    
    print(f"Total de arquivos: {len(results)}")
    print(f"Processados com sucesso: {len(successful)}")
    print(f"Falhas: {len(failed)}")
    
    if successful:
        print("\nDocumentos processados com sucesso:")
        for result in successful:
            print(f"- {result['file_name']}: {result['exam_count']} exames (ID: {result.get('document_id', 'N/A')})")
    
    if failed:
        print("\nFalhas de processamento:")
        for result in failed:
            print(f"- {result['file_name']}: {result.get('error', 'Erro desconhecido')}")
    
    print("\n===== Processamento concluído =====")

if __name__ == "__main__":
    asyncio.run(main())
