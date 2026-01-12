"""Network troubleshooting agent using Strands framework."""
from strands import Agent, tool
from strands.models import BedrockModel
from typing import Dict, Any, List
import httpx
import logging
from config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert network engineer specializing in troubleshooting network infrastructure issues.
You have access to Zabbix monitoring tools to query hosts, problems, metrics, and historical data.

Your role is to:
1. Analyze network alarms and their context
2. Use available Zabbix tools to gather relevant data
3. Identify root causes of network problems
4. Provide clear, actionable remediation steps

Be concise, technical, and focus on practical solutions. Format your responses with:
- **Analysis**: What you found
- **Root Cause**: Why it's happening  
- **Recommended Actions**: Step-by-step fix
- **Escalation**: When to escalate (if needed)
"""

class NetworkTroubleshootAgent:
    """Network troubleshooting agent with Strands and MCP tools."""
    
    def __init__(self, mcp_base_url: str):
        self.mcp_base_url = mcp_base_url
        bedrock_config = config.load_app_config()['bedrock']
        
        # Initialize Bedrock model
        self.model = BedrockModel(
            model_id=bedrock_config['model_id'],
            temperature=bedrock_config.get('temperature', 0.3),
            streaming=True
        )
        
        # Create tools from MCP server
        self.tools = self._create_mcp_tools()
        
        # Create agent
        self.agent = Agent(
            model=self.model,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT
        )
        
        logger.info(f"Strands agent initialized with {len(self.tools)} MCP tools")
    
    def _create_mcp_tools(self) -> List:
        """Create Strands tools from MCP server HTTP API."""
        tools = []
        
        # Define MCP tools as Strands tools
        @tool
        def host_get(instance_id: str, hostids: List[str] = None, search: Dict = None) -> Dict[str, Any]:
            """Get hosts from Zabbix instance.
            
            Args:
                instance_id: Zabbix instance ID
                hostids: List of host IDs to filter
                search: Search criteria dict
            """
            return self._call_mcp_tool("host_get", instance_id, {
                "hostids": hostids,
                "search": search,
                "output": "extend"
            })
        
        @tool
        def problem_get(instance_id: str, hostids: List[str] = None, severities: List[int] = None) -> Dict[str, Any]:
            """Get active problems/alarms from Zabbix.
            
            Args:
                instance_id: Zabbix instance ID
                hostids: List of host IDs
                severities: Severity levels (0-5)
            """
            return self._call_mcp_tool("problem_get", instance_id, {
                "hostids": hostids,
                "severities": severities,
                "recent": True,
                "output": "extend"
            })
        
        @tool
        def item_get(instance_id: str, hostids: List[str] = None, itemids: List[str] = None) -> Dict[str, Any]:
            """Get monitoring items from Zabbix.
            
            Args:
                instance_id: Zabbix instance ID
                hostids: List of host IDs
                itemids: List of item IDs
            """
            return self._call_mcp_tool("item_get", instance_id, {
                "hostids": hostids,
                "itemids": itemids,
                "output": ["itemid", "name", "key_", "lastvalue", "units"],
                "monitored": True
            })
        
        @tool
        def history_get(instance_id: str, itemids: List[str], time_from: int = None, limit: int = 100) -> Dict[str, Any]:
            """Get historical monitoring data.
            
            Args:
                instance_id: Zabbix instance ID
                itemids: List of item IDs
                time_from: Start timestamp
                limit: Max records
            """
            return self._call_mcp_tool("history_get", instance_id, {
                "history": 0,  # Float values
                "itemids": itemids,
                "time_from": time_from,
                "limit": limit,
                "sortorder": "DESC"
            })
        
        @tool
        def trigger_get(instance_id: str, hostids: List[str] = None, triggerids: List[str] = None) -> Dict[str, Any]:
            """Get triggers from Zabbix.
            
            Args:
                instance_id: Zabbix instance ID
                hostids: List of host IDs
                triggerids: List of trigger IDs
            """
            return self._call_mcp_tool("trigger_get", instance_id, {
                "hostids": hostids,
                "triggerids": triggerids,
                "output": "extend",
                "monitored": True
            })
        
        tools = [host_get, problem_get, item_get, history_get, trigger_get]
        return tools
    
    def _call_mcp_tool(self, tool_name: str, instance_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP server tool via HTTP."""
        try:
            # Remove None values from params
            clean_params = {k: v for k, v in params.items() if v is not None}
            
            response = httpx.post(
                f"{self.mcp_base_url}/tools/{tool_name}/invoke",
                json={"instance_id": instance_id, "params": clean_params},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return {"status": "success", "data": result.get('data', [])}
            else:
                return {"status": "error", "error": result.get('error', 'Unknown error')}
        
        except Exception as e:
            logger.error(f"MCP tool call failed: {tool_name} - {e}")
            return {"status": "error", "error": str(e)}
    
    async def investigate(self, alarm: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Investigate an alarm and return response.
        
        Args:
            alarm: Alarm details
            context: Additional context
        
        Returns:
            Full response text
        """
        prompt = f"""Investigate this network alarm:

**Alarm Details:**
- Host: {alarm.get('host')}
- Problem: {alarm.get('description')}
- Severity: {alarm.get('severity')} (Level {alarm.get('severity_code')})
- Duration: {alarm.get('duration')}
- Instance: {alarm.get('instance_name')} ({alarm.get('instance_id')})

**Initial Context:**
{context.get('host_data', 'No host data available')}

Please analyze this alarm using the available Zabbix tools and provide:
1. Root cause analysis
2. Impact assessment  
3. Recommended remediation steps
4. Whether escalation is needed

Use the tools to gather additional information as needed.
"""
        
        # Use Strands agent
        result = self.agent(prompt)
        return result.message["content"][0]["text"]
    
    async def stream_investigate(self, alarm: Dict[str, Any], context: Dict[str, Any]):
        """Stream investigation response.
        
        Yields:
            Response chunks
        """
        prompt = f"""Investigate this network alarm:

**Alarm Details:**
- Host: {alarm.get('host')}
- Problem: {alarm.get('description')}
- Severity: {alarm.get('severity')} (Level {alarm.get('severity_code')})
- Duration: {alarm.get('duration')}
- Instance: {alarm.get('instance_name')} ({alarm.get('instance_id')})

**Initial Context:**
{context.get('host_data', 'No host data available')}

Analyze this alarm using available Zabbix tools and provide root cause analysis and remediation steps.
"""
        
        # Stream response
        async for event in self.agent.stream_async(prompt):
            if "data" in event:
                yield event["data"]

# Global agent instance
_agent = None

def get_agent(mcp_url: str = None) -> NetworkTroubleshootAgent:
    """Get or create global agent instance."""
    global _agent
    if _agent is None:
        if mcp_url is None:
            mcp_url = config.mcp_server_url
        _agent = NetworkTroubleshootAgent(mcp_url)
    return _agent

