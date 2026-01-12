"""Problem and event management tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any, List

def problem_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get problems from Zabbix.
    
    Args:
        hostids: List of host IDs
        severities: List of severity levels (0-5)
        recent: Get only recent problems
        suppressed: Include suppressed problems
        acknowledged: Filter by acknowledgment status
    """
    try:
        result = client.problem.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def event_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get events from Zabbix.
    
    Args:
        eventids: List of event IDs
        hostids: List of host IDs
        time_from: Start timestamp
        time_till: End timestamp
    """
    try:
        result = client.event.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def event_acknowledge(client: ZabbixAPI, eventids: List[str], message: str = "", action: int = 6) -> Dict[str, Any]:
    """Acknowledge events.
    
    Args:
        eventids: List of event IDs to acknowledge
        message: Acknowledgment message
        action: Action flags (6 = acknowledge + close)
    """
    try:
        result = client.event.acknowledge(eventids=eventids, message=message, action=action)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
