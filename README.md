# 佛学大师 (Buddhism Master)

基于知识图谱的佛学智能问答系统，支持大乘、小乘经典的学习与讨论。

## 功能特点

- 📚 **知识库**: 基于Neo4j的佛学知识图谱
- 🤖 **智能问答**: 结合AI和知识图谱的问答系统
- 🔍 **多源检索**: 关键词、语义、图谱多维度检索
- 📖 **学习路径**: 网状关联的佛学概念学习
- 📝 **出处标注**: 所有回答标注经典来源

## 技术栈

- **后端**: Python + FastAPI
- **数据库**: PostgreSQL + Neo4j + Redis
- **AI**: 通义千问/OpenAI (可配置)
- **向量检索**: Milvus/Qdrant

## 项目结构

```
buddhism-master/
├── api/              # FastAPI接口
├── core/             # 核心配置
├── knowledge_builder/# 知识库构建
├── dialogue/         # 对话系统
├── learning/         # 学习系统
├── scripts/          # 工具脚本
└── data/             # 数据目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```env
# AI API
DASHSCOPE_API_KEY=your_key_here

# 数据库
POSTGRES_PASSWORD=your_password
NEO4J_PASSWORD=your_password
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动服务

```bash
python -m api.main
```

访问 http://localhost:8000/docs 查看API文档。

## API接口

### 对话接口

```bash
POST /api/dialogue/ask
{
    "question": "什么是般若？",
    "reasoning_mode": "detailed"
}
```

### 知识库查询

```bash
GET /api/knowledge/concept/空性
GET /api/knowledge/sutra/金刚经
```

## 开发计划

- [x] Phase 1: 基础架构搭建
- [x] Phase 2: API框架搭建
- [ ] Phase 3: 知识库构建系统
- [ ] Phase 4: 对话系统
- [ ] Phase 5: 学习路径系统
- [ ] Phase 6: 数据导入与完善

## 数据源

- [Deerpark API](https://deerpark.app/apidocs) - 主要佛经数据源
- [法鼓文理学院](https://authority.dila.edu.tw/) - 规范数据

## License

MIT
