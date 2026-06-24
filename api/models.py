"""
佛学大师项目 - Pydantic数据模型
"""
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============ 对话相关模型 ============

class DialogueRequest(BaseModel):
    """对话请求"""
    question: str = Field(..., description="用户问题", min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = Field(default=None, description="对话上下文")
    reasoning_mode: Literal["simple", "detailed", "scholarly"] = Field(
        default="detailed",
        description="推理模式: simple简单/detailed详细/scholarly学术"
    )
    conversation_id: Optional[str] = Field(default=None, description="对话ID，用于追踪多轮对话")


class SourceReference(BaseModel):
    """来源引用"""
    type: Literal["sutra", "commentary", "master_quote", "dictionary"] = Field(
        ..., description="来源类型"
    )
    title: str = Field(..., description="标题")
    chapter: Optional[str] = Field(default=None, description="章节/品")
    text: str = Field(..., description="引用文本")
    master: Optional[str] = Field(default=None, description="大师名称(如果是大师开示)")


class DialogueResponse(BaseModel):
    """对话响应"""
    answer: str = Field(..., description="回答内容")
    sources: List[SourceReference] = Field(default_factory=list, description="来源引用")
    related_concepts: List[str] = Field(default_factory=list, description="相关概念")
    suggested_questions: List[str] = Field(default_factory=list, description="建议的后续问题")
    conversation_id: str = Field(..., description="对话ID")


class Message(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    """对话会话"""
    id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ============ 知识库相关模型 ============

class Sutra(BaseModel):
    """佛经模型"""
    id: str = Field(..., description="经典ID")
    title: str = Field(..., description="经典标题")
    sanskrit: Optional[str] = Field(default=None, description="梵文标题")
    pali: Optional[str] = Field(default=None, description="巴利文标题")
    translator: Optional[str] = Field(default=None, description="译者")
    era: Optional[str] = Field(default=None, description="时代")
    school: List[str] = Field(default_factory=list, description="所属宗派")
    chapters: List[str] = Field(default_factory=list, description="章节列表")
    core_concepts: List[str] = Field(default_factory=list, description="核心概念")
    summary: Optional[str] = Field(default=None, description="摘要")


class Chapter(BaseModel):
    """章节模型"""
    id: str = Field(..., description="章节ID")
    sutra_id: str = Field(..., description="所属经典ID")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    order: int = Field(default=0, description="顺序")


class Concept(BaseModel):
    """概念模型"""
    id: str = Field(..., description="概念ID")
    name: str = Field(..., description="概念名称")
    sanskrit: Optional[str] = Field(default=None, description="梵文")
    pali: Optional[str] = Field(default=None, description="巴利文")
    definitions: List[Dict[str, str]] = Field(default_factory=list, description="定义列表")
    related_concepts: List[str] = Field(default_factory=list, description="相关概念")
    sutra_references: List[str] = Field(default_factory=list, description="相关经典")
    explanation: Optional[str] = Field(default=None, description="详细解释")


class Figure(BaseModel):
    """人物模型"""
    id: str = Field(..., description="人物ID")
    name: str = Field(..., description="人物名称")
    title: Optional[str] = Field(default=None, description="称号")
    era: Optional[str] = Field(default=None, description="时代")
    school: List[str] = Field(default_factory=list, description="所属宗派")
    related_figures: List[str] = Field(default_factory=list, description="相关人物")
    teachings: List[str] = Field(default_factory=list, description="主要教导")


class School(BaseModel):
    """宗派模型"""
    id: str = Field(..., description="宗派ID")
    name: str = Field(..., description="宗派名称")
    vehicle: Literal["大乘", "小乘", "金刚乘"] = Field(..., description="乘别")
    founder: Optional[str] = Field(default=None, description="创始人")
    core_teachings: List[str] = Field(default_factory=list, description="核心教义")
    main_sutras: List[str] = Field(default_factory=list, description="主要经典")


class MasterQuote(BaseModel):
    """大师开示模型"""
    id: str = Field(..., description="开示ID")
    master: str = Field(..., description="大师名称")
    content: str = Field(..., description="开示内容")
    source: Optional[str] = Field(default=None, description="出处")
    topic: List[str] = Field(default_factory=list, description="主题")
    era: Optional[str] = Field(default=None, description="时代")


# ============ 知识图谱相关模型 ============

class GraphNode(BaseModel):
    """图谱节点"""
    id: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """图谱边"""
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraph(BaseModel):
    """知识图谱"""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


# ============ 学习路径相关模型 ============

class LearningPath(BaseModel):
    """学习路径"""
    id: str = Field(..., description="路径ID")
    name: str = Field(..., description="路径名称")
    start_concept: str = Field(..., description="起始概念")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="学习步骤")
    related_concepts: List[str] = Field(default_factory=list, description="相关概念")
    estimated_duration: Optional[str] = Field(default=None, description="预计时长")


class LearningProgress(BaseModel):
    """学习进度"""
    user_id: str = Field(..., description="用户ID")
    concept_id: str = Field(..., description="概念ID")
    status: Literal["not_started", "in_progress", "completed"] = Field(
        default="not_started", description="状态"
    )
    progress: float = Field(default=0.0, description="进度(0-1)")
    last_accessed: Optional[datetime] = Field(default=None, description="最后访问时间")


# ============ 管理接口相关模型 ============

class ImportRequest(BaseModel):
    """导入请求"""
    source_type: Literal["sutra", "concept", "master_quote", "figure"] = Field(
        ..., description="来源类型"
    )
    data: Dict[str, Any] = Field(..., description="数据")
    overwrite: bool = Field(default=False, description="是否覆盖已存在的数据")


class ImportResponse(BaseModel):
    """导入响应"""
    success: bool
    message: str
    imported_count: int = Field(default=0, description="导入数量")


class BuildGraphRequest(BaseModel):
    """构建图谱请求"""
    force_rebuild: bool = Field(default=False, description="是否强制重建")
    include_types: Optional[List[str]] = Field(
        default=None,
        description="要包含的实体类型，None表示全部"
    )


class BuildGraphResponse(BaseModel):
    """构建图谱响应"""
    success: bool
    message: str
    nodes_created: int = Field(default=0, description="创建的节点数")
    edges_created: int = Field(default=0, description="创建的边数")


# ============ API通用模型 ============

class APIResponse(BaseModel):
    """通用API响应"""
    success: bool
    data: Optional[Any] = None
    message: str = "success"
    error: Optional[str] = None


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
