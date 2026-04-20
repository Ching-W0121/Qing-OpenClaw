#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆写入器
- 主写入：SQLite 主库 memory/database/optimized_memory.db
- 兼容备份：episodic JSONL / semantic JSON / working JSON
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

MEMORY_ROOT = Path(__file__).parent
DB_PATH = MEMORY_ROOT / 'database' / 'optimized_memory.db'
EPISODIC_DIR = MEMORY_ROOT / 'episodic'
WORKING_DIR = MEMORY_ROOT / 'working'
SEMANTIC_DIR = MEMORY_ROOT / 'semantic'

EPISODIC_DIR.mkdir(parents=True, exist_ok=True)
WORKING_DIR.mkdir(parents=True, exist_ok=True)
SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def db_connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            user_id TEXT,
            channel_id TEXT,
            event_type TEXT,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_episodes_timestamp ON episodes(timestamp DESC)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_episodes_session ON episodes(session_id)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_episodes_event_type ON episodes(event_type)')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            category TEXT,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            usage_count INTEGER DEFAULT 0,
            last_used_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_confidence ON knowledge(confidence DESC)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_usage ON knowledge(usage_count DESC)')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            summary TEXT NOT NULL,
            key_points TEXT,
            episode_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            category TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def append_episode(content: str, *, timestamp: Optional[str] = None, session_id: str = 'agent:main:main',
                   channel: str = 'unknown', event_type: str = 'user_message', metadata: Optional[Dict[str, Any]] = None):
    ensure_tables()
    ts = timestamp or datetime.utcnow().isoformat() + 'Z'
    metadata = metadata or {}

    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO episodes (timestamp, session_id, user_id, channel_id, event_type, content, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (ts, session_id, 'user', channel, event_type, content, json.dumps(metadata, ensure_ascii=False))
    )
    row_id = cur.lastrowid
    conn.commit()
    conn.close()

    date = ts[:10]
    record_id = metadata.get('id') or f'EP-{int(datetime.utcnow().timestamp()*1000)}'
    jsonl_file = EPISODIC_DIR / f'{date}.jsonl'
    record = {
        'timestamp': ts,
        'type': event_type,
        'id': record_id,
        'db_id': row_id,
        'content': content,
        'session_id': session_id,
        'channel': channel,
        'metadata': metadata,
    }
    with open(jsonl_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

    # 双轨：主库写入后立即同步到 FAISS 向量层
    try:
        from vector_memory import upsert_vector
        upsert_vector('episode', str(row_id), content)
    except Exception:
        pass

    return record


def upsert_working(data: Dict[str, Any]):
    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    path = WORKING_DIR / 'session_current.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(path)


def append_working_event(event: Dict[str, Any], *, max_messages: int = 50, session_id: Optional[str] = None,
                         current_goal: Optional[str] = None, active_entities: Optional[list] = None,
                         scratchpad: Optional[str] = None):
    WORKING_DIR.mkdir(parents=True, exist_ok=True)
    path = WORKING_DIR / 'session_current.json'
    now_ts = datetime.utcnow().isoformat() + 'Z'
    data: Dict[str, Any] = {}
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}

    data.setdefault('session_id', session_id or 'agent:main:main')
    data.setdefault('started_at', now_ts)
    data.setdefault('recent_messages', [])
    data.setdefault('active_entities', [])
    data.setdefault('scratchpad', '')

    if session_id:
        data['session_id'] = session_id
    if current_goal is not None:
        data['current_goal'] = current_goal
    if active_entities:
        merged = list(dict.fromkeys(list(data.get('active_entities', [])) + list(active_entities)))
        data['active_entities'] = merged
    if scratchpad is not None:
        data['scratchpad'] = scratchpad

    data['recent_messages'].append(event)
    data['recent_messages'] = data['recent_messages'][-max_messages:]
    data['last_updated'] = event.get('timestamp') or now_ts

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(path)


def upsert_semantic_json(filename: str, data: Dict[str, Any]):
    ensure_tables()
    path = SEMANTIC_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    category = path.stem

    def flatten(obj, prefix=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                nk = f'{prefix}.{k}' if prefix else k
                yield from flatten(v, nk)
        else:
            yield prefix, obj

    conn = db_connect()
    cur = conn.cursor()
    structured_rows = []
    for key, value in flatten(data):
        store_value = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
        full_key = f'{category}.{key}'
        cur.execute(
            '''INSERT OR REPLACE INTO knowledge (key, category, value, confidence, updated_at)
               VALUES (?, ?, ?, ?, ?)''',
            (full_key, category, store_value, 0.8, datetime.utcnow().isoformat() + 'Z')
        )
        structured_rows.append((full_key, store_value))
    conn.commit()
    conn.close()

    # 向量化策略（2026-03-19 收口）：保留结构化 knowledge 表，但不再按每个细碎 key 单独向量化；
    # 改为按文档块/一级分组做更粗粒度的知识向量，减少噪声、降低索引膨胀。
    try:
        from vector_memory import replace_source_type_vectors, upsert_vector

        replace_source_type_vectors('knowledge', prefix=f'{category}.')

        grouped = {}
        for full_key, store_value in structured_rows:
            parts = full_key.split('.')
            group_key = '.'.join(parts[:3]) if len(parts) >= 3 else full_key
            grouped.setdefault(group_key, []).append(f'{full_key}: {store_value}')

        for group_key, items in grouped.items():
            text = '\n'.join(items)
            upsert_vector('knowledge', group_key, text)
    except Exception:
        pass
    return str(path)


def upsert_user_profile(data: Dict[str, Any]):
    ensure_tables()
    path = SEMANTIC_DIR / 'user_profile.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    def flatten(obj, prefix=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                nk = f'{prefix}.{k}' if prefix else k
                yield from flatten(v, nk)
        else:
            yield prefix, obj

    conn = db_connect()
    cur = conn.cursor()
    vector_payloads = []
    for key, value in flatten(data):
        store_value = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
        full_key = f'user_profile.{key}'
        cur.execute(
            '''INSERT OR REPLACE INTO user_profile (key, value, category, updated_at)
               VALUES (?, ?, ?, ?)''',
            (full_key, store_value, 'user_profile', datetime.utcnow().isoformat() + 'Z')
        )
        vector_payloads.append((full_key, f'{full_key} {store_value}'))
    conn.commit()
    conn.close()

    try:
        from vector_memory import upsert_vector
        for full_key, text in vector_payloads:
            upsert_vector('profile', full_key, text)
    except Exception:
        pass
    return str(path)


if __name__ == '__main__':
    ensure_tables()
    print(str(DB_PATH))
