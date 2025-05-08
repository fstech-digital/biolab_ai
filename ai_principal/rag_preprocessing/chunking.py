"""
Módulo de chunking para RAG
Responsável por dividir os documentos em chunks para processamento
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExamChunker:
    """
    Classe para chunking de dados de exames médicos
    Divide os dados em chunks significativos para RAG
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa o chunker com configurações específicas
        
        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres
            chunk_overlap: Sobreposição entre chunks em caracteres
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_exam_data(self, exam_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Divide os dados de exames em chunks significativos
        
        Args:
            exam_data: Dados do exame extraídos do PDF
            
        Returns:
            Lista de chunks com metadados
        """
        chunks = []
        
        # Extrair dados do paciente para metadados
        patient_data = exam_data.get('patient', {})
        patient_name = patient_data.get('name', 'Desconhecido')
        patient_age = patient_data.get('age')
        patient_gender = patient_data.get('gender')
        exam_date = patient_data.get('exam_date')
        
        # Metadados comuns para todos os chunks
        common_metadata = {
            'source': exam_data.get('metadata', {}).get('filename', 'unknown_file'),
            'patient_name': patient_name,
            'exam_date': exam_date,
            'document_type': 'medical_exam'
        }
        
        if patient_age:
            common_metadata['patient_age'] = patient_age
        
        if patient_gender:
            common_metadata['patient_gender'] = patient_gender
        
        # 1. Chunk de informações do paciente
        patient_chunk = {
            'chunk_type': 'patient_info',
            'text': self._format_patient_info(patient_data),
            'metadata': {**common_metadata, 'section': 'patient_info'}
        }
        chunks.append(patient_chunk)
        
        # 2. Chunks para exames individuais
        exams = exam_data.get('exams', [])
        
        # Agrupar exames em chunks significativos
        if exams:
            # Criar chunks de exames relacionados
            current_chunk_text = ""
            current_chunk_exams = []
            
            for exam in exams:
                # Formatar exame como texto
                exam_text = self._format_exam_info(exam)
                
                # Se adicionar este exame exceder o tamanho, criar um novo chunk
                if len(current_chunk_text) + len(exam_text) > self.chunk_size and current_chunk_text:
                    chunks.append({
                        'chunk_type': 'exam_results',
                        'text': current_chunk_text,
                        'metadata': {
                            **common_metadata,
                            'section': 'exam_results',
                            'exams': [e.get('name', 'Unknown Exam') for e in current_chunk_exams]
                        }
                    })
                    
                    # Iniciar novo chunk com sobreposição
                    overlap_exams = current_chunk_exams[-2:] if len(current_chunk_exams) >= 2 else current_chunk_exams
                    current_chunk_text = "\n\n".join(self._format_exam_info(e) for e in overlap_exams)
                    current_chunk_exams = overlap_exams.copy()
                
                # Adicionar exame ao chunk atual
                current_chunk_text += "\n\n" + exam_text
                current_chunk_exams.append(exam)
            
            # Adicionar último chunk se houver dados
            if current_chunk_text:
                chunks.append({
                    'chunk_type': 'exam_results',
                    'text': current_chunk_text,
                    'metadata': {
                        **common_metadata,
                        'section': 'exam_results',
                        'exams': [e.get('name', 'Unknown Exam') for e in current_chunk_exams]
                    }
                })
        
        # 3. Chunk com resumo completo (para consultas gerais)
        summary_text = self._create_exam_summary(exam_data)
        if summary_text:
            chunks.append({
                'chunk_type': 'exam_summary',
                'text': summary_text,
                'metadata': {**common_metadata, 'section': 'exam_summary'}
            })
        
        return chunks
    
    def _format_patient_info(self, patient_data: Dict[str, Any]) -> str:
        """
        Formata as informações do paciente como texto
        
        Args:
            patient_data: Dicionário com dados do paciente
            
        Returns:
            Texto formatado com informações do paciente
        """
        lines = []
        lines.append(f"Paciente: {patient_data.get('name', 'Não informado')}")
        
        if patient_data.get('age'):
            lines.append(f"Idade: {patient_data['age']} anos")
        
        if patient_data.get('gender'):
            gender_map = {'M': 'Masculino', 'F': 'Feminino'}
            gender_str = gender_map.get(patient_data['gender'], patient_data['gender'])
            lines.append(f"Gênero: {gender_str}")
        
        if patient_data.get('date_of_birth'):
            lines.append(f"Data de Nascimento: {patient_data['date_of_birth']}")
        
        if patient_data.get('document'):
            lines.append(f"Documento: {patient_data['document']}")
        
        if patient_data.get('exam_date'):
            lines.append(f"Data do Exame: {patient_data['exam_date']}")
        
        return "\n".join(lines)
    
    def _format_exam_info(self, exam: Dict[str, Any]) -> str:
        """
        Formata as informações de um exame como texto
        
        Args:
            exam: Dicionário com dados do exame
            
        Returns:
            Texto formatado com informações do exame
        """
        lines = []
        
        name = exam.get('name', 'Exame sem nome')
        result = exam.get('result', 'Não informado')
        unit = exam.get('unit', '')
        reference = exam.get('reference', '')
        
        # Linha principal com nome e resultado
        result_str = f"{result} {unit}".strip()
        lines.append(f"Exame: {name}\nResultado: {result_str}")
        
        # Adicionar valor de referência se disponível
        if reference:
            lines.append(f"Valor de Referência: {reference}")
        
        # Adicionar dados da referência enriquecida, se disponíveis
        if 'reference_data' in exam:
            ref_data = exam['reference_data']
            
            # Adicionar referências filtradas por sexo/idade
            refs = ref_data.get('references', [])
            if refs:
                for i, ref in enumerate(refs):
                    ref_value = ref.get('value', '')
                    ref_unit = ref.get('unit', '')
                    ref_sex = ref.get('sex', '')
                    ref_age = ref.get('age_range', '')
                    
                    ref_str = f"Referência {i+1}: {ref_value} {ref_unit}".strip()
                    
                    if ref_sex or ref_age:
                        qualifiers = []
                        if ref_sex:
                            qualifiers.append(f"Sexo: {ref_sex}")
                        if ref_age:
                            qualifiers.append(f"Idade: {ref_age}")
                        
                        ref_str += f" ({', '.join(qualifiers)})"
                    
                    lines.append(ref_str)
        
        return "\n".join(lines)
    
    def _create_exam_summary(self, exam_data: Dict[str, Any]) -> str:
        """
        Cria um resumo geral dos exames
        
        Args:
            exam_data: Dicionário com todos os dados do exame
            
        Returns:
            Texto com resumo dos exames
        """
        patient_data = exam_data.get('patient', {})
        exams = exam_data.get('exams', [])
        
        if not exams:
            return ""
        
        lines = []
        
        # Cabeçalho
        lines.append(f"Resumo de Exames - {patient_data.get('name', 'Paciente')}")
        if patient_data.get('exam_date'):
            lines.append(f"Data: {patient_data['exam_date']}")
        lines.append("")
        
        # Lista de exames
        lines.append(f"Total de exames: {len(exams)}")
        lines.append("")
        lines.append("Exames realizados:")
        
        for i, exam in enumerate(exams, 1):
            name = exam.get('name', 'Exame sem nome')
            result = exam.get('result', 'Não informado')
            unit = exam.get('unit', '')
            
            result_str = f"{result} {unit}".strip()
            lines.append(f"{i}. {name}: {result_str}")
        
        return "\n".join(lines)