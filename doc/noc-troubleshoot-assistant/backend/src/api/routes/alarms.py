"""Alarm management routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from api.dependencies import get_mcp_client
from services import MCPClient, alarm_aggregator
from schemas import Alarm, AlarmAcknowledge

router = APIRouter()

@router.get("", response_model=List[Alarm])
async def get_alarms(
    instance_id: Optional[str] = Query(None, description="Filter by instance ID"),
    severity: Optional[List[str]] = Query(None, description="Filter by severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    host: Optional[str] = Query(None, description="Filter by host name")
):
    """Get all alarms from all instances."""
    alarms = alarm_aggregator.get_all_alarms()
    
    # Apply filters
    if instance_id:
        alarms = [a for a in alarms if a['instance_id'] == instance_id]
    
    if severity:
        alarms = [a for a in alarms if a['severity'] in severity]
    
    if acknowledged is not None:
        alarms = [a for a in alarms if a['acknowledged'] == acknowledged]
    
    if host:
        host_lower = host.lower()
        alarms = [a for a in alarms if host_lower in a['host'].lower()]
    
    return alarms

@router.post("/{alarm_id}/acknowledge")
async def acknowledge_alarm(
    alarm_id: str,
    ack_data: AlarmAcknowledge,
    mcp_client: MCPClient = Depends(get_mcp_client)
):
    """Acknowledge an alarm."""
    try:
        # Get alarm details
        alarm = alarm_aggregator.get_alarm_by_id(alarm_id, ack_data.instance_id)
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")
        
        # Cannot acknowledge synthetic alarms
        if alarm.get('is_synthetic'):
            raise HTTPException(status_code=400, detail="Cannot acknowledge synthetic alarms")
        
        # Acknowledge via MCP
        result = await mcp_client.acknowledge_event(
            ack_data.instance_id,
            [alarm_id],
            ack_data.message
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Acknowledgment failed'))
        
        return {
            "success": True,
            "message": "Alarm acknowledged successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alarm: {str(e)}")

@router.get("/stats")
async def get_alarm_stats():
    """Get alarm statistics."""
    return alarm_aggregator.get_stats()
