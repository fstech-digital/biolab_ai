from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.security import get_current_user
from app.schemas.pdf import ExamDataResponse
from app.services.vector_db.supabase_client import get_exams_by_document_id, get_document_by_id

router = APIRouter()

@router.get("/{document_id}", response_model=ExamDataResponse)
async def get_exam_analysis(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """
    Recupera e retorna a análise de exames para um documento específico.
    """
    # Verificar se o documento existe
    document = await get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )
    
    # Verificar se o documento pertence ao usuário
    metadata = document.get("metadata", {})
    if "user_id" in metadata and metadata["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este documento"
        )
    
    # Recuperar exames do documento
    exams = await get_exams_by_document_id(document_id)
    
    # Formatar e retornar a resposta
    return {
        "document_id": document_id,
        "exams": exams,
        "metadata": metadata
    }

@router.get("/abnormal/{document_id}")
async def get_abnormal_exams(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """
    Retorna apenas os exames com valores fora da referência.
    """
    # Verificar se o documento existe
    document = await get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )
    
    # Verificar se o documento pertence ao usuário
    metadata = document.get("metadata", {})
    if "user_id" in metadata and metadata["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este documento"
        )
    
    # Recuperar todos os exames do documento
    all_exams = await get_exams_by_document_id(document_id)
    
    # Filtrar exames anormais
    abnormal_exams = []
    for exam in all_exams:
        # Verificar se o exame possui valor e referências
        if (exam.get("exam_value") is not None and 
            exam.get("reference_min") is not None and 
            exam.get("reference_max") is not None):
            
            # Verificar se está fora dos limites de referência
            if (exam["exam_value"] < exam["reference_min"] or 
                exam["exam_value"] > exam["reference_max"]):
                abnormal_exams.append(exam)
    
    # Formatar e retornar a resposta
    return {
        "document_id": document_id,
        "exams": abnormal_exams,
        "metadata": metadata,
        "abnormal_count": len(abnormal_exams),
        "total_count": len(all_exams)
    }

@router.get("/history/{exam_code}")
async def get_exam_history(
    exam_code: str,
    limit: Optional[int] = 10,
    current_user = Depends(get_current_user)
):
    """
    Retorna o histórico de resultados para um exame específico.
    """
    # Utilizar a função do Supabase para buscar todos os resultados deste exame
    # para o usuário atual, ordenados por data
    from app.services.vector_db.supabase_client import supabase
    
    # Consulta para buscar o histórico do exame
    response = (
        supabase.table("exam_vectors")
        .select("*")
        .filter("user_id", "eq", current_user.id)
        .filter("exam_code", "eq", exam_code)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    
    # Verificar se houve erro
    if "error" in response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico: {response['error']}"
        )
    
    # Formatar resultados
    results = []
    for item in response.data:
        doc = await get_document_by_id(item.get("document_id"))
        date = doc.get("metadata", {}).get("date_collected", "") if doc else ""
        
        results.append({
            "document_id": item.get("document_id"),
            "date": date,
            "exam_name": item.get("exam_name"),
            "exam_value": item.get("exam_value"),
            "exam_unit": item.get("exam_unit"),
            "reference_min": item.get("reference_min"),
            "reference_max": item.get("reference_max"),
            "reference_text": item.get("reference_text")
        })
    
    return {
        "exam_code": exam_code,
        "history": results,
        "count": len(results)
    }
