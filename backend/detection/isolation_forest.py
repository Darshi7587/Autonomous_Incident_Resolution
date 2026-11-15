import numpy as np
import logging
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("nexus.detection.isolation_forest")

class MultivariateAnomalyDetector:
    """
    Unsupervised Multivariate Anomaly Detector using Scikit-Learn's Isolation Forest.
    Evaluates multi-dimensional telemetry vectors:
    [cpu_util, memory_util, disk_util, net_rate_kb, req_rate_rps, error_rate_pct, latency_ms]
    """
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=42
        )
        self.feature_names = [
            "cpu_util", "memory_util", "disk_util",
            "net_rate_kb", "req_rate_rps", "error_rate_pct", "latency_ms"
        ]
        self.is_fitted = False
        self._training_buffer = []

    def fit_baseline(self, historical_vectors: np.ndarray):
        """Fit Isolation Forest on baseline healthy system observations."""
        if len(historical_vectors) < 20:
            logger.info("Insufficient samples to fit Isolation Forest baseline; accumulating...")
            return False
        try:
            self.model.fit(historical_vectors)
            self.is_fitted = True
            logger.info(f"Isolation Forest baseline successfully fitted on {len(historical_vectors)} samples.")
            return True
        except Exception as e:
            logger.error(f"Error fitting Isolation Forest: {e}")
            return False

    def ingest_sample(self, vector: List[float]):
        """Accumulate samples in memory to continuously retrain baseline."""
        self._training_buffer.append(vector)
        if len(self._training_buffer) >= 30 and not self.is_fitted:
            arr = np.array(self._training_buffer)
            self.fit_baseline(arr)

    def score_vector(self, vector: List[float]) -> Dict[str, Any]:
        """
        Score a real-time observation vector.
        Returns:
            - is_anomalous (bool): True if Isolation Forest flags as outlier (-1)
            - anomaly_score (float): Inverted decision function score [0.0 - 1.0] (higher = more anomalous)
        """
        arr = np.array([vector])
        if not self.is_fitted:
            self.ingest_sample(vector)
            return {
                "is_anomalous": False,
                "anomaly_score": 0.0,
                "model_status": "WARMING_UP",
                "samples_collected": len(self._training_buffer)
            }

        try:
            # -1 for anomaly, 1 for inlier
            prediction = self.model.predict(arr)[0]
            raw_score = self.model.decision_function(arr)[0]
            # Normal inliers have raw_score > 0, anomalous outliers have raw_score < 0
            normalized_score = float(np.clip(0.5 - (raw_score * 2.0), 0.0, 1.0))
            is_anomaly = bool(prediction == -1 or raw_score < 0.0)

            return {
                "is_anomalous": is_anomaly,
                "anomaly_score": round(normalized_score, 3),
                "model_status": "ONLINE",
                "features": dict(zip(self.feature_names, vector))
            }
        except Exception as e:
            logger.error(f"Error evaluating Isolation Forest prediction: {e}")
            return {"is_anomalous": False, "anomaly_score": 0.0, "error": str(e)}
