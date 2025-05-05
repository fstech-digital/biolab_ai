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
CONFIG_FILE = ".biolab_config"
TOKEN = None


async def login():
    """Realiza login no sistema"""
    email = input("Email: ")
    password = getpass("Senha: ")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/auth/login",
                data={"username": email, "password": password},
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                
                # Salvar token para uso posterior
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"token": token}, f)
                
                print("Login realizado com sucesso!")
                return token
            else:
                print(f"Erro ao fazer login: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            return None


async def register():
    """Registra um novo usuário"""
    name = input("Nome: ")
    email = input("Email: ")
    password = getpass("Senha: ")
    password_confirm = getpass("Confirme a senha: ")
    
    if password != password_confirm:
        print("As senhas não conferem!")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/auth/register",
                json={"name": name, "email": email, "password": password},
            )
            
            if response.status_code == 200:
                print("Usuário registrado com sucesso! Faça login para continuar.")
            else:
                print(f"Erro ao registrar usuário: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")


async def upload_pdf():
    """Faz upload de um PDF de exame"""
    global TOKEN
    
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
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
                headers = {"Authorization": f"Bearer {TOKEN}"}
                
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
    global TOKEN
    
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
    if not filename:
        filename = input("Nome do arquivo a processar: ")
    
    # Processar o arquivo
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {TOKEN}"}
            
            # Processar o arquivo
            response = await client.post(
                f"{API_URL}/pdf/process/{filename}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print("Arquivo processado com sucesso!")
                print(f"ID do documento: {result['document_id']}")
                print(f"Exames encontrados: {result['exam_count']}")
                return result['document_id']
            else:
                print(f"Erro ao processar arquivo: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            return None


async def ask_question():
    """Faz uma pergunta ao sistema conversacional"""
    global TOKEN
    
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
    print("\nFaça uma pergunta sobre seus exames (digite 'sair' para voltar):")
    
    chat_history = []
    
    while True:
        question = input("\nVocê: ")
        
        if question.lower() == 'sair':
            break
        
        # Enviar pergunta
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                headers = {"Authorization": f"Bearer {TOKEN}"}
                print(f"\nEnviando pergunta para: {API_URL}/chat/message")
                
                response = await client.post(
                    f"{API_URL}/chat/message",
                    json={"message": question, "chat_history": chat_history},
                    headers=headers
                )
                
                print(f"Status da resposta: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("\nBioLab.Ai:", result['message'])
                    
                    # Exibir fontes das informações
                    if result.get('sources') and len(result.get('sources')) > 0:
                        print("\nFontes da informação:")
                        for i, source in enumerate(result['sources'], 1):
                            source_type = source.get('type', 'Desconhecida')
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
                    chat_history.append({"role": "assistant", "content": result['message']})
                    
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
    global TOKEN
    
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
    if not document_id:
        document_id = input("ID do documento: ")
    
    # Obter detalhes do documento
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {TOKEN}"}
            
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
    global TOKEN
    
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
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
            headers = {"Authorization": f"Bearer {TOKEN}"}
            
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
    global TOKEN
    
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
    document_id = input("ID do documento: ")
    
    # Obter exames anormais
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {TOKEN}"}
            
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
    global TOKEN
    
    # Verificar se já existe um token salvo
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                TOKEN = config.get("token")
        except:
            TOKEN = None
    
    while True:
        print("\n===== BioLab.Ai - Menu Principal =====")
        
        if TOKEN:
            print("1. Upload de PDF de exame")
            print("2. Processar PDF enviado")
            print("3. Perguntar sobre exames (Chat)")
            print("4. Ver detalhes de exames")
            print("5. Gerar relatório")
            print("6. Ver exames com valores anormais")
            print("7. Sair")
            print("8. Logout")
        else:
            print("1. Login")
            print("2. Registrar novo usuário")
            print("3. Sair")
        
        choice = input("\nEscolha uma opção: ")
        
        if TOKEN:
            # Usuário logado
            if choice == "1":
                await upload_pdf()
            elif choice == "2":
                await process_pdf()
            elif choice == "3":
                await ask_question()
            elif choice == "4":
                await view_exam_details()
            elif choice == "5":
                await generate_report()
            elif choice == "6":
                await view_abnormal_exams()
            elif choice == "7":
                print("Saindo do sistema. Até logo!")
                break
            elif choice == "8":
                # Fazer logout
                TOKEN = None
                if os.path.exists(CONFIG_FILE):
                    os.remove(CONFIG_FILE)
                print("Logout realizado com sucesso!")
            else:
                print("Opção inválida!")
        else:
            # Usuário não logado
            if choice == "1":
                TOKEN = await login()
            elif choice == "2":
                await register()
            elif choice == "3":
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
            asyncio.run(httpx.AsyncClient().get(f"{API_URL}/health"))
            print("Servidor online!")
        except:
            print("AVISO: Servidor parece estar offline!")
            print("Certifique-se de iniciar o servidor com 'python run.py' em outro terminal")
            proceed = input("Deseja continuar mesmo assim? (s/n): ").lower()
            if proceed != 's':
                sys.exit(1)
    
    # Iniciar menu principal
    asyncio.run(main_menu())
