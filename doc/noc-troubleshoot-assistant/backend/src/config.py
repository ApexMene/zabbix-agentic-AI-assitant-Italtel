"""Configuration management for the application."""
import os
import yaml
from typing import Dict, Any, List
from pathlib import Path
import re

class ConfigLoader:
    """Load and manage application configuration."""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self._app_config = None
        self._instances_config = None
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """Recursively substitute environment variables in config values."""
        if isinstance(value, str):
            # Replace ${VAR_NAME} with environment variable value
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)
            for var_name in matches:
                env_value = os.getenv(var_name, '')
                value = value.replace(f'${{{var_name}}}', env_value)
            return value
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        return value
    
    def load_app_config(self) -> Dict[str, Any]:
        """Load application configuration from app.yaml."""
        if self._app_config is None:
            config_path = self.config_dir / "app.yaml"
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self._app_config = self._substitute_env_vars(config)
        return self._app_config
    
    def load_instances_config(self) -> List[Dict[str, Any]]:
        """Load Zabbix instances configuration from instances.yaml."""
        if self._instances_config is None:
            config_path = self.config_dir / "instances.yaml"
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            instances = config.get('instances', [])
            self._instances_config = self._substitute_env_vars(instances)
        return self._instances_config
    
    def get_instance_by_id(self, instance_id: str) -> Dict[str, Any]:
        """Get specific instance configuration by ID."""
        instances = self.load_instances_config()
        for instance in instances:
            if instance['id'] == instance_id:
                return instance
        raise ValueError(f"Instance not found: {instance_id}")
    
    def get_enabled_instances(self) -> List[Dict[str, Any]]:
        """Get only enabled instances."""
        instances = self.load_instances_config()
        return [inst for inst in instances if inst.get('enabled', True)]
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return os.getenv("DATABASE_URL", "postgresql://noc_user:noc_password@localhost:13432/noc_db")
    
    @property
    def mcp_server_url(self) -> str:
        """Get MCP server URL."""
        app_config = self.load_app_config()
        return app_config.get('mcp_server', {}).get('url', 'http://localhost:13002')
    
    @property
    def polling_interval(self) -> int:
        """Get polling interval in seconds."""
        app_config = self.load_app_config()
        return app_config.get('polling', {}).get('interval_seconds', 30)
    
    @property
    def retention_days(self) -> int:
        """Get history retention days."""
        app_config = self.load_app_config()
        return app_config.get('history', {}).get('retention_days', 90)

# Global config instance
config = ConfigLoader()
