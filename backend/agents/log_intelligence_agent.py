import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.integrations.loki.client import LokiClient

logger = logging.getLogger("nexus.agent.logs")

class LogIntelligenceAgent:
    """Agent 4: Log Intelligence Agent"""
    def __init__(self, loki_client: LokiClient):
        self.loki_client = loki_client
        self.name = "Log Intelligence Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Searching Loki log streams for error patterns...")
        affected = state.get("affected_resources", [])
        primary_resource = affected[0] if affected else "service"

        # Search error logs for the affected resource
        logs = await self.loki_client.search_errors(container=primary_resource, window_seconds=1800)
        
        parsed_evidence = []
        for entry in logs[:15]:
            parsed_evidence.append({
                "timestamp_ns": entry.get("timestamp_ns"),
                "line": entry.get("line"),
                "container": entry.get("labels", {}).get("container", primary_resource)
            })

        state["log_evidence"] = parsed_evidence
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "LOGS_SEARCHED",
            "summary": f"Retrieved and parsed {len(parsed_evidence)} error log lines from Loki."
        })
        return state
