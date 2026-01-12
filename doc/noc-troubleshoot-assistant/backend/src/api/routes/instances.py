"""Instance management routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from api.dependencies import get_mcp_client
from services import MCPClient
from schemas import InstanceStatus

router = APIRouter()

@router.get("", response_model=List[InstanceStatus])
async def list_instances(mcp_client: MCPClient = Depends(get_mcp_client)):
    """List all Zabbix instances with status."""
    try:
        instances = await mcp_client.get_instances()
        return instances
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get instances: {str(e)}")

@router.get("/{instance_id}/status", response_model=InstanceStatus)
async def get_instance_status(instance_id: str, mcp_client: MCPClient = Depends(get_mcp_client)):
    """Get status for specific instance."""
    try:
        status = await mcp_client.check_instance_status(instance_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check instance: {str(e)}")
