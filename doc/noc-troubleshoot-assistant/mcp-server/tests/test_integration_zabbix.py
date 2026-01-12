"""Integration tests with real Zabbix instances."""
import pytest
import requests
import time

MCP_BASE_URL = "http://localhost:13002"

def test_mcp_server_health():
    """Test MCP server is healthy and connected to Zabbix."""
    response = requests.get(f"{MCP_BASE_URL}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["zabbix_instances"]) == 2
    
    # Check both instances are connected
    for instance in data["zabbix_instances"]:
        assert instance["status"] == "connected"
        assert "version" in instance
        assert instance["version"].startswith("7.")

def test_list_tools():
    """Test listing available tools."""
    response = requests.get(f"{MCP_BASE_URL}/tools")
    assert response.status_code == 200
    
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 9
    
    tool_names = [t["name"] for t in data["tools"]]
    assert "host_get" in tool_names
    assert "problem_get" in tool_names
    assert "event_acknowledge" in tool_names

def test_get_hosts_from_backbone():
    """Test retrieving hosts from backbone instance."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/host_get/invoke",
        json={
            "instance_id": "zabbix-backbone",
            "params": {"output": ["hostid", "host", "name"], "limit": 5}
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    
    # Verify host structure
    first_host = data["data"][0]
    assert "hostid" in first_host
    assert "host" in first_host
    assert "name" in first_host

def test_get_hosts_from_5gcore():
    """Test retrieving hosts from 5G core instance."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/host_get/invoke",
        json={
            "instance_id": "zabbix-5gcore",
            "params": {"output": ["hostid", "host"], "limit": 5}
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    
    # Check for Open5GS hosts
    host_names = [h["host"] for h in data["data"]]
    assert any("open5gs" in name for name in host_names)

def test_get_problems():
    """Test retrieving active problems."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/problem_get/invoke",
        json={
            "instance_id": "zabbix-backbone",
            "params": {"recent": True, "output": "extend"}
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    # May or may not have problems, just check structure
    if len(data["data"]) > 0:
        problem = data["data"][0]
        assert "eventid" in problem
        assert "severity" in problem
        assert "name" in problem

def test_get_api_version():
    """Test getting API version."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/apiinfo_version/invoke",
        json={
            "instance_id": "zabbix-backbone",
            "params": {}
        }
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "version" in data["data"]
    assert data["data"]["version"].startswith("7.")

def test_invalid_instance_id():
    """Test error handling for invalid instance."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/host_get/invoke",
        json={
            "instance_id": "nonexistent",
            "params": {}
        }
    )
    assert response.status_code == 500
    
    data = response.json()
    assert data["success"] is False
    assert "error" in data

def test_missing_instance_id():
    """Test error handling for missing instance_id."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/host_get/invoke",
        json={"params": {}}
    )
    assert response.status_code == 400
    
    data = response.json()
    assert data["success"] is False
    assert "instance_id required" in data["error"]

def test_invalid_tool_name():
    """Test error handling for invalid tool."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/nonexistent_tool/invoke",
        json={
            "instance_id": "zabbix-backbone",
            "params": {}
        }
    )
    assert response.status_code == 404
    
    data = response.json()
    assert data["success"] is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
