from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Schema base para usuários."""
    email: EmailStr
    name: str
    is_active: bool = True


class UserCreate(BaseModel):
    """Schema para criação de usuários."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str


class UserUpdate(BaseModel):
    """Schema para atualização de usuários."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema para usuário armazenado no banco de dados."""
    id: str
    hashed_password: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserResponse(UserBase):
    """Schema para resposta de usuário."""
    id: str

    class Config:
        from_attributes = True
