"""Zabbix API client manager."""
from zabbix_utils import ZabbixAPI
from typing import Dict, Optional
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger(__name__)

class ZabbixClientManager:
    """Manage Zabbix API clients for multiple instances."""
    
    def __init__(self, config_loader=None):
        self.clients: Dict[str, ZabbixAPI] = {}
        if config_loader is None:
            from config import config
            self.config = config
        else:
            self.config = config_loader
        self.instances_config = None
    
    def _load_config(self):
        """Lazy load instances config."""
        if self.instances_config is None:
            self.instances_config = self.config.load_instances()
        return self.instances_config
    
    def get_client(self, instance_id: str) -> ZabbixAPI:
        """Get or create Zabbix API client for instance."""
        if instance_id not in self.clients:
            instance = self.config.get_instance(instance_id)
            
            try:
                client = ZabbixAPI(url=instance['url'], timeout=instance.get('timeout', 30))
                client.login(user=instance['username'], password=instance['password'])
                self.clients[instance_id] = client
                logger.info(f"Connected to Zabbix instance: {instance_id}")
            except Exception as e:
                logger.error(f"Failed to connect to {instance_id}: {e}")
                raise
        
        return self.clients[instance_id]
    
    def check_connection(self, instance_id: str) -> Dict[str, any]:
        """Check connection status for an instance."""
        try:
            client = self.get_client(instance_id)
            version = client.apiinfo.version()
            return {
                "status": "connected",
                "version": version,
                "instance_id": instance_id
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "instance_id": instance_id
            }
    
    def get_all_status(self) -> list:
        """Get connection status for all instances."""
        config = self._load_config()
        return [
            {
                "id": inst['id'],
                "name": inst['name'],
                **self.check_connection(inst['id'])
            }
            for inst in config
        ]
    
    def disconnect(self, instance_id: str):
        """Disconnect from instance."""
        if instance_id in self.clients:
            try:
                self.clients[instance_id].logout()
            except:
                pass
            del self.clients[instance_id]
    
    def disconnect_all(self):
        """Disconnect from all instances."""
        for instance_id in list(self.clients.keys()):
            self.disconnect(instance_id)

# Global client manager (lazy initialization)
_client_manager = None

def get_client_manager():
    """Get or create global client manager."""
    global _client_manager
    if _client_manager is None:
        _client_manager = ZabbixClientManager()
    return _client_manager
