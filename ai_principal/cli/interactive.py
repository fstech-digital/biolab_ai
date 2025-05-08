"""
Modo interativo (chat) para a CLI do BioLab.Ai
Apresenta menus e opções para interação mais amigável
"""

import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Importar comandos
from .commands import cmd_extract, cmd_process, cmd_query, cmd_server, cmd_workflow

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Console rich para saída formatada
console = Console()

def print_header():
    """Imprime o cabeçalho do modo interativo"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]BioLab.Ai - Análise de Exames Médicos[/bold blue]\n"
        "[green]Modo Interativo v0.1.0[/green]",
        border_style="blue"
    ))
    console.print("\n")

def print_menu(title: str, options: List[Dict[str, Any]]):
    """
    Imprime um menu de opções
    
    Args:
        title: Título do menu
        options: Lista de opções com 'key', 'name' e 'description'
    """
    from rich.box import SIMPLE
    table = Table(title=title, show_header=False, box=SIMPLE, expand=False)
    table.add_column("Comando", style="cyan", justify="center")
    table.add_column("Descrição", style="white")
    
    for option in options:
        table.add_row(
            f"[bold]{option['key']}[/bold]", 
            option['description']
        )
    
    console.print(table)
    console.print("\n")

def show_spinner(message: str, duration: int = 2):
    """
    Mostra um spinner para indicar progresso
    
    Args:
        message: Mensagem a ser exibida
        duration: Duração em segundos
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description=message, total=None)
        time.sleep(duration)

def show_success(message: str):
    """Mostra mensagem de sucesso"""
    console.print(f"[bold green]✓[/bold green] {message}")
    console.print("\n")

def interactive_extract():
    """Modo interativo para extrair dados de PDFs"""
    console.print("[bold]Extração de Dados de PDFs[/bold]")
    
    # Opções de extração
    console.print("Selecione uma opção:")
    console.print("1. Extrair um único PDF")
    console.print("2. Extrair todos os PDFs de um diretório")
    console.print("0. Voltar ao menu principal")
    
    choice = Prompt.ask("Opção", choices=["0", "1", "2"], default="1")
    
    if choice == "0":
        return
    
    if choice == "1":
        # Extração de um único PDF
        pdf_path = Prompt.ask("Caminho para o arquivo PDF")
        
        if not os.path.exists(pdf_path):
            console.print("[bold red]Erro: Arquivo não encontrado[/bold red]")
            return
        
        use_reference = Confirm.ask("Usar planilha de referência?")
        reference_path = None
        
        if use_reference:
            reference_path = Prompt.ask("Caminho para a planilha de referência")
            if not os.path.exists(reference_path):
                console.print("[bold yellow]Aviso: Planilha não encontrada, continuando sem referência[/bold yellow]")
                reference_path = None
        
        output_dir = Prompt.ask("Diretório para saída (opcional)", default="")
        
        if output_dir and not os.path.exists(output_dir):
            create_dir = Confirm.ask(f"O diretório {output_dir} não existe. Criar?")
            if create_dir:
                os.makedirs(output_dir)
            else:
                output_dir = ""
        
        # Preparar argumentos
        class Args:
            pass
        
        args = Args()
        args.pdf = pdf_path
        args.dir = None
        args.reference = reference_path
        args.output = output_dir if output_dir else None
        args.pattern = "*.pdf"
        
        # Executar extração
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Extraindo dados do PDF..."),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Processando", total=None)
            result = cmd_extract(args)
        
        # Mostrar resultado
        if result and "exams" in result:
            show_success(f"Extração concluída! {len(result['exams'])} exames encontrados")
            
            if output_dir:
                console.print(f"Dados salvos em: {os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', '_extracted.json'))}")
            else:
                pdf_dir = os.path.dirname(pdf_path)
                console.print(f"Dados salvos em: {os.path.join(pdf_dir, os.path.basename(pdf_path).replace('.pdf', '_extracted.json'))}")
        else:
            console.print("[bold red]Erro na extração. Verifique o arquivo PDF.[/bold red]")
    
    elif choice == "2":
        # Extração de um diretório
        dir_path = Prompt.ask("Caminho para o diretório com PDFs")
        
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            console.print("[bold red]Erro: Diretório não encontrado[/bold red]")
            return
        
        pattern = Prompt.ask("Padrão para filtrar arquivos", default="*.pdf")
        
        use_reference = Confirm.ask("Usar planilha de referência?")
        reference_path = None
        
        if use_reference:
            reference_path = Prompt.ask("Caminho para a planilha de referência")
            if not os.path.exists(reference_path):
                console.print("[bold yellow]Aviso: Planilha não encontrada, continuando sem referência[/bold yellow]")
                reference_path = None
        
        output_dir = Prompt.ask("Diretório para saída (opcional)", default="")
        
        if output_dir and not os.path.exists(output_dir):
            create_dir = Confirm.ask(f"O diretório {output_dir} não existe. Criar?")
            if create_dir:
                os.makedirs(output_dir)
            else:
                output_dir = ""
        
        # Preparar argumentos
        class Args:
            pass
        
        args = Args()
        args.pdf = None
        args.dir = dir_path
        args.reference = reference_path
        args.output = output_dir if output_dir else None
        args.pattern = pattern
        
        # Executar extração
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Extraindo dados dos PDFs..."),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Processando", total=None)
            results = cmd_extract(args)
        
        # Mostrar resultado
        if results:
            show_success(f"Extração concluída! {len(results)} PDFs processados")
            
            if output_dir:
                console.print(f"Dados salvos em: {output_dir}")
            else:
                console.print(f"Dados salvos em: {dir_path}")
        else:
            console.print("[bold red]Erro na extração. Verifique os arquivos PDF.[/bold red]")
    
    # Aguardar antes de voltar ao menu
    Prompt.ask("Pressione Enter para continuar", default="")

