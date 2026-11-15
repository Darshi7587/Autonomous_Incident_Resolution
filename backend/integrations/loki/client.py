import httpx
import logging
import time
from typing import Dict, Any, List, Optional
from backend.core.config import settings

logger = logging.getLogger("nexus.integrations.loki")

class LokiClient:
    """
    Asynchronous client for Grafana Loki LogQL API.
    Enables log pattern search, error stream retrieval, and timestamp-based correlation.
    """
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10):
        self.base_url = (base_url or settings.LOKI_URL).rstrip("/")
        self.timeout = timeout

    async def query_range(
        self,
        query: str,
        start_ns: Optional[int] = None,
        end_ns: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Execute a LogQL range query.
        Timestamps in nanoseconds. Defaults to last 1 hour if unspecified.
        """
        url = f"{self.base_url}/loki/api/v1/query_range"
        now_ns = int(time.time() * 1e9)
        start = start_ns or (now_ns - 3600 * int(1e9))
        end = end_ns or now_ns

        params = {
            "query": query,
            "start": str(start),
            "end": str(end),
            "limit": str(limit),
            "direction": "BACKWARD"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    streams = data.get("data", {}).get("result", [])
                    extracted_logs = []
                    for stream in streams:
                        labels = stream.get("stream", {})
                        values = stream.get("values", [])
                        for val in values:
                            if len(val) >= 2:
                                extracted_logs.append({
                                    "timestamp_ns": int(val[0]),
                                    "line": val[1],
                                    "labels": labels
                                })
                    return extracted_logs
                return []
            except Exception as e:
                logger.error(f"Error executing Loki query ({query}): {e}")
                return []

    async def search_errors(self, service: Optional[str] = None, container: Optional[str] = None, window_seconds: int = 3600) -> List[Dict[str, Any]]:
        """Specialized search for error and exception logs."""
        query_parts = []
        if container:
            query_parts.append(f'container=~".*{container}.*"')
        elif service:
            query_parts.append(f'service=~".*{service}.*"')
        
        selector = f"{{{','.join(query_parts)}}}" if query_parts else '{job=~".+"}'
        logql = f'{selector} |~ "(?i)(error|exception|fail|panic|fatal|timeout|refused)"'
        
        now_ns = int(time.time() * 1e9)
        start_ns = now_ns - window_seconds * int(1e9)
        return await self.query_range(logql, start_ns=start_ns, end_ns=now_ns, limit=200)

    async def check_health(self) -> Dict[str, Any]:
        """Verify Loki server connectivity."""
        url = f"{self.base_url}/ready"
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                response = await client.get(url)
                is_ready = response.status_code == 200
                return {"connected": is_ready, "url": self.base_url, "status": "READY" if is_ready else "NOT_READY"}
            except Exception as e:
                return {"connected": False, "url": self.base_url, "status": "UNREACHABLE", "error": str(e)}
