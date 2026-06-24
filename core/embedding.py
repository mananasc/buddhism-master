"""
佛学大师项目 - 远程 Embedding 服务
调用 Windows 4090 上的 Ollama (bge-m3)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Optional
import asyncio

import httpx
from loguru import logger

from core.config import settings


class RemoteEmbeddingService:
    """
    远程 Embedding 服务

    调用 Windows 4090 上的 Ollama bge-m3
    """

    def __init__(
        self,
        base_url: str = "http://192.168.50.94:11434",  # Windows 4090
        model: str = "bge-m3",
    ):
        self.base_url = base_url
        self.model = model
        self.dimension = 1024  # bge-m3 输出维度

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文本向量

        Args:
            texts: 文本列表

        Returns:
            List[List[float]]: 向量列表
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Ollama embedding API
            response = await client.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.model,
                    "input": texts,
                }
            )
            response.raise_for_status()
            result = response.json()

            embeddings = result.get("embeddings", [])
            logger.debug(f"Embedding {len(texts)} texts -> {len(embeddings)} vectors")
            return embeddings

    async def embed_query(self, query: str) -> List[float]:
        """
        获取查询向量

        Args:
            query: 查询文本

        Returns:
            List[float]: 查询向量
        """
        embeddings = await self.embed_texts([query])
        return embeddings[0] if embeddings else []

    def compute_similarity(
        self,
        query_embedding: List[float],
        doc_embeddings: List[List[float]],
        top_k: int = 5,
    ) -> List[tuple]:
        """
        计算相似度并返回 top-k (余弦相似度)

        Args:
            query_embedding: 查询向量
            doc_embeddings: 文档向量列表
            top_k: 返回数量

        Returns:
            List[tuple]: (索引, 相似度) 列表
        """
        import numpy as np

        query = np.array(query_embedding)
        docs = np.array(doc_embeddings)

        # 余弦相似度
        similarities = docs @ query / (
            np.linalg.norm(docs, axis=1) * np.linalg.norm(query) + 1e-8
        )

        # 获取 top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [(int(idx), float(similarities[idx])) for idx in top_indices]

    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
                logger.info(f"✅ Ollama 连接成功: {self.base_url}")
                logger.info(f"   可用模型: {[m['name'] for m in models]}")
                return True
        except Exception as e:
            logger.error(f"❌ Ollama 连接失败: {e}")
            return False


# 全局实例
_embedding_service: Optional[RemoteEmbeddingService] = None


def get_embedding_service() -> RemoteEmbeddingService:
    """获取 embedding 服务实例"""
    global _embedding_service
    if _embedding_service is None:
        # 从配置读取 Ollama 地址
        ollama_url = getattr(settings, "OLLAMA_BASE_URL", "http://192.168.50.94:11434")
        _embedding_service = RemoteEmbeddingService(base_url=ollama_url)
    return _embedding_service


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """便捷函数：批量嵌入"""
    service = get_embedding_service()
    return await service.embed_texts(texts)


async def embed_query(query: str) -> List[float]:
    """便捷函数：查询嵌入"""
    service = get_embedding_service()
    return await service.embed_query(query)


async def test_embedding():
    """测试 embedding 服务"""
    logger.info("测试远程 Embedding 服务...")

    service = get_embedding_service()

    # 测试连接
    if not await service.test_connection():
        logger.error("无法连接到 Ollama，请检查:")
        logger.error("  1. Windows 4090 是否开机")
        logger.error("  2. Ollama 是否运行")
        logger.error("  3. 网络是否可达")
        return

    # 测试文本
    texts = [
        "空性是佛教核心概念",
        "般若波罗蜜多心经",
        "应无所住而生其心",
        "色即是空，空即是色",
    ]

    # 获取向量
    embeddings = await service.embed_texts(texts)
    logger.info(f"生成 {len(embeddings)} 个向量，维度: {len(embeddings[0])}")

    # 测试查询
    query = "什么是空性？"
    query_embedding = await service.embed_query(query)

    # 计算相似度
    similarities = service.compute_similarity(query_embedding, embeddings, top_k=3)
    logger.info(f"查询: {query}")
    logger.info("Top-3 相似文本:")
    for idx, score in similarities:
        logger.info(f"  {score:.4f} - {texts[idx]}")

    return embeddings


if __name__ == "__main__":
    asyncio.run(test_embedding())