def interactive_process():
    """Modo interativo para processar dados para RAG"""
    console.print("[bold]Pré-processamento RAG[/bold]")
    
    # Opções de processamento
    console.print("Selecione uma opção:")
    console.print("1. Processar um único arquivo JSON")
    console.print("2. Processar todos os JSONs de um diretório")
    console.print("0. Voltar ao menu principal")
    
    choice = Prompt.ask("Opção", choices=["0", "1", "2"], default="1")
    
    if choice == "0":
        return
    
    if choice == "1":
        # Processamento de um único arquivo
        json_path = Prompt.ask("Caminho para o arquivo JSON")
        
        if not os.path.exists(json_path):
            console.print("[bold red]Erro: Arquivo não encontrado[/bold red]")
            return
        
        output_dir = Prompt.ask("Diretório para saída (opcional)", default="")
        
        if output_dir and not os.path.exists(output_dir):
            create_dir = Confirm.ask(f"O diretório {output_dir} não existe. Criar?")
            if create_dir:
                os.makedirs(output_dir)
            else:
                output_dir = ""
        
        chunk_size = Prompt.ask("Tamanho máximo de cada chunk", default="1000")
        chunk_overlap = Prompt.ask("Sobreposição entre chunks", default="200")
        index = Confirm.ask("Indexar no Supabase?")
        
        # Preparar argumentos
        class Args:
            pass
        
        args = Args()
        args.json = json_path
        args.dir = None
        args.output = output_dir if output_dir else None
        args.pattern = "*_extracted.json"
        args.chunk_size = int(chunk_size)
        args.chunk_overlap = int(chunk_overlap)
        args.index = index
        
        # Executar processamento
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Processando dados..."),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Processando", total=None)
            chunks = cmd_process(args)
        
        # Mostrar resultado
        if chunks:
            show_success(f"Processamento concluído! {len(chunks)} chunks gerados")
            
            if args.index:
                console.print("Chunks indexados no Supabase com sucesso!")
            
            json_name = os.path.basename(json_path).replace(".json", "_rag.json")
            if output_dir:
                console.print(f"Dados salvos em: {os.path.join(output_dir, json_name)}")
            else:
                json_dir = os.path.dirname(json_path)
                console.print(f"Dados salvos em: {os.path.join(json_dir, json_name)}")
        else:
            console.print("[bold red]Erro no processamento. Verifique o arquivo JSON.[/bold red]")
    
    elif choice == "2":
        # Processamento de um diretório
        dir_path = Prompt.ask("Caminho para o diretório com JSONs")
        
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            console.print("[bold red]Erro: Diretório não encontrado[/bold red]")
            return
        
        pattern = Prompt.ask("Padrão para filtrar arquivos", default="*_extracted.json")
        
        output_dir = Prompt.ask("Diretório para saída (opcional)", default="")
        
        if output_dir and not os.path.exists(output_dir):
            create_dir = Confirm.ask(f"O diretório {output_dir} não existe. Criar?")
            if create_dir:
                os.makedirs(output_dir)
            else:
                output_dir = ""
        
        chunk_size = Prompt.ask("Tamanho máximo de cada chunk", default="1000")
        chunk_overlap = Prompt.ask("Sobreposição entre chunks", default="200")
        index = Confirm.ask("Indexar no Supabase?")
        
        # Preparar argumentos
        class Args:
            pass
        
        args = Args()
        args.json = None
        args.dir = dir_path
        args.output = output_dir if output_dir else None
        args.pattern = pattern
        args.chunk_size = int(chunk_size)
        args.chunk_overlap = int(chunk_overlap)
        args.index = index
        
        # Executar processamento
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Processando dados..."),
            transient=True,
        ) as progress:
            task = progress.add_task(description="Processando", total=None)
            results = cmd_process(args)
        
        # Mostrar resultado
        if results:
            total_chunks = sum(len(chunk_list) for chunk_list in results)
            show_success(f"Processamento concluído! {len(results)} arquivos, {total_chunks} chunks gerados")
            
            if args.index:
                console.print("Chunks indexados no Supabase com sucesso!")
            
            if output_dir:
                console.print(f"Dados salvos em: {output_dir}")
            else:
                console.print(f"Dados salvos em: {dir_path}")
        else:
            console.print("[bold red]Erro no processamento. Verifique os arquivos JSON.[/bold red]")
    
    # Aguardar antes de voltar ao menu
    Prompt.ask("Pressione Enter para continuar", default="")

