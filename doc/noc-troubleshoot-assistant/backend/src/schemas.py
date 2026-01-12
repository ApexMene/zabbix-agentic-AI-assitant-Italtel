"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# Instance schemas
class InstanceStatus(BaseModel):
    id: str
    name: str
    status: str
    version: Optional[str] = None
    error: Optional[str] = None
    problem_counts: Optional[Dict[str, int]] = None
    last_sync: Optional[datetime] = None

# Alarm schemas
class Alarm(BaseModel):
    id: str
    instance_id: str
    instance_name: str
    host: str
    description: str
    severity: str
    severity_code: int
    duration: str
    acknowledged: bool
    event_id: str
    is_synthetic: bool = False
    started_at: Optional[str] = None

class AlarmAcknowledge(BaseModel):
    instance_id: str
    message: Optional[str] = ""

# Chat schemas
class ChatMessageCreate(BaseModel):
    investigation_id: UUID
    message: str

class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class InvestigateRequest(BaseModel):
    alarm_id: str
    instance_id: str

# Investigation schemas
class InvestigationResponse(BaseModel):
    id: UUID
    started_at: datetime
    ended_at: Optional[datetime]
    status: str
    alarm_id: str
    alarm_description: str
    alarm_severity: str
    host_name: str
    instance_id: str
    
    class Config:
        from_attributes = True

class InvestigationDetail(InvestigationResponse):
    messages: List[ChatMessageResponse]
    tool_calls: List[Dict[str, Any]]

# History schemas
class HistoryFilter(BaseModel):
    search: Optional[str] = None
    instance_id: Optional[str] = None
    severity: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = 1
    limit: int = 20

class HistoryListResponse(BaseModel):
    investigations: List[InvestigationResponse]
    total: int
    page: int
    limit: int
