import pdfplumber
import fitz  # PyMuPDF
import re
from typing import Dict, List, Any
import datetime

# Tipos de laboratórios suportados
SUPPORTED_LABS = [
    "LABORATORIO A",
    "LABORATORIO B",
    "LABORATORIO C"
]

async def extract_exam_data(file_path: str) -> Dict[str, Any]:
    """
    Extrai dados de exames de um arquivo PDF.
    
    Esta função utiliza pdfplumber e PyMuPDF para extrair dados de diferentes
    formatos de laboratórios, reconhecendo padrões específicos.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Dicionário contendo dados estruturados do exame e metadados
    """
    # Metadados do documento
    metadata = {
        "processed_at": datetime.datetime.now().isoformat(),
        "file_name": file_path.split("/")[-1],
    }
    
    # Detectar o tipo/formato do laboratório
    lab_type = await detect_lab_type(file_path)
    metadata["lab_type"] = lab_type
    
    # Extrair informações do paciente
    patient_info = await extract_patient_info(file_path, lab_type)
    metadata.update(patient_info)
    
    # Extrair exames específicos
    exams = await extract_specific_exams(file_path, lab_type)
    
    # Estruturar resultado final
    result = {
        "metadata": metadata,
        "exams": exams
    }
    
    return result

async def detect_lab_type(file_path: str) -> str:
    """
    Detecta o tipo de laboratório com base no conteúdo do PDF.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        String indicando o tipo de laboratório detectado
    """
    with pdfplumber.open(file_path) as pdf:
        text = ""
        # Verificar apenas as primeiras páginas para eficiência
        max_pages = min(3, len(pdf.pages))
        
        for i in range(max_pages):
            text += pdf.pages[i].extract_text() or ""
    
    # Verificar padrões específicos para cada laboratório
    for lab in SUPPORTED_LABS:
        if lab.lower() in text.lower():
            return lab
    
    # Se não encontrar, retornar tipo genérico
    return "UNKNOWN"

async def extract_patient_info(file_path: str, lab_type: str) -> Dict[str, Any]:
    """
    Extrai informações do paciente com base no tipo de laboratório.
    
    Args:
        file_path: Caminho para o arquivo PDF
        lab_type: Tipo de laboratório detectado
        
    Returns:
        Dicionário com informações do paciente
    """
    patient_info = {
        "name": "",
        "age": None,
        "gender": "",
        "date_collected": "",
        "date_reported": ""
    }
    
    with pdfplumber.open(file_path) as pdf:
        # Extrair texto da primeira página
        first_page = pdf.pages[0]
        text = first_page.extract_text() or ""
        
        # Aplicar diferentes extractors baseados no tipo de laboratório
        if lab_type == "LABORATORIO A":
            # Exemplo para um formato específico
            name_match = re.search(r"Nome:[\s]*([^\n]+)", text)
            if name_match:
                patient_info["name"] = name_match.group(1).strip()
                
            age_match = re.search(r"Idade:[\s]*(\d+)", text)
            if age_match:
                patient_info["age"] = int(age_match.group(1))
                
            # Outras extrações específicas...
            
        elif lab_type == "LABORATORIO B":
            # Padrões diferentes para outro laboratório
            name_match = re.search(r"Paciente:[\s]*([^\n]+)", text)
            if name_match:
                patient_info["name"] = name_match.group(1).strip()
            
            # Outras extrações...
            
        else:
            # Abordagem genérica
            name_patterns = [
                r"Nome:[\s]*([^\n]+)",
                r"Paciente:[\s]*([^\n]+)",
                r"Patient:[\s]*([^\n]+)"
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, text)
                if name_match:
                    patient_info["name"] = name_match.group(1).strip()
                    break
            
            # Tentar extrair idade usando padrões genéricos
            age_patterns = [
                r"Idade:[\s]*(\d+)",
                r"Age:[\s]*(\d+)",
                r"Idade:[\s]*(\d+)[\s]*anos"
            ]
            
            for pattern in age_patterns:
                age_match = re.search(pattern, text)
                if age_match:
                    patient_info["age"] = int(age_match.group(1))
                    break
    
    return patient_info

