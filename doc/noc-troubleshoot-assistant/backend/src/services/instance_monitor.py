"""Instance monitoring service."""
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class InstanceMonitor:
    """Monitor Zabbix instance connectivity and generate synthetic alarms."""
    
    def __init__(self, mcp_client, alarm_aggregator, check_interval: int = 30):
        self.mcp_client = mcp_client
        self.alarm_aggregator = alarm_aggregator
        self.check_interval = check_interval
        self.instance_status: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.task = None
    
    async def start(self):
        """Start monitoring loop."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info("Instance monitor started")
    
    async def stop(self):
        """Stop monitoring loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Instance monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                await self.check_all_instances()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def check_all_instances(self):
        """Check all instances and generate/clear synthetic alarms."""
        try:
            instances = await self.mcp_client.get_instances()
            
            for instance in instances:
                instance_id = instance['id']
                current_status = instance.get('status')
                previous_status = self.instance_status.get(instance_id, {}).get('status')
                
                if current_status == 'error':
                    # Instance is down
                    if previous_status != 'error':
                        # Transition to down - generate alarm
                        await self._generate_instance_down_alarm(instance)
                
                elif current_status == 'connected':
                    # Instance is up
                    if previous_status == 'error':
                        # Transition to up - clear alarm
                        self._clear_instance_down_alarm(instance)
                
                self.instance_status[instance_id] = {
                    'status': current_status,
                    'checked_at': datetime.utcnow()
                }
        
        except Exception as e:
            logger.error(f"Failed to check instances: {e}")
    
    async def _generate_instance_down_alarm(self, instance: Dict[str, Any]):
        """Generate synthetic alarm for down instance."""
        alarm_id = f"synthetic-{instance['id']}-down"
        
        alarm = {
            "id": alarm_id,
            "instance_id": instance['id'],
            "instance_name": instance['name'],
            "host": f"Zabbix Server ({instance['name']})",
            "description": f"Zabbix instance '{instance['name']}' is unreachable: {instance.get('error', 'Connection failed')}",
            "severity": "disaster",
            "severity_code": 5,
            "duration": "0s",
            "acknowledged": False,
            "event_id": f"synthetic-{instance['id']}-{int(datetime.utcnow().timestamp())}",
            "is_synthetic": True,
            "started_at": datetime.utcnow().isoformat()
        }
        
        self.alarm_aggregator.add_synthetic_alarm(alarm)
        logger.warning(f"Instance down alarm generated: {instance['name']}")
    
    def _clear_instance_down_alarm(self, instance: Dict[str, Any]):
        """Remove synthetic alarm when instance recovers."""
        alarm_id = f"synthetic-{instance['id']}-down"
        self.alarm_aggregator.remove_synthetic_alarm(alarm_id)
        logger.info(f"Instance recovered: {instance['name']}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status."""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "instances_monitored": len(self.instance_status),
            "last_check": max(
                (s['checked_at'] for s in self.instance_status.values()),
                default=None
            )
        }
