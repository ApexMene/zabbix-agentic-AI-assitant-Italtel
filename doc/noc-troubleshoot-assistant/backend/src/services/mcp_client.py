"""MCP client for communicating with MCP server."""
import httpx
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for MCP server communication."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def get_instances(self) -> List[Dict[str, Any]]:
        """Get all Zabbix instances with status."""
        try:
            response = await self.client.get(f"{self.base_url}/instances")
            response.raise_for_status()
            data = response.json()
            return data.get("instances", [])
        except Exception as e:
            logger.error(f"Failed to get instances: {e}")
            raise
    
    async def check_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Check specific instance status."""
        try:
            response = await self.client.get(f"{self.base_url}/instances/{instance_id}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to check instance {instance_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def invoke_tool(self, tool_name: str, instance_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke MCP tool."""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}/invoke",
                json={"instance_id": instance_id, "params": params}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to invoke {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_hosts(self, instance_id: str, **params) -> Dict[str, Any]:
        """Get hosts from Zabbix instance."""
        return await self.invoke_tool("host_get", instance_id, params)
    
    async def get_problems(self, instance_id: str, **params) -> Dict[str, Any]:
        """Get problems from Zabbix instance."""
        return await self.invoke_tool("problem_get", instance_id, params)
    
    async def acknowledge_event(self, instance_id: str, event_ids: List[str], message: str = "") -> Dict[str, Any]:
        """Acknowledge Zabbix events."""
        return await self.invoke_tool("event_acknowledge", instance_id, {
            "eventids": event_ids,
            "message": message
        })
    
    async def get_items(self, instance_id: str, **params) -> Dict[str, Any]:
        """Get items from Zabbix instance."""
        return await self.invoke_tool("item_get", instance_id, params)
    
    async def get_history(self, instance_id: str, **params) -> Dict[str, Any]:
        """Get historical data from Zabbix instance."""
        return await self.invoke_tool("history_get", instance_id, params)
    
    async def get_triggers(self, instance_id: str, **params) -> Dict[str, Any]:
        """Get triggers from Zabbix instance."""
        return await self.invoke_tool("trigger_get", instance_id, params)
