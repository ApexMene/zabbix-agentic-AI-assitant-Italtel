"""Integration test for database with actual PostgreSQL."""
import pytest
import os
import sys
from pathlib import Path
from sqlalchemy import text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Investigation, ChatMessage, ToolCall, Base, engine, SessionLocal

@pytest.fixture(scope="module")
def db_connection():
    """Test database connection."""
    # This will use the actual PostgreSQL from docker-compose
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        yield engine
    except Exception as e:
        pytest.skip(f"Database not available: {e}")

@pytest.fixture
def db_session(db_connection):
    """Create database session for testing."""
    session = SessionLocal()
    yield session
    # Cleanup
    session.query(Investigation).delete()
    session.commit()
    session.close()

def test_database_connection(db_connection):
    """Test that database is accessible."""
    with db_connection.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        assert "PostgreSQL" in version

def test_tables_exist(db_connection):
    """Test that all required tables exist."""
    with db_connection.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        
        assert "investigations" in tables
        assert "chat_messages" in tables
        assert "tool_calls" in tables

def test_indexes_exist(db_connection):
    """Test that all required indexes exist."""
    with db_connection.connect() as conn:
        result = conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public'
        """))
        indexes = [row[0] for row in result]
        
        assert "idx_investigations_started_at" in indexes
        assert "idx_investigations_instance_id" in indexes
        assert "idx_investigations_status" in indexes
        assert "idx_chat_messages_investigation" in indexes
        assert "idx_tool_calls_investigation" in indexes

def test_full_investigation_workflow(db_session):
    """Test complete investigation workflow with PostgreSQL."""
    # Create investigation
    investigation = Investigation(
        alarm_id="test-alarm-123",
        alarm_description="High CPU usage on production server",
        alarm_severity="high",
        host_name="prod-server-01",
        instance_id="zabbix-backbone"
    )
    db_session.add(investigation)
    db_session.commit()
    
    inv_id = investigation.id
    
    # Add messages
    messages = [
        ChatMessage(investigation_id=inv_id, role="system", content="Starting investigation"),
        ChatMessage(investigation_id=inv_id, role="assistant", content="Analyzing host..."),
        ChatMessage(investigation_id=inv_id, role="user", content="What's the root cause?"),
    ]
    db_session.add_all(messages)
    
    # Add tool calls
    tool_calls = [
        ToolCall(
            investigation_id=inv_id,
            tool_name="host_get",
            parameters={"host": "prod-server-01"},
            result={"hostid": "10001", "name": "prod-server-01"},
            duration_ms=120
        ),
        ToolCall(
            investigation_id=inv_id,
            tool_name="problem_get",
            parameters={"hostids": ["10001"]},
            result={"problems": [{"eventid": "123", "severity": "4"}]},
            duration_ms=85
        ),
    ]
    db_session.add_all(tool_calls)
    db_session.commit()
    
    # Verify relationships
    retrieved = db_session.query(Investigation).filter_by(id=inv_id).first()
    assert retrieved is not None
    assert len(retrieved.messages) == 3
    assert len(retrieved.tool_calls) == 2
    
    # Verify JSONB storage
    first_tool = retrieved.tool_calls[0]
    assert first_tool.parameters["host"] == "prod-server-01"
    assert first_tool.result["hostid"] == "10001"
    
    # Update investigation status
    retrieved.status = "completed"
    db_session.commit()
    
    # Verify update
    updated = db_session.query(Investigation).filter_by(id=inv_id).first()
    assert updated.status == "completed"
    assert updated.updated_at > updated.created_at

def test_cascade_delete_postgresql(db_session):
    """Test cascade delete with PostgreSQL."""
    investigation = Investigation(
        alarm_id="test-cascade",
        alarm_description="Test cascade delete",
        alarm_severity="warning",
        host_name="test-host",
        instance_id="test-instance"
    )
    db_session.add(investigation)
    db_session.commit()
    
    inv_id = investigation.id
    
    # Add related records
    message = ChatMessage(investigation_id=inv_id, role="user", content="Test")
    tool_call = ToolCall(investigation_id=inv_id, tool_name="test", parameters={})
    db_session.add_all([message, tool_call])
    db_session.commit()
    
    # Delete investigation
    db_session.delete(investigation)
    db_session.commit()
    
    # Verify cascade
    assert db_session.query(ChatMessage).filter_by(investigation_id=inv_id).count() == 0
    assert db_session.query(ToolCall).filter_by(investigation_id=inv_id).count() == 0
