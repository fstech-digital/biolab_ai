"""
Módulo de normalização para RAG
Responsável por padronizar termos médicos, unidades e valores
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExamNormalizer:
    """
    Classe para normalização de dados de exames médicos
    Padroniza termos, unidades e valores para melhorar a busca semântica
    """
    
    def __init__(self, normalization_rules: Optional[Dict[str, Any]] = None):
        """
        Inicializa o normalizador com regras específicas
        
        Args:
            normalization_rules: Dicionário com regras de normalização
        """
        # Carregar regras de normalização padrão ou usar as fornecidas
        self.rules = normalization_rules or self._get_default_rules()
    
    def normalize_exam_data(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza os dados do exame
        
        Args:
            exam_data: Dados do exame extraídos do PDF
            
        Returns:
            Dados do exame normalizados
        """
        # Fazer uma cópia para não modificar o original
        normalized_data = exam_data.copy()
        
        # Normalizar dados do paciente
        if 'patient' in normalized_data:
            normalized_data['patient'] = self._normalize_patient_data(normalized_data['patient'])
        
        # Normalizar dados dos exames
        if 'exams' in normalized_data:
            normalized_exams = []
            for exam in normalized_data['exams']:
                normalized_exams.append(self._normalize_exam(exam))
            normalized_data['exams'] = normalized_exams
        
        return normalized_data
    
    def _normalize_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza os dados do paciente
        
        Args:
            patient_data: Dicionário com dados do paciente
            
        Returns:
            Dados do paciente normalizados
        """
        normalized = patient_data.copy()
        
        # Normalizar nome para caixa alta
        if 'name' in normalized and normalized['name']:
            normalized['name'] = self._normalize_name(normalized['name'])
        
        # Normalizar gênero para 'M' ou 'F'
        if 'gender' in normalized and normalized['gender']:
            normalized['gender'] = self._normalize_gender(normalized['gender'])
        
        # Normalizar data para formato padrão (YYYY-MM-DD)
        if 'exam_date' in normalized and normalized['exam_date']:
            normalized['exam_date'] = self._normalize_date(normalized['exam_date'])
        
        if 'date_of_birth' in normalized and normalized['date_of_birth']:
            normalized['date_of_birth'] = self._normalize_date(normalized['date_of_birth'])
        
        return normalized
    
    def _normalize_exam(self, exam: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza os dados de um exame
        
        Args:
            exam: Dicionário com dados do exame
            
        Returns:
            Dados do exame normalizados
        """
        normalized = exam.copy()
        
        # Normalizar nome do exame
        if 'name' in normalized and normalized['name']:
            normalized['name'] = self._normalize_exam_name(normalized['name'])
        
        # Normalizar resultado para formato numérico quando possível
        if 'result' in normalized and normalized['result']:
            normalized['result'] = self._normalize_result_value(normalized['result'])
        
        # Normalizar unidade
        if 'unit' in normalized and normalized['unit']:
            normalized['unit'] = self._normalize_unit(normalized['unit'])
        
        # Adicionar flag de normalização
        normalized['normalized'] = True
        
        return normalized
    
    def _normalize_name(self, name: str) -> str:
        """
        Normaliza o nome do paciente
        
        Args:
            name: Nome do paciente
            
        Returns:
            Nome normalizado
        """
        # Remover múltiplos espaços
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Converter para Title Case (primeira letra de cada palavra em maiúscula)
        name = name.title()
        
        return name
    
    def _normalize_gender(self, gender: str) -> str:
        """
        Normaliza o gênero para 'M' ou 'F'
        
        Args:
            gender: Gênero do paciente
            
        Returns:
            Gênero normalizado ('M' ou 'F')
        """
        gender = gender.upper().strip()
        
        # Mapeamento para normalizar variações
        gender_map = {
            'M': 'M',
            'MASCULINO': 'M',
            'MALE': 'M',
            'F': 'F',
            'FEMININO': 'F',
            'FEMALE': 'F'
        }
        
        return gender_map.get(gender, gender)
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normaliza uma data para formato ISO (YYYY-MM-DD)
        
        Args:
            date_str: String da data
            
        Returns:
            Data normalizada
        """
        # Remover espaços extras
        date_str = date_str.strip()
        
        # Tentar converter formato DD/MM/YYYY para YYYY-MM-DD
        date_match = re.match(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', date_str)
        if date_match:
            day, month, year = date_match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Tentar converter formato MM/DD/YYYY para YYYY-MM-DD
        date_match = re.match(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', date_str)
        if date_match:
            month, day, year = date_match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Se já estiver no formato YYYY-MM-DD, deixar como está
        date_match = re.match(r'(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})', date_str)
        if date_match:
            return date_str
        
        # Se não conseguir converter, retornar como está
        return date_str
    
    def _normalize_exam_name(self, exam_name: str) -> str:
        """
        Normaliza o nome do exame
        
        Args:
            exam_name: Nome do exame
            
        Returns:
            Nome normalizado
        """
        # Remover múltiplos espaços e símbolos especiais
        name = re.sub(r'[^\w\s]', '', exam_name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Verificar mapeamento de nomes
        name_lower = name.lower()
        for pattern, normalized in self.rules['exam_names'].items():
            if pattern.lower() in name_lower or name_lower in pattern.lower():
                return normalized
        
        # Se não encontrar no mapeamento, retornar o nome limpo
        return name.title()
    
    def _normalize_result_value(self, result: str) -> Union[str, float]:
        """
        Normaliza o valor do resultado para número quando possível
        
        Args:
            result: Valor do resultado
            
        Returns:
            Valor normalizado (número ou string)
        """
        # Remover espaços e símbolos não numéricos
        result = result.strip()
        
        # Se for um valor numérico, converter para float
        # Primeiro substituir vírgula por ponto para compatibilidade
        result_norm = result.replace(',', '.')
        
        # Verificar se é um número
        try:
            return float(result_norm)
        except ValueError:
            # Se não for número, retornar como string
            return result
    
    def _normalize_unit(self, unit: str) -> str:
        """
        Normaliza a unidade de medida
        
        Args:
            unit: Unidade de medida
            
        Returns:
            Unidade normalizada
        """
        # Remover espaços
        unit = unit.strip()
        
        # Verificar mapeamento de unidades
        unit_lower = unit.lower()
        for pattern, normalized in self.rules['units'].items():
            if pattern.lower() == unit_lower:
                return normalized
        
        return unit
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """
        Retorna regras de normalização padrão
        
        Returns:
            Dicionário com regras padrão
        """
        return {
            "exam_names": {
                "hemoglobina": "Hemoglobina",
                "hb": "Hemoglobina",
                "hemograma": "Hemograma",
                "glicemia": "Glicose",
                "glicose": "Glicose",
                "colesterol total": "Colesterol Total",
                "hdl": "HDL-Colesterol",
                "ldl": "LDL-Colesterol",
                "triglicerideos": "Triglicerídeos",
                "triglicérides": "Triglicerídeos",
                "tsh": "TSH",
                "t4 livre": "T4 Livre",
                "creatinina": "Creatinina",
                "ureia": "Ureia",
                "acido urico": "Ácido Úrico",
                "ácido úrico": "Ácido Úrico",
                "tgo": "TGO (AST)",
                "ast": "TGO (AST)",
                "tgp": "TGP (ALT)",
                "alt": "TGP (ALT)",
                "gama gt": "Gama-GT",
                "ggt": "Gama-GT",
                "fosfatase alcalina": "Fosfatase Alcalina",
                "vdrl": "VDRL",
                "proteina c reativa": "Proteína C Reativa",
                "pcr": "Proteína C Reativa",
                "vhs": "VHS",
                "ferritina": "Ferritina",
                "ferro": "Ferro Sérico",
                "transferrina": "Transferrina",
                "vitamina b12": "Vitamina B12",
                "vitamina d": "Vitamina D",
                "25-hidroxi vitamina d": "Vitamina D",
                "sodio": "Sódio",
                "sódio": "Sódio",
                "potassio": "Potássio",
                "potássio": "Potássio",
                "calcio": "Cálcio",
                "cálcio": "Cálcio",
                "magnesio": "Magnésio",
                "magnésio": "Magnésio"
            },
            "units": {
                "g/dl": "g/dL",
                "g/dL": "g/dL",
                "mg/dl": "mg/dL",
                "mg/dL": "mg/dL",
                "ng/ml": "ng/mL",
                "ng/mL": "ng/mL",
                "pg/ml": "pg/mL",
                "pg/mL": "pg/mL",
                "u/l": "U/L",
                "u/L": "U/L",
                "U/L": "U/L",
                "ui/l": "UI/L",
                "ui/L": "UI/L",
                "UI/L": "UI/L",
                "uiu/ml": "uIU/mL",
                "uiu/mL": "uIU/mL",
                "uIU/mL": "uIU/mL",
                "mmol/l": "mmol/L",
                "mmol/L": "mmol/L",
                "umol/l": "μmol/L",
                "umol/L": "μmol/L",
                "μmol/L": "μmol/L",
                "meq/l": "mEq/L",
                "meq/L": "mEq/L",
                "mEq/L": "mEq/L",
                "%": "%",
                "mm/h": "mm/h",
                "cel/mm3": "cel/mm³",
                "cel/mm³": "cel/mm³",
                "fL": "fL",
                "pg": "pg"
            }
        }