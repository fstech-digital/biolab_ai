#!/usr/bin/env python
"""
BioLab.Ai - Interface de linha de comando
Este script fornece uma interface simples via terminal para interagir com as
funcionalidades principais do BioLab.Ai sem necessidade de frontend.
"""

import os
import sys
import json
import asyncio
import httpx
from getpass import getpass
from typing import Dict, List, Any, Optional
from pprint import pprint
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_URL = "http://localhost:8000/api/v1"

async def upload_pdf():
    """Faz upload de um PDF de exame"""
    filepath = input("Caminho do arquivo PDF: ")
    
    if not os.path.exists(filepath):
        print(f"Arquivo não encontrado: {filepath}")
        return
    
    if not filepath.lower().endswith('.pdf'):
        print("O arquivo deve ser um PDF")
        return
    
    filename = os.path.basename(filepath)
    
    # Upload do arquivo
    async with httpx.AsyncClient() as client:
        try:
            # Preparar o arquivo para upload
            with open(filepath, "rb") as f:
                files = {"file": (filename, f, "application/pdf")}
                headers = {}
                
                # Fazer upload
                response = await client.post(
                    f"{API_URL}/pdf/upload",
                    files=files,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("Arquivo enviado com sucesso!")
                    print(f"Arquivo: {result['filename']}")
                    
                    # Perguntar se deseja processar o arquivo agora
                    process_now = input("Deseja processar o arquivo agora? (s/n): ").lower()
                    if process_now == 's':
                        await process_pdf(result['filename'])
                else:
                    print(f"Erro ao enviar arquivo: {response.status_code}")
                    print(response.text)
                    
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")


async def process_pdf(filename=None):
    """Processa um PDF previamente enviado"""
    if not filename:
        filename = input("Nome do arquivo a processar: ")
    
    print(f"Iniciando processamento do arquivo: {filename}")
    
    # Processar o arquivo
    try:
        # Usar timeout maior para dar tempo ao processamento do PDF
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                headers = {}
                
                print(f"Enviando solicitação para: {API_URL}/pdf/process/{filename}")
                
                # Processar o arquivo
                response = await client.post(
                    f"{API_URL}/pdf/process/{filename}",
                    headers=headers
                )
                
                print(f"Status da resposta: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("\nArquivo processado com sucesso!")
                    print(f"ID do documento: {result['document_id']}")
                    print(f"Exames encontrados: {result['exam_count']}")
                    return result['document_id']
                else:
                    print(f"\nErro ao processar arquivo: {response.status_code}")
                    if response.text:
                        error_detail = response.text
                        try:
                            # Tentar formatar a resposta se for JSON
                            error_json = response.json()
                            if 'detail' in error_json:
                                error_detail = error_json['detail']
                        except:
                            pass
                        print(f"Detalhes: {error_detail}")
                    return None
            except httpx.ConnectError as e:
                print(f"\nErro ao conectar ao servidor: Servidor inacessível")
                print(f"Detalhes: {str(e)}")
                return None
            except httpx.TimeoutException as e:
                print(f"\nErro de timeout: O servidor está demorando muito para responder")
                print(f"Detalhes: {str(e)}")
                print(f"O processamento pode estar ocorrendo em segundo plano.")
                return None
            except Exception as e:
                print(f"\nErro ao processar PDF: {str(e)[:200]}")
                return None
    except Exception as e:
        print(f"\nErro crítico: {str(e)[:200]}")
        return None


async def ask_question():
    """Faz uma pergunta ao sistema conversacional"""
    print("\nFaça uma pergunta sobre seus exames (digite 'sair' para voltar):")
    
    chat_history = []
    
    while True:
        question = input("\nVocê: ")
        
        if question.lower() == 'sair':
            break
        
        # Enviar pergunta
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                headers = {}
                print(f"\nEnviando pergunta para: {API_URL}/chat/message")
                
                response = await client.post(
                    f"{API_URL}/chat/message",
                    json={"message": question, "chat_history": chat_history},
                    headers=headers
                )
                
                print(f"Status da resposta: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Verificar e mostrar a estrutura da resposta para diagnóstico
                    print(f"Estrutura da resposta: {result.keys()}")
                    
                    # Tentar extrair a mensagem de diferentes locais possíveis
                    if 'message' in result:
                        message_content = result['message']
                    elif 'content' in result:
                        message_content = result['content']
                    elif 'answer' in result:
                        message_content = result['answer']
                    elif 'error' in result:
                        message_content = f"Erro do servidor: {result['error']}"
                    elif 'choices' in result and len(result.get('choices', [])) > 0:
                        # Formato possivelmente semelhante ao formato direto da OpenAI
                        first_choice = result['choices'][0]
                        if isinstance(first_choice, dict) and 'message' in first_choice:
                            message_content = first_choice['message'].get('content', str(first_choice))
                        else:
                            message_content = str(first_choice)
                    else:
                        # Mostrar a resposta bruta como fallback
                        import pprint
                        print("\nResposta bruta do servidor:")
                        pprint.pprint(result)
                        message_content = str(result)
                    
                    print("\nBioLab.Ai:", message_content)
                    
                    # Exibir fontes das informações
                    if result.get('sources') and len(result.get('sources')) > 0:
                        print("\nFontes da informação:")
                        for i, source in enumerate(result['sources'], 1):
                            source_type = source.get('type', 'Desconhecida')
                            if source_type.lower() == 'exame':
                                filename = source.get('filename', '')
                                date = source.get('date', '')
                                exam_name = source.get('name', '')
                                doc_id = source.get('id', '')
                                fonte_str = f"{i}. Fonte: "
                                if filename:
                                    fonte_str += f"{filename}"
                                if date:
                                    fonte_str += f" (data: {date})"
                                if exam_name:
                                    fonte_str += f" | Exame: {exam_name}"
                                if doc_id:
                                    fonte_str += f" | id: {doc_id}"
                                print(fonte_str)
                            else:
                                source_name = source.get('name', '')
                                source_detail = source.get('detail', '')
                                source_info = f"{i}. {source_type}: {source_name}"
                                if source_detail:
                                    source_info += f" - {source_detail}"
                                print(source_info)
                    
                    # Verificar se há ações sugeridas
                    if result.get('suggested_actions'):
                        print("\nAções sugeridas:")
                        for i, action in enumerate(result['suggested_actions']):
                            print(f"{i+1}. {action['description']}")
                        
                        action_choice = input("\nDeseja executar alguma ação? (número ou 'n' para não): ")
                        if action_choice.isdigit() and 1 <= int(action_choice) <= len(result['suggested_actions']):
                            action = result['suggested_actions'][int(action_choice)-1]
                            # Implementar execução de ações específicas aqui
                            if action['type'] == 'view_exam_details':
                                doc_id = input("Digite o ID do documento: ")
                                await view_exam_details(doc_id)
                            elif action['type'] == 'generate_report':
                                doc_id = input("Digite o ID do documento: ")
                                await generate_report(doc_id)
                    
                    # Adicionar à história do chat
                    chat_history.append({"role": "user", "content": question})
                    chat_history.append({"role": "assistant", "content": message_content})
                    
                else:
                    print(f"Erro ao enviar pergunta: {response.status_code}")
                    print(f"Resposta: {response.text}")
            
            except httpx.TimeoutException:
                print("Erro: Tempo limite de conexão excedido. Verifique se o servidor API está rodando.")
            except httpx.ConnectError:
                print("Erro de conexão: Não foi possível conectar ao servidor API.")
                print("Verifique se o servidor está rodando em http://localhost:8000")
            except Exception as e:
                print(f"Erro ao conectar ao servidor: {e}")
                import traceback
                traceback.print_exc()


async def view_exam_details(document_id=None):
    """Visualiza detalhes dos exames de um documento"""
    
    if not document_id:
        document_id = input("ID do documento: ")
    
    # Obter detalhes do documento
    async with httpx.AsyncClient() as client:
        try:
            headers = {}
            
            response = await client.get(
                f"{API_URL}/analysis/{document_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Exibir informações do paciente
                patient = result.get('metadata', {})
                print("\n===== DADOS DO PACIENTE =====")
                print(f"Nome: {patient.get('name', 'N/A')}")
                print(f"Idade: {patient.get('age', 'N/A')}")
                print(f"Laboratório: {patient.get('lab_type', 'N/A')}")
                
                # Exibir exames
                print("\n===== EXAMES =====")
                for exam in result.get('exams', []):
                    value = exam.get('exam_value')
                    ref_min = exam.get('reference_min')
                    ref_max = exam.get('reference_max')
                    
                    # Verificar se está fora da referência
                    status = ""
                    if ref_min is not None and ref_max is not None:
                        if value < ref_min:
                            status = " [ABAIXO]"
                        elif value > ref_max:
                            status = " [ACIMA]"
                    
                    print(f"{exam.get('exam_name')}: {value} {exam.get('exam_unit', '')}{status}")
                    print(f"  Referência: {exam.get('reference_text', 'N/A')}")
                
                print("\nDeseja gerar um relatório para este exame? (s/n): ")
                choice = input().lower()
                if choice == 's':
                    await generate_report(document_id)
            else:
                print(f"Erro ao obter detalhes: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")


async def generate_report(document_id=None):
    """Gera um relatório para um documento"""
    
    if not document_id:
        document_id = input("ID do documento: ")
    
    print("\nTipo de relatório:")
    print("1. Resumido")
    print("2. Completo")
    print("3. Detalhado")
    
    choice = input("Escolha o tipo (1-3): ")
    
    report_type = "complete"  # padrão
    if choice == "1":
        report_type = "summary"
    elif choice == "3":
        report_type = "detailed"
    
    custom_instructions = input("Instruções adicionais (opcional): ")
    
    # Gerar relatório
    async with httpx.AsyncClient() as client:
        try:
            headers = {}
            
            payload = {
                "document_id": document_id,
                "report_type": report_type
            }
            
            if custom_instructions:
                payload["custom_instructions"] = custom_instructions
            
            response = await client.post(
                f"{API_URL}/reports/generate",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n========== RELATÓRIO ==========")
                print(f"Paciente: {result.get('patient_info', {}).get('name', 'N/A')}")
                print(f"Tipo: {report_type.capitalize()}")
                print(f"Gerado em: {result.get('generated_at', 'N/A')}")
                print("\n")
                print(result.get('content', ''))
                print("\n===============================")
                
                # Perguntar se deseja salvar o relatório em arquivo
                save_file = input("\nDeseja salvar o relatório em arquivo? (s/n): ").lower()
                if save_file == 's':
                    filename = f"relatorio_{document_id}_{report_type}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(f"Relatório: {report_type.capitalize()}\n")
                        f.write(f"Paciente: {result.get('patient_info', {}).get('name', 'N/A')}\n")
                        f.write(f"Gerado em: {result.get('generated_at', 'N/A')}\n\n")
                        f.write(result.get('content', ''))
                    
                    print(f"Relatório salvo como: {filename}")
            else:
                print(f"Erro ao gerar relatório: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")


async def view_abnormal_exams():
    """Visualiza exames com resultados anormais"""
    
    document_id = input("ID do documento: ")
    
    # Obter exames anormais
    async with httpx.AsyncClient() as client:
        try:
            headers = {}
            
            response = await client.get(
                f"{API_URL}/analysis/abnormal/{document_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n===== EXAMES COM VALORES ANORMAIS =====")
                print(f"Total de exames anormais: {result.get('abnormal_count', 0)} de {result.get('total_count', 0)}")
                
                for exam in result.get('exams', []):
                    value = exam.get('exam_value')
                    ref_min = exam.get('reference_min')
                    ref_max = exam.get('reference_max')
                    
                    status = "ANORMAL"
                    if ref_min is not None and value < ref_min:
                        status = "ABAIXO"
                    elif ref_max is not None and value > ref_max:
                        status = "ACIMA"
                    
                    print(f"{exam.get('exam_name')}: {value} {exam.get('exam_unit', '')} [{status}]")
                    print(f"  Referência: {exam.get('reference_text', 'N/A')}")
            else:
                print(f"Erro ao obter exames anormais: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")


async def main_menu():
    """Menu principal do aplicativo"""
    
    while True:            
        print("\n===== BioLab.Ai - Menu Principal =====")
        print("1. Upload de PDF de exame")
        print("2. Processar PDF enviado")
        print("3. Perguntar sobre exames (Chat)")
        print("4. Ver detalhes de exames")
        print("5. Sair")
        
        choice = input("\nEscolha uma opção: ")
        
        if choice == "1":
            await upload_pdf()
        elif choice == "2":
            await process_pdf()
        elif choice == "3":
            await ask_question()
        elif choice == "4":
            await view_exam_details()
        elif choice == "5":
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    print("Iniciando BioLab.Ai CLI...")
    
    # Verificar se o servidor está rodando
    if len(sys.argv) > 1 and sys.argv[1] == "--no-check":
        # Pular verificação de servidor
        pass
    else:
        print("Verificando conexão com o servidor...")
        try:
            health_url = "http://localhost:8000/api/v1/health"
            
            # Usar abordagem síncrona mais simples para a verificação de conexão
            import requests
            response = requests.get(health_url, timeout=5)  # Timeout de 5 segundos
            if response.status_code == 200:
                print("Servidor online!")
            else:
                raise Exception(f"Resposta inesperada: {response.status_code}")
        except Exception as e:
            print(f"AVISO: Servidor parece estar offline! Erro: {str(e)[:100]}")
            print("Certifique-se de iniciar o servidor com 'python run.py' em outro terminal")
            proceed = input("Deseja continuar mesmo assim? (s/n): ").lower()
            if proceed != 's':
                sys.exit(1)
    
    # Iniciar menu principal
    asyncio.run(main_menu())