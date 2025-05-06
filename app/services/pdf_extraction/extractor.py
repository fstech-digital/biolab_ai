import pdfplumber
import fitz  # PyMuPDF
import re
from typing import Dict, List, Any
import datetime

# Tipos de laboratórios suportados
SUPPORTED_LABS = [
    "LABORATORIO A",
    "LABORATORIO B",
    "LABORATORIO C",
    "SERGIO FRANCO" # Adicionado laboratório Sérgio Franco
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
    if "SérgioFranco" in text.replace(" ", "") or "Sergio Franco" in text:
        return "SERGIO FRANCO"
        
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
    
    # Tratamento especial para o laboratório Sérgio Franco que utiliza formato tabular
    if lab_type == "SERGIO FRANCO":
        return await extract_sergio_franco_exams(file_path)
    
    # Extrair texto completo do PDF para outros laboratórios
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    # Padrões comuns de exames - formato (padrão regex, código interno, unidade)
    common_exam_patterns = [
        # Hemograma
        (r"Hemoglobina[:\s]*(\d+,?\d*)", "HEMOGLOBINA", "g/dL"),
        (r"Eritrócitos[:\s]*(\d+[,.]?\d*)", "ERITROCITOS", "10¶/µL"),
        (r"Hematócrito[:\s]*(\d+,?\d*)", "HEMATOCRITO", "%"),
        (r"Leucócitos[:\s]*(\d+\.?\d*,?\d*)", "LEUCOCITOS", "/mm³"),
        (r"Plaquetas[:\s]*(\d+\.?\d*,?\d*)", "PLAQUETAS", "/mm³"),
        (r"VCM[:\s]*(\d+[,.]?\d*)", "VCM", "fL"),
        (r"HCM[:\s]*(\d+[,.]?\d*)", "HCM", "pg"),
        (r"CHCM[:\s]*(\d+[,.]?\d*)", "CHCM", "g/dL"),
        (r"RDW[:\s]*(\d+[,.]?\d*)", "RDW", "%"),
        
        # Perfil lipídico
        (r"Colesterol Total[:\s]*(\d+,?\d*)", "COLESTEROL_TOTAL", "mg/dL"),
        (r"HDL[:\s]*(\d+,?\d*)", "HDL", "mg/dL"),
        (r"LDL[:\s]*(\d+,?\d*)", "LDL", "mg/dL"),
        (r"Triglicerideos[:\s]*(\d+,?\d*)", "TRIGLICERIDEOS", "mg/dL"),
        
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

async def extract_sergio_franco_exams(file_path: str) -> List[Dict[str, Any]]:
    """
    Extrai exames específicos do laboratório Sérgio Franco que utiliza formato tabular.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Lista de dicionários, cada um contendo dados de um exame específico
    """
    exams = []
    
    try:
        # Abrir o PDF com pdfplumber para extração de texto estruturado
        with pdfplumber.open(file_path) as pdf:
            # Identificar seções de exames relevantes
            sections = [
                "Hemograma", "Série Vermelha", "Bioquímica", "Lipidograma", 
                "Hormônios", "Eletrólitos", "Função Renal", "Função Hepática"
            ]
            
            # Procurar exames em cada página
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                
                # Verificar se estamos em uma página com exames
                if any(section in text for section in sections):
                    # Extrair linhas para processamento
                    lines = text.split('\n')
                    
                    # Mapas para unidades comuns de exames
                    unit_map = {
                        # Hemograma
                        "Eritrócitos": "10^6/μL",
                        "Hemoglobina": "g/dL", 
                        "Hematócrito": "%",
                        "VCM": "fL",
                        "HCM": "pg",
                        "CHCM": "g/dL",
                        "RDW": "%",
                        "Leucócitos": "/μL",
                        "Neutrófilos": "%",
                        "Linfócitos": "%",
                        "Monócitos": "%",
                        "Eosinófilos": "%",
                        "Basófilos": "%",
                        "Plaquetas": "/μL",
                        # Bioquímica
                        "Glicose": "mg/dL",
                        "Ureia": "mg/dL",
                        "Creatinina": "mg/dL",
                        "Ácido Úrico": "mg/dL",
                        "Colesterol Total": "mg/dL",
                        "HDL": "mg/dL",
                        "LDL": "mg/dL",
                        "Triglicerídeos": "mg/dL",
                        "TGO": "U/L",
                        "TGP": "U/L",
                        "Gama GT": "U/L",
                        "Fosfatase Alcalina": "U/L",
                        "Bilirrubina Total": "mg/dL",
                        "Bilirrubina Direta": "mg/dL",
                        "Bilirrubina Indireta": "mg/dL",
                        "Sódio": "mmol/L",
                        "Potássio": "mmol/L",
                        "Cálcio": "mg/dL",
                        "TSH": "μUI/mL",
                        "T4 Livre": "ng/dL"
                    }
                    
                    # Identificar seção atual
                    current_section = None
                    processing_exams = False
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Verificar se estamos entrando em uma nova seção
                        for section in sections:
                            if section in line and len(line) < 50:  # Evitar falsos positivos em linhas longas
                                current_section = section
                                processing_exams = True
                                break
                                
                        # Sair da seção quando encontrar delimitadores ou palavras-chave
                        if processing_exams and ("----" in line or "====" in line or "MÉTODO" in line.upper() or "OBSERVAÇÃO" in line.upper()):
                            processing_exams = False
                            
                        if not processing_exams:
                            continue
                            
                        # Ignorar linhas de cabeçalho
                        if "RESULTADO" in line.upper() and "VALOR DE REFERÊNCIA" in line.upper():
                            continue
                        
                        # Padrões para capturar diferentes formatos de linha de exame
                        patterns = [
                            # Padrão 1: "Nome do exame    12,3 unid    10,0 a 20,0 unid"
                            r"([\w\s\-\.]+?)\s+([\d,\.]+)\s+([\w\/μ\^\-\(\)\%]+)[^\d]*([\d,\.]+\s*a\s*[\d,\.]+)[^\d]*([\w\/μ\^\-\(\)\%]+)?",
                            # Padrão 2: "Nome do exame    12,3    unid    10,0 - 20,0    unid"
                            r"([\w\s\-\.]+?)\s+([\d,\.]+)\s+([\w\/μ\^\-\(\)\%]+)\s+([\d,\.]+\s*\-\s*[\d,\.]+)\s+([\w\/μ\^\-\(\)\%]+)?"
                        ]
                        
                        match = None
                        for pattern in patterns:
                            match = re.search(pattern, line)
                            if match:
                                break
                                
                        if match:
                            # Extrair informações do exame
                            exam_name = match.group(1).strip()
                            value_str = match.group(2).strip().replace(',', '.')
                            unit = match.group(3).strip() if match.group(3) else ""
                            ref_range_text = match.group(4).strip() if match.group(4) else ""
                            
                            # Normalizar nome do exame - remover caracteres especiais
                            exam_name = re.sub(r'[^\w\s]', '', exam_name).strip()
                            
                            try:
                                value = float(value_str)
                                
                                # Extrair valores de referência
                                ref_range = {"min": None, "max": None, "text": ref_range_text}
                                
                                # Detectar padrão de referência (seja com 'a' ou com '-')
                                ref_match = re.search(r"([\d,\.]+)\s*(?:a|\-)\s*([\d,\.]+)", ref_range_text)
                                if ref_match:
                                    ref_min = float(ref_match.group(1).replace(',', '.'))
                                    ref_max = float(ref_match.group(2).replace(',', '.'))
                                    ref_range = {
                                        "min": ref_min,
                                        "max": ref_max,
                                        "text": ref_range_text
                                    }
                                
                                # Definir código do exame (versão padronizada do nome)
                                exam_code = exam_name.upper().replace(' ', '_')
                                
                                # Criar e adicionar o exame à lista
                                exams.append({
                                    "code": exam_code,
                                    "name": exam_name,
                                    "value": value,
                                    "unit": unit,
                                    "reference_range": ref_range,
                                    "section": current_section
                                })
                            except ValueError:
                                print(f"Erro ao converter valor para {exam_name}: {value_str}")
        
        # Remover possíveis duplicatas baseadas no código do exame
        unique_exams = {}
        for exam in exams:
            if exam["code"] not in unique_exams or abs(exam["value"]) > 0:
                unique_exams[exam["code"]] = exam
                
        return list(unique_exams.values())
                        
    except Exception as e:
        print(f"Erro ao extrair exames do formato Sérgio Franco: {str(e)}")
        return []

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
