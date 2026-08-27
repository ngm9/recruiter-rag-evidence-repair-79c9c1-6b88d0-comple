from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path("/root/task")
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    database_url: str = Field(
        default="postgresql://raguser:ragpass@localhost:5432/ragdb"
    )
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    data_dir: Path = BASE_DIR / "data"
    embedding_model: str = "BAAI/bge-small-en-v1.5"


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql://raguser:ragpass@localhost:5432/ragdb",
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
