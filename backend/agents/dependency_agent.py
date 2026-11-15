import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState

logger = logging.getLogger("nexus.agent.dependency")

class ServiceDependencyAgent:
    """Agent 8: Service Dependency & Blast Radius Agent"""
    def __init__(self):
        self.name = "Service Dependency Agent"
        # Standard microservices topology graph
        self.static_graph = {
            "api-gateway": {"downstream": ["order-service", "auth-service", "payment-service"], "upstream": []},
            "order-service": {"downstream": ["inventory-service", "nexus-demo-cache-db"], "upstream": ["api-gateway"]},
            "payment-service": {"downstream": ["nexus-demo-cache-db", "external-stripe-gateway"], "upstream": ["api-gateway"]},
            "auth-service": {"downstream": ["nexus-demo-cache-db"], "upstream": ["api-gateway"]},
            "inventory-service": {"downstream": ["nexus-demo-cache-db"], "upstream": ["order-service"]},
            "nexus-demo-cache-db": {"downstream": [], "upstream": ["order-service", "payment-service", "auth-service", "inventory-service"]}
        }

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Traversing service topology and calculating blast radius...")
        affected = state.get("affected_resources", [])
        blast_radius = set(affected)

        for resource in affected:
            node_info = self.static_graph.get(resource)
            if node_info:
                # If a database or critical cache fails, all upstreams are within blast radius!
                blast_radius.update(node_info.get("upstream", []))
                blast_radius.update(node_info.get("downstream", []))

        state["dependency_graph"] = self.static_graph
        state["blast_radius"] = list(blast_radius)
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "TOPOLOGY_EVALUATED",
            "summary": f"Identified blast radius of {len(blast_radius)} impacted services."
        })
        return state
