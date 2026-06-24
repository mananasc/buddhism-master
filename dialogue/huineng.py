"""
惠能 - 佛学大师 Agent

独立的佛学问答专家，不接入 SEELE 架构。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config import settings
from core.ai_client import get_ai_client


class HuinengAgent:
    """
    惠能 Agent - 佛学大师

    独立的佛学问答专家，基于知识库回答佛学问题。
    """

    def __init__(self):
        self.ai_client = get_ai_client()
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """加载 system prompt"""
        prompt_path = Path(__file__).parent / "prompts" / "huineng_system.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        # 默认 prompt
        return """你是一位博学多才的佛学大师，法号"惠能"。
你精通大乘、小乘佛教经典，能够以通俗易懂的语言解释深奥的佛理。
你的回答必须标注经典出处，语气温和平和。"""

    async def ask(
        self,
        question: str,
        context: Optional[str] = None,
        retrieved_knowledge: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        回答佛学问题

        Args:
            question: 用户问题
            context: 额外上下文
            retrieved_knowledge: 从知识库检索到的内容
            conversation_history: 对话历史

        Returns:
            Dict[str, Any]: 回答结果
        """
        # 构建消息
        messages = [{"role": "system", "content": self.system_prompt}]

        # 添加检索到的知识
        if retrieved_knowledge:
            knowledge_text = self._format_knowledge(retrieved_knowledge)
            messages.append({
                "role": "system",
                "content": f"以下是从知识库中检索到的相关内容，请参考回答：\n\n{knowledge_text}"
            })

        # 添加额外上下文
        if context:
            messages.append({
                "role": "system",
                "content": f"补充信息：{context}"
            })

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        # 添加用户问题
        messages.append({"role": "user", "content": question})

        # 调用 AI
        answer = await self.ai_client.chat(messages)

        return {
            "answer": answer,
            "sources": retrieved_knowledge or [],
        }

    def _format_knowledge(self, knowledge: List[Dict[str, Any]]) -> str:
        """格式化检索到的知识"""
        parts = []
        for i, item in enumerate(knowledge, 1):
            text = item.get("text", "")
            title = item.get("title", item.get("name", ""))
            score = item.get("score", 0)

            if title:
                parts.append(f"[{i}] {title} (相关度: {score:.2f})\n{text}")
            else:
                parts.append(f"[{i}] {text}")

        return "\n\n".join(parts)


# 全局实例
_agent: Optional[HuinengAgent] = None


def get_huineng_agent() -> HuinengAgent:
    """获取惠能 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = HuinengAgent()
    return _agent


async def test_huineng():
    """测试惠能 Agent"""
    agent = get_huineng_agent()

    # 测试问题
    questions = [
        "什么是般若？",
        "金刚经中'应无所住而生其心'是什么意思？",
        "如何在日常生活中修行？",
    ]

    for q in questions:
        print(f"\n问: {q}")
        print("-" * 40)
        result = await agent.ask(q)
        print(f"答: {result['answer'][:200]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_huineng())
