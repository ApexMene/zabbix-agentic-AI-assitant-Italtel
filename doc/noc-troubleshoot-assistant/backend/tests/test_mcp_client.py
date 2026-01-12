"""Unit tests for MCP client."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.mcp_client import MCPClient

@pytest.fixture
def mcp_client():
    """Create MCP client."""
    return MCPClient("http://localhost:13002")

@pytest.mark.asyncio
async def test_get_instances(mcp_client):
    """Test getting instances."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "instances": [
            {"id": "test-1", "name": "Test 1", "status": "connected"}
        ]
    }
    
    with patch.object(mcp_client.client, 'get', return_value=mock_response):
        instances = await mcp_client.get_instances()
        
        assert len(instances) == 1
        assert instances[0]['id'] == 'test-1'

@pytest.mark.asyncio
async def test_invoke_tool(mcp_client):
    """Test invoking tool."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": [{"hostid": "10001"}]
    }
    
    with patch.object(mcp_client.client, 'post', return_value=mock_response):
        result = await mcp_client.invoke_tool("host_get", "test-instance", {"output": "extend"})
        
        assert result['success'] is True
        assert len(result['data']) == 1

@pytest.mark.asyncio
async def test_get_hosts(mcp_client):
    """Test get_hosts convenience method."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": [{"hostid": "10001", "name": "server-01"}]
    }
    
    with patch.object(mcp_client.client, 'post', return_value=mock_response):
        result = await mcp_client.get_hosts("test-instance", output="extend")
        
        assert result['success'] is True
        assert result['data'][0]['name'] == 'server-01'

@pytest.mark.asyncio
async def test_get_problems(mcp_client):
    """Test get_problems convenience method."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": [{"eventid": "123", "severity": "4"}]
    }
    
    with patch.object(mcp_client.client, 'post', return_value=mock_response):
        result = await mcp_client.get_problems("test-instance", recent=True)
        
        assert result['success'] is True
        assert result['data'][0]['severity'] == '4'

@pytest.mark.asyncio
async def test_acknowledge_event(mcp_client):
    """Test acknowledge_event convenience method."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"eventids": ["123"]}
    }
    
    with patch.object(mcp_client.client, 'post', return_value=mock_response):
        result = await mcp_client.acknowledge_event("test-instance", ["123"], "Investigating")
        
        assert result['success'] is True
