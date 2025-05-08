"""
Comandos da interface CLI do BioLab.Ai
Define os comandos disponíveis na interface de linha de comando
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Importar módulos do projeto
from ai_principal.pdf_extraction.main import process_pdf_file as extract_pdf
from ai_principal.pdf_extraction.main import process_directory as extract_directory
from ai_principal.rag_preprocessing.processor import RAGProcessor
from ai_principal.rag_preprocessing.supabase_indexer import SupabaseIndexer
from ai_principal.mcp_server.server import MCPServer

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cmd_extract(args):
    """
    Comando para extrair dados de PDFs de exames
    
    Args:
        args: Argumentos da linha de comando
    """
    try:
        if args.pdf:
            # Processar um único PDF
            logger.info(f"Extraindo dados do PDF: {args.pdf}")
            result = extract_pdf(
                args.pdf,
                reference_path=args.reference,
                output_dir=args.output
            )
            logger.info(f"Extração concluída: {len(result.get('exams', []))} exames encontrados")
            return result
        
        elif args.dir:
            # Processar um diretório de PDFs
            logger.info(f"Extraindo dados dos PDFs em: {args.dir}")
            results = extract_directory(
                args.dir,
                reference_path=args.reference,
                output_dir=args.output,
                file_pattern=args.pattern
            )
            logger.info(f"Extração concluída: {len(results)} PDFs processados")
            return results
    
    except Exception as e:
        logger.error(f"Erro durante a extração: {e}")
        return {"error": str(e)}

def cmd_process(args):
    """
    Comando para pré-processar dados extraídos para RAG
    
    Args:
        args: Argumentos da linha de comando
    """
    try:
        processor = RAGProcessor(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        
        if args.json:
            # Processar um único arquivo JSON
            logger.info(f"Pré-processando arquivo: {args.json}")
            chunks = processor.process_exam_file(args.json)
            logger.info(f"Pré-processamento concluído: {len(chunks)} chunks gerados")
            
            # Indexar no Supabase, se solicitado
            if args.index:
                logger.info("Indexando chunks no Supabase...")
                indexer = SupabaseIndexer()
                responses = indexer.index_chunks(chunks)
                logger.info(f"Indexação concluída: {len(responses)} chunks indexados")
            
            return chunks
        
        elif args.dir:
            # Processar um diretório de arquivos JSON
            logger.info(f"Pré-processando arquivos em: {args.dir}")
            results = processor.process_directory(
                args.dir,
                file_pattern=args.pattern
            )
            total_chunks = sum(len(chunk_list) for chunk_list in results)
            logger.info(f"Pré-processamento concluído: {len(results)} arquivos, {total_chunks} chunks gerados")
            
            # Indexar no Supabase, se solicitado
            if args.index:
                logger.info("Indexando chunks no Supabase...")
                indexer = SupabaseIndexer()
                
                all_responses = {}
                for i, chunk_list in enumerate(results):
                    responses = indexer.index_chunks(chunk_list)
                    all_responses[f"file_{i}"] = responses
                
                total_indexed = sum(len(resp_list) for resp_list in all_responses.values())
                logger.info(f"Indexação concluída: {total_indexed} chunks indexados")
            
            return results
    
    except Exception as e:
        logger.error(f"Erro durante o pré-processamento: {e}")
        return {"error": str(e)}

def cmd_query(args):
    """
    Comando para consultar exames
    
    Args:
        args: Argumentos da linha de comando
    """
    try:
        from ai_principal.mcp_server.mcp_tools import PatientExamSearchRequest, ExamDateSearchRequest, ExamTypeSearchRequest
        
        # Tentar conexão direta com o Supabase para verificação
        import os
        from dotenv import load_dotenv
        from supabase import create_client, Client
        
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Testar se o servidor MCP está acessível primeiro
        server = MCPServer()
        
        if args.patient:
            # Buscar exames por paciente
            logger.info(f"Buscando exames para paciente: {args.patient}")
            
            # Método 1: Via MCP Server
            try:
                request = {
                    "tool_name": "buscar_exames_paciente",
                    "parameters": {
                        "patient_name": args.patient
                    }
                }
                
                # Executar a consulta via MCP Server
                response = server.handle_request(request)
                
                # Se encontrar resultados, retornar
                if response.get("status") == "success" and response.get("data", []):
                    data = response.get("data", [])
                    return data
            except Exception as mcp_error:
                logger.warning(f"Erro ao buscar via MCP: {mcp_error}. Tentando diretamente no Supabase...")
            
            # Método 2: Direto no Supabase como fallback
            try:
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_KEY")
                vector_collection = os.getenv("VECTOR_COLLECTION", "biolab_documents")
                
                if not supabase_url or not supabase_key:
                    raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no .env")
                
                client = create_client(supabase_url, supabase_key)
                
                # Usar ILIKE para buscar pelo nome parcial
                response = (
                    client.table(vector_collection)
                    .select("*")
                    .filter("metadata->>patient_name", "ilike", f"%{args.patient}%")
                    .execute()
                )
                
                # Se encontrou resultados, retornar
                if response.data:
                    return response.data
                
                # Tentar outras formas de busca
                # Buscar em content
                response = (
                    client.table(vector_collection)
                    .select("*")
                    .filter("content", "ilike", f"%{args.patient}%")
                    .execute()
                )
                
                if response.data:
                    return response.data
            except Exception as supabase_error:
                logger.error(f"Erro ao buscar diretamente no Supabase: {supabase_error}")
            
        elif args.dates:
            # Buscar exames por intervalo de data
            start_date, end_date = args.dates.split(':')
            logger.info(f"Buscando exames no intervalo: {start_date} a {end_date}")
            request = {
                "tool_name": "buscar_exames_data",
                "parameters": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            # Executar a consulta via MCP Server
            response = server.handle_request(request)
            
            # Se encontrar resultados, retornar
            if response.get("status") == "success":
                data = response.get("data", [])
                return data
            
        elif args.exam_type:
            # Buscar exames por tipo
            logger.info(f"Buscando exames do tipo: {args.exam_type}")
            request = {
                "tool_name": "buscar_exames_tipo",
                "parameters": {
                    "exam_type": args.exam_type
                }
            }
            
            # Executar a consulta via MCP Server
            response = server.handle_request(request)
            
            # Se encontrar resultados, retornar
            if response.get("status") == "success":
                data = response.get("data", [])
                return data
            
        else:
            logger.error("É necessário especificar pelo menos um critério de busca")
            return {"error": "Critério de busca não especificado"}
        
        # Se chegou aqui, é porque não encontrou nada
        return []
    
    except Exception as e:
        logger.error(f"Erro durante a consulta: {e}")
        return {"error": str(e)}

def cmd_server(args):
    """
    Comando para iniciar o servidor MCP
    
    Args:
        args: Argumentos da linha de comando
    """
    try:
        from ai_principal.mcp_server.http_server import start_server
        
        # Definir porta
        port = args.port or int(os.getenv("PORT", 8000))
        
        # Iniciar servidor
        logger.info(f"Iniciando servidor MCP na porta {port}...")
        print(f"\nIniciando servidor MCP na porta {port}...")
        print(f"Use Ctrl+C para encerrar o servidor")
        
        start_server(host=args.host, port=port)
        
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
        print("\nServidor encerrado pelo usuário")
    
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        return {"error": str(e)}

def cmd_workflow(args):
    """
    Comando para executar um fluxo completo de processamento
    
    Args:
        args: Argumentos da linha de comando
    """
    try:
        print("\n=== Iniciando fluxo completo de processamento ===\n")
        
        # 1. Extração de PDF
        print("\n[1/3] Extraindo dados do PDF...")
        extract_result = extract_pdf(
            args.pdf,
            reference_path=args.reference,
            output_dir=args.output
        )
        
        # Obter caminho do arquivo JSON extraído
        pdf_name = Path(args.pdf).stem
        output_dir = args.output or os.path.dirname(args.pdf)
        extract_json_path = os.path.join(output_dir, f"{pdf_name}_extracted.json")
        
        print(f"     ✓ Extração concluída: {len(extract_result.get('exams', []))} exames encontrados")
        print(f"     ✓ Dados salvos em: {extract_json_path}")
        
        # 2. Pré-processamento RAG
        print("\n[2/3] Pré-processando dados para RAG...")
        processor = RAGProcessor(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        
        chunks = processor.process_exam_file(extract_json_path)
        
        print(f"     ✓ Pré-processamento concluído: {len(chunks)} chunks gerados")
        
        # 3. Indexação no Supabase
        print("\n[3/3] Indexando dados no Supabase...")
        indexer = SupabaseIndexer()
        responses = indexer.index_chunks(chunks)
        
        print(f"     ✓ Indexação concluída: {len(responses)} chunks indexados")
        
        print("\n=== Fluxo completo concluído com sucesso ===\n")
        
        return {
            "extract": extract_result,
            "chunks": chunks,
            "index": responses
        }
    
    except Exception as e:
        logger.error(f"Erro durante o fluxo de trabalho: {e}")
        print(f"\nErro: {e}")
        return {"error": str(e)}