import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), default="operator")  # admin, operator, auditor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class InfrastructureNode(Base):
    __tablename__ = "infrastructure_nodes"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), unique=True, nullable=False, index=True)
    node_type = Column(String(64), nullable=False)  # host, container, service, database
    status = Column(String(32), default="ONLINE")  # ONLINE, DEGRADED, OFFLINE
    ip_address = Column(String(64), nullable=True)
    metadata_json = Column(JSON, default=dict)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ServiceDependency(Base):
    __tablename__ = "service_dependencies"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    upstream_service = Column(String(128), nullable=False, index=True)
    downstream_service = Column(String(128), nullable=False, index=True)
    dependency_type = Column(String(64), default="HTTP_API")  # HTTP_API, GRPC, DATABASE, QUEUE
    is_critical = Column(Boolean, default=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    fingerprint = Column(String(128), nullable=False, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), default="WARNING")  # INFO, WARNING, CRITICAL
    metric_name = Column(String(128), nullable=False)
    current_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    source = Column(String(64), default="prometheus")
    status = Column(String(32), default="ACTIVE")  # ACTIVE, CORRELATED, RESOLVED
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="alerts")

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(32), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    priority = Column(String(32), default="P2")      # P1, P2, P3, P4
    status = Column(String(32), default="NEW")       # NEW, INVESTIGATING, RCA_COMPLETED, AWAITING_APPROVAL, REMEDIATING, VERIFYING, RESOLVED, ESCALATED, ROLLED_BACK
    source = Column(String(64), default="AI_ANOMALY_DETECTION")
    affected_resources = Column(JSON, default=list)
    detection_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    resolved_time = Column(DateTime, nullable=True)
    assigned_agent = Column(String(64), default="Incident Correlation Agent")
    rca_summary = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)

    alerts = relationship("Alert", back_populates="incident")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan")
    rca_reports = relationship("RCAReport", back_populates="incident", cascade="all, delete-orphan")
    remediation_plans = relationship("RemediationPlan", back_populates="incident", cascade="all, delete-orphan")

class IncidentEvent(Base):
    __tablename__ = "incident_events"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False)  # DETECTED, AGENT_DISPATCHED, RCA_FORMULATED, PLAN_PROPOSED, APPROVED, EXECUTED, VERIFIED, ROLLED_BACK
    message = Column(Text, nullable=False)
    agent_name = Column(String(64), nullable=True)
    payload_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="events")

class RCAReport(Base):
    __tablename__ = "rca_reports"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    root_cause_hypothesis = Column(Text, nullable=False)
    supporting_evidence_json = Column(JSON, default=list)  # Telemetry data, log matches, trace spans
    affected_services_json = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.85)
    impact_assessment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="rca_reports")

class RemediationPlan(Base):
    __tablename__ = "remediation_plans"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    action_name = Column(String(128), nullable=False)
    target_resource = Column(String(128), nullable=False)
    parameters_json = Column(JSON, default=dict)
    risk_level = Column(String(32), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    preconditions = Column(JSON, default=list)
    rollback_procedure = Column(Text, nullable=True)
    verification_criteria = Column(Text, nullable=True)
    status = Column(String(32), default="PENDING")  # PENDING, APPROVED, REJECTED, EXECUTED, VERIFIED, FAILED, ROLLED_BACK
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="remediation_plans")
    approval_requests = relationship("ApprovalRequest", back_populates="plan", cascade="all, delete-orphan")
    execution_records = relationship("ExecutionRecord", back_populates="plan", cascade="all, delete-orphan")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(String(36), nullable=False)
    status = Column(String(32), default="PENDING")  # PENDING, APPROVED, REJECTED
    requested_by = Column(String(64), default="Security & Risk Assessment Agent")
    approved_by = Column(String(64), nullable=True)
    risk_level = Column(String(32), default="MEDIUM")
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    plan = relationship("RemediationPlan", back_populates="approval_requests")

class ExecutionRecord(Base):
    __tablename__ = "execution_records"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("remediation_plans.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(String(36), nullable=False)
    action = Column(String(128), nullable=False)
    target = Column(String(128), nullable=False)
    exit_code = Column(Integer, default=0)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    duration_ms = Column(Float, default=0.0)
    status = Column(String(32), default="SUCCESS")  # SUCCESS, FAILED, ROLLED_BACK
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    plan = relationship("RemediationPlan", back_populates="execution_records")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    actor = Column(String(64), nullable=False)  # User username or AI Agent name
    action = Column(String(128), nullable=False)
    target_type = Column(String(64), nullable=False)  # INCIDENT, CONTAINER, RUNBOOK, SYSTEM_CONFIG
    target_id = Column(String(128), nullable=True)
    details_json = Column(JSON, default=dict)
    ip_address = Column(String(64), default="127.0.0.1")

class IntegrationConfig(Base):
    __tablename__ = "integration_configs"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(64), unique=True, nullable=False)  # Prometheus, Loki, Docker, OpenTelemetry, AWS
    integration_type = Column(String(64), nullable=False)
    endpoint_url = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    last_health_check = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    health_status = Column(String(32), default="UNKNOWN")  # HEALTHY, UNREACHABLE, DEGRADED
