from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    Registra um novo usuário no sistema.
    """
    # Verificar se usuário já existe
    # Registro de usuário desabilitado temporariamente (funções removidas)
    raise HTTPException(status_code=501, detail="Registro de usuário não suportado nesta versão.")

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Obtenção de token de acesso através de credenciais.
    """
    # Login desabilitado temporariamente (funções removidas)
    raise HTTPException(status_code=501, detail="Login não suportado nesta versão.")
