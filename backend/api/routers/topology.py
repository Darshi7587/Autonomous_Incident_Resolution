from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import Incident

router = APIRouter(prefix="/topology", tags=["Service Dependency Topology"])

@router.get("/")
def get_topology(db: Session = Depends(get_db)):
    """
    Returns graph nodes and edges pre-formatted for React Flow rendering.
    Highlights nodes that are currently within the blast radius of active incidents.
    """
    active_incidents = db.query(Incident).filter(
        Incident.status.notin_(["RESOLVED", "ROLLED_BACK"])
    ).all()
    affected_nodes = set()
    for inc in active_incidents:
        for res in (inc.affected_resources or []):
            affected_nodes.add(res)

    nodes = [
        {
            "id": "api-gateway",
            "type": "customServiceNode",
            "data": {
                "label": "API Gateway",
                "service": "api-gateway",
                "type": "gateway",
                "status": "AFFECTED" if "api-gateway" in affected_nodes else "HEALTHY",
                "traffic_rps": 1250,
                "latency_ms": 28.4
            },
            "position": {"x": 250, "y": 50}
        },
        {
            "id": "nexus-demo-order-service",
            "type": "customServiceNode",
            "data": {
                "label": "Order Service",
                "service": "nexus-demo-order-service",
                "type": "microservice",
                "status": "CRITICAL" if "nexus-demo-order-service" in affected_nodes else "HEALTHY",
                "traffic_rps": 480,
                "latency_ms": 142.0
            },
            "position": {"x": 100, "y": 200}
        },
        {
            "id": "auth-service",
            "type": "customServiceNode",
            "data": {
                "label": "Auth Service",
                "service": "auth-service",
                "type": "microservice",
                "status": "AFFECTED" if "auth-service" in affected_nodes else "HEALTHY",
                "traffic_rps": 320,
                "latency_ms": 15.2
            },
            "position": {"x": 400, "y": 200}
        },
        {
            "id": "inventory-service",
            "type": "customServiceNode",
            "data": {
                "label": "Inventory Service",
                "service": "inventory-service",
                "type": "microservice",
                "status": "HEALTHY",
                "traffic_rps": 210,
                "latency_ms": 32.1
            },
            "position": {"x": 100, "y": 350}
        },
        {
            "id": "nexus-demo-cache-db",
            "type": "customServiceNode",
            "data": {
                "label": "Redis Cache Cluster",
                "service": "nexus-demo-cache-db",
                "type": "database",
                "status": "AFFECTED" if "nexus-demo-cache-db" in affected_nodes else "HEALTHY",
                "traffic_rps": 3200,
                "latency_ms": 2.1
            },
            "position": {"x": 300, "y": 480}
        }
    ]

    edges = [
        {"id": "e-gw-order", "source": "api-gateway", "target": "nexus-demo-order-service", "animated": True},
        {"id": "e-gw-auth", "source": "api-gateway", "target": "auth-service", "animated": True},
        {"id": "e-order-inv", "source": "nexus-demo-order-service", "target": "inventory-service", "animated": True},
        {"id": "e-order-cache", "source": "nexus-demo-order-service", "target": "nexus-demo-cache-db", "animated": True},
        {"id": "e-auth-cache", "source": "auth-service", "target": "nexus-demo-cache-db", "animated": True},
        {"id": "e-inv-cache", "source": "inventory-service", "target": "nexus-demo-cache-db", "animated": True}
    ]

    return {"nodes": nodes, "edges": edges}
