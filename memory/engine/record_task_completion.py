#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重大任务完成后，强制即时写入统一记忆主库 + working memory。

用法：
python memory/record_task_completion.py \
  --title "求职 Agent 下午轮运行结果" \
  --summary "完成了抓取/评分/判定，未真实投递" \
  --details "智联筛出 2 个岗位，状态 dry_run；working memory 之前未更新" \
  --tags jobs,critical,realtime-memory \
  --source manual
"""

import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from unified_memory import append_episode, upsert_working, append_working_event, db_connect as memory_db_connect, ensure_tables as ensure_memory_tables  # noqa: E402
from vector_memory import upsert_vector, db_connect as vector_db_connect, ensure_tables as ensure_vector_tables  # noqa: E402

CN_TZ = timezone(timedelta(hours=8))


def configure_stdio():
    for stream_name in ('stdout', 'stderr'):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')


def now_iso():
    return datetime.now(CN_TZ).isoformat()


def parse_args():
    p = argparse.ArgumentParser(description='Record critical task completion into unified memory immediately.')
    p.add_argument('--title', required=True, help='任务标题')
    p.add_argument('--summary', required=True, help='一句话总结')
    p.add_argument('--details', default='', help='详细说明')
    p.add_argument('--tags', default='', help='逗号分隔标签，如 jobs,critical,realtime-memory')
    p.add_argument('--source', default='manual', help='来源 manual|assistant|auto')
    p.add_argument('--channel', default='feishu', help='渠道标识')
    p.add_argument('--session-id', default='agent:main:main', help='会话 ID')
    p.add_argument('--event-type', default='task_completion', help='事件类型')
    return p.parse_args()


def main():
    configure_stdio()
    args = parse_args()
    ts = now_iso()
    tags = [t.strip() for t in args.tags.split(',') if t.strip()]

    content = f"[重大任务完成] {args.title}\n\n总结：{args.summary}"
    if args.details:
        content += f"\n\n详情：{args.details}"

    metadata = {
        'title': args.title,
        'summary': args.summary,
        'details': args.details,
        'tags': tags,
        'source': args.source,
        'priority': 'critical' if 'critical' in tags else 'high',
        'record_mode': 'immediate_required',
        'recorded_at': ts,
    }

    episode = append_episode(
        content=content,
        timestamp=ts,
        session_id=args.session_id,
        channel=args.channel,
        event_type=args.event_type,
        metadata=metadata,
    )

    working = {
        'session_id': args.session_id,
        'started_at': ts,
        'current_goal': f'已完成并即时记录：{args.title}',
        'recent_messages': [
            {
                'role': 'assistant',
                'content': args.summary,
                'timestamp': ts,
            }
        ],
        'active_entities': tags,
        'scratchpad': args.details,
        'last_updated': ts,
        'memory_guard': {
            'critical_task_recorded': True,
            'recorded_at': ts,
            'title': args.title,
        }
    }
    path = upsert_working(working)
    append_working_event(
        {
            'role': 'assistant',
            'type': args.event_type,
            'title': args.title,
            'content': content,
            'timestamp': ts,
            'source': 'record_task_completion',
        },
        session_id=args.session_id,
        current_goal=f'已完成并即时记录：{args.title}',
        active_entities=tags,
        scratchpad=args.details,
    )

    ensure_memory_tables()
    mem_conn = memory_db_connect()
    mem_cur = mem_conn.cursor()
    total_episode_entries = mem_cur.execute('SELECT COUNT(*) FROM episodes').fetchone()[0]
    total_knowledge_entries = mem_cur.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0]
    total_summary_entries = mem_cur.execute('SELECT COUNT(*) FROM conversation_summaries').fetchone()[0]
    total_profile_entries = mem_cur.execute('SELECT COUNT(*) FROM user_profile').fetchone()[0]
    mem_conn.close()

    vector_written = 0
    total_vectors = None
    vector_payloads = {
        'title': args.title,
        'summary': args.summary,
        'details': args.details,
        'tags': ' '.join(tags),
    }
    try:
        for field, value in vector_payloads.items():
            if value:
                if upsert_vector('episode_field', f"{episode.get('id')}:{field}", value):
                    vector_written += 1
        ensure_vector_tables()
        conn = vector_db_connect()
        cur = conn.cursor()
        total_vectors = cur.execute('SELECT COUNT(*) FROM memory_vectors').fetchone()[0]
        conn.close()
    except Exception as e:
        result = {
            'ok': False,
            'episode_id': episode.get('id'),
            'working_file': path,
            'recorded_at': ts,
            'vector_error': str(e),
            'episode_entries': total_episode_entries,
            'knowledge_entries': total_knowledge_entries,
            'summary_entries': total_summary_entries,
            'profile_entries': total_profile_entries,
            'memory_message': f'纳入结构化事件 1 条 / Episodes {total_episode_entries} / Knowledge {total_knowledge_entries} / Summaries {total_summary_entries} / Profile {total_profile_entries}（向量分段写入失败）',
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    result = {
        'ok': True,
        'episode_id': episode.get('id'),
        'working_file': path,
        'recorded_at': ts,
        'vector_written': vector_written,
        'total_vectors': total_vectors,
        'episode_entries': total_episode_entries,
        'knowledge_entries': total_knowledge_entries,
        'summary_entries': total_summary_entries,
        'profile_entries': total_profile_entries,
        'memory_message': f'纳入结构化事件 1 条 / Episodes {total_episode_entries} / Knowledge {total_knowledge_entries} / Summaries {total_summary_entries} / Profile {total_profile_entries} / Vectors {total_vectors}',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
