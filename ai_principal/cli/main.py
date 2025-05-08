"""
Ponto de entrada principal para a CLI do BioLab.Ai
Implementa interface de linha de comando para interação com o sistema
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Importar comandos
from .commands import cmd_extract, cmd_process, cmd_query, cmd_server, cmd_workflow

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Imprime o cabeçalho da CLI"""
    header = f"""
{Colors.BLUE}{Colors.BOLD}===============================
 BioLab.Ai - Análise de Exames
==============================={Colors.ENDC}

{Colors.GREEN}Versão: 0.1.0{Colors.ENDC}
"""
    print(header)

def main():
    """Função principal da CLI"""
    print_header()
    
    # Parser principal
    parser = argparse.ArgumentParser(
        description="BioLab.Ai - Interface de linha de comando para análise de exames médicos",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # Comando extract
    extract_parser = subparsers.add_parser("extract", help="Extrair dados de PDFs de exames")
    extract_group = extract_parser.add_mutually_exclusive_group(required=True)
    extract_group.add_argument("--pdf", type=str, help="Caminho para um único arquivo PDF")
    extract_group.add_argument("--dir", type=str, help="Caminho para diretório com PDFs")
    extract_parser.add_argument("--reference", type=str, help="Caminho para planilha de referência")
    extract_parser.add_argument("--output", type=str, help="Diretório para arquivos de saída")
    extract_parser.add_argument("--pattern", type=str, default="*.pdf", help="Padrão para filtrar arquivos (para --dir)")
    
    # Comando process
    process_parser = subparsers.add_parser("process", help="Pré-processar dados extraídos para RAG")
    process_group = process_parser.add_mutually_exclusive_group(required=True)
    process_group.add_argument("--json", type=str, help="Caminho para um único arquivo JSON")
    process_group.add_argument("--dir", type=str, help="Caminho para diretório com JSONs")
    process_parser.add_argument("--output", type=str, help="Diretório para arquivos de saída")
    process_parser.add_argument("--pattern", type=str, default="*_extracted.json", help="Padrão para filtrar arquivos (para --dir)")
    process_parser.add_argument("--chunk-size", type=int, default=1000, help="Tamanho máximo de cada chunk em caracteres")
    process_parser.add_argument("--chunk-overlap", type=int, default=200, help="Sobreposição entre chunks em caracteres")
    process_parser.add_argument("--index", action="store_true", help="Indexar chunks no Supabase após processamento")
    
    # Comando query
    query_parser = subparsers.add_parser("query", help="Consultar exames no sistema")
    query_group = query_parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--patient", type=str, help="Nome do paciente para busca")
    query_group.add_argument("--dates", type=str, help="Intervalo de datas no formato 'start:end' (YYYY-MM-DD)")
    query_group.add_argument("--exam-type", type=str, help="Tipo de exame a ser buscado")
    query_parser.add_argument("--output", type=str, help="Arquivo para salvar os resultados em JSON")
    
    # Comando server
    server_parser = subparsers.add_parser("server", help="Iniciar servidor MCP")
    server_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host para o servidor")
    server_parser.add_argument("--port", type=int, help="Porta para o servidor")
    
    # Comando workflow
    workflow_parser = subparsers.add_parser("workflow", help="Executar fluxo completo de processamento")
    workflow_parser.add_argument("--pdf", type=str, required=True, help="Caminho para o arquivo PDF")
    workflow_parser.add_argument("--reference", type=str, help="Caminho para planilha de referência")
    workflow_parser.add_argument("--output", type=str, help="Diretório para arquivos de saída")
    workflow_parser.add_argument("--chunk-size", type=int, default=1000, help="Tamanho máximo de cada chunk em caracteres")
    workflow_parser.add_argument("--chunk-overlap", type=int, default=200, help="Sobreposição entre chunks em caracteres")
    
    # Versão
    parser.add_argument('--version', action='version', version='BioLab.Ai CLI v0.1.0')
    
    # Analisar argumentos
    args = parser.parse_args()
    
    # Executar comando
    try:
        if args.command == "extract":
            cmd_extract(args)
        elif args.command == "process":
            cmd_process(args)
        elif args.command == "query":
            cmd_query(args)
        elif args.command == "server":
            cmd_server(args)
        elif args.command == "workflow":
            cmd_workflow(args)
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário")
        return 130
    
    except Exception as e:
        logger.error(f"Erro ao executar comando: {e}")
        print(f"\n{Colors.RED}Erro: {e}{Colors.ENDC}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())