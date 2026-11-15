from typing import TypedDict, List, Dict, Any, Optional

class AgentWorkflowState(TypedDict):
    """
    Unified typed state passed across all 13 agents in the LangGraph cognitive workflow.
    """
    # Incident Identification & Metadata
    incident_id: str
    incident_title: str
    severity: str
    priority: str
    status: str
    affected_resources: List[str]
    detection_time: str

    # Telemetry & Evidence (Agents 1, 2, 3, 4)
    discovered_nodes: List[Dict[str, Any]]
    active_metrics: Dict[str, Any]
    anomaly_findings: List[Dict[str, Any]]
    log_evidence: List[Dict[str, Any]]
    trace_evidence: List[Dict[str, Any]]

    # Topology & Deployments (Agents 8, 9)
    dependency_graph: Dict[str, Any]
    blast_radius: List[str]
    recent_deployments: List[Dict[str, Any]]

    # Correlation & Root Cause (Agents 5, 6)
    correlated_alerts: List[Dict[str, Any]]
    rca_hypothesis: str
    supporting_evidence: List[Dict[str, Any]]
    rca_confidence: float
    impact_assessment: str

    # Knowledge & RAG (Agent 7)
    matched_runbooks: List[Dict[str, Any]]

    # Risk & Remediation Plan (Agents 10, 11)
    proposed_plan: Optional[Dict[str, Any]]
    risk_level: str
    requires_approval: bool
    is_approved: bool

    # Execution & Verification (Agents 12, 13)
    execution_result: Optional[Dict[str, Any]]
    verification_status: str
    post_metrics: Dict[str, Any]
    rollback_executed: bool

    # Audit & Agent Tickers
    agent_logs: List[Dict[str, Any]]
    errors: List[str]
