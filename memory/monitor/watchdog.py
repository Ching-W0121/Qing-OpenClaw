#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory/Reflection watchdog.
目的：独立于主执行链，检查是否遵守：
1. 关键任务是否经过 preflight_guard
2. 是否继续存在 legacy memory 路径
3. 是否出现重复失败而未停下
4. 是否有近期任务只留在 markdown / 会话，未进入主库

用法:
  python memory/watchdog.py --task "任务名" --mode check
  python memory/watchdog.py --mode audit
"""

import argparse
import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import sys

MEMORY_ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = MEMORY_ROOT / 'engine'
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from unified_memory import append_episode

WORKSPACE = Path(r"C:/Users/TR/.openclaw/workspace")
MEMORY = WORKSPACE / "memory"
DB_PATH = MEMORY / "store" / "database" / "optimized_memory.db"
WORKING_PATH = MEMORY / "store" / "working" / "session_current.json"
LEARNINGS = WORKSPACE / ".learnings"

LEGACY_DISABLED = [
    MEMORY / "import_all_text_memories.py.disabled",
    MEMORY / "import_learnings_and_backups.py.disabled",
    MEMORY / "import_recent_memories.py.disabled",
    MEMORY / "import_scattered_memories.py.disabled",
    MEMORY / "memory_migration.py.disabled",
    MEMORY / "memory_rechunk.py.disabled",
    MEMORY / "migrate_to_database.py.disabled",
    MEMORY / "migrate_v2_to_v3.py.disabled",
    MEMORY / "load_context.cmd.disabled",
    MEMORY / "record_event.py.disabled",
    MEMORY / "record_fact.py.disabled",
    MEMORY / "record_step.py.disabled",
    MEMORY / "auto-record.js.disabled",
    MEMORY / "episodic-writer.js.disabled",
    MEMORY / "memory_guard.py.disabled",
]

PRELIGHT_MARKER = MEMORY / "watchdog_last_preflight.json"
WATCHDOG_OUT = MEMORY / "watchdog_report.json"
LAST_BACKFILL_MARKER = MEMORY / "watchdog_last_backfill.json"
DAILY_MD_PATTERN = re.compile(r'^##\s+(\d{4}-\d{2}-\d{2})\s+durable memory flush\s*$', re.MULTILINE)


def now_iso():
    return datetime.now().isoformat()


def db_connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def count_recent_episodes(minutes=180):
    if not DB_PATH.exists():
        return 0
    since = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat() + 'Z'
    conn = db_connect()
    cur = conn.cursor()
    n = cur.execute("SELECT COUNT(*) FROM episodes WHERE timestamp >= ?", (since,)).fetchone()[0]
    conn.close()
    return int(n)


def recent_task_titles(limit=20):
    if not DB_PATH.exists():
        return []
    conn = db_connect()
    cur = conn.cursor()
    rows = cur.execute("SELECT timestamp, metadata, content FROM episodes WHERE event_type IN ('task_completion','job_agent_round') ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    out = []
    for r in rows:
        meta = {}
        try:
            meta = json.loads(r['metadata'] or '{}')
        except Exception:
            meta = {}
        out.append({
            'timestamp': r['timestamp'],
            'title': meta.get('title') or meta.get('summary') or (r['content'][:120] if r['content'] else ''),
        })
    return out


def check_legacy_paths():
    missing = [str(p) for p in LEGACY_DISABLED if not p.exists()]
    return {'ok': len(missing) == 0, 'missing_disabled_files': missing}


def check_preflight(task: str | None):
    marker = load_json(PRELIGHT_MARKER, {}) or {}
    if not task:
        return {'ok': marker.get('checked', False), 'marker': marker}
    return {
        'ok': marker.get('checked', False) and marker.get('task') == task,
        'marker': marker,
        'expected_task': task,
    }


def mark_preflight(task: str):
    payload = {
        'checked': True,
        'task': task,
        'timestamp': now_iso(),
        'recent_episode_count_180m': count_recent_episodes(180),
    }
    save_json(PRELIGHT_MARKER, payload)
    return payload


def check_working_view():
    data = load_json(WORKING_PATH, {}) or {}
    return {
        'ok': bool(data),
        'session_id': data.get('session_id'),
        'last_updated': data.get('last_updated'),
        'current_goal': data.get('current_goal'),
    }


def detect_risk_signals():
    risks = []
    working = load_json(WORKING_PATH, {}) or {}
    scratch = json.dumps(working, ensure_ascii=False)
    if 'timed out' in scratch.lower() or '404' in scratch:
        risks.append('recent_working_view_contains_timeout_or_404')
    err_text = ''
    for file in [LEARNINGS / 'ERRORS.md', LEARNINGS / 'LEARNINGS.md']:
        if file.exists():
            err_text += file.read_text(encoding='utf-8', errors='replace')[-6000:]
    if '一天一换' in err_text or '无脑' in err_text or '无脑重复执行' in err_text:
        risks.append('recent_learning_mentions_path_instability')
    return risks


def extract_daily_flush(date_str: str) -> Optional[str]:
    md_path = MEMORY / f"{date_str}.md"
    if not md_path.exists():
        return None
    text = md_path.read_text(encoding='utf-8', errors='replace')
    match = DAILY_MD_PATTERN.search(text)
    if not match:
        return None
    start = match.start()
    next_match = DAILY_MD_PATTERN.search(text, match.end())
    end = next_match.start() if next_match else len(text)
    block = text[start:end].strip()
    return block or None


def latest_episode_timestamp_for_date(date_str: str) -> Optional[str]:
    if not DB_PATH.exists():
        return None
    conn = db_connect()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT timestamp FROM episodes WHERE substr(timestamp, 1, 10) = ? ORDER BY timestamp DESC LIMIT 1",
        (date_str,)
    ).fetchone()
    conn.close()
    return row['timestamp'] if row else None


def maybe_backfill_daily_flush(date_str: str):
    block = extract_daily_flush(date_str)
    if not block:
        return {'ok': False, 'reason': 'no_daily_flush_markdown'}

    last_episode_ts = latest_episode_timestamp_for_date(date_str)
    marker = load_json(LAST_BACKFILL_MARKER, {}) or {}
    if marker.get('date') == date_str and marker.get('source') == 'daily_flush_markdown':
        return {'ok': True, 'skipped': True, 'reason': 'already_backfilled_by_marker', 'last_episode_ts': last_episode_ts}

    if last_episode_ts and last_episode_ts >= f"{date_str}T12:00:00":
        return {'ok': True, 'skipped': True, 'reason': 'main_db_already_has_afternoon_entry', 'last_episode_ts': last_episode_ts}

    content = f"[重大任务补记忆] {date_str} durable memory flush\n\n{block}"
    metadata = {
        'title': f'{date_str} durable memory flush（watchdog backfill）',
        'summary': 'watchdog 发现当日 durable memory flush 已写入 markdown，但主库缺少对应下午/晚间记录，已自动补入。',
        'details': block,
        'tags': ['memory', 'critical', 'realtime-memory', 'watchdog', 'auto-backfill'],
        'source': 'watchdog',
        'priority': 'critical',
        'record_mode': 'watchdog_backfill',
        'recorded_at': now_iso(),
        'backfill_for_date': date_str,
    }
    record = append_episode(
        content=content,
        timestamp=f"{date_str}T23:59:00+08:00",
        session_id='agent:main:main',
        channel='watchdog',
        event_type='task_completion',
        metadata=metadata,
    )
    save_json(LAST_BACKFILL_MARKER, {
        'date': date_str,
        'source': 'daily_flush_markdown',
        'recorded_at': now_iso(),
        'episode_id': record.get('id'),
    })
    return {'ok': True, 'backfilled': True, 'record': record}


def audit(task: str | None = None):
    report = {
        'generated_at': now_iso(),
        'task': task,
        'preflight': check_preflight(task),
        'legacy_paths': check_legacy_paths(),
        'working_view': check_working_view(),
        'recent_task_titles': recent_task_titles(20),
        'recent_episode_count_180m': count_recent_episodes(180),
        'risk_signals': detect_risk_signals(),
        'auto_backfill': maybe_backfill_daily_flush((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')),
    }
    report['ok'] = all([
        report['legacy_paths']['ok'],
        report['working_view']['ok'],
    ]) and len(report['risk_signals']) == 0
    save_json(WATCHDOG_OUT, report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['check', 'mark', 'audit'], default='audit')
    parser.add_argument('--task', default='')
    args = parser.parse_args()

    if args.mode == 'mark':
        result = mark_preflight(args.task)
    elif args.mode == 'check':
        result = check_preflight(args.task or None)
    else:
        result = audit(args.task or None)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
