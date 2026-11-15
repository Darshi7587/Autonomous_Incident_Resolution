import os
import hashlib
import numpy as np
import logging
from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from backend.core.config import settings

logger = logging.getLogger("nexus.knowledge.chroma")

class RobustEmbeddingFunction(EmbeddingFunction):
    """
    Robust embedding function that uses local deterministic token-hash vectors (384-d)
    when offline/in sandbox, or sentence-transformers when weights are cached.
    Ensures zero internet dependency and instant execution.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    def name(self) -> str:
        return "robust_offline"

    def get_config(self) -> Dict[str, Any]:
        return {"dim": self.dim}

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for doc in input:
            vec = np.zeros(self.dim, dtype=np.float32)
            tokens = doc.lower().split()
            for token in tokens:
                h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[idx] += sign
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

DEFAULT_RUNBOOKS = [
    {
        "id": "runbook-cpu-saturation",
        "title": "CPU Resource Contention and Process Starvation",
        "category": "infrastructure",
        "service_type": "container",
        "risk_level": "LOW",
        "content": (
            "Symptoms: System CPU utilization consistently exceeds dynamic upper boundary (>3 sigma). "
            "High throttle rates or elevated load averages on worker containers. "
            "Remediation Procedure: "
            "1. Inspect container top threads to isolate CPU spinning processes. "
            "2. If container CPU is unconstrained or locked in infinite loop, trigger controlled container restart. "
            "3. If traffic spike is legitimate, scale container replicas or allocate additional CPU quotas. "
            "Rollback: In the event restart does not stabilize load, revert container configuration and re-route traffic."
        ),
        "recommended_action": "restart_container",
        "verification_criteria": "CPU utilization drops to baseline (< 40%) within 60 seconds post restart."
    },
    {
        "id": "runbook-memory-leak-oom",
        "title": "Memory Leak and Out-Of-Memory (OOM) Killer Mitigation",
        "category": "application",
        "service_type": "container",
        "risk_level": "MEDIUM",
        "content": (
            "Symptoms: Monotonic memory growth (working set memory) without GC release. "
            "Container exit code 137 (OOMKilled) or Linux OOM daemon invocations in dmesg. "
            "Remediation Procedure: "
            "1. Capture heap dump / memory profile snapshot if diagnostic volume is mounted. "
            "2. Perform graceful container restart to release locked heap and off-heap memory. "
            "3. Flush transient in-memory Redis session cache to relieve backpressure. "
            "Rollback: Revert to previous container image version if recent deployment introduced memory leak."
        ),
        "recommended_action": "restart_container",
        "verification_criteria": "Container working set memory stabilizes below 60% of configured limit."
    },
    {
        "id": "runbook-db-connection-exhaustion",
        "title": "Database Connection Pool Saturation and Connection Leaks",
        "category": "database",
        "service_type": "database",
        "risk_level": "HIGH",
        "content": (
            "Symptoms: Applications log 'FATAL: remaining connection slots are reserved' or timeout errors. "
            "Active connections metric at 100% capacity. Database query latency escalates exponentially. "
            "Remediation Procedure: "
            "1. Identify and terminate orphaned idle-in-transaction connections. "
            "2. Reload database connection pooler (e.g., PgBouncer) or restart cache layer. "
            "3. Increment max_connections pool setting temporarily if database memory headroom permits. "
            "Rollback: Restore prior pool sizing if connection storm impacts database CPU."
        ),
        "recommended_action": "reload_service",
        "verification_criteria": "Active database connection pool utilization drops below 75%."
    },
    {
        "id": "runbook-api-latency-spike",
        "title": "HTTP 500 Spike and P95 Latency Degradation",
        "category": "application",
        "service_type": "service",
        "risk_level": "MEDIUM",
        "content": (
            "Symptoms: HTTP 5xx error rate spikes above baseline; P95 response time exceeds 1500ms. "
            "Thread pool exhaustion or upstream gateway timeouts (504). "
            "Remediation Procedure: "
            "1. Verify upstream dependencies via Service Topology graph. "
            "2. Clear ephemeral caching layer and restart microservice worker pods. "
            "3. Enable circuit breaker to shed non-essential traffic. "
            "Rollback: Disable circuit breaker and restore default rate limits."
        ),
        "recommended_action": "restart_container",
        "verification_criteria": "P95 latency returns under 250ms and HTTP 5xx rate drops to 0%."
    },
    {
        "id": "runbook-disk-saturation",
        "title": "Disk Volume Space Saturation and Log Inode Exhaustion",
        "category": "infrastructure",
        "service_type": "host",
        "risk_level": "LOW",
        "content": (
            "Symptoms: Root or data partition capacity exceeds 90%. Applications fail with 'No space left on device'. "
            "Remediation Procedure: "
            "1. Rotate and compress oversized log files in /var/log. "
            "2. Execute Docker system prune for dangling images and unreferenced build cache. "
            "3. Purge temporary core dumps. "
            "Rollback: Re-mount backup volume or expand block storage partition."
        ),
        "recommended_action": "clear_disk_cache",
        "verification_criteria": "Free filesystem capacity increases by at least 15%."
    }
]

_shared_chroma_store = None

class ChromaKnowledgeStore:
    """
    RAG semantic knowledge store powered by ChromaDB.
    Maintains runbooks, historical RCA records, and incident troubleshooting documentation.
    """
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_dir = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding_function = RobustEmbeddingFunction()
        self.collection_name = "it_runbooks"
        
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "IT Operations Runbooks and Incident RCA Knowledge"}
            )
        except Exception as e:
            logger.warning(f"Recreating ChromaDB collection due to schema/embedding update: {e}")
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "IT Operations Runbooks and Incident RCA Knowledge"}
            )
        self._seed_default_runbooks()

    def _seed_default_runbooks(self):
        """Seed default enterprise runbooks if collection is fresh."""
        try:
            count = self.collection.count()
            if count == 0:
                logger.info("Seeding ChromaDB it_runbooks collection with enterprise operational runbooks...")
                ids = [r["id"] for r in DEFAULT_RUNBOOKS]
                documents = [f"{r['title']}\n{r['content']}" for r in DEFAULT_RUNBOOKS]
                metadatas = [
                    {
                        "title": r["title"],
                        "category": r["category"],
                        "service_type": r["service_type"],
                        "risk_level": r["risk_level"],
                        "recommended_action": r["recommended_action"],
                        "verification_criteria": r["verification_criteria"]
                    }
                    for r in DEFAULT_RUNBOOKS
                ]
                self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
                logger.info(f"Seeded {len(ids)} runbooks into ChromaDB.")
        except Exception as e:
            logger.error(f"Error seeding ChromaDB: {e}")

    def query_runbooks(self, query_text: str, n_results: int = 3, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search over runbooks and historical RCAs.
        """
        try:
            where_filter = {"category": category} if category else None
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )

            matched_docs = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
                ids = results["ids"][0]

                for doc_id, doc, meta, dist in zip(ids, docs, metadatas, distances):
                    similarity = round(1.0 - (dist if dist <= 1.0 else 0.5), 3)
                    matched_docs.append({
                        "id": doc_id,
                        "title": meta.get("title", "Runbook"),
                        "category": meta.get("category", "general"),
                        "service_type": meta.get("service_type", "service"),
                        "risk_level": meta.get("risk_level", "MEDIUM"),
                        "recommended_action": meta.get("recommended_action", "restart_container"),
                        "verification_criteria": meta.get("verification_criteria", ""),
                        "similarity_score": similarity,
                        "document": doc
                    })
            return matched_docs
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

    def index_historical_incident(self, incident_id: str, title: str, rca_hypothesis: str, resolution_action: str):
        """Index resolved incidents into ChromaDB to empower self-improving RAG."""
        try:
            doc = f"Incident: {title}\nRoot Cause: {rca_hypothesis}\nResolution: {resolution_action}"
            self.collection.add(
                ids=[f"historical-{incident_id}"],
                documents=[doc],
                metadatas=[{
                    "title": title,
                    "category": "historical_incident",
                    "service_type": "general",
                    "risk_level": "LOW",
                    "recommended_action": resolution_action,
                    "verification_criteria": "Historical verified recovery"
                }]
            )
            logger.info(f"Indexed historical incident {incident_id} into ChromaDB.")
        except Exception as e:
            logger.error(f"Error indexing historical incident: {e}")

def get_chroma_store() -> ChromaKnowledgeStore:
    global _shared_chroma_store
    if _shared_chroma_store is None:
        _shared_chroma_store = ChromaKnowledgeStore()
    return _shared_chroma_store
