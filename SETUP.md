# Guia de Configuração do BioLab.Ai

Este guia detalha o processo de configuração e execução do BioLab.Ai.

## Requisitos do Sistema

- Python 3.10 ou superior
- Pip (gerenciador de pacotes Python)
- Acesso à Internet (para APIs externas)
- Conta no Supabase (para banco de dados vetorial)
- Chave de API OpenAI (para embeddings e LLM)

## Instalação

### 1. Preparar ambiente

Recomendamos o uso de um ambiente virtual Python para isolar as dependências:

```bash
# Criar ambiente virtual
python -m venv env

# Ativar ambiente virtual
# No Windows:
env\Scripts\activate
# No Linux/macOS:
source env/bin/activate
```

### 2. Instalar dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```bash
# Copiar o arquivo de exemplo
cp .env.example .env

# Editar o arquivo com suas credenciais
# No Windows:
notepad .env
# No Linux/macOS:
nano .env
```

Preencha as seguintes variáveis no arquivo `.env`:

```
# Chave secreta para JWT
SECRET_KEY=sua_chave_secreta_segura_aqui

# OpenAI API Key
OPENAI_API_KEY=sua_api_key_openai_aqui
OPENAI_MODEL=gpt-4.1
EMBEDDING_MODEL=text-embedding-ada-002

# Supabase
SUPABASE_URL=sua_url_supabase_aqui
SUPABASE_KEY=sua_chave_supabase_aqui
VECTOR_COLLECTION=biolab_documents

# Configurações do servidor
DEBUG=True
PORT=8000
```

### 4. Configurar Supabase

1. Crie uma conta no [Supabase](https://supabase.com/)
2. Crie um novo projeto
3. Configure um banco de dados vetorial:
   - Ative a extensão `pgvector` no SQL Editor:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
   - Crie uma tabela para armazenar os documentos:
     ```sql
     CREATE TABLE biolab_documents (
       id BIGSERIAL PRIMARY KEY,
       content TEXT,
       embedding VECTOR(1536),
       metadata JSONB,
       chunk_type TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
     );
     ```
   - Crie uma função para busca semântica:
     ```sql
     CREATE OR REPLACE FUNCTION match_documents(
       query_embedding VECTOR(1536),
       match_threshold FLOAT,
       match_count INT
     )
     RETURNS TABLE (
       id BIGINT,
       content TEXT,
       metadata JSONB,
       chunk_type TEXT,
       similarity FLOAT
     )
     LANGUAGE plpgsql
     AS $$
     BEGIN
       RETURN QUERY
       SELECT
         id,
         content,
         metadata,
         chunk_type,
         1 - (embedding <=> query_embedding) as similarity
       FROM
         biolab_documents
       WHERE
         1 - (embedding <=> query_embedding) > match_threshold
       ORDER BY
         similarity DESC
       LIMIT match_count;
     END;
     $$;
     ```

4. Copie a URL e a chave de API do Supabase para o arquivo `.env`

## Verificação da Instalação

Para verificar se tudo está instalado corretamente, execute:

```bash
python biolab-cli.py --version
```

Você deve ver a versão do BioLab.Ai sendo exibida.

## Testes Iniciais

### 1. Testar extração de PDF

```bash
python biolab-cli.py extract --pdf docs/pdfs/Exame_Lazaro.pdf --output ./output
```

### 2. Testar o servidor MCP

```bash
python biolab-cli.py server --port 8000
```

Depois de iniciar o servidor, você pode testar os endpoints acessando http://localhost:8000/docs no navegador.

## Solução de Problemas

### Dependências não encontradas

Se você encontrar erros relacionados a módulos não encontrados, verifique se está usando o ambiente virtual e se todas as dependências foram instaladas corretamente:

```bash
pip install -r requirements.txt --force-reinstall
```

### Erros de conexão com Supabase

Verifique se as credenciais do Supabase estão corretas no arquivo `.env`. Também certifique-se de que as extensões e tabelas foram criadas conforme as instruções.

### Erros com a API OpenAI

Verifique se sua chave de API da OpenAI é válida e tem créditos suficientes. O sistema utilizará essa chave para gerar embeddings e consultar o LLM.

## Uso Avançado

Para configurações avançadas e otimizações, consulte:

- [Configurações do MCP Server](ai_principal/mcp_server/README.md)
- [Otimização de Extração de PDFs](ai_principal/pdf_extraction/README.md)
- [Ajustes de Pré-processamento RAG](ai_principal/rag_preprocessing/README.md)

## Atualização

Para atualizar o BioLab.Ai para uma nova versão:

1. Puxe as alterações mais recentes do repositório:
   ```bash
   git pull origin main
   ```

2. Instale quaisquer novas dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Verifique se há alterações no esquema do banco de dados que precisam ser aplicadas.