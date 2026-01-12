"""Unit tests for alarm aggregator."""
import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.alarm_aggregator import AlarmAggregator

@pytest.fixture
def aggregator():
    """Create fresh alarm aggregator."""
    return AlarmAggregator()

@pytest.fixture
def sample_alarms():
    """Sample alarm data."""
    return [
        {
            "id": "1",
            "instance_id": "zabbix-1",
            "instance_name": "Test Instance",
            "host": "server-01",
            "description": "High CPU",
            "severity": "high",
            "severity_code": 4,
            "duration": "5m",
            "acknowledged": False,
            "event_id": "1",
            "is_synthetic": False,
            "started_at": "2024-01-01T10:00:00"
        },
        {
            "id": "2",
            "instance_id": "zabbix-1",
            "instance_name": "Test Instance",
            "host": "server-02",
            "description": "Low disk",
            "severity": "warning",
            "severity_code": 2,
            "duration": "10m",
            "acknowledged": True,
            "event_id": "2",
            "is_synthetic": False,
            "started_at": "2024-01-01T09:50:00"
        }
    ]

def test_set_zabbix_alarms(aggregator, sample_alarms):
    """Test setting Zabbix alarms."""
    aggregator.set_zabbix_alarms(sample_alarms)
    
    assert len(aggregator.zabbix_alarms) == 2
    assert aggregator.last_poll is not None

def test_add_synthetic_alarm(aggregator):
    """Test adding synthetic alarm."""
    synthetic = {
        "id": "synthetic-1",
        "instance_id": "zabbix-1",
        "description": "Instance down",
        "severity": "disaster",
        "severity_code": 5,
        "is_synthetic": True
    }
    
    aggregator.add_synthetic_alarm(synthetic)
    assert "synthetic-1" in aggregator.synthetic_alarms

def test_remove_synthetic_alarm(aggregator):
    """Test removing synthetic alarm."""
    synthetic = {"id": "synthetic-1", "severity_code": 5}
    aggregator.add_synthetic_alarm(synthetic)
    
    aggregator.remove_synthetic_alarm("synthetic-1")
    assert "synthetic-1" not in aggregator.synthetic_alarms

def test_get_all_alarms_combines_sources(aggregator, sample_alarms):
    """Test getting all alarms combines Zabbix and synthetic."""
    aggregator.set_zabbix_alarms(sample_alarms)
    
    synthetic = {
        "id": "synthetic-1",
        "severity_code": 5,
        "started_at": "2024-01-01T11:00:00"
    }
    aggregator.add_synthetic_alarm(synthetic)
    
    all_alarms = aggregator.get_all_alarms()
    assert len(all_alarms) == 3

def test_get_all_alarms_sorted_by_severity(aggregator):
    """Test alarms are sorted by severity."""
    alarms = [
        {"id": "1", "severity_code": 2, "started_at": "2024-01-01T10:00:00"},
        {"id": "2", "severity_code": 5, "started_at": "2024-01-01T10:00:00"},
        {"id": "3", "severity_code": 4, "started_at": "2024-01-01T10:00:00"}
    ]
    aggregator.set_zabbix_alarms(alarms)
    
    sorted_alarms = aggregator.get_all_alarms()
    assert sorted_alarms[0]['severity_code'] == 5
    assert sorted_alarms[1]['severity_code'] == 4
    assert sorted_alarms[2]['severity_code'] == 2

def test_get_alarm_by_id(aggregator, sample_alarms):
    """Test getting specific alarm by ID."""
    aggregator.set_zabbix_alarms(sample_alarms)
    
    alarm = aggregator.get_alarm_by_id("1", "zabbix-1")
    assert alarm is not None
    assert alarm['host'] == "server-01"
    
    not_found = aggregator.get_alarm_by_id("999", "zabbix-1")
    assert not_found is None

def test_get_stats(aggregator, sample_alarms):
    """Test getting alarm statistics."""
    aggregator.set_zabbix_alarms(sample_alarms)
    
    synthetic = {"id": "synthetic-1", "severity_code": 5}
    aggregator.add_synthetic_alarm(synthetic)
    
    stats = aggregator.get_stats()
    
    assert stats['total'] == 3
    assert stats['synthetic'] == 1
    assert stats['zabbix'] == 2
    assert stats['by_severity']['high'] == 1
    assert stats['by_severity']['warning'] == 1
    assert stats['by_severity']['disaster'] == 1
