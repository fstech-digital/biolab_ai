from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user, get_user_by_email

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    Registra um novo usuário no sistema.
    """
    # Verificar se usuário já existe
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Criar novo usuário
    hashed_password = get_password_hash(user_data.password)
    user = await create_user(user_data, hashed_password)
    
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Obtenção de token de acesso através de credenciais.
    """
    user = await get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 dias
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
