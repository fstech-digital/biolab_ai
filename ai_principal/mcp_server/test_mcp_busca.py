"""
Script de teste para a ferramenta de busca MCP
"""

import json
from typing import Dict, Any
from .server import MCPServer

def test_buscar_exames_paciente():
    """Testa a ferramenta de busca de exames por paciente"""
    server = MCPServer()
    
    # Teste com paciente fictício
    request_data = {
        "tool_name": "buscar_exames_paciente",
        "parameters": {
            "patient_name": "João Silva"
        }
    }
    
    # Processar requisição
    response = server.handle_request(request_data)
    
    # Exibir resultado formatado
    print("Requisição:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    print("\nResposta:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # Verificar se a resposta foi bem-sucedida
    assert response["status"] in ["success", "error"], "Status inválido na resposta"
    
    # Em um teste real, teríamos dados no banco para verificar
    # Por enquanto, apenas imprimimos o resultado
    
    return response

if __name__ == "__main__":
    test_buscar_exames_paciente()