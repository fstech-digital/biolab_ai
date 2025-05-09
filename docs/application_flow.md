# BioLab.Ai Application Flow

## Detailed Mermaid Diagram

```mermaid
graph TD
    %% Main Entry Points
    start[User] --> cli[biolab-cli.py]
    start --> chat[biolab-chat.py]
    
    %% CLI Mode
    cli --> cli_main[ai_principal/cli/main.py]
    cli_main --> commands{Commands}
    
    %% Chat Mode
    chat --> interactive[ai_principal/cli/interactive.py]
    interactive --> menu{Interactive Menu}
    
    %% Commands
    commands --> extract[cmd_extract]
    commands --> process[cmd_process]
    commands --> query[cmd_query]
    commands --> server[cmd_server]
    commands --> workflow[cmd_workflow]
    
    %% Interactive Menu
    menu --> int_extract[interactive_extract]
    menu --> int_process[interactive_process]
    menu --> int_query[interactive_query]
    menu --> int_server[interactive_server]
    menu --> int_workflow[interactive_workflow]
    
    %% Extract Flow
    extract --> pdf_extraction[ai_principal/pdf_extraction/main.py]
    int_extract --> pdf_extraction
    pdf_extraction --> extractor_factory[ExtractorFactory]
    extractor_factory --> pdf_extractor[PDFExtractor]
    pdf_extractor --> extract_text
    pdf_extractor --> extract_tables
    pdf_extractor --> extract_metadata
    pdf_extractor --> extract_patient
    pdf_extractor --> extract_exams
    extract_text --> extracted_data[(JSON Data)]
    extract_tables --> extracted_data
    extract_metadata --> extracted_data
    extract_patient --> extracted_data
    extract_exams --> extracted_data
    pdf_extraction --> reference_processor[ExcelReferenceProcessor]
    reference_processor --> enriched_data[(Enriched JSON)]
    
    %% Process Flow
    process --> rag_preprocessing[ai_principal/rag_preprocessing/processor.py]
    int_process --> rag_preprocessing
    rag_preprocessing --> rag_processor[RAGProcessor]
    rag_processor --> normalizer[ExamNormalizer]
    rag_processor --> chunker[ExamChunker]
    rag_processor --> embed_generator[EmbeddingGenerator]
    normalizer --> normalized_data[(Normalized Data)]
    normalized_data --> chunker
    chunker --> chunks[(Text Chunks)]
    chunks --> embed_generator
    embed_generator --> openai_api{OpenAI API}
    openai_api --> chunks_with_embeddings[(Chunks with Embeddings)]
    
    %% Indexing Flow
    process -- index=True --> indexer[SupabaseIndexer]
    int_process -- index=True --> indexer
    chunks_with_embeddings --> indexer
    indexer --> supabase[(Supabase Vector DB)]
    
    %% Query Flow
    query --> mcp_tools[ai_principal/mcp_server/mcp_tools.py]
    int_query --> mcp_tools
    mcp_tools --> buscar_paciente[buscar_exames_paciente]
    mcp_tools --> buscar_data[buscar_exames_data]
    mcp_tools --> buscar_tipo[buscar_exames_tipo]
    mcp_tools --> valores_ref[obter_valores_referencia]
    buscar_paciente --> vector_store[SupabaseVectorStore]
    buscar_data --> vector_store
    buscar_tipo --> vector_store
    valores_ref --> vector_store
    vector_store --> supabase
    
    %% Server Flow
    server --> http_server[ai_principal/mcp_server/http_server.py]
    int_server --> http_server
    http_server --> mcp_server[MCPServer]
    mcp_server --> mcp_tools
    
    %% Workflow Flow
    workflow --> extract
    workflow --> process
    workflow --> indexer
    int_workflow --> int_extract
    int_workflow --> int_process
    int_workflow --> indexer
    
    %% Legend
    classDef module fill:#f9f,stroke:#333,stroke-width:2px
    classDef data fill:#bbf,stroke:#33f,stroke-width:2px
    classDef process fill:#afa,stroke:#3a3,stroke-width:2px
    classDef external fill:#fdb,stroke:#d73,stroke-width:2px
    
    class cli_main,interactive,pdf_extraction,rag_preprocessing,mcp_tools,http_server module
    class extracted_data,enriched_data,normalized_data,chunks,chunks_with_embeddings data
    class extract,process,query,server,workflow,int_extract,int_process,int_query,int_server,int_workflow process
    class supabase,openai_api external
```

## Simplified Application Flow

