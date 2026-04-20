#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path
from typing import List, Dict, Any, Optional

import faiss
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from unified_memory import db_connect as main_db_connect

MEMORY_ROOT = Path(__file__).parent
DB_PATH = MEMORY_ROOT / 'database' / 'optimized_memory.db'
INDEX_PATH = MEMORY_ROOT / 'database' / 'memory_faiss.index'
EMBED_DIM = 2048
API_URL = 'https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal'
API_KEY = 'fddc1778-d04c-403e-8327-ab68ec1ec9dd'
MODEL = 'doubao-embedding-vision-251215'


def configure_stdio():
    for stream_name in ('stdout', 'stderr'):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')


def db_connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _get_vector_columns(cur) -> List[str]:
    rows = cur.execute('PRAGMA table_info(memory_vectors)').fetchall()
    return [r[1] for r in rows]


def ensure_tables():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS memory_vectors (
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding_json TEXT,
            embedding TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (source_type, source_id)
        )
    ''')
    cols = _get_vector_columns(cur)
    if 'embedding_json' not in cols:
        cur.execute('ALTER TABLE memory_vectors ADD COLUMN embedding_json TEXT')
    if 'embedding' not in cols:
        cur.execute('ALTER TABLE memory_vectors ADD COLUMN embedding TEXT')
    conn.commit()
    conn.close()


def get_embedding(text: str) -> Optional[List[float]]:
    body = {
        'model': MODEL,
        'encoding_format': 'float',
        'input': [{'type': 'text', 'text': text}],
    }
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            emb = result.get('data', {}).get('embedding')
            if isinstance(emb, list) and len(emb) == EMBED_DIM:
                return emb
    except Exception:
        return None
    return None


def load_faiss_index() -> faiss.IndexFlatIP:
    if INDEX_PATH.exists():
        return faiss.read_index(str(INDEX_PATH))
    return faiss.IndexFlatIP(EMBED_DIM)


def save_faiss_index(index):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))


def normalize(vec: List[float]) -> np.ndarray:
    arr = np.array(vec, dtype='float32').reshape(1, -1)
    faiss.normalize_L2(arr)
    return arr


def upsert_vector(source_type: str, source_id: str, content: str) -> bool:
    ensure_tables()
    emb = get_embedding(content)
    if emb is None:
        return False

    emb_json = json.dumps(emb, ensure_ascii=False)
    content_hash = str(abs(hash(content)))
    conn = db_connect()
    cur = conn.cursor()
    cols = _get_vector_columns(cur)

    existing = cur.execute(
        'SELECT id FROM memory_vectors WHERE source_type = ? AND source_id = ? LIMIT 1',
        (source_type, source_id),
    ).fetchone() if 'id' in cols else None

    if existing:
        set_parts = ['content = ?', 'updated_at = CURRENT_TIMESTAMP']
        params = [content]
        if 'embedding_json' in cols:
            set_parts.append('embedding_json = ?')
            params.append(emb_json)
        if 'embedding' in cols:
            set_parts.append('embedding = ?')
            params.append(emb_json)
        if 'content_hash' in cols:
            set_parts.append('content_hash = ?')
            params.append(content_hash)
        if 'dim' in cols:
            set_parts.append('dim = ?')
            params.append(EMBED_DIM)
        params.append(existing[0])
        cur.execute(f"UPDATE memory_vectors SET {', '.join(set_parts)} WHERE id = ?", params)
    else:
        insert_cols = ['source_type', 'source_id', 'content']
        insert_vals = [source_type, source_id, content]
        if 'content_hash' in cols:
            insert_cols.append('content_hash')
            insert_vals.append(content_hash)
        if 'embedding_json' in cols:
            insert_cols.append('embedding_json')
            insert_vals.append(emb_json)
        if 'embedding' in cols:
            insert_cols.append('embedding')
            insert_vals.append(emb_json)
        if 'dim' in cols:
            insert_cols.append('dim')
            insert_vals.append(EMBED_DIM)
        placeholders = ', '.join(['?'] * len(insert_cols))
        cur.execute(
            f"INSERT INTO memory_vectors ({', '.join(insert_cols)}) VALUES ({placeholders})",
            insert_vals,
        )

    conn.commit()
    conn.close()
    rebuild_faiss_index()
    return True


def rebuild_faiss_index() -> Dict[str, Any]:
    ensure_tables()
    conn = db_connect()
    cur = conn.cursor()
    cols = _get_vector_columns(cur)
    emb_col = 'embedding_json' if 'embedding_json' in cols else 'embedding'
    rows = cur.execute(f'SELECT {emb_col} AS embedding_data FROM memory_vectors ORDER BY updated_at DESC').fetchall()
    conn.close()

    index = faiss.IndexFlatIP(EMBED_DIM)
    valid = 0
    for row in rows:
        try:
            emb = json.loads(row['embedding_data'])
            arr = normalize(emb)
            index.add(arr)
            valid += 1
        except Exception:
            continue
    save_faiss_index(index)
    return {'ok': True, 'vectors': valid, 'index_path': str(INDEX_PATH)}


def sync_from_main_db(limit: Optional[int] = None) -> Dict[str, Any]:
    ensure_tables()
    conn = main_db_connect()
    cur = conn.cursor()
    sql = 'SELECT id, content FROM episodes ORDER BY id DESC'
    if limit:
        sql += f' LIMIT {int(limit)}'
    rows = cur.execute(sql).fetchall()
    conn.close()

    written = 0
    for row in rows:
        if upsert_vector('episode', str(row['id']), row['content']):
            written += 1
    return {'ok': True, 'requested': len(rows), 'written': written}


def semantic_search(query: str, top_k: int = 8) -> List[Dict[str, Any]]:
    ensure_tables()
    q_emb = get_embedding(query)
    if q_emb is None:
        return []

    q = normalize(q_emb)
    index = load_faiss_index()
    if index.ntotal == 0:
        return []

    scores, ids = index.search(q, min(top_k * 4, index.ntotal))
    flat_ids = [int(i) for i in ids[0] if i != -1]
    if not flat_ids:
        return []

    conn = db_connect()
    cur = conn.cursor()
    rows = cur.execute('SELECT rowid, source_type, source_id, content, updated_at FROM memory_vectors').fetchall()
    row_map = {int(r['rowid']) - 1: r for r in rows}

    query_l = query.lower()
    query_terms = [term for term in query_l.replace('，', ' ').replace(',', ' ').split() if term]
    reranked = []
    now_ts = time.time()

    for i, score in zip(flat_ids, scores[0]):
        row = row_map.get(i)
        if not row:
            continue
        content = row['content'] or ''
        content_l = content.lower()

        keyword_bonus = 0.0
        for term in query_terms:
            if term and term in content_l:
                keyword_bonus += 0.03

        recency_bonus = 0.0
        updated_at = row['updated_at']
        try:
            ts = time.mktime(time.strptime(updated_at, '%Y-%m-%d %H:%M:%S'))
            age_hours = max(0.0, (now_ts - ts) / 3600.0)
            if age_hours <= 1:
                recency_bonus = 0.10
            elif age_hours <= 6:
                recency_bonus = 0.06
            elif age_hours <= 24:
                recency_bonus = 0.03
        except Exception:
            pass

        final_score = float(score) + keyword_bonus + recency_bonus
        reranked.append({
            'source_type': row['source_type'],
            'source_id': row['source_id'],
            'content': content,
            'score': final_score,
            'vector_score': float(score),
            'updated_at': row['updated_at'],
        })

    conn.close()
    reranked.sort(key=lambda x: x['score'], reverse=True)
    return reranked[:top_k]


if __name__ == '__main__':
    configure_stdio()
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stats'
    ensure_tables()
    if cmd == 'sync':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
        print(json.dumps(sync_from_main_db(limit), ensure_ascii=False, indent=2))
    elif cmd == 'search':
        query = ' '.join(sys.argv[2:])
        print(json.dumps(semantic_search(query), ensure_ascii=False, indent=2))
    elif cmd == 'rebuild':
        print(json.dumps(rebuild_faiss_index(), ensure_ascii=False, indent=2))
    else:
        conn = db_connect()
        cur = conn.cursor()
        count = cur.execute('SELECT COUNT(*) FROM memory_vectors').fetchone()[0]
        print(json.dumps({
            'db': str(DB_PATH),
            'vectors': count,
            'faiss_index': str(INDEX_PATH),
            'faiss_exists': INDEX_PATH.exists(),
        }, ensure_ascii=False, indent=2))
        conn.close()
