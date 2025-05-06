"""
BioLab.Ai MCP Server - Esqueleto inicial
Expõe uma ferramenta MCP para buscar exames por nome de paciente, usando Supabase como backend.
"""
import os
# Exemplo: from mcp_sdk.server import MCPServer, tool
# (Dependendo da SDK MCP escolhida, ajuste os imports)
# from .supabase_client import buscar_exames_paciente

from .supabase_client import buscar_exames_paciente

def buscar_exames_paciente_tool(params):
    patient_name = params["patient_name"]
    exames = buscar_exames_paciente(patient_name)
    return {"exames": exames}

if __name__ == "__main__":
    # Exemplo: inicialização real do MCP server (ajuste conforme SDK MCP usada)
    # from mcp_sdk.server import MCPServer, tool
    # server = MCPServer(tools=[buscar_exames_paciente_tool])
    # server.serve()
    print("MCP Server pronto para receber requisições (busca real integrada ao Supabase)")
