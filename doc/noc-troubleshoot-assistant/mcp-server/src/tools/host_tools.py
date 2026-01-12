"""Host management tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any, List, Optional

def host_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get hosts from Zabbix.
    
    Args:
        hostids: List of host IDs
        groupids: List of host group IDs
        output: Fields to return (default: extend)
        search: Search criteria
        filter: Filter criteria
    """
    try:
        result = client.host.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def host_create(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Create a new host.
    
    Args:
        host: Technical name
        name: Visible name
        groups: List of host group IDs
        interfaces: Network interfaces
    """
    try:
        result = client.host.create(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def host_update(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Update existing host.
    
    Args:
        hostid: Host ID to update
        (other host properties to update)
    """
    try:
        result = client.host.update(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def host_delete(client: ZabbixAPI, hostids: List[str]) -> Dict[str, Any]:
    """Delete hosts.
    
    Args:
        hostids: List of host IDs to delete
    """
    try:
        result = client.host.delete(hostids)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
