"""Trigger management tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any, List

def trigger_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get triggers from Zabbix.
    
    Args:
        triggerids: List of trigger IDs
        hostids: List of host IDs
        monitored: Only monitored triggers
        active: Only active triggers
    """
    try:
        result = client.trigger.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def trigger_create(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Create a new trigger.
    
    Args:
        description: Trigger description
        expression: Trigger expression
        priority: Severity (0-5)
    """
    try:
        result = client.trigger.create(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def trigger_update(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Update existing trigger.
    
    Args:
        triggerid: Trigger ID
        (other properties to update)
    """
    try:
        result = client.trigger.update(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def trigger_delete(client: ZabbixAPI, triggerids: List[str]) -> Dict[str, Any]:
    """Delete triggers.
    
    Args:
        triggerids: List of trigger IDs
    """
    try:
        result = client.trigger.delete(triggerids)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
