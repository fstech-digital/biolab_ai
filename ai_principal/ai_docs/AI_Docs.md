Resumo Geral
O projeto visa construir uma aplicação de leitura e análise de exames médicos (PDFs) utilizando Python, LLMs (Modelos de Linguagem Grande) e bancos vetoriais. O objetivo é criar um MVP que permita upload de exames, extração de dados-chave (como valores de hematócrito) e interpretação de resultados com base em faixas de referência. Futuramente, expandir para uma aplicação web responsiva.

APIs Externas a Integrar
Banco de Dados Vetorial (por exemplo, Pinecone, ChromaDB ou FAISS)

Serviços de OCR para melhor extração de PDFs, se necessário (ex: Tesseract, Azure OCR)

LLM API (pode ser OpenAI, Hugging Face, ou modelo proprietário)

Padrões e Convenções Importantes
MVP Primeiro: Priorizar solução simples e funcional antes de escalar.

Busca Semântica: Essencial para tratar variações de nomes em exames.

Documentos Estruturados: Preferência por JSON, CSV ou Markdown para melhor qualidade dos dados.

Testes Práticos: Com alunos e parceiros (MVP+feedback).

Interface Amigável: Evolução para Web App responsivo.

Glossário de Termos Técnicos
LLM: Large Language Model

MVP: Minimum Viable Product

OCR: Optical Character Recognition

Banco Vetorial: Estrutura para armazenamento de embeddings de dados

Busca Semântica: Localização de informações baseada no significado, não no texto exato

Notas de Implementação Específicas ao Domínio
Priorizar exames de sangue inicialmente.

Focar nos 30-40 maiores laboratórios para cobertura de 80% do mercado.

Adaptar sistema para evoluir de relatórios populacionais para timelines de exames individuais.

