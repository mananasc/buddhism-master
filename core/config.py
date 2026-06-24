"""
佛学大师项目 - 核心配置管理
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "buddhism-master"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, description="调试模式")
    API_PREFIX: str = "/api"

    # 服务器配置
    HOST: str = Field(default="0.0.0.0", description="服务主机")
    PORT: int = Field(default=8000, description="服务端口")

    # PostgreSQL配置
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL主机")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL端口")
    POSTGRES_DB: str = Field(default="buddhism_master", description="数据库名")
    POSTGRES_USER: str = Field(default="postgres", description="数据库用户")
    POSTGRES_PASSWORD: str = Field(default="", description="数据库密码")

    @property
    def postgres_url(self) -> str:
        """获取PostgreSQL连接URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def postgres_async_url(self) -> str:
        """获取PostgreSQL异步连接URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Neo4j配置
    NEO4J_URI: str = Field(default="bolt://localhost:7687", description="Neo4j连接URI")
    NEO4J_USER: str = Field(default="neo4j", description="Neo4j用户名")
    NEO4J_PASSWORD: str = Field(default="", description="Neo4j密码")

    # Redis配置
    REDIS_HOST: str = Field(default="localhost", description="Redis主机")
    REDIS_PORT: int = Field(default=6379, description="Redis端口")
    REDIS_DB: int = Field(default=0, description="Redis数据库编号")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis密码")

    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # AI API配置 - 通义千问
    DASHSCOPE_API_KEY: str = Field(default="", description="通义千问API密钥")
    DASHSCOPE_MODEL: str = Field(default="qwen-plus", description="通义千问模型")

    # AI API配置 - OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API密钥")
    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI模型")
    OPENAI_BASE_URL: Optional[str] = Field(default=None, description="OpenAI API基础URL")

    # AI提供商选择: "dashscope" 或 "openai"
    AI_PROVIDER: str = Field(default="dashscope", description="AI提供商")

    # 向量数据库配置 - Milvus
    MILVUS_HOST: str = Field(default="localhost", description="Milvus主机")
    MILVUS_PORT: int = Field(default=19530, description="Milvus端口")
    MILVUS_COLLECTION: str = Field(default="buddhism_knowledge", description="Milvus集合名")

    # 向量数据库配置 - Qdrant (备选)
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant主机")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant端口")
    QDRANT_COLLECTION: str = Field(default="buddhism_knowledge", description="Qdrant集合名")

    # 向量数据库选择: "milvus" 或 "qdrant"
    VECTOR_DB_PROVIDER: str = Field(default="milvus", description="向量数据库提供商")

    # Deerpark API配置
    DEERPARK_API_BASE: str = Field(
        default="https://deerpark.app/api/v1",
        description="Deerpark API基础URL"
    )

    # 对话配置
    MAX_CONVERSATION_HISTORY: int = Field(default=20, description="最大对话历史条数")
    CONVERSATION_CACHE_TTL: int = Field(default=3600, description="对话缓存TTL(秒)")
    MAX_CONTEXT_LENGTH: int = Field(default=4000, description="最大上下文长度(字符)")

    # 检索配置
    TOP_K_RESULTS: int = Field(default=5, description="检索返回结果数量")
    SEMANTIC_SEARCH_THRESHOLD: float = Field(default=0.7, description="语义搜索相似度阈值")

    # 路径配置
    BASE_DIR: str = Field(default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def data_dir(self) -> str:
        """数据目录"""
        return os.path.join(self.BASE_DIR, "data")

    @property
    def raw_data_dir(self) -> str:
        """原始数据目录"""
        return os.path.join(self.data_dir, "raw")

    @property
    def processed_data_dir(self) -> str:
        """处理后数据目录"""
        return os.path.join(self.data_dir, "processed")

    @property
    def export_data_dir(self) -> str:
        """导出数据目录"""
        return os.path.join(self.data_dir, "exports")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
