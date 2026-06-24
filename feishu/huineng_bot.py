"""
惠能飞书 Bot - 独立佛学问答 Bot

权限最小化：仅接收消息 + 发送回复
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
from typing import Optional, Dict, Any

import httpx
from loguru import logger

from core.config import settings
from dialogue.huineng import get_huineng_agent
from dialogue.retriever.semantic_search import SemanticSearch


class HuinengFeishuBot:
    """惠能飞书 Bot"""

    def __init__(
        self,
        app_id: str = "cli_aab6d98f4d78dbfc",
        app_secret: str = "kw5RdKO5yYDeedb5hQRfsg4aCXaZCJLQ",
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.tenant_access_token: Optional[str] = None
        self.token_expire_time: int = 0

        self.huineng = get_huineng_agent()
        self.searcher = SemanticSearch()

    async def get_tenant_access_token(self) -> str:
        """获取 tenant_access_token"""
        import time

        if self.tenant_access_token and time.time() < self.token_expire_time:
            return self.tenant_access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                }
            )
            response.raise_for_status()
            data = response.json()

            self.tenant_access_token = data["tenant_access_token"]
            self.token_expire_time = time.time() + data["expire"] - 60  # 提前60秒刷新

            logger.info("获取 tenant_access_token 成功")
            return self.tenant_access_token

    async def send_message(self, chat_id: str, text: str, msg_type: str = "text"):
        """发送消息"""
        token = await self.get_tenant_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/im/v1/messages",
                params={"receive_id_type": "chat_id"},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "receive_id": chat_id,
                    "msg_type": msg_type,
                    "content": json.dumps({"text": text}) if msg_type == "text" else text,
                }
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") != 0:
                logger.error(f"发送消息失败: {result}")
            else:
                logger.info(f"消息已发送到 {chat_id}")

            return result

    async def handle_message(self, message: Dict[str, Any]) -> str:
        """处理用户消息"""
        # 提取用户问题
        content = message.get("content", "{}")
        try:
            content_data = json.loads(content)
            text = content_data.get("text", "")
        except:
            text = ""

        # 去除 @bot 的部分
        if text.startswith("@"):
            parts = text.split(" ", 1)
            text = parts[1] if len(parts) > 1 else ""

        text = text.strip()
        if not text:
            return "阿弥陀佛，请问有什么佛学问题想讨论？"

        logger.info(f"收到问题: {text}")

        # 1. 先搜索知识库
        knowledge = await self.searcher.search(query=text, top_k=3, threshold=0.4)

        # 2. 调用惠能回答
        result = await self.huineng.ask(
            question=text,
            retrieved_knowledge=knowledge,
        )

        # 3. 后台保存有价值的对话
        if result.get("should_save"):
            asyncio.create_task(
                self.huineng.save_conversation_to_kb(
                    question=text,
                    answer=result["answer"],
                )
            )

        return result["answer"]

    async def run_webhook(self, host: str = "0.0.0.0", port: int = 9000):
        """运行 webhook 服务器（用于接收飞书事件）"""
        from fastapi import FastAPI, Request
        import uvicorn

        app = FastAPI()

        @app.post("/webhook")
        async def webhook(request: Request):
            body = await request.json()
            logger.debug(f"收到 webhook: {body}")

            # 验证 challenge
            if "challenge" in body:
                return {"challenge": body["challenge"]}

            # 处理消息事件
            header = body.get("header", {})
            event = body.get("event", {})

            if header.get("event_type") == "im.message.receive_v1":
                message = event.get("message", {})
                chat_id = message.get("chat_id", "")

                # 处理消息
                reply = await self.handle_message(message)

                # 发送回复
                if chat_id and reply:
                    await self.send_message(chat_id, reply)

            return {"code": 0}

        logger.info(f"启动飞书 webhook 服务器: {host}:{port}")
        uvicorn.run(app, host=host, port=port)


async def test_bot():
    """测试 Bot"""
    bot = HuinengFeishuBot()

    # 测试获取 token
    try:
        token = await bot.get_tenant_access_token()
        logger.info(f"✅ Token 获取成功: {token[:20]}...")
    except Exception as e:
        logger.error(f"❌ Token 获取失败: {e}")
        return

    # 测试回答问题
    test_questions = [
        "什么是般若？",
        "如何理解空性？",
    ]

    for q in test_questions:
        logger.info(f"测试问题: {q}")
        reply = await bot.handle_message({"content": json.dumps({"text": q})})
        logger.info(f"回答: {reply[:100]}...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="惠能飞书 Bot")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--webhook", action="store_true", help="启动 webhook 服务器")
    parser.add_argument("--port", type=int, default=9000, help="webhook 端口")

    args = parser.parse_args()

    bot = HuinengFeishuBot()

    if args.test:
        asyncio.run(test_bot())
    elif args.webhook:
        asyncio.run(bot.run_webhook(port=args.port))
    else:
        print("用法:")
        print("  python -m feishu.huineng_bot --test    # 运行测试")
        print("  python -m feishu.huineng_bot --webhook # 启动 webhook 服务器")
