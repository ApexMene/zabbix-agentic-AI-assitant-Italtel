"""Configuration loader for MCP server."""
import os
import yaml
from pathlib import Path
import re
from typing import Dict, Any, List

class ConfigLoader:
    """Load Zabbix instances configuration."""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self._instances = None
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """Substitute environment variables in config values."""
        if isinstance(value, str):
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
    
    def load_instances(self) -> List[Dict[str, Any]]:
        """Load Zabbix instances configuration."""
        if self._instances is None:
            config_path = self.config_dir / "instances.yaml"
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            instances = config.get('instances', [])
            self._instances = self._substitute_env_vars(instances)
        return self._instances
    
    def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get specific instance by ID."""
        instances = self.load_instances()
        for instance in instances:
            if instance['id'] == instance_id:
                return instance
        raise ValueError(f"Instance not found: {instance_id}")
    
    def get_enabled_instances(self) -> List[Dict[str, Any]]:
        """Get only enabled instances."""
        instances = self.load_instances()
        return [inst for inst in instances if inst.get('enabled', True)]

config = ConfigLoader()
