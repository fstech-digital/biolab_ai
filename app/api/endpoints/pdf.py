import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.pdf import PDFUploadResponse, PDFProcessResponse
from app.services.pdf_extraction.extractor import extract_exam_data
from app.services.vector_db.supabase_client import store_document_vectors

router = APIRouter()

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Endpoint para upload de arquivo PDF de exame.
    """
    # Verificar se o arquivo é um PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos PDF são aceitos"
        )
    
    # Criar diretório de upload se não existir
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    
    # Gerar caminho do arquivo
    file_path = os.path.join(settings.UPLOAD_FOLDER, file.filename)
    
    # Salvar arquivo
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    return {
        "filename": file.filename,
        "file_path": file_path,
        "status": "success",
        "message": "Arquivo recebido com sucesso. Pronto para processamento."
    }

@router.post("/process/{filename}", response_model=PDFProcessResponse)
async def process_pdf(
    filename: str,
    current_user = Depends(get_current_user)
):
    """
    Processa um PDF de exame previamente enviado, extrai os dados e armazena no vector database.
    """
    # Caminho do arquivo
    file_path = os.path.join(settings.UPLOAD_FOLDER, filename)
    
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    try:
        # Extrair dados do PDF
        extracted_data = await extract_exam_data(file_path)
        
        # Armazenar no vector database
        document_id = await store_document_vectors(
            extracted_data, 
            filename, 
            user_id=current_user.id
        )
        
        return {
            "document_id": document_id,
            "filename": filename,
            "status": "success",
            "message": "Exame processado com sucesso",
            "exam_count": len(extracted_data.get("exams", [])),
            "metadata": extracted_data.get("metadata", {})
        }
        
    except Exception as e:
        # Logar o erro
        print(f"Erro ao processar PDF: {str(e)}")
        
        # Retornar erro
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar o exame: {str(e)}"
        )
