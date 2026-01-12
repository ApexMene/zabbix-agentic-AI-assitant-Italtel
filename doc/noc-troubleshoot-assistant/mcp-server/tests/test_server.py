"""Integration tests for Flask MCP server."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import main

@pytest.fixture
def client():
    """Create Flask test client."""
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

@pytest.fixture
def mock_zabbix_client():
    """Mock Zabbix client."""
    mock = Mock()
    mock.apiinfo.version.return_value = "7.0.0"
    mock.host.get.return_value = [{"hostid": "10001", "name": "test-host"}]
    mock.problem.get.return_value = [{"eventid": "123", "severity": "4"}]
    return mock

def test_health_endpoint(client):
    """Test health check endpoint."""
    with patch('main.get_client_manager') as mock_get_manager:
        mock_manager = Mock()
        mock_manager.get_all_status.return_value = [
            {"id": "test-1", "status": "connected", "version": "7.0.0"}
        ]
        mock_get_manager.return_value = mock_manager
        
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] in ["healthy", "degraded"]
        assert "zabbix_instances" in data

def test_list_tools_endpoint(client):
    """Test list tools endpoint."""
    response = client.get('/tools')
    
    assert response.status_code == 200
    data = response.get_json()
    assert "tools" in data
    assert len(data["tools"]) > 0
    assert data["tools"][0]["name"] == "host_get"

def test_invoke_tool_success(client, mock_zabbix_client):
    """Test successful tool invocation."""
    with patch('main.get_client_manager') as mock_get_manager:
        mock_manager = Mock()
        mock_manager.get_client.return_value = mock_zabbix_client
        mock_get_manager.return_value = mock_manager
        
        response = client.post('/tools/host_get/invoke', json={
            "instance_id": "test-instance",
            "params": {"hostids": ["10001"]}
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 1

def test_invoke_tool_missing_instance_id(client):
    """Test tool invocation without instance_id."""
    response = client.post('/tools/host_get/invoke', json={
        "params": {}
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "instance_id required" in data["error"]

def test_invoke_tool_not_found(client):
    """Test invoking non-existent tool."""
    response = client.post('/tools/nonexistent/invoke', json={
        "instance_id": "test-instance",
        "params": {}
    })
    
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False

def test_invoke_tool_connection_error(client):
    """Test tool invocation with connection error."""
    with patch('main.get_client_manager') as mock_get_manager:
        mock_manager = Mock()
        mock_manager.get_client.side_effect = Exception("Connection failed")
        mock_get_manager.return_value = mock_manager
        
        response = client.post('/tools/host_get/invoke', json={
            "instance_id": "test-instance",
            "params": {}
        })
        
        assert response.status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert "Connection failed" in data["error"]

def test_list_instances_endpoint(client):
    """Test list instances endpoint."""
    with patch('main.get_client_manager') as mock_get_manager:
        mock_manager = Mock()
        mock_manager.get_all_status.return_value = [
            {"id": "test-1", "name": "Test 1", "status": "connected"}
        ]
        mock_get_manager.return_value = mock_manager
        
        response = client.get('/instances')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "instances" in data
        assert len(data["instances"]) == 1

def test_instance_status_endpoint(client):
    """Test instance status endpoint."""
    with patch('main.get_client_manager') as mock_get_manager:
        mock_manager = Mock()
        mock_manager.check_connection.return_value = {
            "status": "connected",
            "version": "7.0.0",
            "instance_id": "test-1"
        }
        mock_get_manager.return_value = mock_manager
        
        response = client.get('/instances/test-1/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "connected"
        assert data["version"] == "7.0.0"
