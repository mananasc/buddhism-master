"""
佛学大师项目 - FastAPI主入口
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from core.config import settings
from core.database import init_all_databases, close_all_databases

from api.routes import dialogue, knowledge, learning, admin


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🙏 佛学大师项目启动中...")
    logger.info(f"版本: {settings.APP_VERSION}")

    try:
        await init_all_databases()
        logger.info("✅ 数据库连接初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        # 根据配置决定是否继续启动
        if not settings.DEBUG:
            raise

    yield

    # 关闭时执行
    logger.info("🙏 佛学大师项目关闭中...")
    await close_all_databases()
    logger.info("✅ 数据库连接已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="佛学大师 - Buddhist Master API",
    description="基于知识图谱的佛学智能问答系统",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"API Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else None,
        },
    )


# 注册路由
app.include_router(
    dialogue.router,
    prefix=f"{settings.API_PREFIX}/dialogue",
    tags=["对话"],
)

app.include_router(
    knowledge.router,
    prefix=f"{settings.API_PREFIX}/knowledge",
    tags=["知识库"],
)

app.include_router(
    learning.router,
    prefix=f"{settings.API_PREFIX}/learning",
    tags=["学习路径"],
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_PREFIX}/admin",
    tags=["管理"],
)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "ai_provider": settings.AI_PROVIDER,
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "佛学大师 API",
        "version": settings.APP_VERSION,
        "description": "基于知识图谱的佛学智能问答系统",
        "docs": "/docs" if settings.DEBUG else "Production mode - docs disabled",
    }


def main():
    """启动应用"""
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
