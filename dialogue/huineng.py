"""
惠能 - 佛学大师 Agent

独立的佛学问答专家，具备：
1. 从 Deerpark 导入经典
2. 深度理解用户问题
3. 有理有据的讨论
4. 知识沉淀到 KB
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from loguru import logger

from core.config import settings
from core.ai_client import get_ai_client
from knowledge_builder.importer.api_importer import APIImporter
from knowledge_builder.parser.sutra_parser import SutraParser


class HuinengAgent:
    """
    惠能 Agent - 佛学大师

    独立的佛学问答专家，基于知识库回答佛学问题。
    """

    def __init__(self):
        self.ai_client = get_ai_client()
        self.system_prompt = self._load_system_prompt()
        self.api_importer = APIImporter()
        self.sutra_parser = SutraParser()

    def _load_system_prompt(self) -> str:
        """加载 system prompt"""
        prompt_path = Path(__file__).parent / "prompts" / "huineng_system.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

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

        # 检查是否需要知识沉淀
        should_save = await self._should_save_knowledge(question, answer)

        return {
            "answer": answer,
            "sources": retrieved_knowledge or [],
            "should_save": should_save,
        }

    async def _should_save_knowledge(self, question: str, answer: str) -> bool:
        """判断是否应该保存这次对话为知识"""
        # 简单的判断逻辑：回答长度 > 200 且包含经典引用
        if len(answer) > 200 and ("经》" in answer or "论》" in answer):
            return True
        return False

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

    # ============ Deerpark 导入功能 ============

    async def import_from_deerpark(
        self,
        sutra_ids: Optional[List[str]] = None,
        limit: int = 1,
    ) -> Dict[str, Any]:
        """
        从 Deerpark 导入经典

        Args:
            sutra_ids: 指定经典ID列表，None则自动选择
            limit: 导入数量限制

        Returns:
            Dict[str, Any]: 导入结果
        """
        logger.info(f"开始从 Deerpark 导入经典...")

        # 默认优先导入的经典
        priority_sutras = sutra_ids or [
            # 心经 (T0251)
            "T0251",
            # 杂阿含经 (T0100)
            "T0100",
            # 中阿含经 (T0026)
            "T0026",
        ]

        results = []
        for sutra_id in priority_sutras[:limit]:
            try:
                result = await self._import_single_sutra(sutra_id)
                results.append(result)
            except Exception as e:
                logger.error(f"导入 {sutra_id} 失败: {e}")
                results.append({"sutra_id": sutra_id, "success": False, "error": str(e)})

        return {
            "imported": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results,
        }

    async def _import_single_sutra(self, sutra_id: str) -> Dict[str, Any]:
        """导入单个经典"""
        logger.info(f"导入经典: {sutra_id}")

        # 从 Deerpark 获取
        sutra_data = await self.api_importer.fetch_sutra(sutra_id)

        if not sutra_data:
            return {"sutra_id": sutra_id, "success": False, "error": "Not found"}

        # 解析
        # TODO: 实际解析和保存逻辑

        return {
            "sutra_id": sutra_id,
            "success": True,
            "title": sutra_data.get("title", "Unknown"),
        }

    # ============ 知识沉淀功能 ============

    async def save_conversation_to_kb(
        self,
        question: str,
        answer: str,
        sources: List[Dict[str, Any]] = None,
    ) -> bool:
        """
        将有价值的对话保存到知识库

        Args:
            question: 用户问题
            answer: 惠能的回答
            sources: 引用的经典

        Returns:
            bool: 是否保存成功
        """
        # 生成知识总结
        summary = await self._generate_conversation_summary(question, answer, sources)

        if not summary:
            return False

        # TODO: 保存到知识库
        # 1. 调用 embedding 服务生成向量
        # 2. 保存到 Qdrant 或 JSON 索引

        logger.info(f"保存对话总结到知识库: {summary[:100]}...")
        return True

    async def _generate_conversation_summary(
        self,
        question: str,
        answer: str,
        sources: List[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """生成对话总结"""
        # 使用 AI 生成总结
        prompt = f"""请根据以下佛学对话，生成一个简洁的知识总结：

用户问题：{question}

惠能回答：{answer}

请输出：
1. 核心议题（一句话）
2. 关键讨论点（2-3个要点）
3. 引用经典（如有）
4. 结论/建议（一句话）

格式简洁，适合存入知识库。"""

        messages = [
            {"role": "system", "content": "你是佛学知识整理专家，擅长提炼对话要点。"},
            {"role": "user", "content": prompt},
        ]

        try:
            summary = await self.ai_client.chat(messages, max_tokens=500)
            return summary
        except Exception as e:
            logger.error(f"生成总结失败: {e}")
            return None

    # ============ 每日学习任务 ============

    async def daily_learning_task(self) -> Dict[str, Any]:
        """
        每日学习任务

        自动从 Deerpark 导入新经典，扩充知识库
        """
        logger.info("执行每日学习任务...")

        # 检查今天是否已经学习过
        # TODO: 记录学习历史

        # 导入新经典
        import_result = await self.import_from_deerpark(limit=1)

        return {
            "task": "daily_learning",
            "result": import_result,
            "timestamp": datetime.now().isoformat(),
        }


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
        print(f"是否保存: {result.get('should_save', False)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_huineng())
