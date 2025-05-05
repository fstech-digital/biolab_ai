from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema para token de acesso."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema para payload do token."""
    sub: Optional[str] = None
    exp: Optional[int] = None
