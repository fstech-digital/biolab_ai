from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PDFUploadResponse(BaseModel):
    """Schema para resposta de upload de PDF."""
    filename: str
    file_path: str
    status: str
    message: str


class PDFProcessResponse(BaseModel):
    """Schema para resposta de processamento de PDF."""
    document_id: str
    filename: str
    status: str
    message: str
    exam_count: int
    metadata: Dict[str, Any]


class ExamData(BaseModel):
    """Schema para dados de um exame."""
    code: str
    name: str
    value: float
    unit: str
    reference_range: Dict[str, Any]


class ExamDataResponse(BaseModel):
    """Schema para resposta de dados de exames."""
    document_id: str
    exams: List[ExamData]
    metadata: Dict[str, Any]
