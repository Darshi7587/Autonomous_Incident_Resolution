import os
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database.session import init_db, SessionLocal
from backend.database.models import InfrastructureNode, ServiceDependency, Incident, Alert, IncidentEvent, RemediationPlan, User
from backend.core.security import hash_password
from backend.api.websocket_hub import ws_hub
from backend.api.routers import (
    overview,
    infrastructure,
    incidents,
    agents,
    topology,
    remediation,
    knowledge,
    analytics,
    audit,
    integrations,
    auth
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexus.main")

def seed_initial_data():
    """Seeds default infrastructure inventory and sample incident if database is clean."""
    with SessionLocal() as session:
        node = session.query(InfrastructureNode).first()
        if not node:
            logger.info("Seeding initial infrastructure inventory and topology...")
            nodes = [
                InfrastructureNode(name="nexus-host-primary", node_type="host", status="ONLINE", ip_address="192.168.1.10"),
                InfrastructureNode(name="api-gateway", node_type="service", status="ONLINE", ip_address="172.20.0.2"),
                InfrastructureNode(name="nexus-demo-order-service", node_type="container", status="ONLINE", ip_address="172.20.0.3"),
                InfrastructureNode(name="auth-service", node_type="service", status="ONLINE", ip_address="172.20.0.4"),
                InfrastructureNode(name="nexus-demo-cache-db", node_type="database", status="ONLINE", ip_address="172.20.0.5")
            ]
            session.add_all(nodes)

            deps = [
                ServiceDependency(upstream_service="api-gateway", downstream_service="nexus-demo-order-service"),
                ServiceDependency(upstream_service="api-gateway", downstream_service="auth-service"),
                ServiceDependency(upstream_service="nexus-demo-order-service", downstream_service="nexus-demo-cache-db")
            ]
            session.add_all(deps)

            # Seed Initial Admin & Operator
            admin_user = User(
                username="admin",
                hashed_password=hash_password("nexus_admin_2026"),
                role="admin"
            )
            op_user = User(
                username="operator",
                hashed_password=hash_password("operator_pass_2026"),
                role="operator"
            )
            session.add_all([admin_user, op_user])

            demo_inc_id = "inc-seed-001"
            inc = Incident(
                id=demo_inc_id,
                title="P95 Latency Spike and Thread Contention on Order Service",
                description="Prometheus PromQL rate detected 4.2x standard deviation spike on nexus-demo-order-service.",
                severity="HIGH",
                priority="P2",
                status="AWAITING_APPROVAL",
                source="Statistical Anomaly Detector",
                affected_resources=["nexus-demo-order-service", "nexus-demo-cache-db"],
                detection_time=datetime.now(timezone.utc),
                assigned_agent="Remediation Planning Agent",
                confidence_score=0.92
            )
            session.add(inc)

            alert = Alert(
                fingerprint="fp-order-cpu-01",
                incident_id=demo_inc_id,
                title="High CPU and P95 Response Latency",
                severity="HIGH",
                metric_name="http_request_duration_seconds_bucket",
                current_value=1450.0,
                baseline_value=120.0,
                anomaly_score=0.88,
                source="Prometheus",
                status="ACTIVE"
            )
            session.add(alert)

            event = IncidentEvent(
                incident_id=demo_inc_id,
                event_type="RCA_COMPLETED",
                message="Agent 6 formulated root cause: Process thread contention. Agent 11 generated restart plan.",
                agent_name="Root Cause Analysis Agent"
            )
            session.add(event)

            plan = RemediationPlan(
                incident_id=demo_inc_id,
                action_name="restart_container",
                target_resource="nexus-demo-order-service",
                risk_level="MEDIUM",
                preconditions=["Verify container is responsive to SIGTERM", "Capture thread dump"],
                rollback_procedure="Revert to previous container deployment if health probe fails",
                verification_criteria="P95 latency drops below 250ms within 60s post-restart.",
                status="PENDING"
            )
            session.add(plan)

            session.commit()
            logger.info("Database initialized and seeded with baseline topology and demo incident.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NEXUS AI Operational Core...")
    init_db()
    seed_initial_data()
    yield
    logger.info("Shutting down NEXUS AI Operational Core...")

app = FastAPI(
    title="NEXUS AI - Autonomous IT Operations Platform",
    description="Enterprise-grade autonomous IT incident detection, multi-agent investigation, remediation, and verification.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router, prefix="/api")
app.include_router(infrastructure.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(topology.router, prefix="/api")
app.include_router(remediation.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await ws_hub.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        ws_hub.disconnect(websocket)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": "NEXUS AI AIOps Core"
    }

@app.get("/metrics")
def metrics():
    return "# HELP nexus_ai_active_agents Number of active cognitive agents\n# TYPE nexus_ai_active_agents gauge\nnexus_ai_active_agents 13\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
