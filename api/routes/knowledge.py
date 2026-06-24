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
    top_k: int = Query(3, ge=1, le=10, description="检索相关知识数量"),
):
    """
    佛学问答 - 惠能大师回答

    基于知识库回答佛学问题。
    会先检索相关知识，然后由惠能 Agent 生成回答。

    示例:
    - /ask?q=什么是般若？
    - /ask?q=金刚经和心经有什么关系？
    - /ask?q=如何理解'色即是空'？
    """
    from dialogue.retriever.semantic_search import SemanticSearch
    from dialogue.huineng import get_huineng_agent

    try:
        # 1. 检索相关知识
        searcher = SemanticSearch()
        knowledge = await searcher.search(
            query=q,
            top_k=top_k,
            threshold=0.4,  # 降低阈值，获取更多参考
        )

        # 2. 调用惠能 Agent 回答
        agent = get_huineng_agent()
        result = await agent.ask(
            question=q,
            retrieved_knowledge=knowledge,
        )

        # 3. 知识沉淀（如果有价值）
        if result.get("should_save"):
            # 后台保存，不阻塞响应
            import asyncio
            asyncio.create_task(
                agent.save_conversation_to_kb(
                    question=q,
                    answer=result["answer"],
                    sources=result.get("sources", []),
                )
            )

        return {
            "success": True,
            "question": q,
            "answer": result["answer"],
            "sources": [
                {
                    "text": s.get("text", "")[:200],
                    "title": s.get("title", s.get("name", "")),
                    "score": s.get("score", 0),
                }
                for s in result.get("sources", [])
            ],
            "saved_to_kb": result.get("should_save", False),
        }
    except Exception as e:
        return {
            "success": False,
            "question": q,
            "answer": f"抱歉，回答时出现错误: {str(e)}",
            "sources": [],
        }
