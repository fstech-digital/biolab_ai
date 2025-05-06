"""
Testes para todas as ferramentas MCP implementadas no BioLab.Ai
"""
import os
import sys
import json
from typing import Dict, Any

# Adicionar diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importar configurações e ferramentas MCP
from app.core.config import settings
import mcp_tools
from supabase_client import (
    buscar_exames_paciente,
    buscar_exames_por_data,
    buscar_exames_por_tipo,
    obter_valores_referencia
)

# Configurar variáveis de ambiente manualmente se necessário
if not os.getenv("SUPABASE_URL") and hasattr(settings, "SUPABASE_URL"):
    os.environ["SUPABASE_URL"] = settings.SUPABASE_URL
if not os.getenv("SUPABASE_KEY") and hasattr(settings, "SUPABASE_KEY"):
    os.environ["SUPABASE_KEY"] = settings.SUPABASE_KEY

def imprimir_resultados(nome_ferramenta: str, params: Dict[str, Any], resultado: Any) -> None:
    """Imprime os resultados de uma ferramenta MCP de forma legível."""
    print(f"\n{'=' * 50}")
    print(f"FERRAMENTA: {nome_ferramenta}")
    print(f"PARÂMETROS: {json.dumps(params, indent=2, ensure_ascii=False)}")
    
    if isinstance(resultado, dict) and resultado.get("exames") and len(resultado.get("exames", [])) > 3:
        # Se há muitos exames, mostra apenas os 3 primeiros
        exames = resultado["exames"][:3]
        total = len(resultado["exames"])
        
        # Criar uma cópia e substituir exames pela versão truncada
        resultado_formatado = resultado.copy()
        resultado_formatado["exames"] = exames
        resultado_formatado["nota"] = f"Exibindo 3 de {total} exames encontrados"
        
        print(f"RESULTADO: {json.dumps(resultado_formatado, indent=2, ensure_ascii=False)}")
    else:
        # Mostrar resultado completo
        print(f"RESULTADO: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
    
    print(f"{'=' * 50}\n")

def testar_todas_ferramentas():
    """Testa todas as ferramentas MCP disponíveis com exemplos."""
    print("\n=== TESTE DE TODAS AS FERRAMENTAS MCP ===\n")
    
    # 1. Teste: buscar_exames_paciente
    params = {"patient_name": "Altamiro"}
    resultado = mcp_tools.mcp_buscar_exames_paciente(params)
    imprimir_resultados("buscar_exames_paciente", params, resultado)
    
    # 2. Teste: buscar_exames_por_data
    params = {"start_date": "10/09/2024", "end_date": "07/10/2024"}
    resultado = mcp_tools.mcp_buscar_exames_por_data(params)
    imprimir_resultados("buscar_exames_por_data", params, resultado)
    
    # 3. Teste: buscar_exames_por_tipo
    params = {"exam_type": "hemoglobina"}
    resultado = mcp_tools.mcp_buscar_exames_por_tipo(params)
    imprimir_resultados("buscar_exames_por_tipo", params, resultado)
    
    # 4. Teste: obter_valores_referencia
    params = {"exam_code": "hemoglobina", "age": 42, "gender": "Masculino"}
    resultado = mcp_tools.mcp_obter_valores_referencia(params)
    imprimir_resultados("obter_valores_referencia", params, resultado)
    
    print("\n=== TESTE CONCLUÍDO ===\n")

if __name__ == "__main__":
    # Verificar se as variáveis de ambiente estão configuradas
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("ERRO: As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias.")
        sys.exit(1)
    
    # Executar todos os testes
    testar_todas_ferramentas()
