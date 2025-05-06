"""
Script para testar a função MCP de busca por nome de paciente
"""
import os
import sys
from supabase_client import buscar_exames_paciente

# Carrega as variáveis de ambiente do projeto principal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.config import settings

# Configura as variáveis de ambiente manualmente se necessário
if not os.getenv("SUPABASE_URL") and hasattr(settings, "SUPABASE_URL"):
    os.environ["SUPABASE_URL"] = settings.SUPABASE_URL
if not os.getenv("SUPABASE_KEY") and hasattr(settings, "SUPABASE_KEY"):
    os.environ["SUPABASE_KEY"] = settings.SUPABASE_KEY

def testar_busca_paciente():
    """Testa a busca de exames por nome de paciente via MCP"""
    print("=== TESTE MCP: buscar_exames_paciente ===")
    
    # Pacientes para testar
    pacientes = ["Altamiro", "MARCELO"]
    
    for nome in pacientes:
        print(f"\nBuscando exames para paciente: '{nome}'")
        
        # Simula chamada MCP
        print("MCP Request: {'patient_name': '" + nome + "'}")
        
        # Executa a busca real
        exames = buscar_exames_paciente(nome)
        
        # Formatando a resposta
        print(f"MCP Response: {{ 'exames': {len(exames)} resultados encontrados }}")
        
        if exames:
            print("\nPRIMEIROS 3 RESULTADOS:")
            for i, exam in enumerate(exames[:3]):
                print(f"\n-- Exame {i+1} --")
                print(f"Paciente: {exam.get('patient_name', 'N/A')}, {exam.get('patient_age', 'N/A')} anos, {exam.get('patient_gender', 'N/A')}")
                print(f"Exame: {exam.get('exam_name', 'N/A')}")
                print(f"Valor: {exam.get('exam_value', 'N/A')} {exam.get('exam_unit', '')}")
                print(f"Data: {exam.get('date_collected', 'N/A')}")
        else:
            print("\nNenhum resultado encontrado.")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    testar_busca_paciente()
