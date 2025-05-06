# MCP Server para BioLab.Ai

## Descrição

O MCP (Model Context Protocol) Server é um componente modular do BioLab.Ai que expõe funcionalidades do sistema através de uma API padronizada, permitindo que diferentes LLMs e aplicações clientes acessem recursos do sistema de maneira consistente.

## Arquitetura

```
BioLab.Ai Core <---> MCP Server <---> Supabase
                        |
                    (Endpoints)
                        |
            ---------------------------
            |           |             |
          LLMs      Web Client    Mobile App
```

## Ferramentas MCP (Tools)

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

## Implementação

- **Backend**: Python 3.10+
- **Frameworks**: Supabase (banco de dados), SDK MCP (quando disponível)
- **Dependências**: Ver `requirements.txt` em `ai_principal/mcp_server`

## Integração com Extração de PDFs

O MCP Server se integra com a infraestrutura existente do BioLab.Ai:

1. Os PDFs são processados pelo pipeline de extração
2. Os metadados do paciente (nome, idade, gênero) são extraídos 
3. Cada exame individual é salvo no Supabase com seus respectivos metadados
4. O MCP Server fornece uma camada de abstração para consultar esses dados

## Setup e Execução

```bash
# Instalação de dependências
pip install -r ai_principal/mcp_server/requirements.txt

# Teste da ferramenta de busca
python ai_principal/mcp_server/test_mcp_busca.py
```

## Próximos Passos

1. Implementar protocolo MCP completo usando uma SDK oficial ou implementation manual
2. Adicionar endpoints HTTP via FastAPI para acesso sem MCP
3. Expandir conjunto de ferramentas disponíveis
4. Documentar schemas de dados e exemplos de uso
