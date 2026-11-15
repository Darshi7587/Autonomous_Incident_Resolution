import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("nexus.integrations.docker")

class DockerClient:
    """
    Asynchronous wrapper around Docker Engine API using the Docker SDK for Python.
    Provides infrastructure discovery, live container metrics, logs, and remediation commands.
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            import docker
            if self.base_url:
                self._client = docker.DockerClient(base_url=self.base_url)
            else:
                self._client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}. Docker features will report offline.")
            self._client = None

    def _is_available(self) -> bool:
        if self._client is None:
            self._init_client()
        return self._client is not None

    async def ping(self) -> bool:
        """Check if Docker Daemon is running and responsive."""
        if not self._is_available():
            return False
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, self._client.ping)
        except Exception as e:
            logger.debug(f"Docker ping failed: {e}")
            return False

    async def list_containers(self, all_containers: bool = True) -> List[Dict[str, Any]]:
        """Discover connected containers and their current state."""
        if not self._is_available():
            return []
        loop = asyncio.get_running_loop()
        try:
            containers = await loop.run_in_executor(
                None, lambda: self._client.containers.list(all=all_containers)
            )
            discovered = []
            for c in containers:
                discovered.append({
                    "id": c.id[:12],
                    "name": c.name,
                    "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                    "status": c.status,
                    "state": c.attrs.get("State", {}).get("Status", "unknown"),
                    "created": c.attrs.get("Created"),
                    "restart_count": c.attrs.get("RestartCount", 0),
                    "ports": c.attrs.get("NetworkSettings", {}).get("Ports", {}),
                    "health": c.attrs.get("State", {}).get("Health", {}).get("Status", "none")
                })
            return discovered
        except Exception as e:
            logger.error(f"Error listing Docker containers: {e}")
            return []

    async def get_container_stats(self, container_name_or_id: str) -> Dict[str, Any]:
        """Fetch instantaneous CPU and memory metrics for a container."""
        if not self._is_available():
            return {"error": "Docker client unavailable"}
        loop = asyncio.get_running_loop()
        try:
            container = await loop.run_in_executor(
                None, lambda: self._client.containers.get(container_name_or_id)
            )
            raw_stats = await loop.run_in_executor(
                None, lambda: container.stats(stream=False)
            )
            # Calculate CPU percentage
            cpu_delta = raw_stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0) - \
                        raw_stats.get("precpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
            system_delta = raw_stats.get("cpu_stats", {}).get("system_cpu_usage", 0) - \
                           raw_stats.get("precpu_stats", {}).get("system_cpu_usage", 0)
            online_cpus = raw_stats.get("cpu_stats", {}).get("online_cpus", 1) or 1
            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0

            # Calculate Memory
            mem_usage = raw_stats.get("memory_stats", {}).get("usage", 0)
            mem_limit = raw_stats.get("memory_stats", {}).get("limit", 1) or 1
            mem_percent = (mem_usage / mem_limit) * 100.0

            return {
                "container_id": container.id[:12],
                "container_name": container.name,
                "status": container.status,
                "cpu_percent": round(cpu_percent, 2),
                "memory_usage_mb": round(mem_usage / (1024 * 1024), 2),
                "memory_limit_mb": round(mem_limit / (1024 * 1024), 2),
                "memory_percent": round(mem_percent, 2),
            }
        except Exception as e:
            logger.error(f"Error fetching stats for {container_name_or_id}: {e}")
            return {"error": str(e), "container": container_name_or_id}

    async def get_container_logs(self, container_name_or_id: str, tail: int = 100) -> str:
        """Fetch latest stderr/stdout logs from a container."""
        if not self._is_available():
            return "Docker client unavailable"
        loop = asyncio.get_running_loop()
        try:
            container = await loop.run_in_executor(
                None, lambda: self._client.containers.get(container_name_or_id)
            )
            logs = await loop.run_in_executor(
                None, lambda: container.logs(tail=tail).decode("utf-8", errors="replace")
            )
            return logs
        except Exception as e:
            logger.error(f"Error fetching container logs: {e}")
            return f"Error fetching logs: {e}"

    async def restart_container(self, container_name_or_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Safely restart a container as part of remediation."""
        if not self._is_available():
            return {"success": False, "error": "Docker client unavailable"}
        loop = asyncio.get_running_loop()
        try:
            container = await loop.run_in_executor(
                None, lambda: self._client.containers.get(container_name_or_id)
            )
            await loop.run_in_executor(
                None, lambda: container.restart(timeout=timeout)
            )
            return {
                "success": True,
                "container": container_name_or_id,
                "status": container.status,
                "action": "restart",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error restarting container {container_name_or_id}: {e}")
            return {"success": False, "error": str(e), "container": container_name_or_id}
