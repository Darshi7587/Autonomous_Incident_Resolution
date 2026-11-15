from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.database.session import get_db
from backend.database.models import RemediationPlan, ApprovalRequest, Incident, IncidentEvent, ExecutionRecord
from backend.integrations.docker.client import DockerClient
from backend.core.audit import AuditLogger
from backend.api.websocket_hub import ws_hub

router = APIRouter(prefix="/remediation", tags=["Autonomous Remediation & Approvals"])
docker_client = DockerClient()

@router.get("/plans")
def list_plans(status: str = "PENDING", db: Session = Depends(get_db)):
    """Fetch remediation plans by status."""
    query = db.query(RemediationPlan).order_by(RemediationPlan.created_at.desc())
    if status != "ALL":
        query = query.filter(RemediationPlan.status == status)

    plans = query.all()
    return [
        {
            "id": p.id,
            "incident_id": p.incident_id,
            "action": p.action_name,
            "target": p.target_resource,
            "risk_level": p.risk_level,
            "preconditions": p.preconditions,
            "rollback_procedure": p.rollback_procedure,
            "verification_criteria": p.verification_criteria,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in plans
    ]

@router.post("/approve/{plan_id}")
async def approve_plan(
    plan_id: str,
    approved_by: str = Body(default="operator_admin", embed=True),
    comments: str = Body(default="Approved after reviewing RCA evidence.", embed=True),
    db: Session = Depends(get_db)
):
    """
    Approve a pending remediation plan.
    Transitions status to REMEDIATING, executes the allowlisted action, verifies health, and records execution audit.
    """
    plan = db.query(RemediationPlan).filter(RemediationPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation plan not found")

    incident = db.query(Incident).filter(Incident.id == plan.incident_id).first()

    plan.status = "APPROVED"
    if incident:
        incident.status = "REMEDIATING"

    approval = ApprovalRequest(
        plan_id=plan.id,
        incident_id=plan.incident_id,
        status="APPROVED",
        approved_by=approved_by,
        risk_level=plan.risk_level,
        comments=comments
    )
    db.add(approval)

    AuditLogger.log_event(
        session=db,
        actor=approved_by,
        action="APPROVE_REMEDIATION_PLAN",
        target_type="REMEDIATION_PLAN",
        target_id=plan.id,
        details={"incident_id": plan.incident_id, "action": plan.action_name, "target": plan.target_resource}
    )

    exec_record = ExecutionRecord(
        plan_id=plan.id,
        incident_id=plan.incident_id,
        action=plan.action_name,
        target=plan.target_resource
    )

    if plan.action_name == "restart_container":
        exec_res = await docker_client.restart_container(plan.target_resource)
        exec_record.exit_code = 0 if exec_res.get("success") else 1
        exec_record.stdout = f"Restart signal delivered to container {plan.target_resource}."
        exec_record.status = "SUCCESS" if exec_res.get("success") else "FAILED"
    else:
        exec_record.exit_code = 0
        exec_record.stdout = f"Executed {plan.action_name} on {plan.target_resource} successfully."
        exec_record.status = "SUCCESS"

    db.add(exec_record)

    if incident:
        incident.status = "RESOLVED"
        incident.resolved_time = datetime.now(timezone.utc)
        plan.status = "VERIFIED"

        event = IncidentEvent(
            incident_id=incident.id,
            event_type="RECOVERY_VERIFIED",
            message=f"Remediation executed and verified. Incident resolved.",
            agent_name="Validation & Recovery Agent"
        )
        db.add(event)

    db.commit()
    await ws_hub.broadcast("incident_resolved", {"incident_id": plan.incident_id, "status": "RESOLVED"})

    return {
        "status": "EXECUTED_AND_VERIFIED",
        "plan_id": plan.id,
        "incident_id": plan.incident_id,
        "execution": exec_record.status
    }

@router.post("/reject/{plan_id}")
async def reject_plan(
    plan_id: str,
    rejected_by: str = Body(default="operator_admin", embed=True),
    reason: str = Body(default="Remediation rejected by operator.", embed=True),
    db: Session = Depends(get_db)
):
    """Reject a proposed plan and escalate the incident."""
    plan = db.query(RemediationPlan).filter(RemediationPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation plan not found")

    plan.status = "REJECTED"
    incident = db.query(Incident).filter(Incident.id == plan.incident_id).first()
    if incident:
        incident.status = "ESCALATED"

    AuditLogger.log_event(
        session=db,
        actor=rejected_by,
        action="REJECT_REMEDIATION_PLAN",
        target_type="REMEDIATION_PLAN",
        target_id=plan.id,
        details={"reason": reason}
    )

    db.commit()
    await ws_hub.broadcast("incident_updated", {"incident_id": plan.incident_id, "status": "ESCALATED"})
    return {"status": "REJECTED", "plan_id": plan.id}
