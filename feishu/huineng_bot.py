"""
惠能飞书 Bot - 长连接模式（不需要 webhook/公网）

使用飞书 SDK 的长连接模式，和 SEELE/OpenClaw 一样。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
from typing import Optional, Dict, Any

from loguru import logger

from dialogue.huineng import get_huineng_agent
from dialogue.retriever.semantic_search import SemanticSearch


class HuinengFeishuBot:
    """惠能飞书 Bot - 长连接模式"""

    def __init__(
        self,
        app_id: str = "cli_aab6d98f4d78dbfc",
        app_secret: str = "kw5RdKO5yYDeedb5hQRfsg4aCXaZCJLQ",
    ):
        self.app_id = app_id
        self.app_secret = app_secret

        self.huineng = get_huineng_agent()
        self.searcher = SemanticSearch()

        # 飞书 SDK
        self.client = None

    def init_sdk(self):
        """初始化飞书 SDK"""
        try:
            import lark_oapi as lark

            # 创建客户端（长连接模式）
            self.client = lark.ws.Client(
                app_id=self.app_id,
                app_secret=self.app_secret,
                event_handler=self._create_event_handler(),
                log_level=lark.LogLevel.INFO,
            )

            logger.info("飞书 SDK 初始化成功（长连接模式）")
            return True

        except ImportError:
            logger.error("请安装飞书 SDK: pip install lark-oapi")
            return False
        except Exception as e:
            logger.error(f"飞书 SDK 初始化失败: {e}")
            return False

    def _create_event_handler(self):
        """创建事件处理器"""
        import lark_oapi as lark

        handler = lark.EventDispatcherHandlerBuilder("", "")

        # 注册消息接收事件
        handler.register(
            lark.EventType.IM_MESSAGE_RECEIVE_V1,
            self._on_message_receive
        )

        return handler

    async def _on_message_receive(self, data) -> None:
        """处理收到的消息"""
        try:
            event = data.event
            message = event.message
            chat_id = message.chat_id
            message_type = message.message_type
            content = message.content

            # 只处理文本消息
            if message_type != "text":
                logger.info(f"忽略非文本消息: {message_type}")
                return

            # 解析文本
            try:
                content_data = json.loads(content)
                text = content_data.get("text", "")
            except:
                text = ""

            # 去除 @bot 的部分
            mentions = getattr(event.message, 'mentions', None) or []
            for mention in mentions:
                text = text.replace(mention.key, "").strip()

            text = text.strip()
            if not text:
                return

            logger.info(f"收到问题: {text}")

            # 调用惠能回答
            reply = await self._handle_question(text)

            # 发送回复
            if reply:
                await self._send_reply(chat_id, reply)

        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    async def _handle_question(self, question: str) -> str:
        """处理用户问题"""
        # 1. 搜索知识库
        knowledge = await self.searcher.search(query=question, top_k=3, threshold=0.4)

        # 2. 调用惠能回答
        result = await self.huineng.ask(
            question=question,
            retrieved_knowledge=knowledge,
        )

        # 3. 后台保存有价值的对话
        if result.get("should_save"):
            asyncio.create_task(
                self.huineng.save_conversation_to_kb(
                    question=question,
                    answer=result["answer"],
                )
            )

        return result["answer"]

    async def _send_reply(self, chat_id: str, text: str):
        """发送回复"""
        if not self.client:
            logger.error("飞书客户端未初始化")
            return

        try:
            import lark_oapi as lark
            from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

            # 创建请求
            request = CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type("text")
                    .content(json.dumps({"text": text}))
                    .build()
                ).build()

            # 发送
            response = await self.client.im.v1.message.acreate(request)

            if not response.success():
                logger.error(f"发送消息失败: {response.code} - {response.msg}")
            else:
                logger.info(f"消息已发送到 {chat_id}")

        except Exception as e:
            logger.error(f"发送回复失败: {e}")

    def run(self):
        """运行 Bot（长连接模式）"""
        if not self.init_sdk():
            logger.error("SDK 初始化失败，无法启动")
            return

        logger.info("=" * 50)
        logger.info("惠能飞书 Bot 启动中...")
        logger.info(f"App ID: {self.app_id}")
        logger.info("模式: 长连接 (无需公网)")
        logger.info("=" * 50)

        # 启动长连接
        self.client.start()


async def test_bot():
    """测试 Bot（不连接飞书）"""
    bot = HuinengFeishuBot()

    # 测试回答问题
    test_questions = [
        "什么是般若？",
        "如何理解空性？",
    ]

    for q in test_questions:
        logger.info(f"测试问题: {q}")
        reply = await bot._handle_question(q)
        logger.info(f"回答: {reply[:100]}...")
        print("-" * 40)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="惠能飞书 Bot（长连接模式）")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--run", action="store_true", help="启动 Bot")

    args = parser.parse_args()

    bot = HuinengFeishuBot()

    if args.test:
        asyncio.run(test_bot())
    elif args.run:
        bot.run()
    else:
        print("用法:")
        print("  python -m feishu.huineng_bot --test  # 运行测试")
        print("  python -m feishu.huineng_bot --run   # 启动 Bot（长连接）")
        print()
        print("不需要公网 IP，不需要 webhook！")
