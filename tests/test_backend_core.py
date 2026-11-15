import pytest
import asyncio
import numpy as np
from backend.database.session import init_db
from backend.main import seed_initial_data
from backend.knowledge.chroma_store import get_chroma_store
from backend.detection.dynamic_baseline import DynamicBaselineEstimator
from backend.detection.isolation_forest import MultivariateAnomalyDetector

def test_database_and_chroma():
    async def _run():
        await init_db()
        await seed_initial_data()
        store = get_chroma_store()
        results = store.query_runbooks("High CPU and thread starvation on container")
        assert len(results) > 0
        assert "title" in results[0]
        print(f"Top match: {results[0]['title']}")
    asyncio.run(_run())

def test_dynamic_baseline():
    estimator = DynamicBaselineEstimator(window_size=20, k_factor=2.0)
    # Feed normal values
    for _ in range(15):
        res = estimator.update_and_evaluate("test_metric", 25.0)
    assert not res["is_anomalous"]
    # Feed extreme spike
    spike_res = estimator.update_and_evaluate("test_metric", 98.0)
    assert spike_res["is_anomalous"]
    assert spike_res["severity"] in ["WARNING", "CRITICAL"]

def test_isolation_forest():
    detector = MultivariateAnomalyDetector(contamination=0.1)
    # Feed baseline vectors with slight natural variation
    np.random.seed(42)
    base_pattern = np.array([25.0, 40.0, 30.0, 100.0, 200.0, 0.0, 20.0])
    for _ in range(35):
        jitter = np.random.normal(0, 1.0, size=7)
        detector.ingest_sample((base_pattern + jitter).tolist())
    assert detector.is_fitted

    # Normal sample
    norm = detector.score_vector([25.5, 40.2, 30.1, 101.0, 202.0, 0.0, 21.0])
    assert not norm["is_anomalous"]

    # Extreme outlier anomaly
    outlier = detector.score_vector([99.0, 98.0, 95.0, 5000.0, 10.0, 85.0, 4500.0])
    assert outlier["is_anomalous"]
