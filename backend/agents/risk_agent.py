import logging
from typing import Dict, Any
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.core.config import settings

logger = logging.getLogger("nexus.agent.risk")

class SecurityRiskAgent:
    """Agent 10: Security and Risk Assessment Agent"""
    def __init__(self):
        self.name = "Security and Risk Assessment Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Evaluating operational risk, production blast radius, and permission boundaries...")
        blast_radius = state.get("blast_radius", [])
        severity = state.get("severity", "MEDIUM")
        runbooks = state.get("matched_runbooks", [])

        runbook_risk = runbooks[0].get("risk_level", "MEDIUM") if runbooks else "MEDIUM"

        # Risk scoring matrix based on production blast radius and target sensitivity
        if "nexus-demo-cache-db" in blast_radius or "database" in [r.lower() for r in blast_radius]:
            calculated_risk = "HIGH"
        elif len(blast_radius) > 3 or severity == "CRITICAL":
            calculated_risk = "HIGH"
        elif runbook_risk == "MEDIUM":
            calculated_risk = "MEDIUM"
        else:
            calculated_risk = "LOW"

        # Approval policy
        requires_approval = True
        if calculated_risk == "LOW" and settings.AUTO_APPROVE_LOW_RISK:
            requires_approval = False

        state["risk_level"] = calculated_risk
        state["requires_approval"] = requires_approval
        state["is_approved"] = not requires_approval  # Auto-approved if LOW risk policy permits

        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "RISK_ASSESSED",
            "summary": f"Assessed risk as '{calculated_risk}'. Human approval required: {requires_approval}."
        })
        return state
