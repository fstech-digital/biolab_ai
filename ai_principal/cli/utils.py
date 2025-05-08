"""
Utilitários para CLI do BioLab.Ai
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
from tabulate import tabulate
import rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Console rich para saída formatada
console = Console()

def format_exam_table(exams: List[Dict[str, Any]]) -> str:
    """
    Formata uma lista de exames como tabela
    
    Args:
        exams: Lista de exames
        
    Returns:
        Tabela formatada como string
    """
    if not exams:
        return "Nenhum exame encontrado"
    
    # Extrair colunas relevantes
    data = []
    for exam in exams:
        row = {
            "Nome": exam.get("name", ""),
            "Resultado": exam.get("result", ""),
            "Unidade": exam.get("unit", ""),
            "Referência": exam.get("reference", "")
        }
        data.append(row)
    
    # Criar dataframe para formatação
    df = pd.DataFrame(data)
    
    # Formatar como tabela
    return tabulate(df, headers="keys", tablefmt="grid", showindex=False)

def print_exam_results(exams: List[Dict[str, Any]], patient_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Imprime resultados de exames formatados
    
    Args:
        exams: Lista de exames
        patient_data: Dados do paciente (opcional)
    """
    # Criar tabela rica
    table = Table(title="Resultados de Exames")
    
    # Adicionar colunas
    table.add_column("Nome", style="cyan")
    table.add_column("Resultado", style="green")
    table.add_column("Unidade", style="blue")
    table.add_column("Referência", style="yellow")
    
    # Adicionar linhas
    for exam in exams:
        table.add_row(
            exam.get("name", ""),
            exam.get("result", ""),
            exam.get("unit", ""),
            exam.get("reference", "")
        )
    
    # Imprimir informações do paciente
    if patient_data:
        patient_info = []
        if patient_data.get("name"):
            patient_info.append(f"Paciente: {patient_data['name']}")
        if patient_data.get("age"):
            patient_info.append(f"Idade: {patient_data['age']} anos")
        if patient_data.get("gender"):
            gender_map = {"M": "Masculino", "F": "Feminino"}
            gender = gender_map.get(patient_data["gender"], patient_data["gender"])
            patient_info.append(f"Gênero: {gender}")
        if patient_data.get("exam_date"):
            patient_info.append(f"Data do Exame: {patient_data['exam_date']}")
        
        panel = Panel("\n".join(patient_info), title="Informações do Paciente")
        console.print(panel)
    
    # Imprimir tabela
    console.print(table)

def show_progress(tasks: List[Dict[str, Any]], title: str = "Processando") -> None:
    """
    Mostra barra de progresso para múltiplas tarefas
    
    Args:
        tasks: Lista de tarefas com 'name' e 'total'
        title: Título da barra de progresso
    """
    with Progress() as progress:
        # Criar tarefas
        task_ids = {}
        for task in tasks:
            task_id = progress.add_task(task["name"], total=task["total"])
            task_ids[task["name"]] = task_id
        
        # Atualizar progresso (simulação)
        from time import sleep
        
        for i in range(100):
            for task_name, task_id in task_ids.items():
                # Atualizar apenas se não estiver completa
                if not progress.finished(task_id):
                    progress.update(task_id, advance=1)
            
            # Intervalo para visualização
            sleep(0.05)

def ensure_output_dir(output_dir: Optional[str]) -> str:
    """
    Garante que o diretório de saída exista
    
    Args:
        output_dir: Caminho para o diretório
        
    Returns:
        Caminho para o diretório criado
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        # Usar diretório padrão
        output_dir = os.path.join(os.getcwd(), "biolab_output")
        os.makedirs(output_dir, exist_ok=True)
    
    return output_dir