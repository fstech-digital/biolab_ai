"""
Módulo para processamento da planilha de referência de exames
"""

import os
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelReferenceProcessor:
    """
    Processa a planilha de referência de exames para obter valores de referência
    """
    
    def __init__(self, excel_path: str):
        """
        Inicializa o processador com o caminho para a planilha Excel
        
        Args:
            excel_path: Caminho para o arquivo Excel
        """
        self.excel_path = excel_path
        self.reference_data = {}
        
        # Validar existência do arquivo
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {excel_path}")
    
    def load_reference_data(self) -> Dict[str, Any]:
        """
        Carrega os dados de referência da planilha Excel
        
        Returns:
            Dicionário com dados de referência
        """
        try:
            # Carregar a planilha
            df = pd.read_excel(self.excel_path)
            
            # Limpar e padronizar nomes das colunas
            df.columns = [col.strip().lower() for col in df.columns]
            
            # Verificar se temos as colunas necessárias
            required_columns = ['exame', 'nome_alternativo', 'unidade', 'referencia']
            
            # Ajustar nomes das colunas se necessário para variações comuns
            column_mapping = {}
            for col in df.columns:
                if 'exame' in col or 'teste' in col:
                    column_mapping[col] = 'exame'
                elif 'alternativo' in col or 'sinonimo' in col:
                    column_mapping[col] = 'nome_alternativo'
                elif 'unidade' in col or 'medida' in col:
                    column_mapping[col] = 'unidade'
                elif 'referencia' in col or 'valor' in col:
                    column_mapping[col] = 'referencia'
                elif 'sexo' in col or 'genero' in col:
                    column_mapping[col] = 'sexo'
                elif 'idade' in col or 'faixa' in col:
                    column_mapping[col] = 'idade'
            
            # Renomear colunas
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # Verificar se agora temos as colunas necessárias
            available_columns = set(df.columns)
            
            # Criar dicionário para consulta
            exam_reference = {}
            
            # Se temos colunas específicas por sexo/idade, estruturar adequadamente
            if 'sexo' in available_columns and 'idade' in available_columns:
                # Agrupamento por exame, sexo e idade
                for _, row in df.iterrows():
                    exam_name = str(row.get('exame', '')).strip().lower()
                    if not exam_name or pd.isna(exam_name):
                        continue
                    
                    # Nomes alternativos (podem ser múltiplos separados por vírgula)
                    alt_names = str(row.get('nome_alternativo', '')).strip().lower()
                    alt_names_list = [name.strip() for name in alt_names.split(',')] if alt_names and not pd.isna(alt_names) else []
                    
                    # Criar lista completa de nomes (principal + alternativos)
                    all_names = [exam_name] + alt_names_list
                    
                    # Obter valores específicos por sexo/idade
                    sex = str(row.get('sexo', '')).strip().upper()
                    age_range = str(row.get('idade', '')).strip()
                    unit = str(row.get('unidade', '')).strip()
                    reference = str(row.get('referencia', '')).strip()
                    
                    # Adicionar a todos os nomes do exame
                    for name in all_names:
                        if name not in exam_reference:
                            exam_reference[name] = {
                                'name': exam_name,  # Nome oficial
                                'alternative_names': alt_names_list,
                                'units': [],
                                'references': []
                            }
                        
                        # Adicionar unidade se não existir
                        if unit and unit not in exam_reference[name]['units']:
                            exam_reference[name]['units'].append(unit)
                        
                        # Adicionar referência por sexo/idade
                        if reference:
                            ref_entry = {
                                'value': reference,
                                'unit': unit
                            }
                            
                            # Adicionar sexo e idade se fornecidos
                            if sex and not pd.isna(sex):
                                ref_entry['sex'] = sex
                            
                            if age_range and not pd.isna(age_range):
                                ref_entry['age_range'] = age_range
                            
                            exam_reference[name]['references'].append(ref_entry)
            else:
                # Estrutura mais simples sem sexo/idade
                for _, row in df.iterrows():
                    exam_name = str(row.get('exame', '')).strip().lower()
                    if not exam_name or pd.isna(exam_name):
                        continue
                    
                    # Nomes alternativos
                    alt_names = str(row.get('nome_alternativo', '')).strip().lower()
                    alt_names_list = [name.strip() for name in alt_names.split(',')] if alt_names and not pd.isna(alt_names) else []
                    
                    # Criar lista completa de nomes
                    all_names = [exam_name] + alt_names_list
                    
                    # Obter valores gerais
                    unit = str(row.get('unidade', '')).strip()
                    reference = str(row.get('referencia', '')).strip()
                    
                    # Adicionar a todos os nomes do exame
                    for name in all_names:
                        if name not in exam_reference:
                            exam_reference[name] = {
                                'name': exam_name,  # Nome oficial
                                'alternative_names': alt_names_list,
                                'units': [unit] if unit and not pd.isna(unit) else [],
                                'references': [{
                                    'value': reference,
                                    'unit': unit
                                }] if reference and not pd.isna(reference) else []
                            }
                        elif unit and not pd.isna(unit) and unit not in exam_reference[name]['units']:
                            exam_reference[name]['units'].append(unit)
                            
                            if reference and not pd.isna(reference):
                                exam_reference[name]['references'].append({
                                    'value': reference,
                                    'unit': unit
                                })
            
            self.reference_data = exam_reference
            logger.info(f"Carregados dados de referência para {len(exam_reference)} exames")
            
            return self.reference_data
            
        except Exception as e:
            logger.error(f"Erro ao processar planilha de referência: {e}")
            return {}
    
    def get_reference_for_exam(self, exam_name: str, 
                              sex: Optional[str] = None, 
                              age: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtém valores de referência para um exame específico
        
        Args:
            exam_name: Nome do exame
            sex: Sexo do paciente (M/F)
            age: Idade do paciente
            
        Returns:
            Dicionário com valores de referência
        """
        if not self.reference_data:
            self.load_reference_data()
        
        # Normalizar nome do exame
        exam_name_clean = exam_name.strip().lower()
        
        # Verificar correspondência direta
        if exam_name_clean in self.reference_data:
            exam_info = self.reference_data[exam_name_clean]
        else:
            # Verificar por correspondência parcial (contém)
            potential_matches = []
            for ref_name in self.reference_data:
                if exam_name_clean in ref_name or ref_name in exam_name_clean:
                    potential_matches.append(ref_name)
            
            if not potential_matches:
                # Tentar matching mais flexível com nomes alternativos
                for ref_name, exam_info in self.reference_data.items():
                    for alt_name in exam_info['alternative_names']:
                        if exam_name_clean in alt_name or alt_name in exam_name_clean:
                            potential_matches.append(ref_name)
                            break
            
            if not potential_matches:
                return {"error": f"Exame não encontrado: {exam_name}"}
            
            # Usar a correspondência mais próxima
            # (poderia ser aprimorado com algoritmos de matching mais sofisticados)
            exam_info = self.reference_data[potential_matches[0]]
        
        # Extrair referências
        references = exam_info['references']
        
        # Filtrar por sexo e idade, se fornecidos
        if sex or age:
            filtered_refs = []
            for ref in references:
                sex_match = True
                age_match = True
                
                # Verificar compatibilidade de sexo
                if sex and 'sex' in ref and ref['sex'] != sex:
                    sex_match = False
                
                # Verificar compatibilidade de idade
                if age and 'age_range' in ref:
                    age_range = ref['age_range']
                    # Formatos comuns: "0-5", ">50", "<18", "Adulto"
                    if '-' in age_range:
                        try:
                            min_age, max_age = map(int, age_range.split('-'))
                            if age < min_age or age > max_age:
                                age_match = False
                        except:
                            pass
                    elif age_range.startswith('>'):
                        try:
                            min_age = int(age_range[1:])
                            if age <= min_age:
                                age_match = False
                        except:
                            pass
                    elif age_range.startswith('<'):
                        try:
                            max_age = int(age_range[1:])
                            if age >= max_age:
                                age_match = False
                        except:
                            pass
                
                if sex_match and age_match:
                    filtered_refs.append(ref)
            
            # Se encontrou referências filtradas, usar; caso contrário, usar todas
            if filtered_refs:
                references = filtered_refs
        
        result = {
            "name": exam_info['name'],
            "alternative_names": exam_info['alternative_names'],
            "units": exam_info['units'],
            "references": references
        }
        
        return result