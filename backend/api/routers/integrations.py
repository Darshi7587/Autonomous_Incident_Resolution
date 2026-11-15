from fastapi import APIRouter
from backend.integrations.prometheus.client import PrometheusClient
from backend.integrations.loki.client import LokiClient
from backend.integrations.docker.client import DockerClient
from backend.integrations.opentelemetry.client import OpenTelemetryClient
from backend.core.config import settings

router = APIRouter(prefix="/integrations", tags=["Integrations Configuration & Health"])

prom_client = PrometheusClient()
loki_client = LokiClient()
docker_client = DockerClient()
otel_client = OpenTelemetryClient()

@router.get("/status")
async def get_integrations_status():
    """Execute live health probes against all configured observability systems."""
    prom_health = await prom_client.check_health()
    loki_health = await loki_client.check_health()
    docker_ping = await docker_client.ping()
    otel_health = await otel_client.check_health()

    return [
        {
            "id": "prometheus",
            "name": "Prometheus Monitoring Server",
            "type": "METRICS",
            "endpoint": settings.PROMETHEUS_URL,
            "connected": prom_health.get("connected", False),
            "status": prom_health.get("status", "UNREACHABLE"),
            "description": "Scrapes PromQL metrics from hosts, containers, and applications."
        },
        {
            "id": "loki",
            "name": "Grafana Loki Log Store",
            "type": "LOGS",
            "endpoint": settings.LOKI_URL,
            "connected": loki_health.get("connected", False),
            "status": loki_health.get("status", "UNREACHABLE"),
            "description": "Centralized LogQL stream indexing for containers and services."
        },
        {
            "id": "docker",
            "name": "Docker Engine Daemon",
            "type": "CONTAINER_RUNTIME",
            "endpoint": settings.DOCKER_HOST or "Local Daemon (pipe/socket)",
            "connected": docker_ping,
            "status": "ONLINE" if docker_ping else "STANDBY",
            "description": "Container lifecycle management, telemetry stats, and remediation."
        },
        {
            "id": "opentelemetry",
            "name": "OpenTelemetry Collector",
            "type": "TRACES",
            "endpoint": settings.OTEL_COLLECTOR_URL,
            "connected": otel_health.get("connected", False),
            "status": otel_health.get("status", "STANDBY"),
            "description": "Distributed trace spans, context propagation, and request path tracing."
        }
    ]
