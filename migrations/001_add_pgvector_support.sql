-- Migration: Add pgvector extension and conversation memory table
-- Description: Enables vector similarity search for RAG (Retrieval-Augmented Generation)

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create conversation_memory table for storing embeddings
CREATE TABLE IF NOT EXISTS conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_memory_cliente 
    ON conversation_memory(cliente_id);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_agent 
    ON conversation_memory(agent_name);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_created 
    ON conversation_memory(created_at DESC);

-- Create vector similarity search index (HNSW for better performance)
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding 
    ON conversation_memory 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Create function for automatic updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS update_conversation_memory_updated_at ON conversation_memory;
CREATE TRIGGER update_conversation_memory_updated_at
    BEFORE UPDATE ON conversation_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create agent_sessions table for short-term memory (Redis backup)
CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    messages JSONB DEFAULT '[]',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

-- Create index for session cleanup
CREATE INDEX IF NOT EXISTS idx_agent_sessions_expires 
    ON agent_sessions(expires_at);

-- Create index for active sessions lookup
CREATE INDEX IF NOT EXISTS idx_agent_sessions_cliente_active 
    ON agent_sessions(cliente_id, expires_at) 
    WHERE expires_at > CURRENT_TIMESTAMP;

-- Create function to clean expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_sessions 
    WHERE expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE conversation_memory IS 'Stores conversation history with vector embeddings for RAG';
COMMENT ON COLUMN conversation_memory.embedding IS 'Vector embedding (1536 dimensions) from text-embedding-3-small';
COMMENT ON TABLE agent_sessions IS 'Temporary session storage for active conversations (Redis backup)';

-- Grant permissions (adjust as needed for your user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_memory TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON agent_sessions TO your_app_user;

-- Example query for vector similarity search
-- SELECT id, content, metadata, 1 - (embedding <=> query_embedding) AS similarity
-- FROM conversation_memory
-- WHERE cliente_id = $1
-- ORDER BY embedding <=> query_embedding
-- LIMIT 5;
