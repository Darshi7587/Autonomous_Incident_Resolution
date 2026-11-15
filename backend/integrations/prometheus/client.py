import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.core.config import settings

logger = logging.getLogger("nexus.integrations.prometheus")

class PrometheusClient:
    """
    Asynchronous client for interacting with Prometheus HTTP API.
    Provides PromQL querying, range queries, target inspection, and telemetry fetching.
    """
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10):
        self.base_url = (base_url or settings.PROMETHEUS_URL).rstrip("/")
        self.timeout = timeout

    async def query(self, promql: str) -> Dict[str, Any]:
        """Execute an instant PromQL query."""
        url = f"{self.base_url}/api/v1/query"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params={"query": promql})
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", {})
                logger.warning(f"Prometheus query returned status: {data.get('status')}")
                return {"result": []}
            except Exception as e:
                logger.error(f"Error querying Prometheus ({promql}): {e}")
                return {"result": [], "error": str(e)}

    async def query_range(self, promql: str, start: float, end: float, step: str = "15s") -> Dict[str, Any]:
        """Execute a PromQL range query over a specified timeframe."""
        url = f"{self.base_url}/api/v1/query_range"
        params = {
            "query": promql,
            "start": str(start),
            "end": str(end),
            "step": step
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", {})
                return {"result": []}
            except Exception as e:
                logger.error(f"Error executing range query ({promql}): {e}")
                return {"result": [], "error": str(e)}

    async def get_targets(self) -> List[Dict[str, Any]]:
        """Retrieve active Prometheus scrape targets and their health status."""
        url = f"{self.base_url}/api/v1/targets"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", {}).get("activeTargets", [])
                return []
            except Exception as e:
                logger.error(f"Error fetching Prometheus targets: {e}")
                return []

    async def check_health(self) -> Dict[str, Any]:
        """Verify connectivity to Prometheus."""
        url = f"{self.base_url}/-/healthy"
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                response = await client.get(url)
                is_healthy = response.status_code == 200
                return {"connected": is_healthy, "url": self.base_url, "status": "UP" if is_healthy else "DOWN"}
            except Exception as e:
                return {"connected": False, "url": self.base_url, "status": "UNREACHABLE", "error": str(e)}

    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Gathers comprehensive telemetry across host and containers.
        Queries CPU, Memory, Disk, Network, and application metrics.
        """
        queries = {
            "host_cpu_utilization": "100 - (avg(irate(node_cpu_seconds_total{mode='idle'}[1m])) * 100)",
            "host_memory_utilization": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "host_disk_utilization": "(1 - (node_filesystem_free_bytes{mountpoint='/'} / node_filesystem_size_bytes{mountpoint='/'})) * 100",
            "container_cpu": "sum(rate(container_cpu_usage_seconds_total[1m])) by (name)",
            "container_memory": "sum(container_memory_working_set_bytes) by (name)",
            "http_error_rate": "sum(rate(http_requests_total{status=~'5..'}[1m])) / sum(rate(http_requests_total[1m])) * 100",
            "http_latency_p95": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[1m])) by (le))"
        }

        results = {}
        for metric_name, query_str in queries.items():
            res = await self.query(query_str)
            results[metric_name] = res.get("result", [])
        return results
