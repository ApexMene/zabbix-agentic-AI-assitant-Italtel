"""SQLAlchemy models for investigations, chat messages, and tool calls."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .database import Base

class Investigation(Base):
    """Investigation session model."""
    __tablename__ = "investigations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="in_progress", nullable=False)
    
    # Alarm context
    alarm_id = Column(String(100), nullable=False)
    alarm_description = Column(Text, nullable=False)
    alarm_severity = Column(String(20), nullable=False)
    host_name = Column(String(255), nullable=False)
    instance_id = Column(String(100), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="investigation", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="investigation", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'failed', 'cancelled')",
            name="chk_status"
        ),
    )
    
    def __repr__(self):
        return f"<Investigation(id={self.id}, host={self.host_name}, status={self.status})>"

class ChatMessage(Base):
    """Chat message model."""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    investigation = relationship("Investigation", back_populates="messages")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="chk_role"
        ),
    )
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, investigation_id={self.investigation_id})>"

class ToolCall(Base):
    """Tool call audit trail model."""
    __tablename__ = "tool_calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    parameters = Column(JSONB, nullable=True)
    result = Column(JSONB, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    investigation = relationship("Investigation", back_populates="tool_calls")
    
    def __repr__(self):
        return f"<ToolCall(id={self.id}, tool={self.tool_name}, investigation_id={self.investigation_id})>"