def interactive_query():
    """Modo interativo para consultar exames"""
    console.print("[bold]Consulta de Exames[/bold]")
    
    # Opções de consulta
    console.print("Selecione um critério de busca:")
    console.print("1. Buscar por nome do paciente")
    console.print("2. Buscar por intervalo de data")
    console.print("3. Buscar por tipo de exame")
    console.print("4. Mostrar todos os documentos")
    console.print("0. Voltar ao menu principal")
    
    choice = Prompt.ask("Opção", choices=["0", "1", "2", "3", "4"], default="1")
    
    if choice == "0":
        return
    
    # Preparar argumentos
    class Args:
        pass
    
    args = Args()
    args.patient = None
    args.dates = None
    args.exam_type = None
    args.output = None
    args.all_docs = False
    
    if choice == "1":
        # Busca por paciente
        args.patient = Prompt.ask("Nome do paciente")
        console.print("[dim](Busca por nome completo ou parte do nome)[/dim]")
    elif choice == "2":
        # Busca por data
        start_date = Prompt.ask("Data inicial (YYYY-MM-DD)")
        end_date = Prompt.ask("Data final (YYYY-MM-DD)")
        args.dates = f"{start_date}:{end_date}"
    elif choice == "3":
        # Busca por tipo de exame
        args.exam_type = Prompt.ask("Tipo de exame")
    elif choice == "4":
        # Mostrar todos os documentos
        args.all_docs = True
    
    # Perguntar se quer salvar resultados
    save_results = Confirm.ask("Salvar resultados em arquivo?")
    if save_results:
        args.output = Prompt.ask("Caminho para o arquivo de saída")
    
    # Executar consulta
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Consultando exames..."),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Processando", total=None)
        
        # Se opção é ver todos os documentos, usar uma função alternativa
        if args.all_docs:
            # Importar os módulos necessários aqui para evitar dependência circular
            import os
            from dotenv import load_dotenv
            from supabase import create_client, Client
            
            # Carregar variáveis de ambiente
            load_dotenv()
            
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            vector_collection = os.getenv("VECTOR_COLLECTION", "biolab_documents")
            
            client = create_client(supabase_url, supabase_key)
            
            # Buscar todos os documentos
            response = client.table(vector_collection).select("*").execute()
            results = response.data
        else:
            results = cmd_query(args)
    
    # Mostrar resultado
    if results and not isinstance(results, dict):
        show_success(f"Consulta concluída! {len(results)} resultados encontrados")
        
        # Mostrar resumo dos resultados
        if len(results) > 0:
            console.print("[bold]Resultados da consulta:[/bold]")
            
            # Formatação para melhor legibilidade
            table = Table(title="Documentos Encontrados", show_header=True)
            table.add_column("ID", style="dim")
            table.add_column("Tipo", style="cyan")
            table.add_column("Paciente", style="green")
            table.add_column("Fonte", style="blue")
            
            for i, item in enumerate(results, 1):
                if isinstance(item, dict):
                    doc_id = str(item.get("id", "?"))
                    chunk_type = item.get("chunk_type", "desconhecido")
                    
                    # Tentar obter o nome do paciente de diferentes lugares
                    patient = "Desconhecido"
                    metadata = item.get("metadata", {})
                    if isinstance(metadata, dict):
                        patient = metadata.get("patient_name", "Desconhecido")
                    
                    source = "Desconhecido"
                    if isinstance(metadata, dict):
                        source = metadata.get("source", "Desconhecido")
                    
                    # Adicionar linha à tabela
                    table.add_row(
                        doc_id, 
                        chunk_type, 
                        patient, 
                        source
                    )
            
            console.print(table)
            
            # Mostrar detalhes do primeiro documento como exemplo
            if len(results) > 0:
                first_doc = results[0]
                console.print("\n[bold]Exemplo de documento:[/bold]")
                
                # Mostrar metadados se disponíveis
                metadata = first_doc.get("metadata", {})
                if metadata and isinstance(metadata, dict):
                    console.print("Metadados:", style="bright_blue")
                    try:
                        import json
                        console.print(json.dumps(metadata, indent=2, ensure_ascii=False))
                    except:
                        console.print(str(metadata))
                
                # Mostrar conteúdo se disponível
                content = first_doc.get("content", "")
                if content:
                    console.print("\nConteúdo (primeiros 200 caracteres):", style="bright_blue")
                    console.print(content[:200] + "..." if len(content) > 200 else content)
        
        if args.output:
            console.print(f"Resultados salvos em: {args.output}")
    else:
        console.print("[bold yellow]Nenhum resultado encontrado para a consulta.[/bold yellow]")
        
        # Sugerir verificar a conexão com o banco de dados
        console.print("\n[dim]Sugestões: [/dim]")
        console.print("[dim]1. Verifique se o servidor MCP está rodando[/dim]")
        console.print("[dim]2. Verifique se os documentos foram indexados no Supabase[/dim]")
        console.print("[dim]3. Tente a opção 'Mostrar todos os documentos' para ver o que está no banco[/dim]")
    
    # Aguardar antes de voltar ao menu
    Prompt.ask("Pressione Enter para continuar", default="")

