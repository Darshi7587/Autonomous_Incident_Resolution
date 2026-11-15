import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.agents.state import AgentWorkflowState
from backend.detection.dynamic_baseline import DynamicBaselineEstimator
from backend.detection.isolation_forest import MultivariateAnomalyDetector

logger = logging.getLogger("nexus.agent.anomaly")

class AnomalyDetectionAgent:
    """Agent 3: Statistical & ML Anomaly Detection Agent"""
    def __init__(self, baseline_estimator: DynamicBaselineEstimator, iforest_detector: MultivariateAnomalyDetector):
        self.baseline_estimator = baseline_estimator
        self.iforest_detector = iforest_detector
        self.name = "Anomaly Detection Agent"

    async def execute(self, state: AgentWorkflowState) -> AgentWorkflowState:
        logger.info(f"[{self.name}] Running statistical baseline & Isolation Forest evaluation...")
        active_metrics = state.get("active_metrics", {})
        anomalies = []

        # 1. Statistical Dynamic Baseline Evaluation
        for metric_name, results in active_metrics.items():
            if isinstance(results, list):
                for item in results:
                    val = 0.0
                    if isinstance(item, dict) and "value" in item and len(item["value"]) >= 2:
                        try:
                            val = float(item["value"][1])
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(item, (int, float)):
                        val = float(item)

                    key = f"{metric_name}:{item.get('metric', {}).get('instance', 'default') if isinstance(item, dict) else 'metric'}"
                    eval_result = self.baseline_estimator.update_and_evaluate(key, val)
                    if eval_result.get("is_anomalous"):
                        anomalies.append({
                            "type": "STATISTICAL_BASELINE_DEVIATION",
                            "metric": metric_name,
                            "value": val,
                            "z_score": eval_result.get("z_score"),
                            "upper_bound": eval_result.get("upper_bound"),
                            "severity": eval_result.get("severity")
                        })

        # 2. Multivariate Isolation Forest Evaluation
        # Feature vector: [cpu, memory, disk, net_rate, req_rate, err_rate, latency]
        # In the absence of raw streaming vectors, synthesize sample from current state
        sample_vector = [
            float(active_metrics.get("host_cpu_utilization", 25.0)[0]["value"][1]) if active_metrics.get("host_cpu_utilization") else 45.0,
            float(active_metrics.get("host_memory_utilization", 50.0)[0]["value"][1]) if active_metrics.get("host_memory_utilization") else 60.0,
            42.0, 120.0, 250.0, 0.0, 45.0
        ]
        ml_score = self.iforest_detector.score_vector(sample_vector)
        if ml_score.get("is_anomalous"):
            anomalies.append({
                "type": "MULTIVARIATE_ISOLATION_FOREST_OUTLIER",
                "anomaly_score": ml_score.get("anomaly_score"),
                "features": ml_score.get("features"),
                "severity": "HIGH" if ml_score.get("anomaly_score", 0) > 0.8 else "MEDIUM"
            })

        state["anomaly_findings"] = anomalies
        state["agent_logs"].append({
            "agent": self.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "ANOMALIES_EVALUATED",
            "summary": f"Detected {len(anomalies)} statistical & ML anomalies across monitored streams."
        })
        return state
