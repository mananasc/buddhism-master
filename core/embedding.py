"""
佛学大师项目 - 本地 Embedding 服务
使用本地 GPU (RTX 4090) 运行 embedding 模型
"""
from typing import List, Optional
import asyncio
from functools import lru_cache

import numpy as np
from loguru import logger


class LocalEmbeddingService:
    """
    本地 Embedding 服务

    使用 sentence-transformers 在本地 GPU 上运行
    推荐模型: BAAI/bge-large-zh-v1.5 (中文优化)
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-zh-v1.5",
        device: str = "cuda",  # 使用 GPU
        batch_size: int = 32,
    ):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.model = None
        self.dimension = 1024  # bge-large 的向量维度

    def load_model(self):
        """加载模型（首次调用时）"""
        if self.model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"加载 Embedding 模型: {self.model_name}")
            logger.info(f"设备: {self.device}")

            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )

            # 获取实际维度
            test_embedding = self.model.encode(["测试"])
            self.dimension = len(test_embedding[0])

            logger.info(f"✅ 模型加载成功，向量维度: {self.dimension}")

        except ImportError:
            logger.error("请安装 sentence-transformers: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文本向量

        Args:
            texts: 文本列表

        Returns:
            List[List[float]]: 向量列表
        """
        # 在线程池中运行 CPU/GPU 密集任务
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._embed_sync, texts)

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        """同步嵌入（内部使用）"""
        self.load_model()

        # 分批处理
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            embeddings = self.model.encode(
                batch,
                normalize_embeddings=True,  # L2 归一化
            )
            all_embeddings.extend(embeddings.tolist())

        return all_embeddings

    async def embed_query(self, query: str) -> List[float]:
        """
        获取查询向量

        Args:
            query: 查询文本

        Returns:
            List[float]: 查询向量
        """
        self.load_model()

        # 查询时使用不同的处理
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(
                [query],
                normalize_embeddings=True,
            )[0].tolist()
        )
        return embedding

    def compute_similarity(
        self,
        query_embedding: List[float],
        doc_embeddings: List[List[float]],
        top_k: int = 5,
    ) -> List[tuple]:
        """
        计算相似度并返回 top-k

        Args:
            query_embedding: 查询向量
            doc_embeddings: 文档向量列表
            top_k: 返回数量

        Returns:
            List[tuple]: (索引, 相似度) 列表
        """
        query = np.array(query_embedding)
        docs = np.array(doc_embeddings)

        # 余弦相似度（已归一化，直接点积）
        similarities = docs @ query

        # 获取 top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [(int(idx), float(similarities[idx])) for idx in top_indices]


# 全局实例（延迟加载）
_embedding_service: Optional[LocalEmbeddingService] = None


def get_embedding_service() -> LocalEmbeddingService:
    """获取 embedding 服务实例"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = LocalEmbeddingService()
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
    logger.info("测试本地 Embedding 服务...")

    service = get_embedding_service()

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
