from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.security import get_current_user
from app.schemas.report import (
    ReportRequest, 
    ReportResponse, 
    ComparativeReportRequest, 
    ComparativeReportResponse
)
from app.services.report_generation.generator import (
    generate_report, 
    generate_comparative_report
)

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
async def create_report(
    request: ReportRequest,
    current_user = Depends(get_current_user)
):
    """
    Gera um relatório para um documento específico.
    """
    try:
        # Gerar o relatório
        report = await generate_report(
            document_id=request.document_id,
            user_id=current_user.id,
            report_type=request.report_type,
            custom_instructions=request.custom_instructions
        )
        
        return report
        
    except ValueError as e:
        # Erros de validação (documento não encontrado, acesso não autorizado, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        # Outros erros
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )

@router.post("/comparative", response_model=ComparativeReportResponse)
async def create_comparative_report(
    request: ComparativeReportRequest,
    current_user = Depends(get_current_user)
):
    """
    Gera um relatório comparativo para múltiplos documentos.
    """
    try:
        # Verificar se temos pelo menos dois documentos
        if len(request.document_ids) < 2:
            raise ValueError("São necessários pelo menos dois documentos para comparação")
        
        # Gerar o relatório comparativo
        report = await generate_comparative_report(
            document_ids=request.document_ids,
            user_id=current_user.id,
            exam_codes=request.exam_codes,
            custom_instructions=request.custom_instructions
        )
        
        return report
        
    except ValueError as e:
        # Erros de validação
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        # Outros erros
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório comparativo: {str(e)}"
        )

@router.get("/recent", response_model=List[ReportResponse])
async def get_recent_reports(
    limit: Optional[int] = 5,
    current_user = Depends(get_current_user)
):
    """
    Retorna os relatórios gerados recentemente para o usuário.
    """
    # Implementar busca no banco de dados para relatórios recentes
    # Esta é uma implementação de exemplo que seria substituída por uma consulta real
    
    # Simulação de dados para o MVP - seria substituído pela implementação real
    return []
