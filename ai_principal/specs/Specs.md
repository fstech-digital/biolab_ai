Problema
Dificuldade de alunos e profissionais de saúde em interpretar exames laboratoriais de diferentes laboratórios, devido à variação de formatos e nomenclaturas.

Solução Proposta
Aplicação baseada em Python + LLMs que faz upload de PDFs, extrai valores relevantes e interpreta resultados com auxílio de inteligência artificial.

Arquitetura
Upload de PDF →

Extração de Dados (OCR + pré-processamento) →

Indexação em Banco Vetorial (Supabase) →

MCP Server (Model Context Protocol) →

Interação via LLM para consultas e relatórios →

Interface CLI e Web App

Divisão de Módulos/Fases
MVP CLI:

Upload e leitura básica de exames

Consulta de valores individuais

Web App Inicial:

Interface amigável para uploads e buscas

Escala Educacional:

Testes com alunos, coleta de feedback

Expansão:

Inclusão de múltiplos laboratórios e dashboards de evolução

Critérios de Aceitação
Upload e leitura funcional de PDFs de exames.

Retorno correto de valores solicitados.

Correlação dos valores com faixas etárias/sexo corretos.

Primeira versão testada e validada por alunos.

Auto-Validation
Testes unitários: Extração de valores corretos dos PDFs.

Testes de integração: Upload, processamento e resposta da LLM.

Testes de usabilidade: Coletar feedback prático com usuários reais.

