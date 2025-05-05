-- Habilitar a extensão pgvector para suporte a busca vetorial
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de documentos (PDFs de exames)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de exames com vetores para busca semântica
CREATE TABLE IF NOT EXISTS exam_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    user_id UUID REFERENCES users(id),
    exam_code VARCHAR(100),
    exam_name VARCHAR(255),
    exam_value FLOAT,
    exam_unit VARCHAR(50),
    reference_min FLOAT,
    reference_max FLOAT,
    reference_text VARCHAR(255),
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para Base de Conhecimento (planilhas Excel)
CREATE TABLE IF NOT EXISTS knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sheet_id UUID NOT NULL,
    collection_name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para busca vetorial usando cosine similarity
CREATE INDEX ON exam_vectors USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX ON knowledge_vectors USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Tabela para armazenar relatórios gerados
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    document_id UUID REFERENCES documents(id),
    report_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Política de segurança RLS para usuários
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_self_access ON users
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Política de segurança RLS para documentos
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY documents_user_access ON documents
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Política de segurança RLS para exames
ALTER TABLE exam_vectors ENABLE ROW LEVEL SECURITY;
CREATE POLICY exam_vectors_user_access ON exam_vectors
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Política de segurança RLS para relatórios
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY reports_user_access ON reports
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Política para base de conhecimento (acesso para todos)
ALTER TABLE knowledge_vectors ENABLE ROW LEVEL SECURITY;
CREATE POLICY knowledge_vectors_access ON knowledge_vectors
    USING (true);

-- Índices para otimização de consultas
CREATE INDEX idx_document_user ON documents(user_id);
CREATE INDEX idx_exam_document ON exam_vectors(document_id);
CREATE INDEX idx_exam_user ON exam_vectors(user_id);
CREATE INDEX idx_exam_code ON exam_vectors(exam_code);
CREATE INDEX idx_report_document ON reports(document_id);
CREATE INDEX idx_report_user ON reports(user_id);
CREATE INDEX idx_knowledge_collection ON knowledge_vectors(collection_name);
CREATE INDEX idx_knowledge_sheet ON knowledge_vectors(sheet_id);
