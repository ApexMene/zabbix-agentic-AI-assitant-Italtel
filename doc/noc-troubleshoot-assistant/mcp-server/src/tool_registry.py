"""MCP tool registry and definitions."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from tools import host_tools, problem_tools, trigger_tools, item_tools, template_tools, maintenance_tools, system_tools

# Tool registry mapping tool names to functions
TOOL_HANDLERS = {
    # Host management
    "host_get": host_tools.host_get,
    "host_create": host_tools.host_create,
    "host_update": host_tools.host_update,
    "host_delete": host_tools.host_delete,
    
    # Problems and events
    "problem_get": problem_tools.problem_get,
    "event_get": problem_tools.event_get,
    "event_acknowledge": problem_tools.event_acknowledge,
    
    # Triggers
    "trigger_get": trigger_tools.trigger_get,
    "trigger_create": trigger_tools.trigger_create,
    "trigger_update": trigger_tools.trigger_update,
    "trigger_delete": trigger_tools.trigger_delete,
    
    # Items and history
    "item_get": item_tools.item_get,
    "history_get": item_tools.history_get,
    "trend_get": item_tools.trend_get,
    
    # Templates and groups
    "template_get": template_tools.template_get,
    "hostgroup_get": template_tools.hostgroup_get,
    
    # Maintenance
    "maintenance_get": maintenance_tools.maintenance_get,
    "maintenance_create": maintenance_tools.maintenance_create,
    "maintenance_update": maintenance_tools.maintenance_update,
    "maintenance_delete": maintenance_tools.maintenance_delete,
    
    # System
    "apiinfo_version": system_tools.apiinfo_version,
    "configuration_export": system_tools.configuration_export,
    "configuration_import": system_tools.configuration_import,
}

# Tool definitions for MCP protocol
TOOL_DEFINITIONS = [
    {
        "name": "host_get",
        "description": "Get hosts from Zabbix with optional filters",
        "parameters": {
            "hostids": {"type": "array", "description": "List of host IDs"},
            "groupids": {"type": "array", "description": "List of host group IDs"},
            "output": {"type": "string", "description": "Fields to return"},
            "search": {"type": "object", "description": "Search criteria"},
        }
    },
    {
        "name": "problem_get",
        "description": "Get active problems/alarms from Zabbix",
        "parameters": {
            "hostids": {"type": "array", "description": "List of host IDs"},
            "severities": {"type": "array", "description": "Severity levels (0-5)"},
            "recent": {"type": "boolean", "description": "Only recent problems"},
        }
    },
    {
        "name": "event_acknowledge",
        "description": "Acknowledge Zabbix events/alarms",
        "parameters": {
            "eventids": {"type": "array", "description": "List of event IDs", "required": True},
            "message": {"type": "string", "description": "Acknowledgment message"},
        }
    },
    {
        "name": "trigger_get",
        "description": "Get triggers from Zabbix",
        "parameters": {
            "triggerids": {"type": "array", "description": "List of trigger IDs"},
            "hostids": {"type": "array", "description": "List of host IDs"},
        }
    },
    {
        "name": "item_get",
        "description": "Get monitoring items from Zabbix",
        "parameters": {
            "itemids": {"type": "array", "description": "List of item IDs"},
            "hostids": {"type": "array", "description": "List of host IDs"},
        }
    },
    {
        "name": "history_get",
        "description": "Get historical monitoring data",
        "parameters": {
            "history": {"type": "integer", "description": "Value type (0-4)"},
            "itemids": {"type": "array", "description": "List of item IDs"},
            "time_from": {"type": "integer", "description": "Start timestamp"},
            "time_till": {"type": "integer", "description": "End timestamp"},
        }
    },
    {
        "name": "template_get",
        "description": "Get templates from Zabbix",
        "parameters": {
            "templateids": {"type": "array", "description": "List of template IDs"},
        }
    },
    {
        "name": "maintenance_get",
        "description": "Get maintenance windows",
        "parameters": {
            "maintenanceids": {"type": "array", "description": "List of maintenance IDs"},
        }
    },
    {
        "name": "apiinfo_version",
        "description": "Get Zabbix API version",
        "parameters": {}
    },
]
