# Qing OpenClaw Workspace

> 青（Qing）的 OpenClaw 工作空间备份仓库
> 迁移日期：2026-04-20
> 原始机器：DESKTOP-8AJSH5O

---

## 📦 包含内容

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

### 记忆系统
| 路径 | 说明 |
|------|------|
| `memory/` | SQLite 主库 + 豆包向量层统一记忆系统 |
| `.learnings/` | 错误记录 / 学习日志 / 特性请求 |

### 文档
| 路径 | 说明 |
|------|------|
| `docs/architecture/` | 系统架构文档 |
| `docs/operations/` | 操作手册 |
| `docs/history/` | 历史记录 |
| `archive/` | 历史归档（飞书审计、数据库、文档工具等） |

### 集成
| 路径 | 说明 |
|------|------|
| `integrations/feishu/` | 飞书 Bot 集成（启动脚本、环境配置） |
| `integrations/skills/summarize-qwen/` | Qwen 摘要技能 |

### 脚本
| 文件 | 说明 |
|------|------|
| `scripts/request_tracker.py` | 请求追踪脚本 |
| `scripts/README.md` | 脚本说明 |

---

## 🚫 不包含（排除项）

- **`qing-agent/`** — 求职 Agent 专用目录（含真实投递数据、平台凭证）
- **`node_modules/`** — npm 包，新机器运行 `npm install` 即可
- **`.openclaw/`** — OpenClaw 系统配置（机器相关，重新配对）
- **`CLAWD.md`** — 工作空间状态文件（自动生成）
- **`tmp_zhilian_restore.py`** — 临时恢复脚本（Job Agent 残留）

---

## 🖥️ 新机器初始化步骤

### 1. 安装 OpenClaw
```bash
npm install -g openclaw
openclaw gateway install
```

### 2. 克隆本仓库到工作空间
```bash
# 在新机器的 workspace 目录下
git clone https://github.com/Ching-W0121/Qing-OpenClaw.git .
```

### 3. 安装依赖
```bash
npm install
```

### 4. 配置飞书集成（如需）
```bash
# 复制并编辑环境变量
cp integrations/feishu/.env.example integrations/feishu/.env
# 填写 App ID / App Secret / Bot Token
```

### 5. 初始化记忆系统
```bash
python memory/memory_search.py --help
# 验证 SQLite 主库可用
```

### 6. 配置 OpenClaw 并重启
```bash
openclaw gateway restart
```

### 7. 恢复身份（重要！）
新机器首次启动后，编辑以下文件确认机器名称一致：
- `IDENTITY.md` — AI 身份
- `USER.md` — 用户信息
- `TOOLS.md` — 检查飞书配置是否需要更新

---

## 🔑 重要配置（需重新在新机器填写）

### 飞书发图配置（TOOLS.md）
```
App ID: cli_a93ba86cdfba5bcc
用户 open_id: 待获取（在飞书开发者后台查看）
```

### 豆包向量模型配置（TOOLS.md）
```
Base URL: https://ark.cn-beijing.volces.com/api/v3
API Key: fddc1778-d04c-403e-8327-ab68ec1ec9dd
模型: doubao-embedding-vision-251215
```

---

## 📝 迁移备注

### 求职 Agent 独立迁移
qing-agent 目录包含真实的平台凭证和投递数据，**不**同步到 GitHub。如需在新机器使用：
1. 在新机器上单独部署 qing-agent
2. 重新配置平台登录凭证
3. 数据库文件需单独拷贝（`qing-agent/data/qing_agent.db`）

### 本次排除的临时文件
- `tmp_zhilian_restore.py` — 智联恢复脚本，迁移当天已确认残留，已排除

---

## 📅 迁移记录

| 日期 | 内容 |
|------|------|
| 2026-04-20 | 首次迁移，完整同步除 qing-agent 外的全部 workspace |
