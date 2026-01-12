"""Chat and investigation routes with two-step approach."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID, UUID as parse_uuid
import json
import logging

from models import get_db, SessionLocal
from schemas import InvestigateRequest, ChatMessageCreate, ChatMessageResponse
from services.bedrock_agent import get_agent
from services.investigation_service import InvestigationService
from services import alarm_aggregator
from api.dependencies import get_mcp_client
from config import config

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/investigation/create")
async def create_investigation(
    request: InvestigateRequest,
    db: Session = Depends(get_db)
):
    """Create a new investigation for an alarm."""
    try:
        # Get alarm details
        alarm = alarm_aggregator.get_alarm_by_id(request.alarm_id, request.instance_id)
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")
        
        # Create investigation
        inv_service = InvestigationService(db)
        investigation_id_str = inv_service.create_investigation(alarm)
        
        # Add system message
        inv_service.add_message(
            parse_uuid(investigation_id_str), 
            "system", 
            f"Starting investigation for: {alarm['description']}"
        )
        
        db.commit()
        
        return {
            "investigation_id": investigation_id_str,
            "alarm": alarm
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create investigation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investigation/{investigation_id}/stream")
async def stream_investigation(
    investigation_id: str,
    mcp_client = Depends(get_mcp_client),
    db: Session = Depends(get_db)
):
    """Stream AI investigation response."""
    try:
        # Get investigation
        inv_service = InvestigationService(db)
        investigation = inv_service.get_investigation(parse_uuid(investigation_id))
        if not investigation:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        # Build alarm dict from investigation
        alarm = {
            "id": investigation.alarm_id,
            "description": investigation.alarm_description,
            "severity": investigation.alarm_severity,
            "host": investigation.host_name,
            "instance_id": investigation.instance_id,
        }
        
        # Build context
        context = await _build_context(alarm, mcp_client)
        
        # Get agent
        mcp_url = config.mcp_server_url
        agent = get_agent(mcp_url)
        
        # Stream response
        async def generate():
            try:
                logger.info(f"Streaming investigation {investigation_id}")
                
                full_response = ""
                async for chunk in agent.stream_investigate(alarm, context):
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'content', 'text': chunk})}\n\n"
                
                # Save response
                db2 = SessionLocal()
                try:
                    inv_service2 = InvestigationService(db2)
                    inv_service2.add_message(parse_uuid(investigation_id), "assistant", full_response)
                    db2.commit()
                finally:
                    db2.close()
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                import traceback
                logger.error(f"Stream error: {e}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{investigation_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    investigation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get chat history for investigation."""
    inv_service = InvestigationService(db)
    messages = inv_service.get_messages(investigation_id)
    return messages

async def _build_context(alarm: Dict[str, Any], mcp_client) -> Dict[str, Any]:
    """Build investigation context from Zabbix data."""
    context = {"alarm": alarm}
    
    try:
        # Get host information
        host_result = await mcp_client.get_hosts(
            alarm['instance_id'],
            search={"name": alarm['host']},
            output="extend"
        )
        
        if host_result.get('success') and host_result.get('data'):
            context['host_data'] = host_result['data'][0] if host_result['data'] else None
    
    except Exception as e:
        logger.error(f"Failed to build context: {e}")
    
    return context
