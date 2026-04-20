#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆 API（兼容入口）
旧版 memory_api.py 依赖 qmem 二进制文件；现已切换为统一主记忆系统：
- SQLite 主库: memory/database/optimized_memory.db
- 检索入口: memory/memory_search.py
- 向量层: memory/vector_memory.py
"""

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT = Path(__file__).resolve().parents[1]
MEMORY_ROOT = ROOT / 'memory'
DB_PATH = MEMORY_ROOT / 'database' / 'optimized_memory.db'


@dataclass
class Memory:
    id: str
    date: str
    type: str
    title: str
    tags: List[str]
    timestamp: str
    content: Dict[str, Any]
    size: int


class MemoryDB:
    def __init__(self, path: str = None):
        self.path = path or str(DB_PATH)
        self.conn = None

    def open(self):
        if not Path(self.path).exists():
            raise FileNotFoundError(f'记忆数据库不存在：{self.path}')
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        return self

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _row_to_memory(self, row) -> Memory:
        metadata = {}
        try:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
        except Exception:
            metadata = {}
        content = {
            'text': row['content'],
            'metadata': metadata,
        }
        return Memory(
            id=str(row['id']),
            date=(row['timestamp'] or '')[:10],
            type=row['event_type'] or 'episode',
            title=metadata.get('title') or (row['content'] or '').split('\n', 1)[0][:80],
            tags=metadata.get('tags') or [],
            timestamp=row['timestamp'] or '',
            content=content,
            size=len((row['content'] or '').encode('utf-8', errors='replace')),
        )

    def all(self) -> List[Memory]:
        rows = self.conn.execute(
            'SELECT id, timestamp, event_type, content, metadata FROM episodes ORDER BY timestamp DESC'
        ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def get(self, entry_id: str) -> Optional[Memory]:
        row = self.conn.execute(
            'SELECT id, timestamp, event_type, content, metadata FROM episodes WHERE id = ?',
            (entry_id,)
        ).fetchone()
        return self._row_to_memory(row) if row else None

    def search(self, query: str) -> List[Memory]:
        try:
            import sys
            sys.path.insert(0, str(MEMORY_ROOT))
            from memory_search import smart_query
            result = smart_query(query)
            entries = (result.get('result') or {}).get('entries') or []
            memories = []
            for item in entries:
                content = item.get('content') or json.dumps(item, ensure_ascii=False)
                memories.append(Memory(
                    id=str(item.get('source_id') or item.get('id') or ''),
                    date=(item.get('updated_at') or item.get('timestamp') or '')[:10],
                    type=item.get('source_type') or result.get('layer') or 'memory',
                    title=content.split('\n', 1)[0][:80],
                    tags=[],
                    timestamp=item.get('updated_at') or item.get('timestamp') or '',
                    content={'text': content, 'raw': item},
                    size=len(content.encode('utf-8', errors='replace')),
                ))
            return memories
        except Exception:
            rows = self.conn.execute(
                'SELECT id, timestamp, event_type, content, metadata FROM episodes WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 20',
                (f'%{query}%',)
            ).fetchall()
            return [self._row_to_memory(r) for r in rows]

    def search_by_date(self, start: str, end: str = None) -> List[Memory]:
        end = end or start
        rows = self.conn.execute(
            'SELECT id, timestamp, event_type, content, metadata FROM episodes WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ? ORDER BY timestamp DESC',
            (start, end)
        ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def search_by_tag(self, tag: str) -> List[Memory]:
        rows = self.conn.execute(
            'SELECT id, timestamp, event_type, content, metadata FROM episodes WHERE metadata LIKE ? ORDER BY timestamp DESC LIMIT 50',
            (f'%{tag}%',)
        ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def latest(self, count: int = 5) -> List[Memory]:
        rows = self.conn.execute(
            'SELECT id, timestamp, event_type, content, metadata FROM episodes ORDER BY timestamp DESC LIMIT ?',
            (count,)
        ).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def stats(self) -> Dict[str, Any]:
        episodes = self.conn.execute('SELECT COUNT(*) FROM episodes').fetchone()[0]
        knowledge = self.conn.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0]
        vectors = self.conn.execute('SELECT COUNT(*) FROM memory_vectors').fetchone()[0]
        return {
            'file': self.path,
            'episodes': episodes,
            'knowledge': knowledge,
            'vectors': vectors,
        }

    def summary(self) -> str:
        stats = self.stats()
        latest = self.latest(5)
        lines = [
            '📚 统一记忆数据库摘要',
            f"   DB：{stats['file']}",
            f"   Episodes：{stats['episodes']}",
            f"   Knowledge：{stats['knowledge']}",
            f"   Vectors：{stats['vectors']}",
            '',
            '📅 最近记忆:'
        ]
        for m in latest:
            tags = ', '.join(m.tags) if m.tags else '-'
            lines.append(f"   [{m.date}] {m.title}")
            lines.append(f"           标签：{tags}")
        return '\n'.join(lines)


def open_memory(path: str = None) -> MemoryDB:
    return MemoryDB(path).open()


def search_memory(query: str, path: str = None) -> List[Memory]:
    with MemoryDB(path) as db:
        return db.search(query)


def get_memory(entry_id: str, path: str = None) -> Optional[Memory]:
    with MemoryDB(path) as db:
        return db.get(entry_id)


def latest_memories(count: int = 5, path: str = None) -> List[Memory]:
    with MemoryDB(path) as db:
        return db.latest(count)


if __name__ == '__main__':
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    if len(sys.argv) < 2:
        print('Usage: memory_api.py <command> [args]')
        print('Commands: summary | stats | list [n] | search <query> | get <id> | tag <tag> | date <YYYY-MM-DD>')
        sys.exit(1)

    cmd = sys.argv[1]
    with MemoryDB() as db:
        if cmd == 'summary':
            print(db.summary())
        elif cmd == 'stats':
            print(json.dumps(db.stats(), ensure_ascii=False, indent=2))
        elif cmd == 'list':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            for m in db.latest(count):
                print(f'[{m.date}] {m.title}')
        elif cmd == 'search':
            query = ' '.join(sys.argv[2:])
            results = db.search(query)
            print(f'\n[SEARCH: {query}]')
            print(f'  Found: {len(results)} results')
            for m in results[:20]:
                print(f'  [{m.date}] {m.title}')
        elif cmd == 'get':
            entry_id = sys.argv[2]
            memory = db.get(entry_id)
            if memory:
                print(json.dumps(memory.content, ensure_ascii=False, indent=2))
            else:
                print(f'Not found: {entry_id}')
        elif cmd == 'tag':
            tag = sys.argv[2]
            results = db.search_by_tag(tag)
            print(f'\n[TAG: {tag}]')
            print(f'  Found: {len(results)} results')
            for m in results[:20]:
                print(f'  [{m.date}] {m.title}')
        elif cmd == 'date':
            date = sys.argv[2]
            results = db.search_by_date(date)
            print(f'\n[DATE: {date}]')
            print(f'  Found: {len(results)} results')
            for m in results[:20]:
                print(f'  [{m.date}] {m.title}')
        else:
            print(f'Unknown command: {cmd}')
            sys.exit(1)
