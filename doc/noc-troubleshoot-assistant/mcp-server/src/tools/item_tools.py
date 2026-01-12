"""Item and history data tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any, List

def item_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get items from Zabbix.
    
    Args:
        itemids: List of item IDs
        hostids: List of host IDs
        monitored: Only monitored items
    """
    try:
        result = client.item.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def history_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get historical data.
    
    Args:
        history: Value type (0=float, 1=string, 2=log, 3=int, 4=text)
        itemids: List of item IDs
        time_from: Start timestamp
        time_till: End timestamp
        limit: Max records
    """
    try:
        result = client.history.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def trend_get(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Get trend data (hourly aggregates).
    
    Args:
        itemids: List of item IDs
        time_from: Start timestamp
        time_till: End timestamp
    """
    try:
        result = client.trend.get(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
