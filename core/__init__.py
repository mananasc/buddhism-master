"""
佛学大师项目 - 核心模块
"""
from core.config import settings, get_settings
from core.database import (
    postgres_db,
    neo4j_db,
    redis_db,
    init_all_databases,
    close_all_databases,
)
from core.ai_client import get_ai_client, AIClientFactory

__all__ = [
    "settings",
    "get_settings",
    "postgres_db",
    "neo4j_db",
    "redis_db",
    "init_all_databases",
    "close_all_databases",
    "get_ai_client",
    "AIClientFactory",
]
