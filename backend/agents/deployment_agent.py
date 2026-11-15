import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.integrations.docker.client import DockerClient

logger = logging.getLogger("nexus.agent.deployment")

class DeploymentAnalysisAgent:
    """Agent 9: Deployment & Change Analysis Agent"""
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        self.name = "Deployment Analysis Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Inspecting recent container lifecycle events and changes...")
        containers = await self.docker_client.list_containers(all_containers=True)
        recent_changes = []

        affected = state.get("affected_resources", [])
        for c in containers:
            if any(aff in c["name"] for aff in affected) or c["restart_count"] > 0:
                recent_changes.append({
                    "container": c["name"],
                    "image": c["image"],
                    "state": c["state"],
                    "restart_count": c["restart_count"],
                    "created": c["created"]
                })

        state["recent_deployments"] = recent_changes
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "DEPLOYMENTS_INSPECTED",
            "summary": f"Analyzed container states and detected {len(recent_changes)} recent updates or restarts."
        })
        return state
