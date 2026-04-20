#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把今日 workspace 文件活动回填为结构化记忆事件。
只写记忆层，不碰业务层数据库。
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(r'C:\Users\TR\.openclaw\workspace')
MEMORY_DIR = ROOT / 'memory'
sys.path.insert(0, str(MEMORY_DIR))

from record_event import now_iso  # type: ignore
from unified_memory import append_episode  # type: ignore

SINCE = datetime(2026, 3, 18, 0, 0, 0)
SKIP_DIRS = {'node_modules', '.git', '__pycache__', '.pytest_cache'}


def classify(rel: str) -> str:
    rel_l = rel.lower()
    if rel_l.startswith('memory/'):
        return 'memory'
    if rel_l.startswith('qing-agent/data/'):
        return 'job-agent-data'
    if rel_l.startswith('qing-agent/'):
        return 'job-agent-code'
    if rel_l.startswith('scripts/'):
        return 'scripts'
    if rel_l.startswith('.tmp_') or rel_l.startswith('tmp_'):
        return 'tmp-runtime'
    return 'workspace'


def main():
    buckets = defaultdict(list)
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in SKIP_DIRS for part in rel.split('/')):
            continue
        if datetime.fromtimestamp(path.stat().st_mtime) < SINCE:
            continue
        buckets[classify(rel)].append(rel)

    ts = now_iso()
    created = 0
    for bucket, files in sorted(buckets.items()):
        files = sorted(files)
        sample = files[:30]
        extra = max(0, len(files) - len(sample))
        content = (
            f"今日文件活动分类：{bucket}\n\n"
            f"文件数：{len(files)}\n"
            f"样本文件：\n- " + "\n- ".join(sample)
        )
        if extra:
            content += f"\n- ... 另有 {extra} 个文件"

        append_episode(
            content=content,
            timestamp=ts,
            session_id='agent:main:main',
            channel='local_script',
            event_type='daily_activity_backfill',
            metadata={
                'title': f'今日文件活动回填: {bucket}',
                'summary': f'回填今日 {bucket} 类文件活动 {len(files)} 个',
                'tags': ['memory', 'backfill', 'daily-activity', bucket],
                'bucket': bucket,
                'file_count': len(files),
                'files': sample,
                'truncated': extra > 0,
            }
        )
        created += 1

    print(json.dumps({'created_events': created, 'buckets': {k: len(v) for k, v in buckets.items()}}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
