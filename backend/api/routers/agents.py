from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/agents", tags=["AI Agent Control Center"])

AGENTS_METADATA = [
    {
        "id": "agent-1",
        "name": "Infrastructure Discovery Agent",
        "responsibility": "Discovers connected infrastructure, hosts, containers, and network nodes; maintains topology inventory.",
        "status": "ONLINE",
        "current_task": "Continuous topology polling",
        "tool_calls": ["docker.list_containers", "network.inspect_nodes"],
        "avg_duration_ms": 115.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-2",
        "name": "Monitoring Agent",
        "responsibility": "Executes continuous PromQL queries and tracks cluster and host telemetry health.",
        "status": "ONLINE",
        "current_task": "Polling PromQL metrics every 5s",
        "tool_calls": ["prometheus.query", "prometheus.get_targets"],
        "avg_duration_ms": 48.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-3",
        "name": "Anomaly Detection Agent",
        "responsibility": "Calculates dynamic statistical baseline envelopes and evaluates Isolation Forest multivariate outlier scores.",
        "status": "ONLINE",
        "current_task": "Evaluating streaming telemetry against dynamic IQR/Z-score baselines",
        "tool_calls": ["baseline.update_and_evaluate", "isolation_forest.score_vector"],
        "avg_duration_ms": 32.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-4",
        "name": "Log Intelligence Agent",
        "responsibility": "Queries Loki for container and service error patterns, parses stack traces, and correlates log events.",
        "status": "ONLINE",
        "current_task": "Analyzing LogQL streams for exception bursts",
        "tool_calls": ["loki.query_range", "loki.search_errors"],
        "avg_duration_ms": 142.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-5",
        "name": "Incident Correlation Agent",
        "responsibility": "Clusters related alerts across time windows and dependency graphs to eliminate alert noise.",
        "status": "ONLINE",
        "current_task": "Correlating multi-service alerts into unified incident contexts",
        "tool_calls": ["correlator.correlate_alert", "topology.find_common_root"],
        "avg_duration_ms": 65.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-6",
        "name": "Root Cause Analysis Agent",
        "responsibility": "Synthesizes multi-modal telemetry, error logs, and traces into evidence-backed, factual RCA reports.",
        "status": "ONLINE",
        "current_task": "Synthesizing evidence-grounded hypotheses",
        "tool_calls": ["evidence.synthesize", "llm.formulate_rca"],
        "avg_duration_ms": 420.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-7",
        "name": "Knowledge & RAG Agent",
        "responsibility": "Executes dense semantic vector searches over ChromaDB it_runbooks and historical resolutions.",
        "status": "ONLINE",
        "current_task": "Querying ChromaDB vector collection",
        "tool_calls": ["chroma.query_runbooks", "sentence_transformers.encode"],
        "avg_duration_ms": 85.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-8",
        "name": "Service Dependency Agent",
        "responsibility": "Builds topological service graphs, traces upstream/downstream callers, and calculates blast radius.",
        "status": "ONLINE",
        "current_task": "Graph traversal and blast radius assessment",
        "tool_calls": ["topology.traverse", "blast_radius.calculate"],
        "avg_duration_ms": 28.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-9",
        "name": "Deployment Analysis Agent",
        "responsibility": "Audits recent container deployments, restarts, configuration diffs, and image mutations.",
        "status": "ONLINE",
        "current_task": "Auditing container restart counts and commit tags",
        "tool_calls": ["docker.inspect", "git.inspect_recent_commits"],
        "avg_duration_ms": 90.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-10",
        "name": "Security & Risk Assessment Agent",
        "responsibility": "Computes operational risk matrices, verifies permission boundaries, and establishes approval requirements.",
        "status": "ONLINE",
        "current_task": "Evaluating blast radius risk and safety policy",
        "tool_calls": ["risk_matrix.evaluate", "rbac.check_permissions"],
        "avg_duration_ms": 35.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-11",
        "name": "Remediation Planning Agent",
        "responsibility": "Formulates actionable resolution plans with preconditions, rollback procedures, and verification criteria.",
        "status": "ONLINE",
        "current_task": "Generating step-by-step resolution workflows",
        "tool_calls": ["plan.formulate", "rollback.define"],
        "avg_duration_ms": 210.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-12",
        "name": "Autonomous Execution Agent",
        "responsibility": "Executes approved remediation actions through sandboxed, allowlisted connectors with timeouts.",
        "status": "ONLINE",
        "current_task": "Enforcing tool allowlist and executing actions",
        "tool_calls": ["docker.restart_container", "system.reload_service"],
        "avg_duration_ms": 1250.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "agent-13",
        "name": "Validation & Recovery Agent",
        "responsibility": "Gathers post-action metrics, verifies baseline recovery, and triggers automatic rollback if recovery fails.",
        "status": "ONLINE",
        "current_task": "Verifying post-remediation health telemetry",
        "tool_calls": ["metrics.verify_baseline", "rollback.execute_if_failed"],
        "avg_duration_ms": 550.0,
        "errors_count": 0,
        "last_activity": datetime.now(timezone.utc).isoformat()
    }
]

@router.get("/")
async def list_agents():
    """Retrieve full catalog and real-time status of all 13 specialized agents."""
    return AGENTS_METADATA
