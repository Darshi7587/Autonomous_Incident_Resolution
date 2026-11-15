from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.session import get_db
from backend.database.models import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("/")
def get_audit_trail(
    actor: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve immutable chronological audit records."""
    query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())

    if actor:
        query = query.filter(AuditLog.actor == actor)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))

    logs = query.limit(limit).all()

    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "actor": log.actor,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": log.details_json,
            "ip_address": log.ip_address
        }
        for log in logs
    ]
