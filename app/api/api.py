from fastapi import APIRouter
from app.api.endpoints import auth, pdf, chat, analysis, reports

api_router = APIRouter()

# Incluir rotas dos diferentes endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["autenticação"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["processamento de pdf"])
api_router.include_router(chat.router, prefix="/chat", tags=["interface conversacional"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["análise de exames"])
api_router.include_router(reports.router, prefix="/reports", tags=["relatórios"])

# Rota de verificação de saúde da API
@api_router.get("/health")
def health_check():
    return {"status": "ok"}
