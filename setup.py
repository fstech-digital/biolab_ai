#!/usr/bin/env python
"""
Script de configuração inicial para o BioLab.Ai
Este script realiza a configuração inicial do ambiente para o BioLab.Ai,
incluindo a criação do ambiente virtual, instalação de dependências
e configuração do banco de dados.
"""

import os
import sys
import subprocess
import platform
import argparse

def run_command(command, description=None):
    """Executa um comando e exibe o resultado."""
    if description:
        print(f"\n=== {description} ===")
    
    print(f"Executando: {command}")
    result = subprocess.run(command, shell=True, text=True)
    
    if result.returncode != 0:
        print(f"Erro ao executar o comando: {command}")
        return False
    
    return True

def create_virtual_env():
    """Cria o ambiente virtual Python."""
    if os.path.exists("env") or os.path.exists("venv"):
        print("Ambiente virtual já existe.")
        return True
    
    return run_command("python -m venv env", "Criando ambiente virtual")

def activate_virtual_env():
    """Retorna o comando para ativar o ambiente virtual."""
    if platform.system() == "Windows":
        return "env\\Scripts\\activate"
    else:
        return "source env/bin/activate"

def install_dependencies():
    """Instala as dependências do projeto."""
    activate_cmd = activate_virtual_env()
    
    if platform.system() == "Windows":
        command = f"{activate_cmd} && pip install -r requirements.txt"
    else:
        command = f"{activate_cmd} && pip install -r requirements.txt"
    
    return run_command(command, "Instalando dependências")

def setup_database():
    """Configura o banco de dados Supabase."""
    activate_cmd = activate_virtual_env()
    
    if platform.system() == "Windows":
        command = f"{activate_cmd} && python scripts/setup_supabase.py"
    else:
        command = f"{activate_cmd} && python scripts/setup_supabase.py"
    
    return run_command(command, "Configurando banco de dados")

def check_env_file():
    """Verifica se o arquivo .env existe."""
    if not os.path.exists(".env"):
        print("\nAVISO: Arquivo .env não encontrado!")
        print("Você deve criar um arquivo .env com base no arquivo .env.example")
        print("e configurar as variáveis necessárias.")
        return False
    
    return True

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Configuração inicial do BioLab.Ai")
    parser.add_argument("--skip-venv", action="store_true", help="Pular criação do ambiente virtual")
    parser.add_argument("--skip-deps", action="store_true", help="Pular instalação de dependências")
    parser.add_argument("--skip-db", action="store_true", help="Pular configuração do banco de dados")
    
    args = parser.parse_args()
    
    print("===== Configuração Inicial do BioLab.Ai =====")
    
    # Verificar arquivo .env
    if not check_env_file():
        sys.exit(1)
    
    # Criar ambiente virtual
    if not args.skip_venv:
        if not create_virtual_env():
            sys.exit(1)
    
    # Instalar dependências
    if not args.skip_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Configurar banco de dados
    if not args.skip_db:
        if not setup_database():
            sys.exit(1)
    
    print("\n===== Configuração concluída com sucesso! =====")
    print("\nAgora você pode:")
    print(f"1. Ativar o ambiente virtual: {activate_virtual_env()}")
    print("2. Iniciar o servidor API: python run.py")
    print("3. Em outro terminal, iniciar a interface CLI: python cli.py")

if __name__ == "__main__":
    main()
