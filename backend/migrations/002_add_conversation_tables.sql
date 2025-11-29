-- Migration: Add conversation memory tables (without pgvector for now)
-- Description: Creates tables for storing conversation history
-- Note: pgvector extension is not available in Azure PostgreSQL by default

CREATE TABLE IF NOT EXISTS conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id INTEGER NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding_json JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversation_memory_cliente ON conversation_memory(cliente_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_agent ON conversation_memory(agent_name);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_created ON conversation_memory(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_memory_embedding ON conversation_memory USING GIN (embedding_json);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_conversation_memory_updated_at ON conversation_memory;
CREATE TRIGGER update_conversation_memory_updated_at
    BEFORE UPDATE ON conversation_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id INTEGER NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    messages JSONB DEFAULT '[]',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

CREATE INDEX IF NOT EXISTS idx_agent_sessions_expires ON agent_sessions(expires_at);

CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_sessions WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
