import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from backend.agents.state import AgentWorkflowState
from backend.agents.discovery_agent import DiscoveryAgent
from backend.agents.monitoring_agent import MonitoringAgent
from backend.agents.anomaly_agent import AnomalyDetectionAgent
from backend.agents.log_intelligence_agent import LogIntelligenceAgent
from backend.agents.correlation_agent import CorrelationAgent
from backend.agents.rca_agent import RootCauseAnalysisAgent
from backend.agents.rag_agent import KnowledgeRAGAgent
from backend.agents.dependency_agent import ServiceDependencyAgent
from backend.agents.deployment_agent import DeploymentAnalysisAgent
from backend.agents.risk_agent import SecurityRiskAgent
from backend.agents.remediation_agent import RemediationPlanningAgent
from backend.agents.execution_agent import AutonomousExecutionAgent
from backend.agents.validation_agent import ValidationRecoveryAgent

from backend.integrations.prometheus.client import PrometheusClient
from backend.integrations.loki.client import LokiClient
from backend.integrations.docker.client import DockerClient
from backend.detection.dynamic_baseline import DynamicBaselineEstimator
from backend.detection.isolation_forest import MultivariateAnomalyDetector
from backend.knowledge.chroma_store import ChromaKnowledgeStore

logger = logging.getLogger("nexus.workflow.orchestrator")

class NexusAIOpsOrchestrator:
    """
    LangGraph Multi-Agent Cognitive Orchestrator for Autonomous IT Operations.
    Coordinates all 13 specialized agents through a deterministic state machine with approval gates.
    """
    def __init__(
        self,
        prom_client: PrometheusClient,
        loki_client: LokiClient,
        docker_client: DockerClient,
        chroma_store: ChromaKnowledgeStore,
        baseline_estimator: DynamicBaselineEstimator,
        iforest_detector: MultivariateAnomalyDetector
    ):
        self.prom_client = prom_client
        self.loki_client = loki_client
        self.docker_client = docker_client
        self.chroma_store = chroma_store

        # Instantiate 13 Specialized Agents
        self.agent_discovery = DiscoveryAgent(docker_client)
        self.agent_monitoring = MonitoringAgent(prom_client)
        self.agent_anomaly = AnomalyDetectionAgent(baseline_estimator, iforest_detector)
        self.agent_logs = LogIntelligenceAgent(loki_client)
        self.agent_dependency = ServiceDependencyAgent()
        self.agent_deployment = DeploymentAnalysisAgent(docker_client)
        self.agent_correlation = CorrelationAgent()
        self.agent_rag = KnowledgeRAGAgent(chroma_store)
        self.agent_rca = RootCauseAnalysisAgent()
        self.agent_risk = SecurityRiskAgent()
        self.agent_remediation = RemediationPlanningAgent()
        self.agent_execution = AutonomousExecutionAgent(docker_client)
        self.agent_validation = ValidationRecoveryAgent(prom_client, docker_client)

        self.workflow = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentWorkflowState)

        # Register Agent Nodes
        graph.add_node("agent_discovery", self.agent_discovery.execute)
        graph.add_node("agent_monitoring", self.agent_monitoring.execute)
        graph.add_node("agent_anomaly", self.agent_anomaly.execute)
        graph.add_node("agent_logs", self.agent_logs.execute)
        graph.add_node("agent_dependency", self.agent_dependency.execute)
        graph.add_node("agent_deployment", self.agent_deployment.execute)
        graph.add_node("agent_correlation", self.agent_correlation.execute)
        graph.add_node("agent_rag", self.agent_rag.execute)
        graph.add_node("agent_rca", self.agent_rca.execute)
        graph.add_node("agent_risk", self.agent_risk.execute)
        graph.add_node("agent_remediation", self.agent_remediation.execute)
        graph.add_node("agent_execution", self.agent_execution.execute)
        graph.add_node("agent_validation", self.agent_validation.execute)

        # Edges
        graph.set_entry_point("agent_discovery")
        graph.add_edge("agent_discovery", "agent_monitoring")
        graph.add_edge("agent_monitoring", "agent_anomaly")
        graph.add_edge("agent_anomaly", "agent_logs")
        graph.add_edge("agent_logs", "agent_dependency")
        graph.add_edge("agent_dependency", "agent_deployment")
        graph.add_edge("agent_deployment", "agent_correlation")
        graph.add_edge("agent_correlation", "agent_rag")
        graph.add_edge("agent_rag", "agent_rca")
        graph.add_edge("agent_rca", "agent_risk")
        graph.add_edge("agent_risk", "agent_remediation")

        # Conditional Approval Gate
        def check_approval_gate(state: AgentWorkflowState):
            if state.get("requires_approval") and not state.get("is_approved"):
                return "await_approval"
            return "proceed_to_execution"

        graph.add_conditional_edges(
            "agent_remediation",
            check_approval_gate,
            {
                "await_approval": END,
                "proceed_to_execution": "agent_execution"
            }
        )

        graph.add_edge("agent_execution", "agent_validation")
        graph.add_edge("agent_validation", END)

        return graph.compile()

    async def run_investigation(self, initial_state: AgentWorkflowState) -> AgentWorkflowState:
        """Run full investigation through the compiled LangGraph workflow."""
        logger.info(f"Dispatching LangGraph workflow for incident {initial_state.get('incident_id')}...")
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state

    async def execute_approved_remediation(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Resume workflow for an approved incident through Execution and Validation."""
        state["is_approved"] = True
        state["status"] = "REMEDIATING"
        state = await self.agent_execution.execute(state)
        state = await self.agent_validation.execute(state)
        return state
