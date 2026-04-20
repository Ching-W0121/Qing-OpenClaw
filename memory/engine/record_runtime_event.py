#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
唯一正式的运行期事件写入入口。
所有运行期记录统一写入 SQLite 主库，并同步 working view 与向量层。
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from unified_memory import append_episode, append_working_event


def configure_stdio():
    for stream_name in ('stdout', 'stderr'):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')


def main():
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--content', required=True)
    parser.add_argument('--tags', default='')
    parser.add_argument('--session-id', default='agent:main:main')
    parser.add_argument('--channel', default='local_script')
    args = parser.parse_args()

    ts = datetime.utcnow().isoformat() + 'Z'
    tags = [t.strip() for t in args.tags.split(',') if t.strip()]
    metadata = {
        'title': args.title,
        'summary': args.content[:200],
        'tags': tags,
        'source': 'record_runtime_event',
    }
    rec = append_episode(
        content=f"[{args.title}]\n\n{args.content}",
        timestamp=ts,
        session_id=args.session_id,
        channel=args.channel,
        event_type=args.type,
        metadata=metadata,
    )
    append_working_event({
        'role': 'system',
        'content': args.content,
        'timestamp': ts,
        'title': args.title,
        'type': args.type,
    }, session_id=args.session_id)
    print(json.dumps({'ok': True, 'record': rec}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
