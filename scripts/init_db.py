"""
佛学大师项目 - 数据库初始化脚本
"""
import asyncio
from loguru import logger

from core.config import settings
from core.database import postgres_db, neo4j_db


async def init_postgres():
    """初始化PostgreSQL数据库表"""
    logger.info("初始化PostgreSQL表结构...")

    # TODO: 使用SQLAlchemy创建表结构
    # 表包括：sutras, chapters, concepts, figures, schools, quotes

    logger.info("PostgreSQL初始化完成")


async def init_neo4j():
    """初始化Neo4j约束和索引"""
    logger.info("初始化Neo4j约束和索引...")

    # 创建约束
    constraints = [
        "CREATE CONSTRAINT sutra_id IF NOT EXISTS FOR (s:Sutra) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT figure_id IF NOT EXISTS FOR (f:Figure) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT school_id IF NOT EXISTS FOR (sc:School) REQUIRE sc.id IS UNIQUE",
    ]

    for constraint in constraints:
        try:
            await neo4j_db.execute_query(constraint)
            logger.info(f"创建约束: {constraint[:50]}...")
        except Exception as e:
            logger.warning(f"约束创建失败或已存在: {e}")

    logger.info("Neo4j初始化完成")


async def main():
    """主函数"""
    logger.info("开始初始化数据库...")

    try:
        await postgres_db.init()
        await init_postgres()

        await neo4j_db.init()
        await init_neo4j()

        logger.info("✅ 数据库初始化完成")

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise

    finally:
        await postgres_db.close()
        await neo4j_db.close()


if __name__ == "__main__":
    asyncio.run(main())
