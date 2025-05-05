from typing import Dict, List, Any, Optional
import json
import httpx
from app.core.config import settings

async def get_embeddings(text: str) -> List[float]:
    """
    Gera embeddings para o texto fornecido utilizando o modelo de embeddings da OpenAI.
    
    Args:
        text: Texto para gerar embeddings
        
    Returns:
        Lista de floats representando o embedding do texto
    """
    if not text.strip():
        raise ValueError("Texto vazio não pode gerar embeddings")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }
    
    payload = {
        "input": text,
        "model": settings.EMBEDDING_MODEL
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
    if response.status_code != 200:
        raise Exception(f"Erro ao gerar embeddings: {response.text}")
    
    result = response.json()
    return result["data"][0]["embedding"]

async def get_chat_response(
    message: str,
    context: List[Dict[str, Any]] = None,
    chat_history: List[Dict[str, str]] = None,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Obtém resposta do modelo LLM da OpenAI para uma mensagem, utilizando contexto relevante.
    
    Args:
        message: Mensagem do usuário
        context: Lista de documentos de contexto relevantes
        chat_history: Histórico de conversa
        user_id: ID do usuário
        
    Returns:
        Dicionário contendo a resposta do LLM e metadados
    """
    if context is None:
        context = []
    
    if chat_history is None:
        chat_history = []
    
    # Construir o sistema de prompt com informações sobre o propósito do sistema
    system_prompt = """
    Você é um assistente especializado em análise de exames clínicos do BioLab.Ai. 
    Seu objetivo é ajudar os usuários a compreender seus exames, fornecer insights 
    personalizados e responder perguntas relacionadas à saúde com base nos dados disponíveis.
    
    Você deve:
    1. Analisar os exames fornecidos com precisão
    2. Explicar os resultados em linguagem acessível
    3. Destacar valores fora da referência
    4. Fornecer sugestões baseadas nas melhores práticas médicas
    5. Nunca fazer diagnósticos definitivos
    6. Sempre recomendar a consulta com profissionais de saúde
    
    Você tem acesso a uma base de conhecimento sobre exames clínicos e seus significados.
    Utilize essas informações para fornecer respostas precisas e personalizadas.
    
    Formato de respostas:
    - Para perguntas gerais: Forneça informações claras e concisas
    - Para análise de exames: Destaque valores anormais e explique seu significado
    - Para recomendações: Base suas sugestões na literatura científica atual
    
    Ao responder, sempre privilegie a clareza e precisão sobre tecnicidade excessiva.
    """
    
    # Formatar o contexto para o prompt
    context_text = ""
    if context:
        context_text = "Informações relevantes de contexto:\n\n"
        for i, doc in enumerate(context):
            context_text += f"[Documento {i+1}]\n"
            context_text += f"Nome: {doc.get('exam_name', '')}\n"
            context_text += f"Valor: {doc.get('exam_value', '')} {doc.get('exam_unit', '')}\n"
            context_text += f"Referência: {doc.get('reference_text', '')}\n"
            context_text += f"Conteúdo: {doc.get('content', '')}\n\n"
    
    # Formatar o histórico de conversa para o prompt
    conversation_history = []
    
    # Adicionar mensagem do sistema
    conversation_history.append({
        "role": "system",
        "content": system_prompt
    })
    
    # Adicionar histórico de conversa
    for message_entry in chat_history[-10:]:  # Limitar para os últimos 10 mensagens
        role = message_entry.get("role", "user" if message_entry.get("isUser") else "assistant")
        conversation_history.append({
            "role": role,
            "content": message_entry.get("content", "")
        })
    
    # Adicionar contexto e mensagem atual
    user_content = message
    if context_text:
        user_content = f"{user_content}\n\n{context_text}"
    
    conversation_history.append({
        "role": "user",
        "content": user_content
    })
    
    # Configurar requisição para a API da OpenAI
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": conversation_history,
        "temperature": 0.7,
        "max_tokens": 2048,
        "user": user_id or "anonymous_user"
    }
    
    # Fazer requisição para API da OpenAI
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0
        )
    
    if response.status_code != 200:
        raise Exception(f"Erro na API da OpenAI: {response.text}")
    
    result = response.json()
    
    # Processar resposta
    assistant_message = result["choices"][0]["message"]["content"]
    
    # Analisar a resposta para identificar intenções e ações sugeridas
    intent, suggested_actions = parse_assistant_response(assistant_message)
    
    return {
        "message": assistant_message,
        "intent": intent,
        "suggested_actions": suggested_actions,
        "references": [doc.get("document_id") for doc in context if "document_id" in doc]
    }

def parse_assistant_response(message: str) -> (str, List[Dict[str, Any]]):
    """
    Analisa a resposta do assistente para identificar intenção e ações sugeridas.
    
    Args:
        message: Texto da resposta do assistente
        
    Returns:
        Tuple contendo (intenção, lista de ações sugeridas)
    """
    # Lista de palavras-chave para diferentes intenções
    intent_keywords = {
        "analise_exame": ["analise", "análise", "examinar", "resultado", "exame", "avaliar"],
        "comparar_historico": ["comparar", "histórico", "tendência", "evolução", "progressão"],
        "gerar_relatorio": ["relatório", "report", "documento", "resumo", "compilar"],
        "recomendacao": ["recomendar", "sugerir", "indicar", "orientar", "melhorar"],
        "explicacao": ["explicar", "significado", "o que é", "para que serve", "função"]
    }
    
    # Detectar intenção com base nas palavras-chave
    detected_intent = "general"
    max_matches = 0
    
    message_lower = message.lower()
    for intent, keywords in intent_keywords.items():
        matches = sum(1 for keyword in keywords if keyword.lower() in message_lower)
        if matches > max_matches:
            max_matches = matches
            detected_intent = intent
    
    # Lista para armazenar ações sugeridas
    suggested_actions = []
    
    # Detectar ações sugeridas com base na intenção
    if detected_intent == "analise_exame":
        suggested_actions.append({
            "type": "view_exam_details",
            "description": "Ver detalhes completos dos exames"
        })
    elif detected_intent == "comparar_historico":
        suggested_actions.append({
            "type": "view_historic_chart",
            "description": "Visualizar gráfico histórico"
        })
    elif detected_intent == "gerar_relatorio":
        suggested_actions.append({
            "type": "generate_report",
            "description": "Gerar relatório completo"
        })
    
    return detected_intent, suggested_actions
