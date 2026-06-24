# 佛学大师 - Mac mini 部署指南

## 架构

```
Mac mini (服务中枢)
├── Buddhism Master API (port 8000)
├── Qdrant (port 6333) - 向量数据库，与 Knowledge Hub 共用
├── PostgreSQL (port 5432) - 元数据
└── Redis (port 6379) - 对话缓存

Windows 4090 (算力节点)
└── Ollama (port 11434) - bge-m3 Embedding + qwen3:14b
```

## 快速部署

### 1. 克隆代码

```bash
cd ~/manana-hub  # 或你的工作目录
git clone git@github.com:mananasc/buddhism-master.git
cd buddhism-master
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，设置:
# - OLLAMA_BASE_URL=http://192.168.50.94:11434 (Windows 4090 IP)
# - QDRANT_HOST=localhost
# - POSTGRES_PASSWORD=你的密码
```

### 4. 启动 Qdrant (Docker)

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v ~/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### 5. 构建索引

```bash
# 确保 Windows 4090 Ollama 已启动
python scripts/build_index.py
```

### 6. 启动服务

```bash
python -m api.main
```

访问 http://localhost:8000/docs 查看 API 文档。

## 使用 launchd 守护运行

创建 `~/Library/LaunchAgents/com.manana.buddhism-master.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.manana.buddhism-master</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/jgmao/work/buddhism-master/.venv/bin/python</string>
        <string>-m</string>
        <string>api.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/jgmao/work/buddhism-master</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/jgmao/work/buddhism-master/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jgmao/work/buddhism-master/logs/stderr.log</string>
</dict>
</plist>
```

加载服务:
```bash
mkdir -p logs
launchctl load ~/Library/LaunchAgents/com.manana.buddhism-master.plist
```

## API 使用

### 通用搜索

```bash
curl "http://localhost:8000/api/knowledge/search?q=空性"
```

### 佛学问答

```bash
curl "http://localhost:8000/api/knowledge/ask?q=什么是般若？"
```

## 数据存储位置

| 数据类型 | 位置 | 说明 |
|---------|------|------|
| 代码 | ~/work/buddhism-master/ | Git 仓库 |
| 原始数据 | data/raw/ | JSON 格式的经文、概念 |
| 向量索引 | data/processed/embeddings_index.json | 本地文件索引 |
| Qdrant | ~/qdrant_storage/ | Docker volume |
| PostgreSQL | Mac mini 本地 | 元数据 |

## 与 SEELE 架构集成

Buddhism Master 可以作为 Knowledge Hub 的数据源之一：

```
Knowledge Hub (port 4300)
    └── 可选: 定期从 Buddhism Master 同步数据
```

或者独立运行，通过 API 互相调用。
