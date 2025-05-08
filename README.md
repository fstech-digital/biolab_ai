# BioLab.Ai

BioLab.Ai é um sistema para análise automatizada de exames médicos em formato PDF. O sistema utiliza tecnologias de processamento de linguagem natural, banco de dados vetorial e RAG (Retrieval Augmented Generation) para extrair, analisar e consultar dados de exames médicos.

## Visão Geral

O BioLab.Ai resolve o problema da dificuldade em interpretar exames laboratoriais de diferentes laboratórios, devido à variação de formatos e nomenclaturas. O sistema processa os PDFs de exames, extrai dados relevantes, normaliza as informações e disponibiliza consultas inteligentes através de uma interface de linha de comando (CLI).

## Arquitetura

O sistema é composto por quatro componentes principais:

1. **MCP Server**: Servidor que implementa o protocolo MCP (Model Context Protocol) para integração de LLMs com ferramentas externas. Fornece APIs para consulta de dados.

2. **PDF Extraction**: Módulo responsável pela extração de dados de exames em PDFs, identificando dados do paciente, resultados de exames e valores de referência.

3. **RAG Preprocessing**: Módulo de pré-processamento para RAG, que normaliza os dados, divide em chunks significativos e gera embeddings para busca semântica.

4. **CLI**: Interface de linha de comando que permite interagir com o sistema, executando tarefas como extração, processamento, consulta e execução do servidor.

<p align="center">
  <img src="docs/architecture.png" alt="Arquitetura BioLab.Ai" width="700">
</p>

## Fluxo de Dados

O fluxo de dados no BioLab.Ai segue a seguinte sequência:

1. Upload do PDF de exame médico
2. Extração de texto, tabelas e metadados do PDF
3. Normalização dos termos médicos, unidades e valores
4. Chunking dos dados para processamento RAG
5. Geração de embeddings para busca semântica
6. Indexação no banco vetorial Supabase
7. Consulta e análise via MCP e LLM

## Principais Recursos

- Extração de dados de PDFs de exames de diferentes laboratórios
- Normalização de termos médicos e unidades de medida
- Busca semântica de exames por paciente, data ou tipo
- Integração com LLMs via protocolo MCP
- Interface de linha de comando (CLI) para todas as funcionalidades

## Requisitos

- Python 3.10+
- Supabase (banco de dados vetorial)
- OpenAI API (ou compatível para embeddings)
- Bibliotecas Python listadas em requirements.txt

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/biolab-ai.git
   cd biolab-ai
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente no arquivo `.env`:
   ```
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

## Uso

O BioLab.Ai pode ser usado através da interface de linha de comando (CLI).

### Comandos Básicos

1. **Extrair dados de um PDF:**
   ```bash
   python biolab-cli.py extract --pdf /caminho/para/exame.pdf
   ```

2. **Processar dados para RAG:**
   ```bash
   python biolab-cli.py process --json /caminho/para/exame_extracted.json --index
   ```

3. **Consultar exames:**
   ```bash
   python biolab-cli.py query --patient "Nome do Paciente"
   ```

4. **Iniciar servidor MCP:**
   ```bash
   python biolab-cli.py server
   ```

5. **Executar fluxo completo:**
   ```bash
   python biolab-cli.py workflow --pdf /caminho/para/exame.pdf
   ```

Para mais detalhes sobre os comandos disponíveis, consulte a [documentação da CLI](ai_principal/cli/README.md).

## Estrutura do Projeto

```
/
├── ai_principal/               # Diretório principal do código
│   ├── cli/                    # Interface de linha de comando
│   ├── mcp_server/             # Servidor MCP
│   ├── pdf_extraction/         # Módulo de extração de PDFs
│   ├── rag_preprocessing/      # Módulo de pré-processamento RAG
│   ├── ai_docs/                # Documentação do projeto
│   └── specs/                  # Especificações e requisitos
├── docs/                       # Exemplos e documentação adicional
│   ├── pdfs/                   # PDFs de exemplo
│   └── planilhas/              # Planilhas de referência
├── .env.example                # Exemplo de configuração de ambiente
├── biolab-cli.py               # Script principal da CLI
└── requirements.txt            # Dependências do projeto
```

## Módulos Principais

### MCP Server

O MCP Server implementa o protocolo Model Context Protocol, permitindo que LLMs acessem funcionalidades do sistema através de uma API padronizada. Inclui ferramentas como busca de exames por paciente, data e tipo.

[Documentação do MCP Server](ai_principal/mcp_server/README.md)

### PDF Extraction

O módulo de extração de PDFs é responsável por processar os arquivos de exames, identificando dados do paciente, resultados de exames e valores de referência. Possui extratores especializados para diferentes formatos de laboratórios.

[Documentação de Extração de PDFs](ai_principal/pdf_extraction/README.md)

### RAG Preprocessing

O módulo de pré-processamento RAG normaliza os dados extraídos, divide em chunks significativos e gera embeddings para busca semântica. Facilita a recuperação contextual de informações para LLMs.

[Documentação de Pré-processamento RAG](ai_principal/rag_preprocessing/README.md)

### CLI

A interface de linha de comando (CLI) fornece acesso a todas as funcionalidades do sistema, permitindo extrair dados, processar para RAG, consultar exames e iniciar o servidor MCP.

[Documentação da CLI](ai_principal/cli/README.md)

## Roadmap

Consulte o [Roadmap de Desenvolvimento](ai_principal/ai_docs/Projeto%20BioLab_Ai.md) para detalhes sobre as próximas funcionalidades e melhorias planejadas.

## Contribuição

Para contribuir com o projeto:

1. Crie um fork do repositório
2. Crie um branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Faça push para o branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob os termos da licença MIT.