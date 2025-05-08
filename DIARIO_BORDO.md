# Diário de Bordo - Projeto BioLab.Ai

## 07/05/2025 - Organização do projeto e implementação inicial

### Atividades Realizadas
- Compreensão da estrutura do projeto BioLab.Ai
- Organização dos requisitos funcionais do MVP CLI
- Mapeamento da arquitetura técnica do sistema
- Criação do plano de desenvolvimento com cronograma estimado (12 semanas)
- Atualização da arquitetura para incluir pré-processamento RAG
- Implementação do MCP Server básico
- Implementação do pipeline de extração de PDFs
- Implementação do módulo de pré-processamento RAG
- Criação da interface CLI básica e modo interativo (chat)

### Problemas Encontrados
1. **Integração com Supabase**
   - Problema: Coluna "patient_name" não encontrada na tabela biolab_documents
   - Causa: Estrutura da tabela diferente do esperado, com dados de paciente no campo metadata (JSONB)
   - Solução: Atualização do código para buscar o nome do paciente no campo metadata->patient_name

2. **Consulta por nome parcial**
   - Problema: Busca por "Lazaro" não encontrava documentos com nome completo "Lazaro Alessandro Soares Nunes"
   - Solução: Implementação de busca com ILIKE para considerar correspondências parciais

3. **Visualização de resultados**
   - Problema: Interface CLI não mostrava detalhes suficientes sobre os exames
   - Solução parcial: Implementação de tabela formatada mostrando ID, tipo de documento, paciente e fonte

4. **Inconsistência nos documentos indexados**
   - Observação: Documento ID 1 sem nome de paciente nos metadados
   - Causa: Processamento anterior incompleto ou incorreto
   - Status: Não crítico para funcionamento, documentos mais recentes estão corretos

### Próximos Passos
1. **Aprimoramento da interface de resultados**
   - Implementar visualização detalhada dos resultados de exames
   - Mostrar valores de referência e comparar com resultados
   - Adicionar formatação visual para indicar resultados normais/alterados

2. **Refinamento da busca**
   - Implementar busca por intervalo de datas
   - Implementar busca por tipo de exame
   - Melhorar agrupamento de resultados por paciente

3. **Funcionalidades adicionais para CLI**
   - Exportação de resultados em formato amigável (PDF, HTML)
   - Visualização de tendências para múltiplos exames do mesmo paciente
   - Integração com planilha de referência para validação de resultados

## Observações Gerais

- O fluxo básico de extração, processamento e consulta está funcionando
- A arquitetura baseada em chunks de RAG permite buscas semânticas avançadas no futuro
- A separação em módulos (MCP Server, Extração PDF, RAG, CLI) facilita extensões futuras
- Necessário testar com mais exemplos de PDFs de diferentes laboratórios

## Decisões Técnicas
- Uso de Supabase para armazenamento vetorial
- Divisão de documentos em chunks (info paciente, resultados e resumo)
- Implementação de duas interfaces: CLI comando e modo interativo (chat)
- Abordagem de fallback para consultas (tenta via MCP, depois direto na Supabase)