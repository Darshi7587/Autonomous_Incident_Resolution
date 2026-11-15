import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from backend.database.session import init_db
from backend.main import seed_initial_data
from backend.knowledge.chroma_store import get_chroma_store
from backend.detection.dynamic_baseline import DynamicBaselineEstimator
from backend.detection.isolation_forest import MultivariateAnomalyDetector

def test_db_and_chroma():
    print("[TEST 1] Testing Database Schema & ChromaDB RAG...")
    init_db()
    seed_initial_data()
    store = get_chroma_store()
    results = store.query_runbooks("High CPU and thread starvation on container")
    assert len(results) > 0, "No runbooks returned from ChromaDB"
    print(f"  -> Chroma returned {len(results)} runbooks. Top match: '{results[0]['title']}'")
    print("  -> Database and ChromaDB RAG passed.")

def test_dynamic_baseline():
    print("[TEST 2] Testing Dynamic Statistical Baselining (IQR / Z-score)...")
    estimator = DynamicBaselineEstimator(window_size=20, k_factor=2.0)
    for _ in range(15):
        res = estimator.update_and_evaluate("test_metric", 25.0)
    assert not res["is_anomalous"], "Baseline flagged normal traffic during warm-up"
    spike_res = estimator.update_and_evaluate("test_metric", 98.0)
    assert spike_res["is_anomalous"], "Dynamic baseline failed to detect extreme metric spike"
    print(f"  -> Dynamic baseline detected anomaly with Z-Score: {spike_res['z_score']}")
    print("  -> Dynamic baseline passed.")

def test_isolation_forest():
    print("[TEST 3] Testing Scikit-Learn Isolation Forest Multivariate Detection...")
    detector = MultivariateAnomalyDetector(contamination=0.1)
    np.random.seed(42)
    base = np.array([25.0, 40.0, 30.0, 100.0, 200.0, 0.0, 20.0])
    for _ in range(35):
        detector.ingest_sample((base + np.random.normal(0, 1, 7)).tolist())
    assert detector.is_fitted, "Isolation Forest failed to fit"
    norm = detector.score_vector([25.5, 40.2, 30.1, 101.0, 202.0, 0.0, 21.0])
    assert not norm["is_anomalous"], "Normal vector flagged as anomaly"
    outlier = detector.score_vector([99.0, 98.0, 95.0, 5000.0, 10.0, 85.0, 4500.0])
    assert outlier["is_anomalous"], "Extreme outlier missed by Isolation Forest"
    print(f"  -> Isolation Forest anomaly score: {outlier['anomaly_score']}")
    print("  -> Isolation Forest passed.")

def main():
    print("=== NEXUS AI CORE TEST SUITE ===")
    test_db_and_chroma()
    test_dynamic_baseline()
    test_isolation_forest()
    print("=== ALL CORE TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
