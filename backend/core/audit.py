import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.database.models import AuditLog

logger = logging.getLogger("nexus.audit")

class AuditLogger:
    @staticmethod
    def log_event(
        session: Session,
        actor: str,
        action: str,
        target_type: str,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "127.0.0.1"
    ):
        try:
            entry = AuditLog(
                actor=actor,
                action=action,
                target_type=target_type,
                target_id=target_id,
                details_json=details or {},
                ip_address=ip_address,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(entry)
            session.commit()
            logger.info(f"[AUDIT] {actor} performed '{action}' on {target_type}:{target_id}")
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
