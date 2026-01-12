"""Configuration export/import tools."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Any

def configuration_export(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Export Zabbix configuration.
    
    Args:
        options: Export options (hosts, templates, etc.)
        format: Export format (json, xml)
    """
    try:
        result = client.configuration.export(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def configuration_import(client: ZabbixAPI, **params) -> Dict[str, Any]:
    """Import Zabbix configuration.
    
    Args:
        format: Import format (json, xml)
        source: Configuration data
        rules: Import rules
    """
    try:
        result = client.configuration.import_(**params)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def apiinfo_version(client: ZabbixAPI) -> Dict[str, Any]:
    """Get Zabbix API version."""
    try:
        result = client.apiinfo.version()
        return {"success": True, "data": {"version": result}}
    except Exception as e:
        return {"success": False, "error": str(e)}
