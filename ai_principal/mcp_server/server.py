"""
Servidor MCP (Model Context Protocol) para BioLab.Ai
Implementa um servidor MCP que expõe ferramentas para acessar dados do Supabase.
"""
import os
import sys
import json
import logging
from typing import Dict, List, Any, Union
from .mcp_tools import get_available_tools, execute_tool, SCHEMAS

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("biolab_mcp_server")

def parse_mcp_request(data: str) -> Dict[str, Any]:
    """
    Processa uma requisição MCP recebida do stdin.
    
    Args:
        data: String JSON com a requisição MCP
    
    Returns:
        Dicionário contendo os dados da requisição
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar requisição MCP: {e}")
        return {}

def format_mcp_response(response: Dict[str, Any]) -> str:
    """
    Formata uma resposta para o protocolo MCP.
    
    Args:
        response: Dicionário com dados da resposta
    
    Returns:
        String JSON formatada para MCP
    """
    return json.dumps(response, ensure_ascii=False)

def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa uma requisição MCP e retorna uma resposta.
    
    Args:
        request: Dicionário contendo a requisição MCP
    
    Returns:
        Dicionário contendo a resposta MCP
    """
    # Verificar o tipo de requisição
    request_type = request.get("type", "")
    
    # Tratamento para requisição de listagem de ferramentas
    if request_type == "list_tools":
        logger.info("Requisição de listagem de ferramentas")
        return {
            "type": "tool_list",
            "tools": get_available_tools()
        }
    
    # Tratamento para chamada de ferramenta
    elif request_type == "tool_call":
        tool_name = request.get("tool", {}).get("name", "")
        parameters = request.get("tool", {}).get("parameters", {})
        
        logger.info(f"Chamada de ferramenta: {tool_name} com parâmetros: {parameters}")
        
        if not tool_name or tool_name not in SCHEMAS:
            return {
                "type": "error",
                "error": f"Ferramenta não encontrada: {tool_name}"
            }
        
        try:
            result = execute_tool(tool_name, parameters)
            return {
                "type": "tool_result",
                "tool": tool_name,
                "result": result
            }
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
            return {
                "type": "error",
                "tool": tool_name,
                "error": str(e)
            }
    
    # Tratamento para requisições não suportadas
    else:
        logger.warning(f"Tipo de requisição não suportado: {request_type}")
        return {
            "type": "error",
            "error": f"Tipo de requisição não suportada: {request_type}"
        }

def read_stdin_line() -> str:
    """Lê uma linha do stdin"""
    return sys.stdin.readline()

def write_stdout_line(line: str) -> None:
    """Escreve uma linha no stdout e força flush"""
    sys.stdout.write(line + "\n")
    sys.stdout.flush()

def run_mcp_server() -> None:
    """
    Inicia o servidor MCP lendo requisições do stdin e 
    escrevendo respostas no stdout.
    """
    logger.info("Iniciando servidor MCP BioLab.Ai")
    
    # Informações de inicialização
    print(f"BioLab.Ai MCP Server v0.1.0")
    print(f"Ferramentas disponíveis: {', '.join(SCHEMAS.keys())}")
    
    try:
        while True:
            # Ler uma linha de entrada (requisição MCP)
            line = read_stdin_line()
            
            # Se a linha estiver vazia, pode ser EOF
            if not line:
                break
            
            # Processar a requisição
            request = parse_mcp_request(line.strip())
            if not request:
                continue
            
            # Gerar resposta
            response = handle_mcp_request(request)
            
            # Enviar resposta
            write_stdout_line(format_mcp_response(response))
            
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
    finally:
        logger.info("Encerrando servidor MCP")

if __name__ == "__main__":
    # Verificações de ambiente antes de iniciar
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("ERRO: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são obrigatórias")
        sys.exit(1)
    
    # Iniciar o servidor
    run_mcp_server()
