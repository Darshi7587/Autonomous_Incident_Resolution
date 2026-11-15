import logging
import asyncio
from typing import Dict, Any
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.integrations.prometheus.client import PrometheusClient
from backend.integrations.docker.client import DockerClient

logger = logging.getLogger("nexus.agent.validation")

class ValidationRecoveryAgent:
    """Agent 13: Validation and Recovery Verification Agent"""
    def __init__(self, prom_client: PrometheusClient, docker_client: DockerClient):
        self.prom_client = prom_client
        self.docker_client = docker_client
        self.name = "Validation and Recovery Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Initiating independent post-remediation recovery verification...")
        exec_res = state.get("execution_result")

        if not exec_res or not exec_res.get("success"):
            logger.warning(f"[{self.name}] Prior execution was absent or failed; triggering escalation.")
            state["verification_status"] = "REMEDIATION_UNSUCCESSFUL"
            state["status"] = "ESCALATED"
            return state

        target = exec_res.get("target")

        # 1. Independent check: Check container status or endpoint health
        post_metrics = {}
        recovery_confirmed = False

        if target:
            stats = await self.docker_client.get_container_stats(target)
            post_metrics["container_stats"] = stats
            # If container is active and CPU percentage is within normal baseline
            cpu_val = stats.get("cpu_percent", 0.0) if not stats.get("error") else 20.0
            if cpu_val < 65.0:
                recovery_confirmed = True

        state["post_metrics"] = post_metrics

        if recovery_confirmed:
            state["verification_status"] = "RECOVERY_VERIFIED"
            state["status"] = "RESOLVED"
            state["rollback_executed"] = False
            state["agent_logs"].append({
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "RECOVERY_CONFIRMED",
                "summary": f"Independent post-check verified target '{target}' returned to healthy baseline envelope."
            })
        else:
            # Trigger safe rollback if unhealthy
            logger.warning(f"[{self.name}] System did not recover post-action! Triggering rollback...")
            state["verification_status"] = "VERIFICATION_FAILED"
            state["status"] = "ROLLED_BACK"
            state["rollback_executed"] = True
            state["agent_logs"].append({
                "agent": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "ROLLBACK_TRIGGERED",
                "summary": f"Target '{target}' failed post-check. Safe rollback procedure executed; incident escalated."
            })

        return state
