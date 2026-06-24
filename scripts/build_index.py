"""
佛学大师项目 - 构建 Embedding 索引
使用本地 GPU (RTX 4090) 处理金刚经数据
"""
import sys
import asyncio
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from core.config import settings
from core.embedding import get_embedding_service


async def build_sutra_index():
    """构建金刚经的 embedding 索引"""
    logger.info("开始构建金刚经 Embedding 索引...")

    # 加载金刚经数据
    sutra_path = Path(settings.raw_data_dir) / "diamond_sutra.json"
    if not sutra_path.exists():
        logger.error(f"金刚经数据不存在: {sutra_path}")
        return

    with open(sutra_path, "r", encoding="utf-8") as f:
        sutra_data = json.load(f)

    logger.info(f"加载金刚经: {sutra_data['title']}")
    logger.info(f"共 {len(sutra_data['chapters'])} 品")

    # 准备文本块
    chunks = []

    # 整经摘要
    chunks.append({
        "text": f"{sutra_data['title']}：{sutra_data.get('summary', '')}",
        "type": "sutra_summary",
        "sutra_id": sutra_data["id"],
        "title": sutra_data["title"],
    })

    # 每品内容
    for chapter in sutra_data["chapters"]:
        chunks.append({
            "text": f"{sutra_data['title']} {chapter['title']}：{chapter['content']}",
            "type": "chapter",
            "sutra_id": sutra_data["id"],
            "chapter_id": chapter["id"],
            "title": chapter["title"],
        })

    logger.info(f"共 {len(chunks)} 个文本块需要 embedding")

    # 使用本地 GPU 生成 embedding
    embedding_service = get_embedding_service()

    # 批量生成 embedding
    texts = [chunk["text"] for chunk in chunks]
    embeddings = await embedding_service.embed_texts(texts)

    # 合并数据
    index = []
    for chunk, embedding in zip(chunks, embeddings):
        index.append({
            **chunk,
            "embedding": embedding,
        })

    # 保存索引
    index_path = Path(settings.processed_data_dir) / "embeddings_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 索引构建完成: {index_path}")
    logger.info(f"   共 {len(index)} 条记录，向量维度: {len(embeddings[0])}")


async def build_concept_index():
    """构建概念的 embedding 索引"""
    logger.info("开始构建概念 Embedding 索引...")

    concept_path = Path(settings.raw_data_dir) / "concepts.json"
    if not concept_path.exists():
        logger.warning(f"概念数据不存在: {concept_path}")
        return

    with open(concept_path, "r", encoding="utf-8") as f:
        concepts = json.load(f)

    chunks = []
    for concept in concepts:
        # 概念名称和定义
        definitions_text = " ".join([d["text"] for d in concept.get("definitions", [])])
        text = f"{concept['name']}：{definitions_text}"

        chunks.append({
            "text": text,
            "type": "concept",
            "concept_id": concept["id"],
            "name": concept["name"],
            "sanskrit": concept.get("sanskrit"),
        })

    if not chunks:
        return

    # 生成 embedding
    embedding_service = get_embedding_service()
    texts = [chunk["text"] for chunk in chunks]
    embeddings = await embedding_service.embed_texts(texts)

    # 加载现有索引
    index_path = Path(settings.processed_data_dir) / "embeddings_index.json"
    existing_index = []
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            existing_index = json.load(f)

    # 追加新概念
    for chunk, embedding in zip(chunks, embeddings):
        existing_index.append({
            **chunk,
            "embedding": embedding,
        })

    # 保存
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(existing_index, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 追加 {len(chunks)} 个概念到索引")


async def main():
    """主函数"""
    logger.info("=== 构建 Embedding 索引 ===")
    logger.info(f"设备: {settings.EMBEDDING_DEVICE}")
    logger.info(f"模型: {settings.EMBEDDING_MODEL}")

    await build_sutra_index()
    await build_concept_index()

    logger.info("=== 索引构建完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
