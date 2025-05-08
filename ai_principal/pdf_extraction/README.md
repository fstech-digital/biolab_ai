# Módulo de Extração de PDFs - BioLab.Ai

## Descrição

Este módulo é responsável pela extração de dados de exames médicos em formato PDF. Ele utiliza múltiplas bibliotecas (PyMuPDF e PDFPlumber) para extrair texto e tabelas dos PDFs, identificando dados do paciente e resultados de exames.

## Características

- Extração de metadados do PDF
- Identificação de dados do paciente (nome, idade, gênero)
- Extração de resultados de exames e valores de referência
- Suporte a múltiplos formatos de laboratórios
- Integração com planilha de referência para enriquecimento de dados

## Componentes

### PDFExtractor

Classe base com funcionalidades genéricas para extração de PDFs:
- Extração de texto usando PyMuPDF (rápido) e PDFPlumber (melhor para tabelas)
- Identificação de padrões comuns para dados de pacientes
- Extração básica de resultados de exames

### Extractores Especializados

Implementações específicas para diferentes formatos de laboratórios:
- `GenericLabExtractor`: Para laboratórios não identificados
- `RamosMedicinaExtractor`: Especializado para PDFs da Ramos Medicina
- `ExtractorFactory`: Fábrica para selecionar o extrator mais adequado

### ExcelReferenceProcessor

Processador para planilha de referência:
- Carrega valores de referência para exames
- Permite busca por nome de exame
- Filtra por sexo e idade quando disponíveis

## Uso

### Via Linha de Comando

Processar um único PDF:
```bash
python -m ai_principal.pdf_extraction.main --pdf /caminho/para/exame.pdf --reference /caminho/para/planilha_referencia.xlsx
```

Processar um diretório de PDFs:
```bash
python -m ai_principal.pdf_extraction.main --dir /caminho/para/pdfs --reference /caminho/para/planilha_referencia.xlsx --output /caminho/para/saida
```

### Via API Python

```python
from ai_principal.pdf_extraction.main import process_pdf_file

# Processar um PDF
resultado = process_pdf_file(
    "/caminho/para/exame.pdf",
    reference_path="/caminho/para/planilha_referencia.xlsx"
)

# Acessar dados extraídos
paciente = resultado["patient"]
exames = resultado["exams"]

# Imprimir nome do paciente e resultados
print(f"Paciente: {paciente['name']}")
for exame in exames:
    print(f"{exame['name']}: {exame['result']} {exame['unit']}")
```

## Fluxo de Processamento

1. Seleção do extrator apropriado para o formato do PDF
2. Extração de texto e tabelas do PDF
3. Identificação de dados do paciente (nome, idade, gênero)
4. Extração de resultados de exames
5. Enriquecimento com valores de referência da planilha (se disponível)
6. Geração de arquivo JSON com todos os dados extraídos

## Saída

O resultado da extração é salvo em arquivos JSON:
- `*_extracted.json`: Dados extraídos diretamente do PDF
- `*_enriched.json`: Dados enriquecidos com valores de referência da planilha