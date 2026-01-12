"""Unit tests for MCP tool handlers."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools import host_tools, problem_tools, trigger_tools, item_tools

@pytest.fixture
def mock_client():
    """Create mock Zabbix client."""
    return Mock()

# Host tools tests
def test_host_get_success(mock_client):
    """Test successful host_get."""
    mock_client.host.get.return_value = [{"hostid": "10001", "name": "server-01"}]
    
    result = host_tools.host_get(mock_client, hostids=["10001"])
    
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["name"] == "server-01"

def test_host_get_error(mock_client):
    """Test host_get with error."""
    mock_client.host.get.side_effect = Exception("API error")
    
    result = host_tools.host_get(mock_client)
    
    assert result["success"] is False
    assert "API error" in result["error"]

def test_host_create_success(mock_client):
    """Test successful host creation."""
    mock_client.host.create.return_value = {"hostids": ["10002"]}
    
    result = host_tools.host_create(
        mock_client,
        host="new-server",
        name="New Server",
        groups=[{"groupid": "2"}]
    )
    
    assert result["success"] is True
    assert "10002" in result["data"]["hostids"]

# Problem tools tests
def test_problem_get_success(mock_client):
    """Test successful problem_get."""
    mock_client.problem.get.return_value = [
        {"eventid": "123", "severity": "4", "name": "High CPU"}
    ]
    
    result = problem_tools.problem_get(mock_client, severities=[4, 5])
    
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["severity"] == "4"

def test_event_acknowledge_success(mock_client):
    """Test successful event acknowledgment."""
    mock_client.event.acknowledge.return_value = {"eventids": ["123"]}
    
    result = problem_tools.event_acknowledge(
        mock_client,
        eventids=["123"],
        message="Investigating"
    )
    
    assert result["success"] is True
    mock_client.event.acknowledge.assert_called_once()

# Trigger tools tests
def test_trigger_get_success(mock_client):
    """Test successful trigger_get."""
    mock_client.trigger.get.return_value = [
        {"triggerid": "456", "description": "CPU too high"}
    ]
    
    result = trigger_tools.trigger_get(mock_client, hostids=["10001"])
    
    assert result["success"] is True
    assert len(result["data"]) == 1

# Item tools tests
def test_item_get_success(mock_client):
    """Test successful item_get."""
    mock_client.item.get.return_value = [
        {"itemid": "789", "name": "CPU usage", "key_": "system.cpu.util"}
    ]
    
    result = item_tools.item_get(mock_client, hostids=["10001"])
    
    assert result["success"] is True
    assert result["data"][0]["name"] == "CPU usage"

def test_history_get_success(mock_client):
    """Test successful history_get."""
    mock_client.history.get.return_value = [
        {"itemid": "789", "clock": "1234567890", "value": "85.5"}
    ]
    
    result = item_tools.history_get(
        mock_client,
        history=0,
        itemids=["789"],
        limit=100
    )
    
    assert result["success"] is True
    assert len(result["data"]) == 1
