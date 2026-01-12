"""Alarm polling service."""
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

SEVERITY_MAP = {
    "0": ("not_classified", 0),
    "1": ("information", 1),
    "2": ("warning", 2),
    "3": ("average", 3),
    "4": ("high", 4),
    "5": ("disaster", 5)
}

class AlarmPoller:
    """Poll Zabbix instances for active problems."""
    
    def __init__(self, mcp_client, alarm_aggregator, poll_interval: int = 30):
        self.mcp_client = mcp_client
        self.alarm_aggregator = alarm_aggregator
        self.poll_interval = poll_interval
        self.running = False
        self.task = None
    
    async def start(self):
        """Start polling loop."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._poll_loop())
        logger.info("Alarm poller started")
    
    async def stop(self):
        """Stop polling loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Alarm poller stopped")
    
    async def _poll_loop(self):
        """Main polling loop."""
        while self.running:
            try:
                await self.poll_all_instances()
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
            
            await asyncio.sleep(self.poll_interval)
    
    async def poll_all_instances(self):
        """Poll all instances for problems."""
        try:
            instances = await self.mcp_client.get_instances()
            all_alarms = []
            
            for instance in instances:
                if instance.get('status') != 'connected':
                    continue
                
                try:
                    alarms = await self._poll_instance(instance)
                    all_alarms.extend(alarms)
                except Exception as e:
                    logger.error(f"Failed to poll {instance['id']}: {e}")
            
            self.alarm_aggregator.set_zabbix_alarms(all_alarms)
            logger.info(f"Polled {len(all_alarms)} alarms from {len(instances)} instances")
        
        except Exception as e:
            logger.error(f"Failed to poll instances: {e}")
    
    async def _poll_instance(self, instance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Poll single instance for problems."""
        instance_id = instance['id']
        instance_name = instance['name']
        
        result = await self.mcp_client.get_problems(
            instance_id,
            recent=True,
            output="extend"
        )
        
        if not result.get('success'):
            logger.error(f"Failed to get problems from {instance_id}: {result.get('error')}")
            return []
        
        problems = result.get('data', [])
        alarms = []
        
        for problem in problems:
            severity_str = problem.get('severity', '0')
            severity_name, severity_code = SEVERITY_MAP.get(severity_str, ("not_classified", 0))
            
            # Calculate duration
            clock = int(problem.get('clock', 0))
            duration = self._format_duration(datetime.utcnow().timestamp() - clock)
            
            alarm = {
                "id": problem.get('eventid'),
                "instance_id": instance_id,
                "instance_name": instance_name,
                "host": problem.get('name', '').split(':')[0].strip() if ':' in problem.get('name', '') else 'Unknown',
                "description": problem.get('name', 'Unknown problem'),
                "severity": severity_name,
                "severity_code": severity_code,
                "duration": duration,
                "acknowledged": problem.get('acknowledged') == '1',
                "event_id": problem.get('eventid'),
                "is_synthetic": False,
                "started_at": datetime.fromtimestamp(clock).isoformat() if clock else None
            }
            alarms.append(alarm)
        
        return alarms
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            return f"{days}d {hours}h"
