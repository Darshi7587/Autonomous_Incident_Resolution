import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState

logger = logging.getLogger("nexus.agent.correlation")

class CorrelationAgent:
    """Agent 5: Incident Correlation Agent"""
    def __init__(self):
        self.name = "Incident Correlation Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Correlating multi-modal signals into consolidated incident...")
        anomalies = state.get("anomaly_findings", [])
        logs = state.get("log_evidence", [])
        blast_radius = state.get("blast_radius", [])

        correlated = []
        for anom in anomalies:
            correlated.append({
                "source": "METRIC_ANOMALY",
                "detail": f"{anom.get('metric', 'multivariate')}: {anom.get('value', anom.get('anomaly_score'))}",
                "severity": anom.get("severity", "WARNING")
            })

        for log_item in logs[:3]:
            correlated.append({
                "source": "LOKI_LOG_EXCEPTION",
                "detail": log_item.get("line", "")[:120],
                "severity": "HIGH"
            })

        state["correlated_alerts"] = correlated
        # Dynamically set title based on correlated evidence
        if anomalies:
            first_anom = anomalies[0]
            metric_tag = first_anom.get("metric", "Resource")
            state["incident_title"] = f"Correlated Alert: {metric_tag} Deviation on {', '.join(state.get('affected_resources', ['Cluster']))}"

        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "ALERTS_CORRELATED",
            "summary": f"Unified {len(correlated)} telemetry and log signals into one incident domain."
        })
        return state
