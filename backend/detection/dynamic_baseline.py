import numpy as np
import logging
from typing import Dict, Any, List, Optional
from collections import deque

logger = logging.getLogger("nexus.detection.baseline")

class DynamicBaselineEstimator:
    """
    Continuous statistical baseline estimator for streaming time-series metrics.
    Applies Median Absolute Deviation (MAD), Interquartile Range (IQR),
    and Exponential Moving Averages (EMA) to compute dynamic bounds without static thresholds.
    """
    def __init__(self, window_size: int = 60, k_factor: float = 2.5):
        self.window_size = window_size
        self.k_factor = k_factor
        self.history: Dict[str, deque] = {}

    def update_and_evaluate(self, metric_key: str, value: float) -> Dict[str, Any]:
        """
        Record a new metric observation and evaluate whether it deviates statistically
        from its historical dynamic baseline.
        """
        if metric_key not in self.history:
            self.history[metric_key] = deque(maxlen=self.window_size)

        buffer = self.history[metric_key]
        buffer.append(value)

        # Require a warm-up sample count before flagging anomalies
        if len(buffer) < 10:
            return {
                "metric_key": metric_key,
                "current_value": value,
                "is_anomalous": False,
                "reason": "BASELINE_WARMUP",
                "sample_count": len(buffer),
                "z_score": 0.0,
                "upper_bound": None,
                "lower_bound": None
            }

        arr = np.array(buffer)
        median = float(np.median(arr))
        q25, q75 = np.percentile(arr, [25, 75])
        iqr = float(q75 - q25)
        mean = float(np.mean(arr))
        std = float(np.std(arr))

        # Dynamic upper & lower bounds using adaptive IQR
        effective_iqr = max(iqr, 0.05 * (abs(median) if median != 0 else 1.0))
        upper_bound = median + (self.k_factor * effective_iqr)
        lower_bound = max(0.0, median - (self.k_factor * effective_iqr))

        # Modified Z-Score using Median Absolute Deviation (MAD) for robust outlier detection
        mad = float(np.median(np.abs(arr - median)))
        if mad > 0:
            modified_z_score = float(0.6745 * (value - median) / mad)
        elif std > 0:
            modified_z_score = float((value - mean) / std)
        else:
            modified_z_score = 0.0

        is_anomalous = (value > upper_bound) or (value < lower_bound) or (abs(modified_z_score) > self.k_factor * 1.5)

        severity = "INFO"
        if is_anomalous:
            if abs(modified_z_score) > self.k_factor * 2.5:
                severity = "CRITICAL"
            else:
                severity = "WARNING"

        return {
            "metric_key": metric_key,
            "current_value": value,
            "is_anomalous": bool(is_anomalous),
            "severity": severity,
            "median": round(median, 2),
            "mean": round(mean, 2),
            "std": round(std, 2),
            "iqr": round(effective_iqr, 2),
            "upper_bound": round(upper_bound, 2),
            "lower_bound": round(lower_bound, 2),
            "z_score": round(modified_z_score, 2),
            "sample_count": len(buffer)
        }
