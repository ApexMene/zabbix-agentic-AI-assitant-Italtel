"""Investigation history routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json

from models import get_db, Investigation, ChatMessage, ToolCall
from schemas import InvestigationResponse, InvestigationDetail, HistoryFilter, HistoryListResponse

router = APIRouter()

@router.get("", response_model=HistoryListResponse)
async def list_investigations(
    search: Optional[str] = Query(None, description="Full-text search"),
    instance_id: Optional[str] = Query(None),
    severity: Optional[List[str]] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List investigation history with filtering."""
    query = db.query(Investigation)
    
    # Apply filters
    if instance_id:
        query = query.filter(Investigation.instance_id == instance_id)
    
    if severity:
        query = query.filter(Investigation.alarm_severity.in_(severity))
    
    if from_date:
        query = query.filter(Investigation.started_at >= from_date)
    
    if to_date:
        query = query.filter(Investigation.started_at <= to_date)
    
    if search:
        # Full-text search across alarm description and host
        query = query.filter(
            or_(
                Investigation.alarm_description.ilike(f"%{search}%"),
                Investigation.host_name.ilike(f"%{search}%")
            )
        )
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * limit
    investigations = query.order_by(Investigation.started_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "investigations": investigations,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{investigation_id}", response_model=InvestigationDetail)
async def get_investigation_detail(
    investigation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed investigation with messages and tool calls."""
    investigation = db.query(Investigation).filter_by(id=investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Get messages
    messages = db.query(ChatMessage).filter_by(
        investigation_id=investigation_id
    ).order_by(ChatMessage.timestamp).all()
    
    # Get tool calls
    tool_calls = db.query(ToolCall).filter_by(
        investigation_id=investigation_id
    ).order_by(ToolCall.timestamp).all()
    
    return {
        **investigation.__dict__,
        "messages": messages,
        "tool_calls": [
            {
                "id": str(tc.id),
                "tool_name": tc.tool_name,
                "parameters": tc.parameters,
                "result": tc.result,
                "duration_ms": tc.duration_ms,
                "timestamp": tc.timestamp
            }
            for tc in tool_calls
        ]
    }

@router.delete("/{investigation_id}")
async def delete_investigation(
    investigation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an investigation."""
    investigation = db.query(Investigation).filter_by(id=investigation_id).first()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    db.delete(investigation)
    db.commit()
    
    return {"success": True, "message": "Investigation deleted"}

@router.get("/export/json")
async def export_investigations(
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Export investigations as JSON."""
    query = db.query(Investigation)
    
    if from_date:
        query = query.filter(Investigation.started_at >= from_date)
    if to_date:
        query = query.filter(Investigation.started_at <= to_date)
    
    investigations = query.order_by(Investigation.started_at.desc()).all()
    
    export_data = []
    for inv in investigations:
        messages = db.query(ChatMessage).filter_by(investigation_id=inv.id).all()
        tool_calls = db.query(ToolCall).filter_by(investigation_id=inv.id).all()
        
        export_data.append({
            "id": str(inv.id),
            "started_at": inv.started_at.isoformat(),
            "ended_at": inv.ended_at.isoformat() if inv.ended_at else None,
            "status": inv.status,
            "alarm": {
                "id": inv.alarm_id,
                "description": inv.alarm_description,
                "severity": inv.alarm_severity,
                "host": inv.host_name,
                "instance_id": inv.instance_id
            },
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ],
            "tool_calls": [
                {
                    "tool_name": tc.tool_name,
                    "parameters": tc.parameters,
                    "result": tc.result,
                    "duration_ms": tc.duration_ms,
                    "timestamp": tc.timestamp.isoformat()
                }
                for tc in tool_calls
            ]
        })
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "investigations": export_data
    }
