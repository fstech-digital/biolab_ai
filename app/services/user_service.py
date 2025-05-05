from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from app.schemas.user import UserCreate, UserInDB
from app.services.vector_db.supabase_client import supabase

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Busca um usuário pelo e-mail.
    
    Args:
        email: E-mail do usuário
        
    Returns:
        Objeto de usuário ou None se não encontrado
    """
    # Consultar usuário na tabela de usuários
    response = (
        supabase.table("users")
        .select("*")
        .filter("email", "eq", email)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao buscar usuário: {response['error']}")
    
    # Verificar se o usuário foi encontrado
    if not response.data or len(response.data) == 0:
        return None
    
    # Converter para objeto UserInDB
    user_data = response.data[0]
    return UserInDB(
        id=user_data["id"],
        email=user_data["email"],
        name=user_data["name"],
        is_active=user_data["is_active"],
        hashed_password=user_data["hashed_password"],
        created_at=user_data.get("created_at"),
        updated_at=user_data.get("updated_at")
    )

async def create_user(user_data: UserCreate, hashed_password: str) -> UserInDB:
    """
    Cria um novo usuário.
    
    Args:
        user_data: Dados do usuário
        hashed_password: Senha já com hash
        
    Returns:
        Objeto de usuário criado
    """
    # Gerar ID único para o usuário
    user_id = str(uuid.uuid4())
    
    # Data atual para timestamps
    now = datetime.now().isoformat()
    
    # Preparar dados para inserção
    user_dict = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "is_active": True,
        "hashed_password": hashed_password,
        "created_at": now,
        "updated_at": now
    }
    
    # Inserir na tabela de usuários
    response = supabase.table("users").insert(user_dict).execute()
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao criar usuário: {response['error']}")
    
    # Converter para objeto UserInDB
    return UserInDB(**user_dict)

async def update_user(user_id: str, update_data: Dict[str, Any]) -> UserInDB:
    """
    Atualiza dados de um usuário.
    
    Args:
        user_id: ID do usuário
        update_data: Dados a serem atualizados
        
    Returns:
        Objeto de usuário atualizado
    """
    # Adicionar timestamp de atualização
    update_data["updated_at"] = datetime.now().isoformat()
    
    # Atualizar na tabela de usuários
    response = (
        supabase.table("users")
        .update(update_data)
        .filter("id", "eq", user_id)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao atualizar usuário: {response['error']}")
    
    # Verificar se o usuário foi atualizado
    if not response.data or len(response.data) == 0:
        raise ValueError(f"Usuário não encontrado: {user_id}")
    
    # Converter para objeto UserInDB
    user_data = response.data[0]
    return UserInDB(
        id=user_data["id"],
        email=user_data["email"],
        name=user_data["name"],
        is_active=user_data["is_active"],
        hashed_password=user_data["hashed_password"],
        created_at=user_data.get("created_at"),
        updated_at=user_data.get("updated_at")
    )

async def delete_user(user_id: str) -> bool:
    """
    Desativa um usuário (soft delete).
    
    Args:
        user_id: ID do usuário
        
    Returns:
        True se o usuário foi desativado com sucesso
    """
    # Atualizar status do usuário para inativo
    response = (
        supabase.table("users")
        .update({"is_active": False, "updated_at": datetime.now().isoformat()})
        .filter("id", "eq", user_id)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise Exception(f"Erro ao desativar usuário: {response['error']}")
    
    # Verificar se o usuário foi atualizado
    if not response.data or len(response.data) == 0:
        raise ValueError(f"Usuário não encontrado: {user_id}")
    
    return True
