from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema para uma mensagem individual do chat."""
    role: str
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Schema para requisição de chat."""
    message: str
    chat_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class SuggestedAction(BaseModel):
    """Schema para ação sugerida pelo assistente."""
    type: str
    description: str
    data: Optional[Dict[str, Any]] = None


class Source(BaseModel):
    """Schema para fonte de informação usada na resposta."""
    type: str
    name: str
    detail: Optional[str] = None
    id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema para resposta de chat."""
    message: str
    intent: Optional[str] = None
    suggested_actions: Optional[List[SuggestedAction]] = Field(default_factory=list)
    references: Optional[List[str]] = Field(default_factory=list)
    sources: Optional[List[Source]] = Field(default_factory=list)
