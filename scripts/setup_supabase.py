#!/usr/bin/env python
"""
Script para configuração do Supabase para o BioLab.Ai
Este script configura as tabelas necessárias no Supabase,
incluindo a extensão pgvector e as tabelas do sistema.
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Erro: SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    exit(1)

async def execute_sql_query(query):
    """Executa uma consulta SQL no Supabase."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "params=single-object",
    }
    
    data = {
        "query": query
    }
    
    url = f"{SUPABASE_URL}/rest/v1/rpc/execute"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP: {e}")
        print(f"Resposta: {e.response.text}")
        return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

async def setup_database():
    """Configura o banco de dados no Supabase."""
    print("Configurando banco de dados no Supabase...")
    
    # Ler o arquivo SQL
    try:
        with open("scripts/setup_database.sql", "r") as f:
            sql_script = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo SQL: {e}")
        return False
    
    # Dividir o script em declarações individuais
    statements = sql_script.split(";")
    
    # Executar cada declaração
    for statement in statements:
        if statement.strip():
            print(f"Executando: {statement.strip()}")
            result = await execute_sql_query(statement)
            if result is None:
                print("Falha na execução da consulta.")
                return False
    
    print("Banco de dados configurado com sucesso!")
    return True

async def main():
    """Função principal do script."""
    print("===== Configuração do Supabase para BioLab.Ai =====")
    
    # Verificar conexão com Supabase
    print(f"Conectando ao Supabase: {SUPABASE_URL}")
    
    # Configurar banco de dados
    success = await setup_database()
    
    if success:
        print("\nConfiguração concluída com sucesso!")
        print("O BioLab.Ai está pronto para ser utilizado.")
    else:
        print("\nErro durante a configuração. Verifique os logs acima.")

if __name__ == "__main__":
    asyncio.run(main())
