"""Unit tests for database models."""
import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import Investigation, ChatMessage, ToolCall, Base
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    # Replace JSONB with JSON for SQLite compatibility
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_investigation(db_session):
    """Test creating an investigation."""
    investigation = Investigation(
        alarm_id="12345",
        alarm_description="High CPU usage",
        alarm_severity="high",
        host_name="server-01",
        instance_id="zabbix-backbone"
    )
    db_session.add(investigation)
    db_session.commit()
    
    assert investigation.id is not None
    assert investigation.status == "in_progress"
    assert investigation.started_at is not None
    assert investigation.created_at is not None

def test_investigation_relationships(db_session):
    """Test investigation relationships with messages and tool calls."""
    investigation = Investigation(
        alarm_id="12345",
        alarm_description="High CPU usage",
        alarm_severity="high",
        host_name="server-01",
        instance_id="zabbix-backbone"
    )
    db_session.add(investigation)
    db_session.commit()
    
    # Add chat message
    message = ChatMessage(
        investigation_id=investigation.id,
        role="user",
        content="What's causing the high CPU?"
    )
    db_session.add(message)
    
    # Add tool call
    tool_call = ToolCall(
        investigation_id=investigation.id,
        tool_name="host_get",
        parameters={"host": "server-01"},
        result={"status": "ok"},
        duration_ms=150
    )
    db_session.add(tool_call)
    db_session.commit()
    
    # Verify relationships
    assert len(investigation.messages) == 1
    assert len(investigation.tool_calls) == 1
    assert investigation.messages[0].content == "What's causing the high CPU?"
    assert investigation.tool_calls[0].tool_name == "host_get"

def test_chat_message_role_constraint(db_session):
    """Test chat message role constraint."""
    investigation = Investigation(
        alarm_id="12345",
        alarm_description="Test",
        alarm_severity="high",
        host_name="server-01",
        instance_id="test"
    )
    db_session.add(investigation)
    db_session.commit()
    
    # Valid roles
    for role in ['user', 'assistant', 'system']:
        message = ChatMessage(
            investigation_id=investigation.id,
            role=role,
            content=f"Test message from {role}"
        )
        db_session.add(message)
    
    db_session.commit()
    assert len(investigation.messages) == 3

def test_investigation_status_constraint(db_session):
    """Test investigation status constraint."""
    # Valid statuses
    for status in ['in_progress', 'completed', 'failed', 'cancelled']:
        investigation = Investigation(
            alarm_id=f"test-{status}",
            alarm_description="Test",
            alarm_severity="high",
            host_name="server-01",
            instance_id="test",
            status=status
        )
        db_session.add(investigation)
    
    db_session.commit()
    
    investigations = db_session.query(Investigation).all()
    assert len(investigations) == 4

def test_cascade_delete(db_session):
    """Test cascade delete of messages and tool calls."""
    investigation = Investigation(
        alarm_id="12345",
        alarm_description="Test",
        alarm_severity="high",
        host_name="server-01",
        instance_id="test"
    )
    db_session.add(investigation)
    db_session.commit()
    
    # Add related records
    message = ChatMessage(
        investigation_id=investigation.id,
        role="user",
        content="Test"
    )
    tool_call = ToolCall(
        investigation_id=investigation.id,
        tool_name="test_tool",
        parameters={}
    )
    db_session.add_all([message, tool_call])
    db_session.commit()
    
    investigation_id = investigation.id
    
    # Delete investigation
    db_session.delete(investigation)
    db_session.commit()
    
    # Verify cascade delete
    assert db_session.query(ChatMessage).filter_by(investigation_id=investigation_id).count() == 0
    assert db_session.query(ToolCall).filter_by(investigation_id=investigation_id).count() == 0

def test_tool_call_jsonb_fields(db_session):
    """Test JSONB fields in tool calls."""
    investigation = Investigation(
        alarm_id="12345",
        alarm_description="Test",
        alarm_severity="high",
        host_name="server-01",
        instance_id="test"
    )
    db_session.add(investigation)
    db_session.commit()
    
    tool_call = ToolCall(
        investigation_id=investigation.id,
        tool_name="host_get",
        parameters={"host": "server-01", "filters": ["active"]},
        result={"hosts": [{"name": "server-01", "status": "active"}]},
        duration_ms=250
    )
    db_session.add(tool_call)
    db_session.commit()
    
    # Retrieve and verify
    retrieved = db_session.query(ToolCall).first()
    assert retrieved.parameters["host"] == "server-01"
    assert retrieved.result["hosts"][0]["name"] == "server-01"
    assert retrieved.duration_ms == 250