def interactive_workflow():
    """Modo interativo para fluxo completo"""
    console.print("[bold]Fluxo Completo de Processamento[/bold]")
    console.print("Este fluxo executará extração, processamento RAG e indexação em sequência.\n")
    
    # Selecionar PDF
    pdf_path = Prompt.ask("Caminho para o arquivo PDF")
    
    if not os.path.exists(pdf_path):
        console.print("[bold red]Erro: Arquivo não encontrado[/bold red]")
        return
    
    use_reference = Confirm.ask("Usar planilha de referência?")
    reference_path = None
    
    if use_reference:
        reference_path = Prompt.ask("Caminho para a planilha de referência")
        if not os.path.exists(reference_path):
            console.print("[bold yellow]Aviso: Planilha não encontrada, continuando sem referência[/bold yellow]")
            reference_path = None
    
    output_dir = Prompt.ask("Diretório para saída (opcional)", default="")
    
    if output_dir and not os.path.exists(output_dir):
        create_dir = Confirm.ask(f"O diretório {output_dir} não existe. Criar?")
        if create_dir:
            os.makedirs(output_dir)
        else:
            output_dir = ""
    
    chunk_size = Prompt.ask("Tamanho máximo de cada chunk", default="1000")
    chunk_overlap = Prompt.ask("Sobreposição entre chunks", default="200")
    
    # Preparar argumentos
    class Args:
        pass
    
    args = Args()
    args.pdf = pdf_path
    args.reference = reference_path
    args.output = output_dir if output_dir else None
    args.chunk_size = int(chunk_size)
    args.chunk_overlap = int(chunk_overlap)
    
    # Executar fluxo completo
    console.print("\n[bold]Iniciando fluxo completo...[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Executando fluxo completo..."),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Processando", total=None)
        result = cmd_workflow(args)
    
    # Mostrar resultado
    if result and not isinstance(result, dict):
        show_success("Fluxo completo concluído com sucesso!")
        
        # Mostrar resumo
        extract_result = result.get("extract", {})
        chunks = result.get("chunks", [])
        index_result = result.get("index", [])
        
        console.print(f"Exames extraídos: {len(extract_result.get('exams', []))}")
        console.print(f"Chunks gerados: {len(chunks)}")
        console.print(f"Chunks indexados: {len(index_result)}")
        
        pdf_name = os.path.basename(pdf_path)
        if output_dir:
            console.print(f"Dados salvos em: {os.path.join(output_dir, pdf_name.replace('.pdf', '_extracted.json'))}")
        else:
            pdf_dir = os.path.dirname(pdf_path)
            console.print(f"Dados salvos em: {os.path.join(pdf_dir, pdf_name.replace('.pdf', '_extracted.json'))}")
    else:
        console.print("[bold red]Erro durante o fluxo de trabalho.[/bold red]")
    
    # Aguardar antes de voltar ao menu
    Prompt.ask("Pressione Enter para continuar", default="")

