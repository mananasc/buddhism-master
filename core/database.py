"""
佛学大师项目 - 数据库连接管理
支持 PostgreSQL, Neo4j, Redis
"""
from typing import AsyncGenerator, Optional, Any
from contextlib import asynccontextmanager

import asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from neo4j import AsyncGraphDatabase, AsyncDriver
import redis.asyncio as redis

from core.config import settings


# ============ PostgreSQL 连接 ============

class PostgreSQLManager:
    """PostgreSQL 异步连接管理器"""

    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.async_session: Optional[async_sessionmaker] = None

    async def init(self):
        """初始化数据库连接"""
        self.engine = create_async_engine(
            settings.postgres_async_url,
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话的上下文管理器"""
        if not self.async_session:
            raise RuntimeError("Database not initialized. Call init() first.")

        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# ============ Neo4j 连接 ============

class Neo4jManager:
    """Neo4j 异步连接管理器"""

    def __init__(self):
        self.driver: Optional[AsyncDriver] = None

    async def init(self):
        """初始化Neo4j连接"""
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        # 验证连接
        await self.driver.verify_connectivity()

    async def close(self):
        """关闭Neo4j连接"""
        if self.driver:
            await self.driver.close()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[Any, None]:
        """获取Neo4j会话的上下文管理器"""
        if not self.driver:
            raise RuntimeError("Neo4j not initialized. Call init() first.")

        async with self.driver.session() as session:
            yield session

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        database: str = "neo4j"
    ) -> list:
        """执行Cypher查询"""
        async with self.session() as session:
            result = await session.run(query, parameters or {}, database=database)
            return await result.data()


# ============ Redis 连接 ============

class RedisManager:
    """Redis 异步连接管理器"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def init(self):
        """初始化Redis连接"""
        self.client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # 验证连接
        await self.client.ping()

    async def close(self):
        """关闭Redis连接"""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        """获取数据"""
        if not self.client:
            raise RuntimeError("Redis not initialized. Call init() first.")
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """设置数据"""
        if not self.client:
            raise RuntimeError("Redis not initialized. Call init() first.")
        return await self.client.set(key, value, ex=ex)

    async def delete(self, key: str) -> int:
        """删除数据"""
        if not self.client:
            raise RuntimeError("Redis not initialized. Call init() first.")
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        if not self.client:
            raise RuntimeError("Redis not initialized. Call init() first.")
        return bool(await self.client.exists(key))

    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if not self.client:
            raise RuntimeError("Redis not initialized. Call init() first.")
        return bool(await self.client.expire(key, seconds))


# ============ 全局数据库管理器实例 ============

postgres_db = PostgreSQLManager()
neo4j_db = Neo4jManager()
redis_db = RedisManager()


async def init_all_databases():
    """初始化所有数据库连接"""
    await postgres_db.init()
    await neo4j_db.init()
    await redis_db.init()


async def close_all_databases():
    """关闭所有数据库连接"""
    await postgres_db.close()
    await neo4j_db.close()
    await redis_db.close()


# ============ 依赖注入函数 ============

async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """获取PostgreSQL会话的依赖函数 (用于FastAPI Depends)"""
    async with postgres_db.session() as session:
        yield session


async def get_neo4j_session():
    """获取Neo4j会话的依赖函数 (用于FastAPI Depends)"""
    async with neo4j_db.session() as session:
        yield session