```
1. Entry Points
   - biolab-cli.py (Command Line Mode)
   - biolab-chat.py (Interactive Mode)

2. Command Line Workflows
   a. Extract Command
      PDF File(s) → PDF Extractor → JSON Data → (Optional: Enrichment) → Enriched JSON
   
   b. Process Command
      JSON Data → RAG Processor → Normalizer → Chunker → Embedding Generator → Chunks with Embeddings → (Optional: Indexer) → Supabase Vector DB
   
   c. Query Command
      Query Parameters → MCP Tools → Supabase Vector Store → Results
   
   d. Server Command
      Start HTTP Server → Host MCP Server → Handle MCP Requests
   
   e. Workflow Command
      PDF File → Extract → Process → Index → Complete Workflow

3. Interactive Mode Workflows
   - Menu-based interface to the same commands
   - Step-by-step guided flow with user prompts
   - Same underlying components as CLI mode

4. Data Flow Diagram
   Raw PDF → Extracted Text/Tables → Structured JSON → Normalized Data → Text Chunks → Vector Embeddings → Vector Database → Query Results
```

## Visual Representation (Markdown ASCII)

```
+----------+     +----------------+     +-------------------+
|   User   |---->| biolab-cli.py  |---->| cli/main.py       |
|          |     +----------------+     | (Command Parser)  |
|          |                            +-------------------+
|          |                                     |
|          |                                     v
|          |                            +-------------------+
|          |                            | Commands:         |
|          |                            | - extract         |
|          |                            | - process         |
|          |                            | - query           |
|          |                            | - server          |
|          |                            | - workflow        |
|          |                            +-------------------+
|          |                                     |
|          |                              +------+------+
|          |                              v             v
|          |     +----------------+     +-------+     +--------+
|          |---->| biolab-chat.py |---->| Menu  |---->| Cmds   |
+----------+     +----------------+     +-------+     +--------+
                                                        |
                                                        v
+-------------------------------------------------------------+
|                                                             |
|                      PDF EXTRACTION                         |
|  +------------+     +----------------+     +--------------+ |
|  | PDF Files  |---->| PDF Extractor  |---->| JSON Data    | |
|  +------------+     +----------------+     +--------------+ |
|                            |                      |         |
|                            v                      v         |
|                     +--------------+     +--------------+   |
|                     | Reference    |---->| Enriched     |   |
|                     | Processor    |     | JSON         |   |
|                     +--------------+     +--------------+   |
|                                                             |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                                                             |
|                     RAG PREPROCESSING                       |
|  +--------------+     +--------------+     +--------------+ |
|  | JSON Data    |---->| Normalizer   |---->| Chunker      | |
|  +--------------+     +--------------+     +--------------+ |
|                                                   |         |
|                                                   v         |
|  +--------------+     +--------------+     +--------------+ |
|  | Embeddings   |<----| OpenAI API   |<----| Text Chunks  | |
|  +--------------+     +--------------+     +--------------+ |
|        |                                                    |
|        v                                                    |
|  +--------------+                                           |
|  | Supabase     |                                           |
|  | Vector DB    |                                           |
|  +--------------+                                           |
|                                                             |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                                                             |
|                        MCP SERVER                           |
|  +--------------+     +--------------+     +--------------+ |
|  | HTTP Server  |---->| MCP Server   |---->| MCP Tools    | |
|  +--------------+     +--------------+     +--------------+ |
|                                                   |         |
|                                                   v         |
|  +--------------+     +--------------+                      |
|  | Search       |---->| Supabase     |                      |
|  | Results      |<----| Vector Store |                      |
|  +--------------+     +--------------+                      |
|                                                             |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                                                             |
|                    COMPLETE WORKFLOW                        |
|                                                             |
|  +-------+     +--------+     +--------+     +----------+   |
|  | PDF   |---->| Extract|---->| Process|---->| Index    |   |
|  | File  |     | Data   |     | RAG    |     | Supabase |   |
|  +-------+     +--------+     +--------+     +----------+   |
|                                                             |
+-------------------------------------------------------------+
```

## Component Descriptions

### Entry Points
- **biolab-cli.py**: Command-line interface for direct command execution
- **biolab-chat.py**: Interactive menu-based navigation for easier usage

### Key Components
- **PDF Extraction Module**: Extracts structured data from PDF medical exam files
- **RAG Preprocessing Module**: Normalizes data, chunks text, and generates embeddings for semantic search
- **MCP Server**: Implements Model Context Protocol for integration with LLMs
- **Supabase Integration**: Vector database storage and retrieval

### Workflows
1. **Extract**: PDF → Structured JSON
2. **Process**: JSON → Vector Embeddings
3. **Query**: Search Parameters → Matching Exams
4. **Server**: Expose MCP API for LLM Integration
5. **Workflow**: End-to-end Processing (PDF → Indexed Database)