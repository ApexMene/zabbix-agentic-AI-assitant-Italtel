"""Maintenance window tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any, List

def maintenance_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get maintenance windows.
    
    Args:
        maintenanceids: List of maintenance IDs
        hostids: List of host IDs
    """
    try:
        result = client.maintenance.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def maintenance_create(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Create maintenance window.
    
    Args:
        name: Maintenance name
        active_since: Start timestamp
        active_till: End timestamp
        hostids: List of host IDs
        timeperiods: Time period definitions
    """
    try:
        result = client.maintenance.create(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def maintenance_update(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Update maintenance window."""
    try:
        result = client.maintenance.update(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def maintenance_delete(client: ZabbixAPI, maintenanceids: List[str]) -> Dict[str, Any]:
    """Delete maintenance windows."""
    try:
        result = client.maintenance.delete(maintenanceids)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
