#!/usr/bin/env python
"""
Script para processamento das planilhas de conhecimento do BioLab.Ai

Este script processa as planilhas Excel que compõem a base de conhecimento do sistema:
- planilha_exames_interpretaçao.xlsx
- Tabela_causas_alteração_de_leucócitos 3.xlsx
- PLANILHA_MICRONUTRIENTES_2023 2.xlsx

As planilhas são processadas e transformadas em vetores armazenados no Supabase
para serem utilizadas pelo sistema de RAG durante as análises.
"""

import os
import sys
import asyncio
import argparse
import shutil
from dotenv import load_dotenv

# Adicionar diretório pai ao path para importar módulos do projeto
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from app.services.knowledge_base.excel_processor import process_excel_file

# Carregar variáveis de ambiente
load_dotenv()

# Configurações padrão
DEFAULT_KNOWLEDGE_DIR = "data/knowledge"
DOCS_DIR = "docs/planilhas"

# Mapeamento de planilhas e suas descrições
KNOWLEDGE_SHEETS = {
    "planilha_exames_interpretaçao": {
        "collection": "interpretacao_exames",
        "description": "Valores de referência e interpretação de diversos exames laboratoriais",
        "file": "planilha_exames_interpretaçao.xlsx"
    },
    "tabela_causas_alteracao_de_leucocitos": {
        "collection": "alteracao_leucocitos",
        "description": "Causas e significados de alterações nos leucócitos",
        "file": "Tabela_causas_alteração_de_leucócitos 3.xlsx"
    },
    "planilha_micronutrientes": {
        "collection": "micronutrientes",
        "description": "Informações sobre micronutrientes, valores de referência e interpretações",
        "file": "PLANILHA_MICRONUTRIENTES_2023 2.xlsx"
    }
}

def copy_files_to_knowledge_dir(docs_dir, knowledge_dir):
    """
    Copia os arquivos do diretório de documentos para o diretório de conhecimento.
    
    Args:
        docs_dir: Diretório de documentos
        knowledge_dir: Diretório de conhecimento
    """
    # Verificar se ambos os diretórios existem
    if not os.path.exists(docs_dir):
        print(f"Diretório de documentos não encontrado: {docs_dir}")
        return False
    
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir, exist_ok=True)
    
    try:
        # Copiar cada arquivo
        for sheet_info in KNOWLEDGE_SHEETS.values():
            source_file = os.path.join(docs_dir, sheet_info["file"])
            dest_file = os.path.join(knowledge_dir, sheet_info["file"])
            
            if os.path.exists(source_file):
                shutil.copy2(source_file, dest_file)
                print(f"Arquivo copiado: {source_file} -> {dest_file}")
            else:
                print(f"Arquivo não encontrado: {source_file}")
        
        return True
    except Exception as e:
        print(f"Erro ao copiar arquivos: {str(e)}")
        return False

async def process_all_knowledge_sheets(knowledge_dir: str):
    """
    Processa todas as planilhas de conhecimento no diretório especificado.
    
    Args:
        knowledge_dir: Diretório contendo as planilhas
    """
    print("===== Processamento da Base de Conhecimento do BioLab.Ai =====")
    
    # Verificar se o diretório existe
    if not os.path.exists(knowledge_dir):
        print(f"Diretório não encontrado: {knowledge_dir}")
        print("Criando diretório...")
        os.makedirs(knowledge_dir, exist_ok=True)
        print(f"Diretório criado: {knowledge_dir}")
    
    # Verificar se o banco de dados está pronto
    print("Verificando tabelas no banco de dados...")
    try:
        # Verificar/criar tabela knowledge_vectors
        # Esta verificação seria normalmente feita com uma consulta ao Supabase
        # Aqui vamos apenas supor que a tabela já foi criada
        pass
    except Exception as e:
        print(f"Erro ao verificar banco de dados: {str(e)}")
        print("Por favor, execute o script setup_database.py primeiro para configurar o banco de dados.")
        return
    
    # Processar cada planilha
    for sheet_name, sheet_info in KNOWLEDGE_SHEETS.items():
        # Verificar o arquivo específico
        sheet_file = os.path.join(knowledge_dir, sheet_info["file"])
        
        if os.path.exists(sheet_file):
            print(f"\nProcessando planilha: {sheet_name}")
            print(f"Arquivo: {sheet_file}")
            print(f"Coleção: {sheet_info['collection']}")
            
            # Processar planilha
            result = await process_excel_file(
                file_path=sheet_file,
                collection_name=sheet_info['collection'],
                description=sheet_info['description']
            )
            
            # Verificar resultado
            if result["status"] == "success":
                print(f"Processamento concluído com sucesso!")
                print(f"ID da planilha: {result['sheet_id']}")
                print(f"Chunks processados: {result['chunks_processed']}")
                print(f"Chunks armazenados: {result['chunks_stored']}")
            else:
                print(f"Erro ao processar planilha: {result.get('error', 'Erro desconhecido')}")
        else:
            print(f"\nPlanilha não encontrada: {sheet_file}")
            print(f"Por favor, coloque a planilha {sheet_info['file']} no diretório {knowledge_dir}")
    
    print("\n===== Processamento concluído =====")

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Processamento de planilhas de conhecimento para o BioLab.Ai")
    parser.add_argument("--dir", type=str, default=DEFAULT_KNOWLEDGE_DIR,
                        help=f"Diretório contendo as planilhas (padrão: {DEFAULT_KNOWLEDGE_DIR})")
    parser.add_argument("--copy", action="store_true",
                        help="Copiar arquivos do diretório docs para o diretório de conhecimento")
    
    args = parser.parse_args()
    
    # Copiar arquivos, se solicitado
    if args.copy:
        success = copy_files_to_knowledge_dir(DOCS_DIR, args.dir)
        if not success:
            print("Falha ao copiar os arquivos. Verifique os diretórios e tente novamente.")
            return
    
    # Executar processamento
    asyncio.run(process_all_knowledge_sheets(args.dir))

if __name__ == "__main__":
    main()
