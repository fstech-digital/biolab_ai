import os
import uvicorn
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

if __name__ == "__main__":
    # Configurações do servidor
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    # Imprimir informações de inicialização
    print(f"Iniciando BioLab.Ai em modo {'desenvolvimento' if debug else 'produção'}")
    print(f"Servidor disponível em: http://localhost:{port}")
    print("Pressione CTRL+C para sair")
    
    # Iniciar o servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )
