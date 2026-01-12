-- Network Troubleshooting Assistant Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Investigations table
CREATE TABLE investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    
    -- Alarm context
    alarm_id VARCHAR(100) NOT NULL,
    alarm_description TEXT NOT NULL,
    alarm_severity VARCHAR(20) NOT NULL,
    host_name VARCHAR(255) NOT NULL,
    instance_id VARCHAR(100) NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_status CHECK (status IN ('in_progress', 'completed', 'failed', 'cancelled'))
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_role CHECK (role IN ('user', 'assistant', 'system'))
);

-- Tool calls table (audit trail)
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    parameters JSONB,
    result JSONB,
    duration_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_investigations_started_at ON investigations(started_at DESC);
CREATE INDEX idx_investigations_instance_id ON investigations(instance_id);
CREATE INDEX idx_investigations_status ON investigations(status);
CREATE INDEX idx_investigations_host_name ON investigations(host_name);

CREATE INDEX idx_chat_messages_investigation ON chat_messages(investigation_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp DESC);

CREATE INDEX idx_tool_calls_investigation ON tool_calls(investigation_id);
CREATE INDEX idx_tool_calls_timestamp ON tool_calls(timestamp DESC);
CREATE INDEX idx_tool_calls_tool_name ON tool_calls(tool_name);

-- Full-text search index for chat messages
CREATE INDEX idx_chat_messages_content_fts ON chat_messages 
    USING gin(to_tsvector('english', content));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_investigations_updated_at
    BEFORE UPDATE ON investigations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE investigations IS 'Stores investigation sessions for network troubleshooting';
COMMENT ON TABLE chat_messages IS 'Stores chat conversation history for each investigation';
COMMENT ON TABLE tool_calls IS 'Audit trail of all MCP tool invocations during investigations';

COMMENT ON COLUMN investigations.status IS 'Current status: in_progress, completed, failed, cancelled';
COMMENT ON COLUMN chat_messages.role IS 'Message sender: user, assistant, system';
COMMENT ON COLUMN tool_calls.duration_ms IS 'Tool execution time in milliseconds';
