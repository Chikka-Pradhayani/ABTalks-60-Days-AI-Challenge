"""AURONIX Production Backend Configuration.

Supports dynamic environment variable injection for:
- Railway Staging (isolated DB, staging FAISS path, staging API key)
- Railway Production (production DB, production FAISS path, vault key)
- Local Development / Docker Compose
"""

import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Settings:
    environment: str
    port: int
    host: str
    data_dir: str
    faiss_index_path: str
    database_url: str
    auronix_api_key: str
    openai_api_key: str
    redis_url: str
    cors_origins: List[str]
    rate_limit_per_hour: int
    version: str = "1.0.0"
    service_name: str = "auronix-backend"

    @property
    def is_staging(self) -> bool:
        return self.environment.lower() == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


def get_settings() -> Settings:
    """Loads and validates settings from environment variables."""
    environment = os.getenv("ENVIRONMENT", "production").strip().lower()
    
    # Railway dynamically supplies PORT
    port_str = os.getenv("PORT", "8001").strip()
    try:
        port = int(port_str)
    except ValueError:
        port = 8001

    host = os.getenv("HOST", "0.0.0.0").strip()

    # Data directory and vector index paths isolated per environment
    default_data_dir = os.path.join(os.getcwd(), "data", environment)
    data_dir = os.getenv("DATA_DIR", default_data_dir).strip()
    
    default_faiss_path = os.path.join(data_dir, f"faiss_index_{environment}.bin")
    faiss_index_path = os.getenv("FAISS_INDEX_PATH", default_faiss_path).strip()

    default_db_url = f"sqlite:///{os.path.join(data_dir, f'auronix_{environment}.db')}"
    database_url = os.getenv("DATABASE_URL", default_db_url).strip()

    auronix_api_key = os.getenv(
        "AURONIX_API_KEY",
        "auronix-staging-key-2026" if environment == "staging" else "auronix-production-vault-key-2026"
    ).strip()

    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    redis_url = os.getenv("REDIS_URL", "").strip()

    cors_raw = os.getenv("CORS_ORIGINS", "*").strip()
    if cors_raw == "*":
        cors_origins = ["*"]
    else:
        cors_origins = [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

    rate_limit = int(os.getenv("RATE_LIMIT_PER_HOUR", "20"))

    return Settings(
        environment=environment,
        port=port,
        host=host,
        data_dir=data_dir,
        faiss_index_path=faiss_index_path,
        database_url=database_url,
        auronix_api_key=auronix_api_key,
        openai_api_key=openai_api_key,
        redis_url=redis_url,
        cors_origins=cors_origins,
        rate_limit_per_hour=rate_limit,
    )
