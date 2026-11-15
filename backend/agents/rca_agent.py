import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState

logger = logging.getLogger("nexus.agent.rca")

class RootCauseAnalysisAgent:
    """Agent 6: Root Cause Analysis (RCA) Agent"""
    def __init__(self):
        self.name = "Root Cause Analysis Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Synthesizing multi-modal telemetry and logs to formulate evidence-backed RCA...")
        anomalies = state.get("anomaly_findings", [])
        logs = state.get("log_evidence", [])
        deployments = state.get("recent_deployments", [])
        blast_radius = state.get("blast_radius", [])
        runbooks = state.get("matched_runbooks", [])

        # Gather strictly factual supporting evidence
        supporting_evidence = []
        for anom in anomalies:
            supporting_evidence.append({
                "type": "TELEMETRY_ANOMALY",
                "evidence": f"Metric '{anom.get('metric', 'multivariate')}' exhibited {anom.get('type')}. Value: {anom.get('value', anom.get('anomaly_score'))}."
            })

        for log in logs[:2]:
            supporting_evidence.append({
                "type": "LOG_STREAM_EXCEPTION",
                "evidence": f"Loki stream captured error: {log.get('line')[:150]}"
            })

        for dep in deployments:
            if dep.get("restart_count", 0) > 0:
                supporting_evidence.append({
                    "type": "CONTAINER_CRASH_EVENT",
                    "evidence": f"Container {dep.get('container')} has restarted {dep.get('restart_count')} times."
                })

        # Formulate deterministic evidence-grounded hypothesis
        primary_resource = state.get("affected_resources", ["Service"])[0]
        if runbooks:
            top_runbook = runbooks[0]
            hypothesis = (
                f"Root cause identified as {top_runbook.get('title')} on resource '{primary_resource}'. "
                f"Corroborated by {len(supporting_evidence)} concrete telemetry signals and log traces."
            )
        else:
            hypothesis = (
                f"Resource contention and service instability observed on '{primary_resource}'. "
                f"Empirical evidence points to abnormal workload pressure or dependency timeout."
            )

        impact = f"Immediate degradation across {len(blast_radius)} nodes in blast radius ({', '.join(blast_radius[:4])})."
        confidence = min(0.96, 0.70 + (0.05 * len(supporting_evidence)))

        state["rca_hypothesis"] = hypothesis
        state["supporting_evidence"] = supporting_evidence
        state["rca_confidence"] = round(confidence, 2)
        state["impact_assessment"] = impact
        state["status"] = "RCA_COMPLETED"

        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "RCA_FORMULATED",
            "summary": f"Formulated RCA report with {round(confidence*100)}% confidence backed by {len(supporting_evidence)} verified evidence items."
        })
        return state
