"""
佛学大师项目 - 知识库路由
简化为通用查询接口
"""
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/search")
async def search(
    q: str = Query(..., description="搜索查询", min_length=1),
    top_k: int = Query(5, ge=1, le=20, description="返回结果数量"),
    threshold: float = Query(0.5, ge=0.0, le=1.0, description="相似度阈值"),
):
    """
    通用知识搜索

    统一入口，支持搜索经典、概念、人物、开示等所有内容。
    内部自动进行语义检索。

    示例:
    - /search?q=空性
    - /search?q=金刚经第三品
    - /search?q=应无所住而生其心
    """
    from dialogue.retriever.semantic_search import SemanticSearch

    try:
        searcher = SemanticSearch()
        results = await searcher.search(
            query=q,
            top_k=top_k,
            threshold=threshold,
        )

        return {
            "success": True,
            "query": q,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        return {
            "success": False,
            "query": q,
            "results": [],
            "total": 0,
            "error": str(e),
        }


@router.get("/ask")
async def ask(
    q: str = Query(..., description="佛学问题", min_length=1),
):
    """
    佛学问答

    基于知识库回答问题，会检索相关内容并生成回答。

    示例:
    - /ask?q=什么是般若？
    - /ask?q=金刚经和心经有什么关系？
    """
    # TODO: 集成对话引擎
    # 1. 语义检索相关知识
    # 2. 构建 prompt
    # 3. 调用 AI 生成回答
    # 4. 标注出处

    return {
        "success": True,
        "question": q,
        "answer": "功能开发中...",
        "sources": [],
    }
