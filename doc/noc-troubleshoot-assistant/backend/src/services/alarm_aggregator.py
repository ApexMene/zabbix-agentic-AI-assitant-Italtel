"""Alarm aggregation service."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AlarmAggregator:
    """Aggregate alarms from multiple Zabbix instances."""
    
    def __init__(self):
        self.zabbix_alarms: List[Dict[str, Any]] = []
        self.synthetic_alarms: Dict[str, Dict[str, Any]] = {}
        self.last_poll: Optional[datetime] = None
    
    def set_zabbix_alarms(self, alarms: List[Dict[str, Any]]):
        """Update alarms from Zabbix polling."""
        self.zabbix_alarms = alarms
        self.last_poll = datetime.utcnow()
        logger.info(f"Updated {len(alarms)} Zabbix alarms")
    
    def add_synthetic_alarm(self, alarm: Dict[str, Any]):
        """Add synthetic alarm (e.g., instance down)."""
        self.synthetic_alarms[alarm['id']] = alarm
        logger.info(f"Added synthetic alarm: {alarm['id']}")
    
    def remove_synthetic_alarm(self, alarm_id: str):
        """Remove synthetic alarm."""
        if alarm_id in self.synthetic_alarms:
            del self.synthetic_alarms[alarm_id]
            logger.info(f"Removed synthetic alarm: {alarm_id}")
    
    def get_all_alarms(self) -> List[Dict[str, Any]]:
        """Get combined list of Zabbix + synthetic alarms."""
        all_alarms = list(self.synthetic_alarms.values()) + self.zabbix_alarms
        
        # Sort by severity (desc) then started_at (desc)
        return sorted(
            all_alarms,
            key=lambda a: (-a.get('severity_code', 0), a.get('started_at', '')),
            reverse=False
        )
    
    def get_alarm_by_id(self, alarm_id: str, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get specific alarm by ID."""
        for alarm in self.get_all_alarms():
            if alarm['id'] == alarm_id and alarm['instance_id'] == instance_id:
                return alarm
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alarm statistics."""
        all_alarms = self.get_all_alarms()
        
        severity_counts = {
            "disaster": 0,
            "high": 0,
            "average": 0,
            "warning": 0,
            "information": 0,
            "not_classified": 0
        }
        
        severity_map = {5: "disaster", 4: "high", 3: "average", 2: "warning", 1: "information", 0: "not_classified"}
        
        for alarm in all_alarms:
            severity_key = severity_map.get(alarm.get('severity_code', 0), "not_classified")
            severity_counts[severity_key] += 1
        
        return {
            "total": len(all_alarms),
            "by_severity": severity_counts,
            "synthetic": len(self.synthetic_alarms),
            "zabbix": len(self.zabbix_alarms),
            "last_poll": self.last_poll.isoformat() if self.last_poll else None
        }

# Global alarm aggregator
alarm_aggregator = AlarmAggregator()
