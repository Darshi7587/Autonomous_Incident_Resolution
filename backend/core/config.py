import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Server
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "nexus-ai-enterprise-secret-key-change-in-production"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/nexus_ai.db"

    # ChromaDB Vector Store
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Prometheus
    PROMETHEUS_URL: str = "http://localhost:9090"
    PROMETHEUS_TIMEOUT_SECONDS: int = 10

    # Loki
    LOKI_URL: str = "http://localhost:3100"
    LOKI_TIMEOUT_SECONDS: int = 10

    # Docker
    DOCKER_HOST: Optional[str] = None

    # OpenTelemetry
    OTEL_COLLECTOR_URL: str = "http://localhost:4318"

    # LLM Settings
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Anomaly Detection
    ANOMALY_SENSITIVITY: float = 2.5
    DYNAMIC_BASELINE_WINDOW: int = 50
    ISOLATION_FOREST_CONTAMINATION: float = 0.05

    # Remediation
    AUTO_APPROVE_LOW_RISK: bool = True
    REQUIRE_HUMAN_APPROVAL_HIGH_RISK: bool = True
    REMEDIATION_TIMEOUT_SECONDS: int = 60

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
