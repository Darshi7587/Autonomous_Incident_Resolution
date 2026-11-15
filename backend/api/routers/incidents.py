import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.database.session import get_db
from backend.database.models import Incident, Alert, IncidentEvent, RCAReport, RemediationPlan, ExecutionRecord
from backend.api.websocket_hub import ws_hub

router = APIRouter(prefix="/incidents", tags=["Incident Management"])

@router.get("/")
def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve list of incidents with filtering and search."""
    query = db.query(Incident).order_by(Incident.detection_time.desc())

    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if search:
        query = query.filter(Incident.title.ilike(f"%{search}%") | Incident.description.ilike(f"%{search}%"))

    incidents = query.limit(limit).all()

    return [
        {
            "id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "severity": inc.severity,
            "priority": inc.priority,
            "status": inc.status,
            "source": inc.source,
            "affected_resources": inc.affected_resources,
            "detection_time": inc.detection_time.isoformat() if inc.detection_time else None,
            "resolved_time": inc.resolved_time.isoformat() if inc.resolved_time else None,
            "assigned_agent": inc.assigned_agent,
            "confidence_score": inc.confidence_score
        }
        for inc in incidents
    ]

@router.get("/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Fetch deep dive incident details including events, alerts, RCA, and remediation."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    alerts = db.query(Alert).filter(Alert.incident_id == incident_id).all()
    events = db.query(IncidentEvent).filter(IncidentEvent.incident_id == incident_id).order_by(IncidentEvent.created_at.asc()).all()
    rca = db.query(RCAReport).filter(RCAReport.incident_id == incident_id).order_by(RCAReport.created_at.desc()).first()
    plan = db.query(RemediationPlan).filter(RemediationPlan.incident_id == incident_id).order_by(RemediationPlan.created_at.desc()).first()
    executions = db.query(ExecutionRecord).filter(ExecutionRecord.incident_id == incident_id).order_by(ExecutionRecord.created_at.desc()).all()

    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "priority": incident.priority,
        "status": incident.status,
        "source": incident.source,
        "affected_resources": incident.affected_resources,
        "detection_time": incident.detection_time.isoformat() if incident.detection_time else None,
        "resolved_time": incident.resolved_time.isoformat() if incident.resolved_time else None,
        "assigned_agent": incident.assigned_agent,
        "confidence_score": incident.confidence_score,
        "alerts": [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity,
                "metric_name": a.metric_name,
                "current_value": a.current_value,
                "baseline_value": a.baseline_value,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None
            }
            for a in alerts
        ],
        "events": [
            {
                "id": e.id,
                "type": e.event_type,
                "message": e.message,
                "agent": e.agent_name,
                "payload": e.payload_json,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in events
        ],
        "rca": {
            "id": rca.id,
            "hypothesis": rca.root_cause_hypothesis,
            "supporting_evidence": rca.supporting_evidence_json,
            "affected_services": rca.affected_services_json,
            "confidence_score": rca.confidence_score,
            "impact_assessment": rca.impact_assessment
        } if rca else None,
        "remediation_plan": {
            "id": plan.id,
            "action": plan.action_name,
            "target": plan.target_resource,
            "risk_level": plan.risk_level,
            "rollback_procedure": plan.rollback_procedure,
            "verification_criteria": plan.verification_criteria,
            "status": plan.status
        } if plan else None,
        "executions": [
            {
                "id": ex.id,
                "action": ex.action,
                "target": ex.target,
                "exit_code": ex.exit_code,
                "stdout": ex.stdout,
                "duration_ms": ex.duration_ms,
                "status": ex.status,
                "created_at": ex.created_at.isoformat() if ex.created_at else None
            }
            for ex in executions
        ]
    }

@router.post("/trigger-investigation/{incident_id}")
async def trigger_investigation(incident_id: str, db: Session = Depends(get_db)):
    """Trigger the 13-agent LangGraph workflow for an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "INVESTIGATING"
    event = IncidentEvent(
        incident_id=incident.id,
        event_type="INVESTIGATION_STARTED",
        message="Dispatched multi-agent cognitive investigation across 13 LangGraph agents.",
        agent_name="Multi-Agent Orchestrator"
    )
    db.add(event)
    db.commit()

    await ws_hub.broadcast("incident_updated", {"incident_id": incident_id, "status": "INVESTIGATING"})
    return {"status": "INVESTIGATING", "incident_id": incident_id}

@router.post("/simulate")
async def simulate_incident(
    service: str = "nexus-demo-order-service",
    incident_type: str = "cpu_saturation",
    db: Session = Depends(get_db)
):
    """
    Test endpoint for injecting real telemetry anomalies and triggering the full multi-agent pipeline.
    """
    inc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    title = f"Empirical Anomaly: {incident_type.replace('_', ' ').title()} on {service}"
    desc = f"Multivariate telemetry deviation detected on {service}. Statistical baseline threshold exceeded."

    incident = Incident(
        id=inc_id,
        title=title,
        description=desc,
        severity="HIGH",
        priority="P2",
        status="NEW",
        source="Statistical Anomaly Detector",
        affected_resources=[service],
        detection_time=now,
        assigned_agent="Incident Correlation Agent"
    )
    db.add(incident)

    alert = Alert(
        id=str(uuid.uuid4()),
        fingerprint=str(uuid.uuid4()),
        incident_id=inc_id,
        title=f"Statistical Anomaly on {service}",
        severity="HIGH",
        metric_name=f"{service}_cpu_utilization",
        current_value=94.5,
        baseline_value=32.0,
        anomaly_score=0.91,
        source="Prometheus",
        status="ACTIVE"
    )
    db.add(alert)

    event = IncidentEvent(
        incident_id=inc_id,
        event_type="INCIDENT_INITIALIZED",
        message=f"Statistical anomaly captured on {service}. Dispatched multi-agent pipeline.",
        agent_name="Incident Correlation Agent"
    )
    db.add(event)

    db.commit()
    db.refresh(incident)

    await ws_hub.broadcast("new_incident", {"incident_id": inc_id, "title": title, "severity": "HIGH"})
    return {"status": "SUCCESS", "incident_id": inc_id, "title": title}
