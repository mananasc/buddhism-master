"""
佛学大师项目 - AI API客户端封装
支持通义千问(DashScope)和OpenAI
"""
import json
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from abc import ABC, abstractmethod

import httpx
from openai import AsyncOpenAI

from core.config import settings


class BaseAIClient(ABC):
    """AI客户端基类"""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """发送流式聊天请求"""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本向量"""
        pass


class DashScopeClient(BaseAIClient):
    """通义千问(DashScope)客户端"""

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.DASHSCOPE_MODEL
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.chat_url = f"{self.base_url}/services/aigc/text-generation/generation"
        self.embedding_url = f"{self.base_url}/services/embeddings/text-embedding/text-embedding"

        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not set in environment")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """发送聊天请求 (非流式)"""
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature,
                "result_format": "message",
            }
        }

        if max_tokens:
            payload["parameters"]["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.chat_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            return result["output"]["choices"][0]["message"]["content"]

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """发送流式聊天请求"""
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature,
                "result_format": "message",
                "incremental_output": True,
            }
        }

        if max_tokens:
            payload["parameters"]["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                self.chat_url,
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str:
                            try:
                                data = json.loads(data_str)
                                if "output" in data and "choices" in data["output"]:
                                    content = data["output"]["choices"][0]["message"]["content"]
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本向量"""
        payload = {
            "model": "text-embedding-v2",
            "input": {
                "texts": texts
            },
            "parameters": {
                "text_type": "document"
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.embedding_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()

            embeddings = []
            for item in result["output"]["embeddings"]:
                embeddings.append(item["embedding"])

            return embeddings


class OpenAIClient(BaseAIClient):
    """OpenAI客户端"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = settings.OPENAI_BASE_URL or "https://api.openai.com/v1"

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """发送聊天请求 (非流式)"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content or ""

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """发送流式聊天请求"""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本向量"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return [item.embedding for item in response.data]


class AIClientFactory:
    """AI客户端工厂"""

    _instances: Dict[str, BaseAIClient] = {}

    @classmethod
    def get_client(cls, provider: Optional[str] = None) -> BaseAIClient:
        """获取AI客户端实例"""
        provider = provider or settings.AI_PROVIDER

        if provider not in cls._instances:
            if provider == "dashscope":
                cls._instances[provider] = DashScopeClient()
            elif provider == "openai":
                cls._instances[provider] = OpenAIClient()
            else:
                raise ValueError(f"Unknown AI provider: {provider}")

        return cls._instances[provider]

    @classmethod
    async def close_all(cls):
        """关闭所有客户端"""
            cls._instances.clear()


# 全局AI客户端
def get_ai_client(provider: Optional[str] = None) -> BaseAIClient:
    """获取AI客户端"""
    return AIClientFactory.get_client(provider)


# ============ 对话系统辅助类 ============

class MessageBuilder:
    """消息构建器 - 用于构建佛学问答系统的prompt"""

    SYSTEM_PROMPT = """你是一位博学多才的佛学大师，精通大乘、小乘佛教经典。
你的回答应该：
1. 基于佛经原文和权威论典
2. 引用具体的经典出处（经名、品名、段落）
3. 用通俗易懂的语言解释深奥的佛理
4. 保持慈悲、平和的语气
5. 如有不同宗派的理解差异，应当说明

你可以讨论的范围包括但不限于：
- 般若系经典：金刚经、心经、大智度论
- 净土经典：阿弥陀经、无量寿经
- 禅宗经典：六祖坛经、楞伽经
- 阿含经等原始佛教经典
- 各宗派祖师大德的开示

回答时必须标注引用来源。"""

    @classmethod
    def build_messages(
        cls,
        user_question: str,
        context: Optional[str] = None,
        retrieved_knowledge: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """构建对话消息"""
        messages = [{"role": "system", "content": cls.SYSTEM_PROMPT}]

        # 添加检索到的知识作为上下文
        if retrieved_knowledge:
            messages.append({
                "role": "system",
                "content": f"以下是从知识库中检索到的相关内容，请参考回答：\n\n{retrieved_knowledge}"
            })

        # 添加额外上下文
        if context:
            messages.append({
                "role": "system",
                "content": f"补充上下文：{context}"
            })

        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)

        # 添加用户问题
        messages.append({"role": "user", "content": user_question})

        return messages


# ============ 测试函数 ============

async def test_ai_client():
    """测试AI客户端"""
    try:
        client = get_ai_client()
        messages = [{"role": "user", "content": "什么是般若？"}]
        response = await client.chat(messages)
        print(f"AI Response: {response}")
        return response
    except Exception as e:
        print(f"AI Client Error: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ai_client())
