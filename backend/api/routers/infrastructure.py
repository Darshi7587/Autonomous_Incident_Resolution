from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.session import get_db
from backend.database.models import InfrastructureNode
from backend.integrations.docker.client import DockerClient
from backend.integrations.prometheus.client import PrometheusClient

router = APIRouter(prefix="/infrastructure", tags=["Live Infrastructure"])
docker_client = DockerClient()
prom_client = PrometheusClient()

@router.get("/nodes")
def get_nodes(db: Session = Depends(get_db)):
    """Retrieve all registered infrastructure nodes."""
    nodes = db.query(InfrastructureNode).all()
    return [
        {
            "id": n.id,
            "name": n.name,
            "type": n.node_type,
            "status": n.status,
            "ip_address": n.ip_address,
            "metadata": n.metadata_json,
            "last_seen": n.last_seen.isoformat() if n.last_seen else None
        }
        for n in nodes
    ]

@router.get("/containers")
async def get_containers():
    """Discover running and stopped Docker containers with live status."""
    containers = await docker_client.list_containers(all_containers=True)
    return containers

@router.get("/containers/{container_id}/stats")
async def get_container_stats(container_id: str):
    """Retrieve instantaneous CPU and memory metrics for a Docker container."""
    stats = await docker_client.get_container_stats(container_id)
    return stats

@router.get("/metrics/live")
async def get_live_metrics():
    """Fetch live Prometheus metrics across host and cluster."""
    metrics = await prom_client.get_system_metrics()
    return metrics
