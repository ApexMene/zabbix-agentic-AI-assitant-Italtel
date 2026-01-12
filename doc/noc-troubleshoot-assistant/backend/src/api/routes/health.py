"""Health check routes."""
from fastapi import APIRouter
from models import check_connection
from services import alarm_aggregator
from config import config
import httpx

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check database
    db_status = "connected" if check_connection() else "disconnected"
    
    # Check MCP server
    mcp_status = "disconnected"
    try:
        mcp_url = config.mcp_server_url
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{mcp_url}/health")
            if response.status_code == 200:
                mcp_status = "connected"
    except:
        pass
    
    # Overall status
    is_healthy = db_status == "connected" and mcp_status == "connected"
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "services": {
            "database": db_status,
            "mcp_server": mcp_status
        },
        "alarm_stats": alarm_aggregator.get_stats()
    }
