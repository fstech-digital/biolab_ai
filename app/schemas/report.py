from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    """Schema para requisição de geração de relatório."""
    document_id: str
    report_type: str = "complete"  # "summary", "complete", "detailed"
    custom_instructions: Optional[str] = None


class ComparativeReportRequest(BaseModel):
    """Schema para requisição de relatório comparativo."""
    document_ids: List[str]
    exam_codes: Optional[List[str]] = None
    custom_instructions: Optional[str] = None


class PatientInfo(BaseModel):
    """Schema para informações do paciente no relatório."""
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    date_collected: Optional[str] = None
    date_reported: Optional[str] = None


class LabInfo(BaseModel):
    """Schema para informações do laboratório no relatório."""
    lab_name: str
    file_name: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema para resposta de relatório gerado."""
    document_id: str
    generated_at: str
    report_type: str
    patient_info: PatientInfo
    lab_info: LabInfo
    content: str
    references: List[str] = Field(default_factory=list)


class ComparativeReportResponse(BaseModel):
    """Schema para resposta de relatório comparativo."""
    document_ids: List[str]
    generated_at: str
    report_type: str = "comparative"
    patient_info: PatientInfo
    content: str
    references: List[str] = Field(default_factory=list)
