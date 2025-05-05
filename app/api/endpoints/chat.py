from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm.openai_client import get_chat_response
from app.services.rag.retriever import get_relevant_context

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    """
    Endpoint para interface conversacional com o sistema.
    Processa mensagens de texto do usuário, identifica a intenção e retorna respostas.
    """
    try:
        # Obter contexto relevante para a consulta
        context = await get_relevant_context(
            query=request.message,
            user_id=current_user.id
        )
        
        # Processar a mensagem com o modelo LLM
        response = await get_chat_response(
            message=request.message,
            context=context,
            chat_history=request.chat_history,
            user_id=current_user.id
        )
        
        # Verificar se a mensagem contém uma intenção específica
        # que requer ações adicionais no backend
        
        return {
            "message": response.get("message", ""),
            "intent": response.get("intent", "general"),
            "suggested_actions": response.get("suggested_actions", []),
            "references": response.get("references", [])
        }
        
    except Exception as e:
        # Logar o erro
        print(f"Erro no processamento da mensagem: {str(e)}")
        
        # Retornar erro
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )
