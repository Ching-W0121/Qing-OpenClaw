# Workspace Architecture v1

## Core Systems
- `qing-agent/` : 求职 Agent 主业务系统
- `memory/` : 记忆主系统
- `.learnings/` : 错误/教训/纠正沉淀

## Integration Layer
- `integrations/feishu/` : 手机端飞书集成
- `integrations/skills/` : workspace 技能层

## Support Systems
- `scripts/` : 全工程通用正式脚本层
- `docs/` : 正式文档层
- `archive/` : 历史资产、旧链路、旧数据库、旧实验归档层

## Runtime / Environment
- `.openclaw/` : OpenClaw 本地运行环境目录
- `node_modules/` + `package*.json` : Node 依赖层

## Governance Files
- `AGENTS.md` / `SOUL.md` / `TOOLS.md` / `USER.md` / `MEMORY.md` / `HEARTBEAT.md` / `IDENTITY.md`
