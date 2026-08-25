# config/settings.py

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Central configuration for ClaimGuard AI."""

    # ---------------------------------------------------------
    # Base directories
    # ---------------------------------------------------------
    BASE_DIR = Path(__file__).resolve().parent.parent

    DATA_DIR = BASE_DIR / "data"
    POLICY_DIR = DATA_DIR / "policies"
    QDRANT_DIR = BASE_DIR / "qdrant_db"

    # ---------------------------------------------------------
    # OpenAI
    # ---------------------------------------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    LLM_MODEL = os.getenv(
        "LLM_MODEL",
        "gpt-4o-mini",
    )

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    EMBEDDING_DIMENSION = int(
        os.getenv("EMBEDDING_DIMENSION", "1536")
    )

    # ---------------------------------------------------------
    # Qdrant - Embedded Local Storage
    # ---------------------------------------------------------
    QDRANT_COLLECTION = os.getenv(
        "QDRANT_COLLECTION",
        "claimguard_policies",
    )

    # ---------------------------------------------------------
    # Mem0
    # ---------------------------------------------------------
    MEM0_COLLECTION = os.getenv(
        "MEM0_COLLECTION",
        "claimguard_patient_memory",
    )

    MEM0_DB_PATH = BASE_DIR / "mem0_db"

    # ---------------------------------------------------------
    # MCP Services
    # ---------------------------------------------------------
    MCP_ICD10_URL = os.getenv(
        "MCP_ICD10_URL",
        "http://localhost:8002",
    )

    MCP_TARIFF_URL = os.getenv(
        "MCP_TARIFF_URL",
        "http://localhost:8003",
    )

    MCP_CALCULATION_URL = os.getenv(
        "MCP_CALCULATION_URL",
        "http://localhost:8004",
    )

    # ---------------------------------------------------------
    # LangSmith
    # ---------------------------------------------------------
    LANGCHAIN_TRACING_V2 = os.getenv(
        "LANGCHAIN_TRACING_V2",
        "true",
    )

    LANGCHAIN_ENDPOINT = os.getenv(
        "LANGCHAIN_ENDPOINT",
        "https://api.smith.langchain.com",
    )

    LANGCHAIN_API_KEY = os.getenv(
        "LANGCHAIN_API_KEY",
        "",
    )

    LANGCHAIN_PROJECT = os.getenv(
        "LANGCHAIN_PROJECT",
        "ClaimGuard-AI",
    )

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------
    APP_NAME = os.getenv(
        "APP_NAME",
        "ClaimGuard AI",
    )

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development",
    )

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )


settings = Settings()