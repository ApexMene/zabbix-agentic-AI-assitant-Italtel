"""FastAPI dependencies."""
from fastapi import HTTPException
from services import MCPClient

# Global MCP client (initialized in main.py lifespan)
_mcp_client: MCPClient = None

def set_mcp_client(client: MCPClient):
    """Set global MCP client."""
    global _mcp_client
    _mcp_client = client

def get_mcp_client() -> MCPClient:
    """Get MCP client dependency."""
    if _mcp_client is None:
        raise HTTPException(status_code=503, detail="MCP client not initialized")
    return _mcp_client
