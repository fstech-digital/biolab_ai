import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    # Informações do projeto
    PROJECT_NAME: str = "BioLab.Ai"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "API para análise de exames clínicos utilizando IA"
    
    # Configuração da API
    API_V1_STR: str = "/api/v1"
    
    # Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_padrao")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    VECTOR_COLLECTION: str = os.getenv("VECTOR_COLLECTION", "biolab_documents")
    
    # Configurações de armazenamento
    UPLOAD_FOLDER: str = "tmp/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    # Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

    # Novos campos para leitura do .env
    DEBUG: bool = False
    PORT: int = 8000
    TEST_USER_ID: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
