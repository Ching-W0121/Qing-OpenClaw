#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆合并/导入工具（已迁移到 SQLite + FAISS 主记忆链）

旧版 memory_merge.py 用于生成 memories.qmem。
现在改为：
- merge: 将 memory/ 下的日记/JSON/JSONL 重新导入统一主记忆库
- list/get/stats: 直接读取统一主记忆库
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
MEMORY_ROOT = ROOT / 'memory'
DB_PATH = MEMORY_ROOT / 'database' / 'optimized_memory.db'


def db_connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def import_via_script(script_name: str):
    import subprocess
    result = subprocess.run(
        ['python', str(MEMORY_ROOT / script_name)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout or f'{script_name} failed')
    return result.stdout.strip()


def merge_all():
    outputs = {}
    for script in [
        'import_all_text_memories.py',
        'import_reference_memories.py',
        'import_scattered_memories.py',
        'import_learnings_and_backups.py',
        'import_recent_memories.py',
    ]:
        try:
            outputs[script] = json.loads(import_via_script(script))
        except Exception as e:
            outputs[script] = {'ok': False, 'error': str(e)}
    return outputs


def stats():
    conn = db_connect()
    cur = conn.cursor()
    result = {
        'db': str(DB_PATH),
        'episodes': cur.execute('SELECT COUNT(*) FROM episodes').fetchone()[0],
        'knowledge': cur.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0],
        'vectors': cur.execute('SELECT COUNT(*) FROM memory_vectors').fetchone()[0],
    }
    conn.close()
    return result


def list_latest(limit: int = 20):
    conn = db_connect()
    rows = conn.execute(
        'SELECT id, timestamp, event_type, substr(content,1,120) as preview FROM episodes ORDER BY timestamp DESC LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_entry(entry_id: str) -> Optional[dict]:
    conn = db_connect()
    row = conn.execute(
        'SELECT id, timestamp, event_type, content, metadata FROM episodes WHERE id = ?',
        (entry_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == '__main__':
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    if len(sys.argv) < 2:
        print('Usage: memory_merge.py <command> [args]')
        print('Commands: merge | list [n] | get <id> | stats')
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'merge':
        print(json.dumps(merge_all(), ensure_ascii=False, indent=2))
    elif cmd == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print(json.dumps(list_latest(limit), ensure_ascii=False, indent=2))
    elif cmd == 'get':
        if len(sys.argv) < 3:
            print('Usage: memory_merge.py get <id>')
            sys.exit(1)
        print(json.dumps(get_entry(sys.argv[2]), ensure_ascii=False, indent=2))
    elif cmd == 'stats':
        print(json.dumps(stats(), ensure_ascii=False, indent=2))
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)
