#!/usr/bin/env python3
"""
统一记忆检索工具 - 优先查询 SQLite 主库，回退到文件层。

用法:
    python memory_search.py --layer working
    python memory_search.py --layer episodic --today
    python memory_search.py --layer semantic --type profile
    python memory_search.py --query "今天做了什么"
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = Path(__file__).parent
DB_PATH = MEMORY_ROOT / 'database' / 'optimized_memory.db'

HARD_MATCH_MAP = {
    'gemini': ['Gemini', 'browser_chain_validation', '固定链路', '动态定位'],
    'browser': ['browser', '动态网页', 'ref 失效', '验证'],
    '慢任务': ['子会话', '并发', 'subsession', '主会话'],
    'slow task': ['子会话', '并发', 'subsession', '主会话'],
    'subsession': ['子会话', '并发', '主会话'],
    '反思': ['reflection', '反思', 'learn', '闸门'],
}


def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def load_jsonl(path):
    entries = []
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        continue
    except FileNotFoundError:
        return []
    return entries


def db_connect():
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def query_working():
    data = load_json(MEMORY_ROOT / 'working' / 'session_current.json')
    if not data:
        return {"error": "No active session"}
    return {
        "session_id": data.get("session_id"),
        "current_goal": data.get("current_goal"),
        "message_count": len(data.get("recent_messages", [])),
        "active_entities": data.get("active_entities", [])
    }


def query_episodic(date=None, since=None, until=None, keyword=None):
    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        sql = "SELECT timestamp, session_id, event_type, content, metadata FROM episodes WHERE 1=1"
        params = []
        if date:
            sql += " AND DATE(timestamp) = ?"
            params.append(date)
        if since:
            sql += " AND timestamp >= ?"
            params.append(since)
        if until:
            sql += " AND timestamp <= ?"
            params.append(until)
        if keyword:
            sql += " AND content LIKE ?"
            params.append(f"%{keyword}%")
        sql += " ORDER BY timestamp DESC LIMIT 20"
        rows = cursor.execute(sql, params).fetchall()
        conn.close()
        return {
            "count": len(rows),
            "entries": [dict(r) for r in rows]
        }

    if date:
        file = MEMORY_ROOT / 'episodic' / f"{date}.jsonl"
        entries = load_jsonl(file)
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        file = MEMORY_ROOT / 'episodic' / f"{today}.jsonl"
        entries = load_jsonl(file)

    if keyword:
        entries = [e for e in entries if keyword.lower() in str(e).lower()]

    return {"count": len(entries), "entries": entries[:20]}


def query_semantic(type=None):
    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        if type == 'profile':
            rows = cursor.execute("SELECT key, value, category FROM user_profile ORDER BY key").fetchall()
            conn.close()
            return {"profile": {r['key']: r['value'] for r in rows}}
        elif type == 'preferences':
            rows = cursor.execute("SELECT key, value FROM knowledge WHERE category = 'preferences' ORDER BY key").fetchall()
            conn.close()
            return {"preferences": {r['key']: r['value'] for r in rows}}
        elif type == 'knowledge':
            rows = cursor.execute("SELECT key, value, confidence FROM knowledge ORDER BY confidence DESC, usage_count DESC LIMIT 50").fetchall()
            conn.close()
            return {"knowledge": [dict(r) for r in rows]}
        else:
            profile = cursor.execute("SELECT key, value FROM user_profile ORDER BY key").fetchall()
            preferences = cursor.execute("SELECT key, value FROM knowledge WHERE category = 'preferences' ORDER BY key").fetchall()
            knowledge = cursor.execute("SELECT key, value, confidence FROM knowledge ORDER BY confidence DESC, usage_count DESC LIMIT 50").fetchall()
            conn.close()
            return {
                "profile": {r['key']: r['value'] for r in profile},
                "preferences": {r['key']: r['value'] for r in preferences},
                "knowledge": [dict(r) for r in knowledge]
            }

    result = {}
    if type == 'profile' or type is None:
        result['profile'] = load_json(MEMORY_ROOT / 'semantic' / 'user_profile.json')
    if type == 'preferences' or type is None:
        result['preferences'] = load_json(MEMORY_ROOT / 'semantic' / 'preferences.json')
    if type == 'knowledge' or type is None:
        result['knowledge'] = load_json(MEMORY_ROOT / 'semantic' / 'knowledge_base.json')
    return result


def hard_match_lookup(query_text):
    conn = db_connect()
    if not conn:
        return None
    query_lower = query_text.lower()
    terms = []
    for key, values in HARD_MATCH_MAP.items():
        if key in query_lower:
            terms.extend(values)
    if not terms:
        return None
    cursor = conn.cursor()
    rows = []
    for term in terms[:8]:
        rows.extend(cursor.execute(
            "SELECT timestamp, content, metadata FROM episodes WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 5",
            (f"%{term}%",)
        ).fetchall())
    conn.close()
    seen = set()
    deduped = []
    for r in rows:
        key = (r['timestamp'], r['content'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(r))
    if not deduped:
        return None
    return {"layer": "episodic_hard_match", "result": {"count": len(deduped), "entries": deduped[:12]}}


def smart_query(query_text):
    query_lower = query_text.lower()
    hard = hard_match_lookup(query_text)
    if hard:
        return hard
    time_keywords = ["今天", "昨天", "刚才", "上周", "做什么", "做了什么", "最近", "刚刚", "完成了什么", "记住了吗"]
    if any(kw in query_lower for kw in time_keywords):
        if "刚才" in query_lower or "现在" in query_lower or "刚刚" in query_lower:
            return {"layer": "working", "result": query_working()}
        target_date = None
        if "昨天" in query_lower:
            from datetime import timedelta
            target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif "今天" in query_lower:
            target_date = datetime.now().strftime("%Y-%m-%d")
        return {"layer": "episodic", "result": query_episodic(date=target_date)}

    profile_keywords = ["偏好", "喜欢", "画像", "目标", "薪资", "城市"]
    if any(kw in query_lower for kw in profile_keywords):
        return {"layer": "semantic", "result": query_semantic()}

    # 明确事实/事件类问题，优先走结构化层，避免误入重语义链
    event_keywords = ["投递", "进展", "申请", "反思", "蒸馏", "任务", "链路", "修复", "更新"]
    if any(kw in query_lower for kw in event_keywords):
        result = query_episodic(keyword=query_text)
        if result.get("count"):
            return {"layer": "episodic_keyword", "result": result}

    conn = db_connect()
    if conn:
        cursor = conn.cursor()
        # 先做精确文本命中优先，保证“刚刚记录的明确短语”能被优先找到
        rows = cursor.execute(
            "SELECT timestamp, content, metadata FROM episodes WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 20",
            (f"%{query_text}%",)
        ).fetchall()
        if rows:
            conn.close()
            return {
                "layer": "episodic_exact",
                "result": {"count": len(rows), "entries": [dict(r) for r in rows]}
            }
        conn.close()

    # 默认优先走 FAISS 语义检索
    try:
        from vector_memory import semantic_search
        vector_hits = semantic_search(query_text, 8)
        if vector_hits:
            return {"layer": "vector", "result": {"count": len(vector_hits), "entries": vector_hits}}
    except Exception:
        pass

    if conn is None:
        return {
            "working": query_working(),
            "episodic": query_episodic(keyword=query_text),
            "semantic": query_semantic()
        }

    return {"layer": "episodic", "result": {"count": 0, "entries": []}}

    return {
        "working": query_working(),
        "episodic": query_episodic(keyword=query_text),
        "semantic": query_semantic()
    }


def query_stats():
    conn = db_connect()
    if not conn:
        return {'db_exists': False, 'db_path': str(DB_PATH)}
    cur = conn.cursor()
    stats = {
        'db_exists': True,
        'db_path': str(DB_PATH),
        'episode_entries': cur.execute('SELECT COUNT(*) FROM episodes').fetchone()[0],
        'knowledge_entries': cur.execute('SELECT COUNT(*) FROM knowledge').fetchone()[0],
        'summary_entries': cur.execute('SELECT COUNT(*) FROM conversation_summaries').fetchone()[0],
        'profile_entries': cur.execute('SELECT COUNT(*) FROM user_profile').fetchone()[0],
    }
    try:
        stats['vector_entries'] = cur.execute('SELECT COUNT(*) FROM memory_vectors').fetchone()[0]
        stats['vector_breakdown'] = [dict(source_type=r[0], count=r[1]) for r in cur.execute('SELECT source_type, COUNT(*) FROM memory_vectors GROUP BY source_type ORDER BY COUNT(*) DESC').fetchall()]
    except Exception:
        pass
    conn.close()
    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="统一记忆检索工具")
    parser.add_argument("--layer", choices=["working", "episodic", "semantic", "stats"], help="指定记忆层")
    parser.add_argument("--query", type=str, help="智能查询文本")
    parser.add_argument("--date", type=str, help="查询日期 (YYYY-MM-DD)")
    parser.add_argument("--since", type=str, help="开始时间 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--until", type=str, help="结束时间 (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--keyword", type=str, help="关键词过滤")
    parser.add_argument("--type", type=str, help="语义记忆类型 (profile/preferences/knowledge)")
    args = parser.parse_args()

    if args.query:
        result = smart_query(args.query)
    elif args.layer == 'working':
        result = query_working()
    elif args.layer == 'episodic':
        result = query_episodic(args.date, args.since, args.until, args.keyword)
    elif args.layer == 'semantic':
        result = query_semantic(args.type)
    elif args.layer == 'stats':
        result = query_stats()
    else:
        result = {
            'db_exists': DB_PATH.exists(),
            'db_path': str(DB_PATH),
            'working': query_working(),
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
    main()
