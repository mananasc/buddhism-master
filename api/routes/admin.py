"""
佛学大师项目 - 管理路由
"""
from fastapi import APIRouter, HTTPException

from api.models import (
    ImportRequest,
    ImportResponse,
    BuildGraphRequest,
    BuildGraphResponse,
    Sutra,
    Concept,
    MasterQuote,
    APIResponse,
)

router = APIRouter()


# ============ 数据导入 ============

@router.post("/sutra", response_model=APIResponse)
async def add_sutra(sutra: Sutra):
    """添加经典"""
    # TODO: 实现经典添加
    return APIResponse(success=True, message="Sutra added")


@router.post("/concept", response_model=APIResponse)
async def add_concept(concept: Concept):
    """添加概念"""
    # TODO: 实现概念添加
    return APIResponse(success=True, message="Concept added")


@router.post("/master-quote", response_model=APIResponse)
async def add_master_quote(quote: MasterQuote):
    """添加大师开示"""
    # TODO: 实现开示添加
    return APIResponse(success=True, message="Quote added")


@router.post("/import", response_model=ImportResponse)
async def import_data(request: ImportRequest):
    """
    批量导入数据

    支持导入经典、概念、大师开示等
    """
    # TODO: 实现批量导入
    return ImportResponse(
        success=True,
        message="Import completed",
        imported_count=0,
    )


# ============ 知识图谱管理 ============

@router.post("/build-graph", response_model=BuildGraphResponse)
async def build_graph(request: BuildGraphRequest):
    """
    构建/重建知识图谱

    从数据库数据构建Neo4j知识图谱
    """
    # TODO: 实现图谱构建
    return BuildGraphResponse(
        success=True,
        message="Graph built successfully",
        nodes_created=0,
        edges_created=0,
    )


@router.post("/sync-graph")
async def sync_graph():
    """
    同步知识图谱

    增量同步新增数据到图谱
    """
    # TODO: 实现图谱同步
    return APIResponse(success=True, message="Graph synced")


@router.delete("/graph")
async def clear_graph():
    """清空知识图谱"""
    # TODO: 实现图谱清空
    return APIResponse(success=True, message="Graph cleared")


# ============ 数据源管理 ============

@router.post("/fetch-deerpark")
async def fetch_from_deerpark(
    sutra_id: str = None,
    limit: int = 10,
):
    """
    从Deerpark API获取数据

    参数:
    - sutra_id: 指定经典ID，不指定则获取列表
    - limit: 获取数量限制
    """
    # TODO: 实现Deerpark数据获取
    return APIResponse(success=True, message="Fetch completed")


# ============ 惠能 Agent 管理 ============

@router.post("/huineng/learn")
async def huineng_learn(limit: int = 1):
    """
    触发惠能学习任务

    从 Deerpark 导入新经典，扩充知识库
    """
    from dialogue.huineng import get_huineng_agent

    agent = get_huineng_agent()
    result = await agent.import_from_deerpark(limit=limit)

    return {
        "success": True,
        "message": "Learning task completed",
        "result": result,
    }


@router.post("/huineng/daily-task")
async def huineng_daily_task():
    """
    触发惠能每日学习任务
    """
    from dialogue.huineng import get_huineng_agent

    agent = get_huineng_agent()
    result = await agent.daily_learning_task()

    return {
        "success": True,
        "message": "Daily task completed",
        "result": result,
    }


# ============ 系统管理 ============

@router.get("/stats")
async def get_stats():
    """获取系统统计信息"""
    import json
    from pathlib import Path
    from core.config import settings

    # 读取索引文件统计
    index_path = Path(settings.processed_data_dir) / "embeddings_index.json"
    index_stats = {"total": 0, "by_type": {}}

    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
            index_stats["total"] = len(index)

            # 按类型统计
            for item in index:
                item_type = item.get("type", "unknown")
                index_stats["by_type"][item_type] = index_stats["by_type"].get(item_type, 0) + 1

    # 读取原始数据统计
    raw_dir = Path(settings.raw_data_dir)
    raw_stats = {"sutras": 0, "concepts": 0, "files": []}

    if raw_dir.exists():
        for f in raw_dir.glob("*.json"):
            raw_stats["files"].append(f.name)
            if "sutra" in f.name or "diamond" in f.name:
                raw_stats["sutras"] += 1
            elif "concept" in f.name:
                raw_stats["concepts"] += 1

    return {
        "index": index_stats,
        "raw_data": raw_stats,
        "embedding": {
            "provider": "Ollama bge-m3 (Windows 4090)",
            "dimension": 1024,
        },
        "agent": {
            "name": "惠能",
            "model": "L1R-deepseek-reasoning (via Smart Router)",
        },
    }


@router.post("/reset")
async def reset_system():
    """
    重置系统

    清空所有数据，谨慎使用！
    """
    # TODO: 实现系统重置
    return APIResponse(success=True, message="System reset")
