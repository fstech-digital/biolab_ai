from typing import Dict, List, Any, Optional
import json
import httpx
import os
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
    
    _cached_prompt = None
    def _get_system_prompt() -> str:
        """
        Lê o prompt do sistema do arquivo ai_principal/Reusable_Prompts/context_prime.md.
        Usa cache simples para evitar múltiplas leituras.
        """
        nonlocal _cached_prompt
        if _cached_prompt is None:
            # Caminho absoluto subindo três níveis para garantir a raiz do projeto
            prompt_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '../../../ai_principal/Reusable_Prompts/context_prime.md')
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                _cached_prompt = f.read().strip()
        return _cached_prompt
    
    system_prompt = _get_system_prompt()
    
    # Extrair informações de contexto para o prompt
    context_text = ""
    source_info = []
    
    if context and len(context) > 0:
        context_text = "CONTEXTO RELEVANTE:\n\n"
        for i, doc in enumerate(context, 1):
            # Capturar informações sobre a fonte
            source = {
                "id": doc.get("id", ""),
                "document_id": doc.get("document_id", ""),
                "source_type": "",
                "source_name": ""
            }
            
            # Identificar o tipo de fonte
            if "sheet_id" in doc and "collection_name" in doc:
                source["source_type"] = "knowledge_base"
                source["source_name"] = doc.get("collection_name", "")
                if doc.get("metadata") and isinstance(doc.get("metadata"), dict):
                    if "sheet_name" in doc.get("metadata"):
                        source["source_detail"] = doc.get("metadata").get("sheet_name", "")
            elif "exam_name" in doc:
                source["source_type"] = "exam"
                source["source_name"] = "Exame de Laboratório"
                source["source_detail"] = doc.get("exam_name", "")
            
            source_info.append(source)
            
            # Adicionar ao contexto para o prompt
            context_text += f"Contexto {i}:\n"
            if "exam_name" in doc and "exam_value" in doc:
                context_text += f"Exame: {doc.get('exam_name', '')}\n"
                context_text += f"Valor: {doc.get('exam_value', '')} {doc.get('exam_unit', '')}\n"
                context_text += f"Referência: {doc.get('reference_text', '')}\n"
            
            if "content" in doc:
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
        "temperature": 0.13,
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
    
    # Formatar fontes para exibição
    formatted_sources = []
    for source in source_info:
        if source["source_type"] == "knowledge_base":
            formatted_sources.append({
                "type": "Base de Conhecimento",
                "name": source["source_name"],
                "detail": source.get("source_detail", "")
            })
        elif source["source_type"] == "exam":
            formatted_sources.append({
                "type": "Exame",
                "name": source["source_detail"],
                "id": source["document_id"]
            })
    
    return {
        "message": assistant_message,
        "intent": intent,
        "suggested_actions": suggested_actions,
        "references": [doc.get("document_id") for doc in context if "document_id" in doc],
        "sources": formatted_sources
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
