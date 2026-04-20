# Cleanup / Framework Operations v1

## Cleanup policy
1. 非主干文件不留根目录
2. 历史方案 / 旧实验 / 旧数据库进入 `archive/`
3. 临时脚本直接删除，不批量滞留
4. `integrations/feishu/` 作为独立集成保留，不与 `qing-agent/` / `memory/` 混放
5. `scripts/` 只保留正式全工程通用脚本

## Current scripts status
- `request_tracker.py` : 请求追踪工具（跨任务通用）

## Current integration status
- `integrations/feishu/` : 手机端飞书集成
- `integrations/skills/` : workspace 技能层
