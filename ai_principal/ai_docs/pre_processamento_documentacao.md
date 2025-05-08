# Documentação do Módulo de Pré-Processamento - 07/05/2025

## Visão Geral

O módulo de pré-processamento foi desenvolvido para melhorar a qualidade e consistência dos dados extraídos de PDFs e planilhas de exames laboratoriais antes do armazenamento no banco de dados vetorial (Supabase). Este módulo inclui normalização de dados, detecção automática de laboratórios, validação de resultados e enriquecimento com metadados.

## Componentes Principais

### 1. PDFPreProcessor

Classe responsável pelo pré-processamento de PDFs de exames laboratoriais.

#### Funcionalidades:
- **Detecção automática de laboratório**: Identifica o laboratório com base em padrões de texto
- **Extração específica por laboratório**: Aplica extratores otimizados para cada formato
- **Normalização de unidades e valores**: Uniformiza formatos numéricos e unidades
- **Validação de dados**: Verifica consistência e valores biologicamente plausíveis
- **Enriquecimento com metadados**: Adiciona categorias, flags e informações contextuais

#### Laboratórios Suportados:
- Sabin
- Sérgio Franco
- LABI
- Ramos Medicina
- SL Diagnósticos
- Extrator genérico para formatos não reconhecidos

### 2. ExcelPreProcessor

Classe responsável pelo pré-processamento de planilhas de exames.

#### Funcionalidades:
- **Normalização de cabeçalhos**: Mapeia variações para nomes padronizados
- **Padronização de valores**: Converte formatos regionais para padrão
- **Extração de valores de referência**: Identifica valores min/max em textos
- **Validação de dados**: Verifica integridade e consistência
- **Conversão para formato unificado**: Estrutura dados compatíveis com o modelo vetorial

### 3. Módulo de Integração

Conecta o pré-processamento ao fluxo existente de armazenamento na Supabase.

#### Funcionalidades:
- **Identificação automática do tipo de arquivo**: PDF ou Excel
- **Aplicação do processador adequado**: Baseado na extensão do arquivo
- **Preparação para armazenamento vetorial**: Estrutura dados no formato esperado
- **Geração de conteúdo textual**: Para pesquisa e embeddings

## Fluxo de Pré-Processamento

1. **Detecção inicial**: Identificação do tipo de arquivo e laboratório
2. **Extração bruta**: Aplicação do extrator específico para o formato detectado 
3. **Normalização**: Padronização de unidades, valores e nomes de exames
4. **Validação**: Verificação de integridade e coerência dos dados extraídos
5. **Enriquecimento**: Adição de metadados, categorias e flags para valores alterados
6. **Integração**: Preparação para armazenamento vetorial

## Uso do Módulo

### Pré-processamento de PDF

```python
from preprocessor import PDFPreProcessor

# Criar instância do processador
processor = PDFPreProcessor()

# Processar um arquivo PDF
result = processor.process("/caminho/para/exame.pdf")

# Verificar resultado
if "error" in result:
    print(f"Erro: {result['error']}")
else:
    # Acessar dados processados
    processed_data = result["data"]
    
    # Informações do paciente
    patient = processed_data["patient"]
    print(f"Paciente: {patient.get('name')}")
    
    # Exames extraídos
    for exam in processed_data["exams"]:
        print(f"{exam['name']}: {exam['value']} {exam['unit']}")
    
    # Exames por categoria
    for category, exams in processed_data["exams_by_category"].items():
        print(f"Categoria {category}: {len(exams)} exames")
```

### Pré-processamento de Planilha

```python
from preprocessor import ExcelPreProcessor

# Criar instância do processador
processor = ExcelPreProcessor()

# Processar uma planilha
result = processor.process("/caminho/para/planilha.xlsx")

# Verificar resultado
if "error" in result:
    print(f"Erro: {result['error']}")
else:
    # Acessar dados processados
    processed_data = result["data"]
    
    # Exames extraídos
    for exam in processed_data["exams"]:
        print(f"{exam['name']}: {exam['value']} {exam['unit']}")
```

### Integração com Supabase

```python
import asyncio
from integration import preprocess_and_extract, integrate_with_supabase
from services.vector_db.supabase_client import SupabaseClient

async def process_and_store(file_path):
    # Configurar cliente Supabase
    supabase_client = SupabaseClient()
    
    # Pré-processar o arquivo
    processed_data = await preprocess_and_extract(file_path)
    
    # Integrar com Supabase
    result = await integrate_with_supabase(processed_data, supabase_client)
    
    return result

# Executar o processamento
file_path = "/caminho/para/exame.pdf"
result = asyncio.run(process_and_store(file_path))
```

## Script de Teste

O módulo inclui um script de teste (`test_preprocessor.py`) que pode ser usado para verificar o funcionamento do pré-processamento:

```bash
# Testar um arquivo específico
python test_preprocessor.py /caminho/para/exame.pdf

# Testar todos os arquivos em um diretório
python test_preprocessor.py /diretorio/com/exames/
```

## Mapeamentos e Configurações

### Mapeamento de Unidades

O sistema normaliza diversas unidades de medida para formato padronizado:

| Entrada | Saída Normalizada |
|---------|-------------------|
| g/dl    | g/dL              |
| 10^6/μl | 10^6/μL           |
| /mm^3   | /μL               |
| mg/dl   | mg/dL             |
| U/l     | U/L               |

### Mapeamento de Nomes de Exames

O sistema reconhece várias formas de nomear os mesmos exames:

| Entrada                | Código Normalizado |
|------------------------|-------------------|
| hemoglobina, hb        | HEMOGLOBINA       |
| eritrócitos, hemácias  | ERITROCITOS       |
| leucócitos             | LEUCOCITOS        |
| colesterol total       | COLESTEROL_TOTAL  |
| hdl, hdl-colesterol    | HDL               |

### Categorias de Exames

Os exames são classificados nas seguintes categorias:

- HEMOGRAMA
- LIPIDOGRAMA
- FUNCAO_RENAL
- GLICEMIA
- FUNCAO_HEPATICA
- ELETROLITOS
- HORMONIOS

## Considerações para Manutenção

Para adicionar suporte a novos laboratórios:

1. Identificar padrões de texto característicos do laboratório
2. Adicionar ao dicionário `lab_patterns` em `_detect_lab_type()`
3. Implementar função específica `_extract_NOME_LABORATORIO_data()`
4. Adicionar condição em `_extract_raw_data()`

Para adicionar suporte a novos exames:

1. Adicionar ao dicionário `EXAM_NAME_MAPPING`
2. Se necessário, adicionar ao dicionário `UNIT_MAPPING`
3. Categorizar o exame em `EXAM_CATEGORIES`

## Limitações Conhecidas

1. **Extração de Tabelas Complexas**: Alguns PDFs com layouts complexos ainda podem apresentar desafios de extração
2. **Variações Regionais**: Formatos de data e número podem variar conforme a região
3. **Laboratórios Não Reconhecidos**: O sistema cai no extrator genérico quando não reconhece o laboratório
4. **OCR Parcial**: O atual sistema não aplica OCR em todo o documento, apenas extrai texto reconhecido