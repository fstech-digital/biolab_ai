"""
Módulo principal para execução do MCP Server BioLab.Ai

Fornece as funções e interfaces de linha de comando para iniciar os 
diferentes componentes do MCP Server.
"""

import os
import argparse
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def run_http_server(host: str = "0.0.0.0", port: int = None):
    """
    Inicia o servidor HTTP
    
    Args:
        host: Host para o servidor
        port: Porta para o servidor (usa PORT do .env se None)
    """
    from .http_server import start_server
    start_server(host, port)

def run_test_busca():
    """Executa um teste básico de busca de exames"""
    from .mcp_tools import MCPTools, PatientExamSearchRequest
    
    tools = MCPTools()
    
    # Teste com nome de paciente fictício
    request = PatientExamSearchRequest(patient_name="João Silva")
    results = tools.buscar_exames_paciente(request)
    
    print(f"Resultados para '{request.patient_name}':")
    for i, result in enumerate(results, 1):
        print(f"[{i}] {result}")
    
    if not results:
        print("Nenhum resultado encontrado.")

def main():
    """Função principal para execução via linha de comando"""
    parser = argparse.ArgumentParser(description="BioLab.Ai MCP Server")
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # Subcomando para servidor HTTP
    http_parser = subparsers.add_parser("http", help="Iniciar servidor HTTP")
    http_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host para o servidor")
    http_parser.add_argument("--port", type=int, default=None, help="Porta para o servidor")
    
    # Subcomando para teste de busca
    test_parser = subparsers.add_parser("test_busca", help="Testar busca de exames")
    
    args = parser.parse_args()
    
    if args.command == "http":
        run_http_server(args.host, args.port)
    elif args.command == "test_busca":
        run_test_busca()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()