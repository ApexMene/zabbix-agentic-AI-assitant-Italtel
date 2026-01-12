"""Unit tests for Zabbix client manager."""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_config():
    """Mock configuration."""
    return [
        {
            "id": "test-instance-1",
            "name": "Test Instance 1",
            "url": "http://test1.local/api",
            "username": "admin",
            "password": "password1",
            "timeout": 30,
            "enabled": True
        },
        {
            "id": "test-instance-2",
            "name": "Test Instance 2",
            "url": "http://test2.local/api",
            "username": "admin",
            "password": "password2",
            "timeout": 30,
            "enabled": True
        }
    ]

@pytest.fixture
def client_manager(mock_config):
    """Create client manager with mocked config."""
    mock_config_loader = Mock()
    mock_config_loader.load_instances.return_value = mock_config
    mock_config_loader.get_instance.side_effect = lambda id: next(
        (inst for inst in mock_config if inst['id'] == id),
        None
    ) or (_ for _ in ()).throw(ValueError(f"Instance not found: {id}"))
    
    from zabbix_client import ZabbixClientManager
    manager = ZabbixClientManager(config_loader=mock_config_loader)
    return manager

def test_client_manager_initialization(client_manager):
    """Test client manager initializes correctly."""
    assert client_manager.clients == {}
    assert client_manager.instances_config is None  # Lazy loaded
    config = client_manager._load_config()
    assert len(config) == 2

@patch('zabbix_client.ZabbixAPI')
def test_get_client_creates_new_connection(mock_zabbix_api, client_manager):
    """Test getting client creates new connection."""
    mock_client = Mock()
    mock_zabbix_api.return_value = mock_client
    
    client = client_manager.get_client("test-instance-1")
    
    assert client == mock_client
    mock_zabbix_api.assert_called_once_with(url="http://test1.local/api", timeout=30)
    mock_client.login.assert_called_once_with(user="admin", password="password1")

@patch('zabbix_client.ZabbixAPI')
def test_get_client_reuses_existing_connection(mock_zabbix_api, client_manager):
    """Test getting client reuses existing connection."""
    mock_client = Mock()
    mock_zabbix_api.return_value = mock_client
    
    client1 = client_manager.get_client("test-instance-1")
    client2 = client_manager.get_client("test-instance-1")
    
    assert client1 == client2
    assert mock_zabbix_api.call_count == 1  # Only called once

@patch('zabbix_client.ZabbixAPI')
def test_check_connection_success(mock_zabbix_api, client_manager):
    """Test successful connection check."""
    mock_client = Mock()
    mock_client.apiinfo.version.return_value = "7.0.0"
    mock_zabbix_api.return_value = mock_client
    
    status = client_manager.check_connection("test-instance-1")
    
    assert status["status"] == "connected"
    assert status["version"] == "7.0.0"
    assert status["instance_id"] == "test-instance-1"

@patch('zabbix_client.ZabbixAPI')
def test_check_connection_failure(mock_zabbix_api, client_manager):
    """Test failed connection check."""
    mock_zabbix_api.side_effect = Exception("Connection refused")
    
    status = client_manager.check_connection("test-instance-1")
    
    assert status["status"] == "error"
    assert "Connection refused" in status["error"]

@patch('zabbix_client.ZabbixAPI')
def test_get_all_status(mock_zabbix_api, client_manager):
    """Test getting status for all instances."""
    mock_client = Mock()
    mock_client.apiinfo.version.return_value = "7.0.0"
    mock_zabbix_api.return_value = mock_client
    
    statuses = client_manager.get_all_status()
    
    assert len(statuses) == 2
    assert statuses[0]["id"] == "test-instance-1"
    assert statuses[1]["id"] == "test-instance-2"

@patch('zabbix_client.ZabbixAPI')
def test_disconnect(mock_zabbix_api, client_manager):
    """Test disconnecting from instance."""
    mock_client = Mock()
    mock_zabbix_api.return_value = mock_client
    
    # Connect first
    client_manager.get_client("test-instance-1")
    assert "test-instance-1" in client_manager.clients
    
    # Disconnect
    client_manager.disconnect("test-instance-1")
    assert "test-instance-1" not in client_manager.clients
    mock_client.logout.assert_called_once()

@patch('zabbix_client.ZabbixAPI')
def test_disconnect_all(mock_zabbix_api, client_manager):
    """Test disconnecting from all instances."""
    mock_client = Mock()
    mock_zabbix_api.return_value = mock_client
    
    # Connect to both
    client_manager.get_client("test-instance-1")
    client_manager.get_client("test-instance-2")
    assert len(client_manager.clients) == 2
    
    # Disconnect all
    client_manager.disconnect_all()
    assert len(client_manager.clients) == 0
