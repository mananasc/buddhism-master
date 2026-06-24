"""
佛学大师项目 - 经典导入脚本
"""
import asyncio
from pathlib import Path
from loguru import logger

from knowledge_builder.importer.api_importer import APIImporter
from knowledge_builder.importer.file_importer import FileImporter
from knowledge_builder.parser.sutra_parser import SutraParser


async def import_from_deerpark(sutra_ids: list = None):
    """从Deerpark API导入经典"""
    logger.info("从Deerpark API导入经典...")

    importer = APIImporter()
    parser = SutraParser()

    # 默认导入的核心经典
    if sutra_ids is None:
        sutra_ids = [
            # TODO: 添加实际的Deerpark经典ID
        ]

    for sutra_id in sutra_ids:
        try:
            # 获取经典内容
            sutra_data = await importer.fetch_sutra(sutra_id)
            if not sutra_data:
                logger.warning(f"未找到经典: {sutra_id}")
                continue

            # 解析经典
            # TODO: 解析并保存到数据库

            logger.info(f"✅ 导入成功: {sutra_id}")

        except Exception as e:
            logger.error(f"导入失败 {sutra_id}: {e}")


async def import_from_files(data_dir: Path):
    """从本地文件导入经典"""
    logger.info(f"从本地文件导入: {data_dir}")

    importer = FileImporter()
    result = await importer.import_directory(data_dir)

    logger.info(f"导入完成: {result}")


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="导入佛经数据")
    parser.add_argument("--source", choices=["deerpark", "file"], default="deerpark")
    parser.add_argument("--dir", type=str, help="本地文件目录")

    args = parser.parse_args()

    if args.source == "deerpark":
        await import_from_deerpark()
    elif args.source == "file" and args.dir:
        await import_from_files(Path(args.dir))
    else:
        logger.error("请指定有效的数据源")


if __name__ == "__main__":
    asyncio.run(main())
