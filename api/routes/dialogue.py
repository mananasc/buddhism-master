"""
佛学大师项目 - 对话路由
"""
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from loguru import logger

from api.models import (
    DialogueRequest,
    DialogueResponse,
    SourceReference,
    Conversation,
    Message,
    APIResponse,
)
from core.config import settings

router = APIRouter()


# ============ 临时内存存储 (后续改为Redis) ============
_conversations: dict = {}


# ============ 对话接口 ============

@router.post("/ask", response_model=DialogueResponse)
async def ask_question(
    request: DialogueRequest,
    background_tasks: BackgroundTasks,
):
    """
    提问接口

    用户提出佛学相关问题，系统基于知识图谱回答

    ## 参数说明
    - question: 用户问题
    - context: 可选的上下文信息
    - reasoning_mode: 推理模式
        - simple: 简洁回答
        - detailed: 详细解释
        - scholarly: 学术性回答
    - conversation_id: 对话ID，用于多轮对话
    """
    try:
        # 生成或使用现有对话ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # TODO: 调用对话引擎获取回答
        # 这里是临时实现，后续会集成完整的对话系统
        answer = await _generate_answer(
            question=request.question,
            reasoning_mode=request.reasoning_mode,
        )

        # 构建响应
        response = DialogueResponse(
            answer=answer,
            sources=[
                SourceReference(
                    type="sutra",
                    title="金刚般若波罗蜜经",
                    chapter="妙行无住分第四",
                    text="应无所住而生其心",
                ),
            ],
            related_concepts=["般若", "无住", "空性"],
            suggested_questions=[
                "什么是般若？",
                "金刚经和心经有什么关系？",
                "如何理解'色即是空'？",
            ],
            conversation_id=conversation_id,
        )

        # 后台任务：保存对话历史
        background_tasks.add_task(
            _save_conversation,
            conversation_id,
            request.question,
            answer,
        )

        return response

    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """获取对话历史"""
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conversations[conversation_id]


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话历史"""
    if conversation_id in _conversations:
        del _conversations[conversation_id]
    return {"success": True, "message": "Conversation deleted"}


@router.post("/clear-all")
async def clear_all_conversations():
    """清除所有对话历史"""
    _conversations.clear()
    return {"success": True, "message": "All conversations cleared"}


# ============ 辅助函数 ============

async def _generate_answer(question: str, reasoning_mode: str) -> str:
    """
    生成回答 (临时实现)

    TODO: 集成完整的对话引擎
    - 知识检索
    - 图谱查询
    - AI生成
    """
    # 临时回答模板
    templates = {
        "simple": f"关于您的问题「{question}」，这是一个很好的佛学问题。简单回答是：一切众生皆有佛性，皆能成佛。",
        "detailed": f"关于您的问题「{question}」，从佛法的角度来看，这涉及到般若智慧的核心教义。《金刚经》云：'凡所有相，皆是虚妄。若见诸相非相，则见如来。' 这意味着我们需要超越表象，认识到事物的空性本质。",
        "scholarly": f"关于您的问题「{question}」，这是一个深具学术价值的问题。从佛教哲学角度来看，这涉及到中观学派的'空'思想与唯识学派的'识'理论之间的关系。龙树菩萨在《中论》中提出'八不中道'，即'不生亦不灭，不常亦不断，不一亦不异，不来亦不出'，为我们理解这一问题提供了重要的理论框架。",
    }

    return templates.get(reasoning_mode, templates["detailed"])


async def _save_conversation(
    conversation_id: str,
    question: str,
    answer: str,
):
    """保存对话到存储"""
    if conversation_id not in _conversations:
        _conversations[conversation_id] = Conversation(
            id=conversation_id,
            messages=[],
        )

    conversation = _conversations[conversation_id]
    conversation.messages.append(Message(role="user", content=question))
    conversation.messages.append(Message(role="assistant", content=answer))

    logger.info(f"Saved conversation {conversation_id}, total messages: {len(conversation.messages)}")


# ============ 测试接口 ============

@router.get("/test")
async def test_dialogue():
    """测试接口"""
    return {
        "status": "ok",
        "message": "Dialogue API is working",
        "endpoints": {
            "ask": "POST /api/dialogue/ask",
            "conversation": "GET /api/dialogue/conversation/{id}",
            "delete": "DELETE /api/dialogue/conversation/{id}",
        }
    }
