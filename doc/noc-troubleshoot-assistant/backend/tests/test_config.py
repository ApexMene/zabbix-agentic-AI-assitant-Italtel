"""Unit tests for configuration management."""
import pytest
import os
import yaml
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import ConfigLoader

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory with test files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create app.yaml
    app_config = {
        "server": {"host": "0.0.0.0", "port": 13001},
        "polling": {"interval_seconds": 30},
        "database": {"url": "${DATABASE_URL}"},
        "mcp_server": {"url": "http://localhost:13002"},
        "history": {"retention_days": 90}
    }
    with open(config_dir / "app.yaml", 'w') as f:
        yaml.dump(app_config, f)
    
    # Create instances.yaml
    instances_config = {
        "instances": [
            {
                "id": "test-instance-1",
                "name": "Test Instance 1",
                "url": "http://test1.local/api",
                "username": "admin",
                "password": "${TEST_PASSWORD}",
                "enabled": True
            },
            {
                "id": "test-instance-2",
                "name": "Test Instance 2",
                "url": "http://test2.local/api",
                "username": "admin",
                "password": "plain_password",
                "enabled": False
            }
        ]
    }
    with open(config_dir / "instances.yaml", 'w') as f:
        yaml.dump(instances_config, f)
    
    return config_dir

def test_load_app_config(temp_config_dir):
    """Test loading application configuration."""
    loader = ConfigLoader(str(temp_config_dir))
    config = loader.load_app_config()
    
    assert config is not None
    assert config['server']['port'] == 13001
    assert config['polling']['interval_seconds'] == 30
    assert config['history']['retention_days'] == 90

def test_load_instances_config(temp_config_dir):
    """Test loading instances configuration."""
    loader = ConfigLoader(str(temp_config_dir))
    instances = loader.load_instances_config()
    
    assert len(instances) == 2
    assert instances[0]['id'] == 'test-instance-1'
    assert instances[1]['id'] == 'test-instance-2'

def test_env_var_substitution(temp_config_dir, monkeypatch):
    """Test environment variable substitution."""
    monkeypatch.setenv("TEST_PASSWORD", "secret123")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    
    loader = ConfigLoader(str(temp_config_dir))
    
    # Test app config substitution
    app_config = loader.load_app_config()
    assert app_config['database']['url'] == "postgresql://test:test@localhost/test"
    
    # Test instances config substitution
    instances = loader.load_instances_config()
    assert instances[0]['password'] == "secret123"
    assert instances[1]['password'] == "plain_password"  # No substitution

def test_get_instance_by_id(temp_config_dir):
    """Test getting instance by ID."""
    loader = ConfigLoader(str(temp_config_dir))
    
    instance = loader.get_instance_by_id("test-instance-1")
    assert instance['name'] == "Test Instance 1"
    
    with pytest.raises(ValueError, match="Instance not found"):
        loader.get_instance_by_id("non-existent")

def test_get_enabled_instances(temp_config_dir):
    """Test filtering enabled instances."""
    loader = ConfigLoader(str(temp_config_dir))
    enabled = loader.get_enabled_instances()
    
    assert len(enabled) == 1
    assert enabled[0]['id'] == 'test-instance-1'

def test_config_properties(temp_config_dir, monkeypatch):
    """Test configuration property accessors."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    
    loader = ConfigLoader(str(temp_config_dir))
    
    assert loader.database_url == "postgresql://test:test@localhost/test"
    assert loader.mcp_server_url == "http://localhost:13002"
    assert loader.polling_interval == 30
    assert loader.retention_days == 90

def test_config_caching(temp_config_dir):
    """Test that configs are cached after first load."""
    loader = ConfigLoader(str(temp_config_dir))
    
    config1 = loader.load_app_config()
    config2 = loader.load_app_config()
    assert config1 is config2  # Same object reference
    
    instances1 = loader.load_instances_config()
    instances2 = loader.load_instances_config()
    assert instances1 is instances2  # Same object reference
