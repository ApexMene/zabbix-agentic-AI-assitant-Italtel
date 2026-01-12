"""Integration tests for backend API."""
import pytest
import requests
import time

BACKEND_URL = "http://localhost:13001"

def test_backend_health():
    """Test backend health endpoint."""
    response = requests.get(f"{BACKEND_URL}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert data["services"]["database"] == "connected"

def test_list_instances():
    """Test listing Zabbix instances."""
    response = requests.get(f"{BACKEND_URL}/api/instances")
    assert response.status_code == 200
    
    instances = response.json()
    assert len(instances) == 2
    assert instances[0]["id"] in ["zabbix-backbone", "zabbix-5gcore"]
    assert instances[0]["status"] == "connected"

def test_get_alarms():
    """Test getting all alarms."""
    response = requests.get(f"{BACKEND_URL}/api/alarms")
    assert response.status_code == 200
    
    alarms = response.json()
    assert isinstance(alarms, list)
    
    if len(alarms) > 0:
        alarm = alarms[0]
        assert "id" in alarm
        assert "instance_id" in alarm
        assert "severity" in alarm
        assert "host" in alarm

def test_filter_alarms_by_instance():
    """Test filtering alarms by instance."""
    response = requests.get(f"{BACKEND_URL}/api/alarms?instance_id=zabbix-backbone")
    assert response.status_code == 200
    
    alarms = response.json()
    for alarm in alarms:
        assert alarm["instance_id"] == "zabbix-backbone"

def test_filter_alarms_by_severity():
    """Test filtering alarms by severity."""
    response = requests.get(f"{BACKEND_URL}/api/alarms?severity=average&severity=high")
    assert response.status_code == 200
    
    alarms = response.json()
    for alarm in alarms:
        assert alarm["severity"] in ["average", "high"]

def test_get_alarm_stats():
    """Test getting alarm statistics."""
    response = requests.get(f"{BACKEND_URL}/api/alarms/stats")
    assert response.status_code == 200
    
    stats = response.json()
    assert "total" in stats
    assert "by_severity" in stats
    assert "last_poll" in stats

def test_alarm_polling_updates():
    """Test that alarm polling updates data."""
    # Get initial stats
    response1 = requests.get(f"{BACKEND_URL}/api/alarms/stats")
    stats1 = response1.json()
    last_poll1 = stats1["last_poll"]
    
    # Wait for next poll cycle (30s + buffer)
    time.sleep(35)
    
    # Get updated stats
    response2 = requests.get(f"{BACKEND_URL}/api/alarms/stats")
    stats2 = response2.json()
    last_poll2 = stats2["last_poll"]
    
    # Verify polling happened
    assert last_poll2 is not None
    if last_poll1:
        assert last_poll2 > last_poll1

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
