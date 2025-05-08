# Projeto BioLab.Ai - Roadmap de Desenvolvimento

## Descrição do Projeto
O BioLab.Ai é uma aplicação de leitura e análise de exames médicos (PDFs) utilizando Python, LLMs e bancos vetoriais. O objetivo é criar um MVP que permita upload de exames, extração de dados-chave (como valores de hematócrito) e interpretação de resultados com base em faixas de referência.

## Requisitos Funcionais do MVP CLI
1. Upload e processamento de PDFs de exames médicos
2. Extração de dados essenciais (valores/métricas, paciente, data)
3. Pré-processamento RAG dos dados extraídos
4. Armazenamento no banco vetorial Supabase
5. Consulta básica de valores específicos de exames
6. Interpretação contextualizada com faixas de referência
7. Interface CLI funcional para testar o fluxo completo

## Arquitetura Técnica

### Componentes Principais
- Módulo de Upload e Processamento PDF (PyMuPDF, PDFPlumber)
- Extração de Dados com OCR e LLM
- Pré-processamento RAG
- Banco Vetorial (Supabase + pgvector)
- MCP Server (FastAPI)
- Interface CLI (inicial) / Web (futura)

### Fluxo de Dados
Upload PDF → Extração (OCR + LLM) → Pré-processamento RAG → Embedding → Indexação Supabase → Disponibilização via MCP

### Componentes do Pré-processamento RAG
- Chunking: Dividir texto em segmentos gerenciáveis
- Normalização: Padronizar termos médicos e unidades
- Filtragem: Remover informações irrelevantes
- Enriquecimento: Adicionar metadados e contexto
- Embedding: Geração de vetores semânticos

### Tecnologias
- Backend: Python 3.10+ (FastAPI)
- Processamento: LangChain + OpenAI
- Armazenamento: Supabase (vetores)
- Comunicação: MCP Protocol

## Cronograma de Desenvolvimento (12 semanas)

### Fase 1: Reconstrução MCP Server (2 semanas)
- **Semana 1**: Setup básico do servidor FastAPI e integração Supabase
- **Semana 2**: Implementação ferramentas MCP iniciais

### Fase 2: Pipeline de Extração PDF (2 semanas)
- **Semana 3-4**: Desenvolvimento de extratores para formatos comuns de exames

### Fase 3: Pré-processamento RAG (3 semanas)
- **Semana 5**: Implementação de chunking e normalização
- **Semana 6**: Desenvolvimento de filtragem e enriquecimento
- **Semana 7**: Geração de embeddings e integração MCP

### Fase 4: CLI e MVP (2 semanas)
- **Semana 8-9**: Interface de linha de comando e testes do MVP completo

### Fase 5: Web App Básico (3 semanas)
- **Semana 10-12**: Desenvolvimento da interface web

## Próximos Passos
1. Recriar componentes do MCP Server (módulo removido)
2. Implementar pipeline de extração de PDFs de exames
3. Configurar conexão com Supabase para banco vetorial
4. Desenvolver módulo de pré-processamento RAG
5. Criar interface CLI básica para testes iniciais
6. Implementar ferramenta `buscar_exames_paciente` e outras planejadas
7. Criar testes unitários para validação do processamento
8. Preparar integração com interface web (próxima fase)

## Ferramentas MCP (API)

### Implementadas
| Nome | Descrição | Parâmetros | Retorno |
|------|-----------|------------|---------|
| `buscar_exames_paciente` | Busca exames por nome do paciente | `patient_name: string` | Lista de exames com dados do paciente e valores |

### Planejadas
| Nome | Descrição | Parâmetros | Retorno |
|------|-----------|------------|---------|
| `buscar_exames_data` | Busca exames por intervalo de data | `start_date: string, end_date: string` | Lista de exames nesse período |
| `buscar_exames_tipo` | Busca por tipo de exame | `exam_type: string` | Lista de exames do tipo especificado |
| `obter_valores_referencia` | Obter valores de referência para um exame | `exam_code: string, age: int, gender: string` | Valores de referência para o exame |