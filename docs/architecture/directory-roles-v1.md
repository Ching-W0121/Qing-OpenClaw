# Directory Roles v1

| Path | Role | Keep | Notes |
|---|---|---|---|
| `qing-agent/` | 求职业务主系统 | yes | 不与记忆系统混放 |
| `memory/` | 记忆系统主干 | yes | SQLite 主库优先 |
| `.learnings/` | 错误/学习沉淀 | yes | 反思输出层 |
| `integrations/skills/` | 必要技能层 | yes | 仅保留在用技能 |
| `integrations/feishu/` | 飞书手机端集成 | yes | 独立集成项目 |
| `scripts/` | 通用脚本层 | yes | 只保留全工程通用脚本 |
| `docs/` | 正式文档层 | yes | architecture / operations / history |
| `archive/` | 历史资产层 | yes | 非主干都归这里 |
| `.openclaw/` | 运行环境层 | keep-for-runtime | 不算业务框架 |
| `node_modules/` | 依赖层 | keep-for-runtime | 可重建 |
