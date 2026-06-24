"""
佛学大师项目 - API路由
"""
from api.routes.dialogue import router as dialogue_router
from api.routes.knowledge import router as knowledge_router
from api.routes.learning import router as learning_router
from api.routes.admin import router as admin_router

__all__ = [
    "dialogue_router",
    "knowledge_router",
    "learning_router",
    "admin_router",
]
