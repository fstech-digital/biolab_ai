# Módulo de Pré-processamento RAG - BioLab.Ai

## Descrição

Este módulo é responsável pelo pré-processamento de dados de exames médicos para Retrieval Augmented Generation (RAG). Ele prepara os dados extraídos para busca semântica e fornecimento de contexto preciso para LLMs.

## Características

- Normalização de termos médicos, unidades e valores
- Chunking inteligente adaptado para dados de exames
- Geração de embeddings para busca semântica
- Indexação no banco vetorial Supabase

## Componentes

### ExamNormalizer

Normaliza dados para consistência e melhor busca:
- Padronização de nomes de exames
- Normalização de unidades de medida
- Conversão de valores para formatos padronizados
- Normalização de datas e informações do paciente

### ExamChunker

Divide os dados em chunks significativos:
- Chunk de informações do paciente
- Chunks de resultados de exames relacionados
- Chunk de resumo para consultas gerais
- Metadados ricos para cada chunk

### EmbeddingGenerator

Gera vetores para busca semântica:
- Integração com OpenAI API
- Geração de embeddings para chunks de texto
- Suporte para modelos configuráveis
- Utilitários para similaridade de cosseno

### SupabaseIndexer

Armazena chunks e embeddings no banco vetorial:
- Integração com Supabase para armazenamento
- Indexação de chunks e seus metadados
- Suporte para indexação em lote

### RAGProcessor

Orquestra o fluxo completo de pré-processamento:
- Coordena normalização, chunking e embeddings
- Processamento de arquivos individuais ou diretórios
- Configurações ajustáveis para diferentes casos de uso

## Uso

### Via Linha de Comando

Processar um único arquivo JSON:
```bash
python -m ai_principal.rag_preprocessing.main --json /caminho/para/exame_extracted.json
```

Processar um diretório de arquivos JSON:
```bash
python -m ai_principal.rag_preprocessing.main --dir /caminho/para/diretorio --pattern "*_extracted.json" --output /caminho/para/saida
```

### Via API Python

```python
from ai_principal.rag_preprocessing.processor import RAGProcessor
from ai_principal.rag_preprocessing.supabase_indexer import SupabaseIndexer

# Processar dados extraídos
processor = RAGProcessor()
chunks = processor.process_exam_file("/caminho/para/exame_extracted.json")

# Indexar no Supabase
indexer = SupabaseIndexer()
indexer.index_chunks(chunks)
```

## Fluxo de Processamento

1. Normalização dos dados extraídos para consistência
2. Chunking dos dados em segmentos significativos com metadados
3. Geração de embeddings para cada chunk
4. Indexação dos chunks no banco vetorial Supabase

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
```