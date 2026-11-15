import logging
from typing import Dict, Any
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.integrations.docker.client import DockerClient

logger = logging.getLogger("nexus.agent.discovery")

class DiscoveryAgent:
    """Agent 1: Infrastructure Discovery Agent"""
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        self.name = "Infrastructure Discovery Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Initiating live infrastructure topology scan...")
        discovered = []

        # 1. Inspect Docker containers
        containers = await self.docker_client.list_containers(all_containers=True)
        for c in containers:
            discovered.append({
                "id": c["id"],
                "name": c["name"],
                "type": "container",
                "image": c["image"],
                "status": c["status"],
                "restart_count": c["restart_count"],
                "ports": c["ports"]
            })

        # 2. Add local host node
        discovered.append({
            "id": "host-primary",
            "name": "nexus-host-primary",
            "type": "host",
            "status": "ONLINE",
            "os": "Windows / Linux",
            "services": ["fastapi", "prometheus", "loki", "docker"]
        })

        state["discovered_nodes"] = discovered
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "DISCOVERY_COMPLETED",
            "summary": f"Discovered {len(discovered)} infrastructure nodes and containers."
        })
        return state
