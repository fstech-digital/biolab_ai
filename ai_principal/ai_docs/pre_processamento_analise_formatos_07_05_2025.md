# Análise de Formatos e Requisitos para Pré-Processamento - 07/05/2025

## Visão Geral
Após análise do código e arquivos existentes, identificamos requisitos e desafios específicos para implementar um módulo eficaz de pré-processamento de PDFs e planilhas de exames laboratoriais antes do armazenamento na Supabase.

## Análise do Módulo de Extração Atual

### Funcionalidades Existentes
- Detecção automática de laboratório (função `detect_lab_type`)
- Extração de dados do paciente (função `extract_patient_info`)
- Extração de exames específicos (função `extract_specific_exams`)
- Tratamento especial para o formato do laboratório Sérgio Franco
- Extração de valores de referência

### Limitações Identificadas
1. Suporte limitado a formatos de laboratório (apenas alguns formatos reconhecidos)
2. Padrões de reconhecimento baseados em regex simples
3. Falta de normalização para unidades e valores
4. Ausência de validação de dados extraídos
5. Sem detecção de valores anormais
6. Tratamento simplificado para layouts de tabela complexos

## Desafios por Tipo de Documento

### PDFs de Laboratórios
1. **Laboratório Sabin**
   - Utiliza formato de blocos delimitados por sublinhados
   - Valores apresentados como "RESULTADO: X unidade"
   - Valores de referência no formato "Valor de referência: X a Y unidade"

2. **Laboratório Sérgio Franco**
   - Utiliza formato tabular mais complexo
   - Seções bem definidas (Hemograma, Bioquímica, etc.)
   - Valores e referências na mesma linha com padrões variados
   - Remoção de possíveis duplicatas

3. **Outros Laboratórios**
   - Detectados via padrões de texto (regex)
   - Extração baseada em padrões comuns para exames típicos

### Planilhas de Exames
As planilhas necessitam de um tratamento diferente dos PDFs, com foco em:
- Normalização de cabeçalhos
- Padronização de unidades
- Mapeamento de nomes de exames
- Tratamento de células vazias ou valores inconsistentes

## Requisitos para o Módulo de Pré-Processamento

### 1. Normalização de Dados
- **Unidades**: Padronizar unidades de medida (ex: mg/dL, g/L)
- **Nomes de Exames**: Mapear variações de nomes para códigos padronizados
- **Valores**: Converter formatos regionais (vírgula/ponto) para padrão numérico
- **Datas**: Padronizar formatos de data para ISO 8601

### 2. Enriquecimento de Dados
- **Categorização**: Classificar exames por tipo (hematologia, bioquímica, etc.)
- **Metadados**: Adicionar informações de laboratório, método de análise
- **Relações**: Vincular exames relacionados (ex: perfil lipídico)
- **Flags**: Marcar valores fora da faixa de referência

### 3. Validação de Dados
- **Integridade**: Verificar presença de campos obrigatórios
- **Consistência**: Checar valores dentro de limites biológicos possíveis
- **Estrutura**: Validar formato antes do armazenamento vetorial
- **Qualidade**: Identificar problemas de extração que necessitam revisão

### 4. Sistema de Detecção Aprimorado
- **Reconhecimento de Laboratório**: Algoritmo mais robusto usando múltiplos sinais
- **Extração Contextual**: Usar contexto para melhorar extração de valores
- **Detecção de Tabelas**: Melhorar extração de dados tabulares complexos
- **OCR Seletivo**: Aplicar OCR apenas em áreas com texto em imagens

## Proposta de Novos Componentes

### 1. Módulo de Pré-Processamento de PDFs
```python
class PDFPreProcessor:
    def __init__(self, config=None):
        self.config = config or default_config
        self.lab_detectors = self._load_lab_detectors()
        self.normalizers = self._load_normalizers()
        self.validators = self._load_validators()
    
    def process(self, file_path):
        # Detectar laboratório
        lab_type = self._detect_lab_type(file_path)
        
        # Extrair dados brutos
        raw_data = self._extract_raw_data(file_path, lab_type)
        
        # Normalizar dados
        normalized_data = self._normalize_data(raw_data, lab_type)
        
        # Validar dados
        validated_data, validation_issues = self._validate_data(normalized_data)
        
        # Enriquecer dados
        enriched_data = self._enrich_data(validated_data)
        
        return {
            "processed_data": enriched_data,
            "validation_issues": validation_issues,
            "metadata": {
                "lab_type": lab_type,
                "process_timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
```

### 2. Módulo de Pré-Processamento de Planilhas
```python
class ExcelPreProcessor:
    def __init__(self, config=None):
        self.config = config or default_excel_config
        self.header_map = self._load_header_mapping()
        self.unit_normalizer = self._load_unit_normalizer()
    
    def process(self, file_path):
        # Carregar planilha
        df = pd.read_excel(file_path)
        
        # Normalizar cabeçalhos
        df = self._normalize_headers(df)
        
        # Padronizar valores
        df = self._standardize_values(df)
        
        # Validar dados
        df, validation_issues = self._validate_data(df)
        
        # Converter para formato compatível
        processed_data = self._convert_to_format(df)
        
        return {
            "processed_data": processed_data,
            "validation_issues": validation_issues,
            "metadata": {
                "sheet_name": df.sheet_names,
                "row_count": len(df),
                "process_timestamp": datetime.now().isoformat()
            }
        }
```

## Próximos Passos

1. **Desenvolvimento Incremental**:
   - Começar com laboratórios mais comuns (Sabin, Sérgio Franco)
   - Adicionar suporte a novos formatos progressivamente

2. **Testes com Casos Reais**:
   - Testar o sistema com diversos PDFs para validar precisão
   - Comparar resultados com extração manual para avaliação

3. **Integração com Fluxo Existente**:
   - Inserir a etapa de pré-processamento antes do armazenamento vetorial
   - Garantir compatibilidade com o sistema de consulta existente

4. **Sistema de Feedback**:
   - Implementar mecanismo para marcar e corrigir extrações incorretas
   - Usar feedback para melhorar algoritmos de extração