async def extract_specific_exams(file_path: str, lab_type: str) -> List[Dict[str, Any]]:
    """
    Extrai informações dos exames específicos.
    
    Args:
        file_path: Caminho para o arquivo PDF
        lab_type: Tipo de laboratório detectado
        
    Returns:
        Lista de dicionários, cada um contendo dados de um exame específico
    """
    exams = []
    
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    # Lista de padrões de exames comuns a serem procurados
    common_exam_patterns = [
        # Hemograma
        (r"Hemoglobina[:\s]*(\d+,?\d*)", "HEMOGLOBINA", "g/dL"),
        (r"Hematócrito[:\s]*(\d+,?\d*)", "HEMATOCRITO", "%"),
        (r"Leucócitos[:\s]*(\d+\.?\d*,?\d*)", "LEUCOCITOS", "/mm³"),
        (r"Plaquetas[:\s]*(\d+\.?\d*,?\d*)", "PLAQUETAS", "/mm³"),
        
        # Perfil lipídico
        (r"Colesterol Total[:\s]*(\d+,?\d*)", "COLESTEROL_TOTAL", "mg/dL"),
        (r"HDL[:\s]*(\d+,?\d*)", "HDL", "mg/dL"),
        (r"LDL[:\s]*(\d+,?\d*)", "LDL", "mg/dL"),
        (r"Triglicerídeos[:\s]*(\d+,?\d*)", "TRIGLICERIDEOS", "mg/dL"),
        
        # Função renal
        (r"Creatinina[:\s]*(\d+,?\d*)", "CREATININA", "mg/dL"),
        (r"Ureia[:\s]*(\d+,?\d*)", "UREIA", "mg/dL"),
        
        # Glicemia
        (r"Glicose[:\s]*(\d+,?\d*)", "GLICOSE", "mg/dL"),
        
        # Função hepática
        (r"ALT[:\s]*(\d+,?\d*)", "ALT", "U/L"),
        (r"AST[:\s]*(\d+,?\d*)", "AST", "U/L"),
        (r"Fosfatase Alcalina[:\s]*(\d+,?\d*)", "FOSFATASE_ALCALINA", "U/L"),
        (r"Gama GT[:\s]*(\d+,?\d*)", "GAMA_GT", "U/L"),
    ]
    
    # Extrair valores para cada padrão
    for pattern, exam_code, unit in common_exam_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            value_str = match.group(1).replace(".", "").replace(",", ".")
            try:
                value = float(value_str)
                
                # Buscar os valores de referência
                ref_range = extract_reference_range(text, exam_code, lab_type)
                
                exams.append({
                    "code": exam_code,
                    "name": exam_code.replace("_", " ").title(),
                    "value": value,
                    "unit": unit,
                    "reference_range": ref_range
                })
            except ValueError:
                # Ignorar se não for possível converter para float
                continue
    
    return exams

def extract_reference_range(text: str, exam_code: str, lab_type: str) -> Dict[str, Any]:
    """
    Extrai o intervalo de referência para um exame específico.
    
    Args:
        text: Texto completo do PDF
        exam_code: Código do exame
        lab_type: Tipo de laboratório
        
    Returns:
        Dicionário com valores de referência mínimo e máximo
    """
    reference_range = {
        "min": None,
        "max": None,
        "text": ""
    }
    
    # Padrões de busca para intervalos de referência
    # Isto dependerá muito do formato específico de cada laboratório
    
    # Exemplo genérico: Valores de Referência: 10-20 mg/dL
    # Procurar próximo ao nome do exame
    exam_name = exam_code.replace("_", " ").title()
    
    # Procurar por padrões como "Valores de Referência: 10-20"
    ref_patterns = [
        r"(?:Valores de Referência|Valor de Referência|Intervalo de Referência)[\s:]*(\d+,?\d*)[\s\-a]*(\d+,?\d*)",
        r"(?:VR|Ref\.)[\s:]*(\d+,?\d*)[\s\-a]*(\d+,?\d*)",
    ]
    
    context_size = 200  # Caracteres ao redor do exame para procurar referências
    
    # Encontrar a posição do exame no texto
    exam_pos = text.find(exam_name)
    if exam_pos == -1:
        # Tentar com o código
        exam_pos = text.find(exam_code)
    
    if exam_pos >= 0:
        # Extrair contexto ao redor do exame
        start = max(0, exam_pos - context_size)
        end = min(len(text), exam_pos + context_size)
        context = text[start:end]
        
        # Tentar diferentes padrões
        for pattern in ref_patterns:
            ref_match = re.search(pattern, context, re.IGNORECASE)
            if ref_match:
                try:
                    min_val = ref_match.group(1).replace(",", ".")
                    max_val = ref_match.group(2).replace(",", ".")
                    reference_range["min"] = float(min_val)
                    reference_range["max"] = float(max_val)
                    reference_range["text"] = f"{min_val}-{max_val}"
                    break
                except (ValueError, IndexError):
                    continue
    
    return reference_range
