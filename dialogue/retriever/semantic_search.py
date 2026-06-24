"""
佛学大师项目 - 语义检索
使用本地 GPU (RTX 4090) 进行 embedding
"""
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from loguru import logger

from core.config import settings
from core.embedding import get_embedding_service


class SemanticSearch:
    """
    语义检索

    基于向量相似度的语义搜索
    使用本地 embedding 模型 (BAAI/bge-large-zh-v1.5)
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.index: List[Dict[str, Any]] = []  # 内存索引（临时方案）
        self.index_loaded = False

    async def load_index(self, index_path: Optional[Path] = None):
        """
        加载索引

        Args:
            index_path: 索引文件路径，默认从配置读取
        """
        if index_path is None:
            index_path = Path(settings.processed_data_dir) / "embeddings_index.json"

        if not index_path.exists():
            logger.warning(f"索引文件不存在: {index_path}")
            logger.info("需要先构建索引，请运行: python scripts/build_index.py")
            return

        with open(index_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)

        self.index_loaded = True
        logger.info(f"✅ 加载索引成功，共 {len(self.index)} 条记录")

    async def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        执行语义搜索

        Args:
            query: 搜索查询
            top_k: 返回结果数量
            threshold: 相似度阈值

        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        if not self.index_loaded:
            await self.load_index()

        if not self.index:
            logger.warning("索引为空，无法搜索")
            return []

        # 获取查询向量
        query_embedding = await self.embedding_service.embed_query(query)

        # 提取所有文档向量
        doc_embeddings = [item["embedding"] for item in self.index]

        # 计算相似度
        similarities = self.embedding_service.compute_similarity(
            query_embedding,
            doc_embeddings,
            top_k=top_k,
        )

        # 过滤并构建结果
        results = []
        for idx, score in similarities:
            if score >= threshold:
                item = self.index[idx].copy()
                item["score"] = score
                # 移除 embedding 字段（太大）
                item.pop("embedding", None)
                results.append(item)

        logger.info(f"语义搜索: '{query}' -> {len(results)} 条结果")
        return results

    async def add_to_index(
        self,
        text: str,
        metadata: Dict[str, Any],
    ):
        """
        添加文档到索引

        Args:
            text: 文档文本
            metadata: 元数据
        """
        # 获取 embedding
        embedding = await self.embedding_service.embed_query(text)

        # 添加到索引
        self.index.append({
            "text": text,
            "embedding": embedding,
            **metadata,
        })

        self.index_loaded = True

    async def save_index(self, index_path: Optional[Path] = None):
        """保存索引到文件"""
        if index_path is None:
            index_path = Path(settings.processed_data_dir) / "embeddings_index.json"

        # 确保目录存在
        index_path.parent.mkdir(parents=True, exist_ok=True)

        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ 索引已保存: {index_path}")
