from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.schemas.token import TokenPayload
from app.services.user_service import get_user_by_email

# Configurar contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT.
    
    Args:
        data: Dados a serem codificados no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha está correta.
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenada
        
    Returns:
        True se a senha está correta, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash de senha.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    """
    Valida o token JWT e retorna o usuário correspondente.
    
    Args:
        token: Token JWT
        
    Returns:
        Usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_email(token_data.sub)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
        
    return user
