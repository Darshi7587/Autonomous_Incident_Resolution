import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.knowledge.chroma_store import ChromaKnowledgeStore

logger = logging.getLogger("nexus.agent.rag")

class KnowledgeRAGAgent:
    """Agent 7: Knowledge & RAG Agent"""
    def __init__(self, chroma_store: ChromaKnowledgeStore):
        self.chroma_store = chroma_store
        self.name = "Knowledge & RAG Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Performing semantic vector retrieval against ChromaDB it_runbooks...")
        title = state.get("incident_title", "infrastructure anomaly")
        affected = state.get("affected_resources", [])
        anomalies = state.get("anomaly_findings", [])
        metric_hint = anomalies[0].get("metric", "") if anomalies else ""

        query_text = f"Incident: {title}. Affected: {', '.join(affected)}. Metric: {metric_hint}"
        runbooks = self.chroma_store.query_runbooks(query_text=query_text, n_results=2)

        state["matched_runbooks"] = runbooks
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "RUNBOOKS_RETRIEVED",
            "summary": f"Retrieved {len(runbooks)} relevant operational runbooks (top match: {runbooks[0]['title'] if runbooks else 'None'})."
        })
        return state
