"""Investigation management service."""
from sqlalchemy.orm import Session
from models import Investigation, ChatMessage, ToolCall
from typing import Dict, Any, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class InvestigationService:
    """Manage investigation sessions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_investigation(self, alarm: Dict[str, Any]) -> str:
        """Create new investigation from alarm. Returns investigation ID as string."""
        investigation = Investigation(
            alarm_id=alarm['id'],
            alarm_description=alarm['description'],
            alarm_severity=alarm['severity'],
            host_name=alarm['host'],
            instance_id=alarm['instance_id']
        )
        self.db.add(investigation)
        self.db.flush()
        
        # Get ID as string immediately
        inv_id_str = str(investigation.id)
        
        # Expunge to completely detach from session
        self.db.expunge(investigation)
        
        # Commit
        self.db.commit()
        
        # Don't log the investigation object, only the ID string
        logger.info(f"Created investigation {inv_id_str}")
        
        # Delete the investigation variable to ensure no references remain
        del investigation
        
        return inv_id_str
    
    def add_message(self, investigation_id: UUID, role: str, content: str) -> ChatMessage:
        """Add message to investigation."""
        message = ChatMessage(
            investigation_id=investigation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        return message
    
    def add_tool_call(
        self, 
        investigation_id: UUID, 
        tool_name: str, 
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        duration_ms: int
    ) -> ToolCall:
        """Log tool call to investigation."""
        tool_call = ToolCall(
            investigation_id=investigation_id,
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            duration_ms=duration_ms
        )
        self.db.add(tool_call)
        self.db.commit()
        return tool_call
    
    def get_investigation(self, investigation_id: UUID) -> Optional[Investigation]:
        """Get investigation by ID."""
        return self.db.query(Investigation).filter_by(id=investigation_id).first()
    
    def get_messages(self, investigation_id: UUID) -> list:
        """Get all messages for investigation."""
        return self.db.query(ChatMessage).filter_by(
            investigation_id=investigation_id
        ).order_by(ChatMessage.timestamp).all()
    
    def complete_investigation(self, investigation_id: UUID):
        """Mark investigation as completed."""
        investigation = self.get_investigation(investigation_id)
        if investigation:
            investigation.status = 'completed'
            from datetime import datetime
            investigation.ended_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Investigation {investigation_id} completed")
