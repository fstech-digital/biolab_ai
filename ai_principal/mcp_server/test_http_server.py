"""
Script para testar o servidor HTTP do MCP Server
Executa requisições de teste para todos os endpoints REST.
"""
import os
import sys
import json
import requests
from typing import Dict, Any

# Configurações de teste
BASE_URL = "http://localhost:8000"
TIMEOUT = 10  # segundos

def executar_request(url: str, metodo: str = "GET", dados: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Executa uma requisição HTTP e retorna o resultado
    
    Args:
        url: URL completa para o endpoint
        metodo: Método HTTP (GET ou POST)
        dados: Dados a serem enviados (para POST)
    
    Returns:
        Resposta da API convertida para dicionário
    """
    try:
        if metodo == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif metodo == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=dados, headers=headers, timeout=TIMEOUT)
        else:
            raise ValueError(f"Método HTTP não suportado: {metodo}")
        
        response.raise_for_status()  # Lança exceção se status != 2xx
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao executar requisição: {e}")
        return {"erro": str(e)}

def imprimir_resultado(nome_teste: str, url: str, metodo: str, dados: Dict[str, Any], resultado: Dict[str, Any]) -> None:
    """Imprime o resultado de um teste de forma legível"""
    print(f"\n{'=' * 60}")
    print(f"TESTE: {nome_teste}")
    print(f"URL: {url}")
    print(f"MÉTODO: {metodo}")
    
    if dados:
        print(f"DADOS: {json.dumps(dados, ensure_ascii=False, indent=2)}")
    
    # Limitar exibição de listas longas
    resultado_formatado = resultado
    if isinstance(resultado, dict) and "exames" in resultado and len(resultado.get("exames", [])) > 3:
        resultado_copia = resultado.copy()
        resultado_copia["exames"] = resultado["exames"][:3]
        resultado_copia["nota"] = f"Exibindo 3 de {len(resultado['exames'])} exames"
        resultado_formatado = resultado_copia
    
    print(f"RESULTADO: {json.dumps(resultado_formatado, ensure_ascii=False, indent=2)}")
    print(f"{'=' * 60}\n")

def testar_todos_endpoints():
    """Executa testes para todos os endpoints da API"""
    print("\n=== TESTES DO SERVIDOR HTTP MCP ===\n")
    print(f"Servidor: {BASE_URL}\n")
    
    # Teste 1: Endpoint raiz
    url = f"{BASE_URL}/"
    resultado = executar_request(url)
    imprimir_resultado("Endpoint Raiz", url, "GET", None, resultado)
    
    # Teste 2: Buscar exames por paciente (POST)
    url = f"{BASE_URL}/api/exames/paciente"
    dados = {"patient_name": "Altamiro"}
    resultado = executar_request(url, "POST", dados)
    imprimir_resultado("Buscar Exames por Paciente (POST)", url, "POST", dados, resultado)
    
    # Teste 3: Buscar exames por paciente (GET)
    url = f"{BASE_URL}/api/exames/paciente/Altamiro"
    resultado = executar_request(url)
    imprimir_resultado("Buscar Exames por Paciente (GET)", url, "GET", None, resultado)
    
    # Teste 4: Buscar exames por data (POST)
    url = f"{BASE_URL}/api/exames/data"
    dados = {"start_date": "10/09/2024", "end_date": "07/10/2024"}
    resultado = executar_request(url, "POST", dados)
    imprimir_resultado("Buscar Exames por Data (POST)", url, "POST", dados, resultado)
    
    # Teste 5: Buscar exames por tipo (POST)
    url = f"{BASE_URL}/api/exames/tipo"
    dados = {"exam_type": "hemoglobina"}
    resultado = executar_request(url, "POST", dados)
    imprimir_resultado("Buscar Exames por Tipo (POST)", url, "POST", dados, resultado)
    
    # Teste 6: Buscar valores de referência (POST)
    url = f"{BASE_URL}/api/exames/referencia"
    dados = {"exam_code": "hemoglobina", "age": 42, "gender": "Masculino"}
    resultado = executar_request(url, "POST", dados)
    imprimir_resultado("Obter Valores de Referência (POST)", url, "POST", dados, resultado)
    
    print("\n=== TESTES CONCLUÍDOS ===\n")

if __name__ == "__main__":
    # Verificar se requests está instalado
    try:
        import requests
    except ImportError:
        print("ERRO: O pacote 'requests' é necessário. Instale com 'pip install requests'")
        sys.exit(1)
    
    # Executar todos os testes
    testar_todos_endpoints()
