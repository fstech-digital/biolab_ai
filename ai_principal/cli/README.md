# Interface CLI - BioLab.Ai

## Descrição

Interface de linha de comando (CLI) para o sistema BioLab.Ai. Permite interagir com todas as funcionalidades do sistema através de comandos simples.

## Comandos Disponíveis

### extract

Extrai dados de PDFs de exames médicos.

```bash
python biolab-cli.py extract --pdf /caminho/para/exame.pdf --reference /caminho/para/planilha.xlsx
```

Opções:
- `--pdf`: Caminho para um único arquivo PDF
- `--dir`: Caminho para diretório com PDFs
- `--reference`: Caminho para planilha de referência (opcional)
- `--output`: Diretório para arquivos de saída (opcional)
- `--pattern`: Padrão para filtrar arquivos (para `--dir`, padrão: `*.pdf`)

### process

Pré-processa dados extraídos para RAG.

```bash
python biolab-cli.py process --json /caminho/para/exame_extracted.json --index
```

Opções:
- `--json`: Caminho para um único arquivo JSON
- `--dir`: Caminho para diretório com JSONs
- `--output`: Diretório para arquivos de saída (opcional)
- `--pattern`: Padrão para filtrar arquivos (para `--dir`, padrão: `*_extracted.json`)
- `--chunk-size`: Tamanho máximo de cada chunk em caracteres (padrão: 1000)
- `--chunk-overlap`: Sobreposição entre chunks em caracteres (padrão: 200)
- `--index`: Indexar chunks no Supabase após processamento

### query

Consulta exames no sistema.

```bash
python biolab-cli.py query --patient "João Silva" --output resultados.json
```

Opções:
- `--patient`: Nome do paciente para busca
- `--dates`: Intervalo de datas no formato 'start:end' (YYYY-MM-DD)
- `--exam-type`: Tipo de exame a ser buscado
- `--output`: Arquivo para salvar os resultados em JSON (opcional)

### server

Inicia o servidor MCP.

```bash
python biolab-cli.py server --port 8000
```

Opções:
- `--host`: Host para o servidor (padrão: 0.0.0.0)
- `--port`: Porta para o servidor (padrão: valor da variável PORT no .env ou 8000)

### workflow

Executa o fluxo completo de processamento (extração + RAG + indexação).

```bash
python biolab-cli.py workflow --pdf /caminho/para/exame.pdf --reference /caminho/para/planilha.xlsx
```

Opções:
- `--pdf`: Caminho para o arquivo PDF (obrigatório)
- `--reference`: Caminho para planilha de referência (opcional)
- `--output`: Diretório para arquivos de saída (opcional)
- `--chunk-size`: Tamanho máximo de cada chunk em caracteres (padrão: 1000)
- `--chunk-overlap`: Sobreposição entre chunks em caracteres (padrão: 200)

## Exemplos de Uso

### Fluxo Completo

Para processar um exame do início ao fim:

```bash
python biolab-cli.py workflow --pdf docs/pdfs/Exame_Lazaro.pdf --reference docs/planilhas/planilha_exames_interpretaçao.xlsx
```

### Processamento em Etapas

1. Extrair dados do PDF:
```bash
python biolab-cli.py extract --pdf docs/pdfs/Exame_Lazaro.pdf --reference docs/planilhas/planilha_exames_interpretaçao.xlsx
```

2. Pré-processar para RAG:
```bash
python biolab-cli.py process --json docs/pdfs/Exame_Lazaro_extracted.json --index
```

3. Consultar exames:
```bash
python biolab-cli.py query --patient "Lazaro"
```

### Processar Múltiplos Arquivos

Para processar todos os PDFs em um diretório:

```bash
python biolab-cli.py extract --dir docs/pdfs --reference docs/planilhas/planilha_exames_interpretaçao.xlsx
python biolab-cli.py process --dir docs/pdfs --pattern "*_extracted.json" --index
```

## Requisitos

- Python 3.10+
- Todas as dependências listadas em requirements.txt
- Variáveis de ambiente configuradas no arquivo .env

## Configuração

Configure as seguintes variáveis no arquivo `.env`:

```
# OpenAI
OPENAI_API_KEY=sua_api_key_aqui
EMBEDDING_MODEL=text-embedding-ada-002

# Supabase
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase
VECTOR_COLLECTION=biolab_documents

# Servidor
PORT=8000
```