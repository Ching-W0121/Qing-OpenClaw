# memory Architecture v1

## Runtime truth path
- database/ : 主库与向量索引
- working/ : 当前会话投影视图
- episodic/ : 兼容事件视图
- semantic/ : 兼容语义/画像视图
- compat/ : memory 兼容入口

## Active runtime files
- unified_memory.py
- memory_search.py
- vector_memory.py
- record_task_completion.py
- record_runtime_event.py
- preflight_guard.py
- sentinel_monitor.py
- watchdog.py
- reflection-worker.js
- execution_gate.py
- probe_token.py

## Moved out
- disabled migration/import helpers
- old markdown root summaries
- test files
- old one-off reflection/guard notes
