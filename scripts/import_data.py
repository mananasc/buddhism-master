"""
佛学大师项目 - 按需导入脚本

用法:
    python scripts/import_data.py --source file --type sutra --file data/raw/diamond_sutra.json
    python scripts/import_data.py --source deerpark --id T0235  # 金刚经在Deerpark的ID
"""
import sys
import asyncio
import json
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from core.config import settings


class OnDemandImporter:
    """按需导入器"""

    def __init__(self):
        self.data_dir = Path(settings.BASE_DIR) / "data"

    async def import_sutra_from_file(self, file_path: Path) -> dict:
        """从JSON文件导入经典"""
        logger.info(f"从文件导入经典: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # TODO: 保存到数据库
        # TODO: 构建知识图谱节点

        logger.info(f"✅ 成功导入经典: {data.get('title', 'Unknown')}")
        logger.info(f"   - 章节数: {len(data.get('chapters', []))}")
        logger.info(f"   - 核心概念: {', '.join(data.get('core_concepts', []))}")

        return data

    async def import_concepts_from_file(self, file_path: Path) -> list:
        """从JSON文件导入概念"""
        logger.info(f"从文件导入概念: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # TODO: 保存到数据库
        # TODO: 构建知识图谱节点

        logger.info(f"✅ 成功导入 {len(data)} 个概念")
        for concept in data:
            logger.info(f"   - {concept.get('name')} ({concept.get('sanskrit', '')})")

        return data

    async def import_from_deerpark(self, sutra_id: str) -> dict:
        """从Deerpark API导入经典"""
        logger.info(f"从Deerpark导入经典: {sutra_id}")

        from knowledge_builder.importer.api_importer import APIImporter
        importer = APIImporter()

        # 获取经典内容
        sutra_data = await importer.fetch_sutra(sutra_id)

        if not sutra_data:
            logger.warning(f"未找到经典: {sutra_id}")
            return {}

        # TODO: 解析并保存

        logger.info(f"✅ 成功从Deerpark导入: {sutra_id}")
        return sutra_data

    async def search_and_import(self, query: str) -> list:
        """搜索并导入"""
        logger.info(f"搜索: {query}")

        from knowledge_builder.importer.api_importer import APIImporter
        importer = APIImporter()

        results = await importer.search_sutra(query)
        logger.info(f"找到 {len(results)} 个结果")

        return results


async def main():
    parser = argparse.ArgumentParser(description="按需导入佛学数据")
    parser.add_argument(
        "--source",
        choices=["file", "deerpark", "search"],
        default="file",
        help="数据来源"
    )
    parser.add_argument(
        "--type",
        choices=["sutra", "concept"],
        default="sutra",
        help="数据类型"
    )
    parser.add_argument("--file", type=str, help="本地文件路径")
    parser.add_argument("--id", type=str, help="Deerpark经典ID")
    parser.add_argument("--query", type=str, help="搜索关键词")

    args = parser.parse_args()

    importer = OnDemandImporter()

    if args.source == "file":
        if not args.file:
            # 默认导入金刚经
            args.file = str(importer.data_dir / "raw" / "diamond_sutra.json")

        file_path = Path(args.file)

        if args.type == "sutra":
            await importer.import_sutra_from_file(file_path)
        elif args.type == "concept":
            await importer.import_concepts_from_file(file_path)

    elif args.source == "deerpark":
        if not args.id:
            logger.error("请指定Deerpark经典ID (--id)")
            return
        await importer.import_from_deerpark(args.id)

    elif args.source == "search":
        if not args.query:
            logger.error("请指定搜索关键词 (--query)")
            return
        await importer.search_and_import(args.query)


if __name__ == "__main__":
    asyncio.run(main())
