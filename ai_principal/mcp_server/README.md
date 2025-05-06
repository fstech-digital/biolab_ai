# BioLab.Ai MCP Server

Este componente expõe ferramentas do BioLab.Ai através do protocolo MCP (Model Context Protocol) e uma API HTTP REST.

## Estrutura

```
mcp_server/
├── mcp_tools.py       # Definição das ferramentas MCP
├── supabase_client.py # Cliente de acesso ao Supabase
├── server.py          # Servidor MCP (stdin/stdout)
├── http_server.py     # Servidor HTTP REST (FastAPI)
├── requirements.txt   # Dependências
└── test_*.py          # Scripts de teste
```

## Ferramentas disponíveis

- **buscar_exames_paciente**: Busca exames por nome de paciente
- **buscar_exames_por_data**: Busca exames por intervalo de data
- **buscar_exames_por_tipo**: Busca exames por tipo/nome do exame
- **obter_valores_referencia**: Obtém valores de referência para um exame

## Uso do servidor HTTP

O servidor HTTP expõe todas as ferramentas MCP como endpoints REST.

### Iniciar o servidor HTTP:

```bash
python ai_principal/mcp_server/http_server.py
```

O servidor estará disponível em `http://localhost:8000`.

### Endpoints disponíveis:

- **POST /api/exames/paciente**: Buscar exames por paciente
  ```json
  { "patient_name": "Altamiro" }
  ```

- **POST /api/exames/data**: Buscar exames por data
  ```json
  { "start_date": "10/09/2024", "end_date": "07/10/2024" }
  ```

- **POST /api/exames/tipo**: Buscar exames por tipo
  ```json
  { "exam_type": "hemoglobina" }
  ```

- **POST /api/exames/referencia**: Obter valores de referência
  ```json
  { "exam_code": "hemoglobina", "age": 42, "gender": "Masculino" }
  ```

**Também possui endpoints GET para facilitar testes:**
- GET /api/exames/paciente/{patient_name}
- GET /api/exames/tipo/{exam_type}
- GET /api/exames/referencia/{exam_code}?age=42&gender=Masculino

## Uso do servidor MCP

Para aplicações que requerem integração MCP completa:

```bash
python -m ai_principal.mcp_server.server
```

## Dependências

As dependências estão em `requirements.txt`. Instale com:

```bash
pip install -r ai_principal/mcp_server/requirements.txt
```

## Variáveis de ambiente

- **SUPABASE_URL**: URL do seu projeto Supabase
- **SUPABASE_KEY**: Key de acesso ao Supabase
- **MCP_HTTP_PORT**: (opcional) Porta para o servidor HTTP (padrão: 8000)

## Licença

Este projeto é parte do BioLab.Ai e segue a mesma licença do projeto principal.