def interactive_server():
    """Modo interativo para iniciar servidor"""
    console.print("[bold]Iniciar Servidor MCP[/bold]")
    
    host = Prompt.ask("Host para o servidor", default="0.0.0.0")
    port = Prompt.ask("Porta para o servidor", default="8000")
    
    # Preparar argumentos
    class Args:
        pass
    
    args = Args()
    args.host = host
    args.port = int(port)
    
    try:
        console.print(f"\nIniciando servidor MCP em {host}:{port}...")
        console.print("Pressione Ctrl+C para encerrar o servidor")
        console.print("\n")
        
        # Iniciar servidor
        cmd_server(args)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Servidor encerrado pelo usuário[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Erro ao iniciar servidor: {e}[/bold red]")
    
    # Aguardar antes de voltar ao menu
    Prompt.ask("Pressione Enter para continuar", default="")

def interactive_mode():
    """Função principal do modo interativo"""
    print_header()
    
    while True:
        # Menu principal
        main_options = [
            {"key": "1", "name": "Extrair", "description": "Extrair dados de PDFs de exames"},
            {"key": "2", "name": "Processar", "description": "Pré-processar dados para RAG"},
            {"key": "3", "name": "Consultar", "description": "Consultar exames no sistema"},
            {"key": "4", "name": "Workflow", "description": "Executar fluxo completo"},
            {"key": "5", "name": "Servidor", "description": "Iniciar servidor MCP"},
            {"key": "0", "name": "Sair", "description": "Sair do programa"}
        ]
        
        print_menu("Menu Principal", main_options)
        
        choice = Prompt.ask("Escolha uma opção", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            console.print("[bold blue]Até logo![/bold blue]")
            return
        
        elif choice == "1":
            interactive_extract()
        
        elif choice == "2":
            interactive_process()
        
        elif choice == "3":
            interactive_query()
        
        elif choice == "4":
            interactive_workflow()
        
        elif choice == "5":
            interactive_server()
        
        # Limpar tela entre menus
        console.clear()
        print_header()

if __name__ == "__main__":
    interactive_mode()