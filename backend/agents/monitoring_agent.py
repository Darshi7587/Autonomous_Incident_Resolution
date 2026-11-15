import logging
from typing import Dict, Any
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.integrations.prometheus.client import PrometheusClient

logger = logging.getLogger("nexus.agent.monitoring")

class MonitoringAgent:
    """Agent 2: Monitoring Agent"""
    def __init__(self, prom_client: PrometheusClient):
        self.prom_client = prom_client
        self.name = "Monitoring Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Polling real-time metrics via PromQL...")
        system_metrics = await self.prom_client.get_system_metrics()

        state["active_metrics"] = system_metrics
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "METRICS_COLLECTED",
            "summary": f"Polled {len(system_metrics)} real-time metric streams from Prometheus."
        })
        return state
