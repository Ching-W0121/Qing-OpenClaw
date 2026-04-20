# Qing OpenClaw Workspace

> 青（Qing）的 OpenClaw 工作空间备份仓库
> 迁移日期：2026-04-20
> 原始机器：DESKTOP-8AJSH5O

---

## 🎯 用途

本仓库用于在新机器上快速恢复青的工作环境，**不包含** qing-agent（求职 Agent）。

---

## 📦 本仓库包含

### 核心身份文件
| 文件 | 说明 |
|------|------|
| `IDENTITY.md` | AI 身份定义（名称：青） |
| `SOUL.md` | 人格与原则 |
| `USER.md` | 用户档案（庆，深圳，品牌策划方向） |
| `MEMORY.md` | 长期记忆蒸馏版 |
| `AGENTS.md` | Agent 工作规范（含双重反思机制） |
| `TOOLS.md` | 本地工具配置与记忆系统用法 |
| `HEARTBEAT.md` | 定时任务检查清单 |

### 学习记录 ✅
| 文件 | 说明 |
|------|------|
| `.learnings/ERRORS.md` | 错误记录（26 条教训） |
| `.learnings/LEARNINGS.md` | 学习日志 |
| `.learnings/FEATURE_REQUESTS.md` | 特性请求 |

### 记忆系统 ✅
| 路径 | 说明 |
|------|------|
| `memory/engine/database/optimized_memory.db` | SQLite 主库（3MB） |
| `memory/engine/database/memory_faiss.index` | FAISS 向量索引（8KB） |
| `memory/engine/episodic/*.jsonl` | 每日事件日志（03-27 ~ 03-30） |
| `memory/engine/memory_search.py` | 统一检索入口 |
| `memory/engine/unified_memory.py` | 统一写入器 |
| `memory/engine/vector_memory.py` | 向量层管理 |

### 飞书集成
| 路径 | 说明 |
|------|------|
| `integrations/feishu/.env.example` | 环境变量模板 |
| `integrations/feishu/README.md` | 集成说明 |
| `integrations/feishu/check_config.py` | 配置检查脚本 |
| `integrations/feishu/start.bat` | 启动脚本 |

### 技能
| 路径 | 说明 |
|------|------|
| `integrations/skills/summarize-qwen/SKILL.md` | Qwen 摘要技能 |

### 架构文档
| 路径 | 说明 |
|------|------|
| `docs/architecture/` | 目录角色、记忆架构等 |
| `docs/operations/feishu/` | 飞书集成操作手册 |
| `docs/operations/framework-operations-v1.md` | 框架操作说明 |

---

## 🚫 不包含

- **`qing-agent/`** — 求职 Agent（含平台凭证和投递数据），单独管理
- **`node_modules/`** — npm 包，运行 `npm install` 安装
- **`.openclaw/`** — OpenClaw 系统配置（机器相关，重新配对）
- **机器相关配置** — `.env`（飞书凭证等），根据 `.env.example` 重新填写

---

## 🖥️ 新机器初始化

```bash
# 1. 克隆仓库到 workspace
git clone https://github.com/Ching-W0121/Qing-OpenClaw.git C:\Users\TR\.openclaw\workspace

# 2. 安装依赖
npm install

# 3. 初始化 OpenClaw（首次）
openclaw gateway install

# 4. 恢复飞书配置
cp integrations/feishu/.env.example integrations/feishu/.env
# 编辑 integrations/feishu/.env，填写 App ID / App Secret / Bot Token

# 5. 重启 OpenClaw
openclaw gateway restart
```

---

## 📅 提交历史

| Commit | 说明 |
|--------|------|
| `59d3bb4` | 清理 qing-agent 和旧数据（删除 151 个文件，34 万行） |
| `3b37b4d` | 初始迁移 |
