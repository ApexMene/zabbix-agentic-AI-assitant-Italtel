"""Template management tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any

def template_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get templates from Zabbix.
    
    Args:
        templateids: List of template IDs
        hostids: List of host IDs
        output: Fields to return
    """
    try:
        result = client.template.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def hostgroup_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get host groups.
    
    Args:
        groupids: List of group IDs
        hostids: List of host IDs
    """
    try:
        result = client.hostgroup.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
