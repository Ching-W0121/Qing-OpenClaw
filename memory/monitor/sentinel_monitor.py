#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sentinel monitor for memory/reflection/execution-gate enforcement.
Outputs PASS/WARN/BLOCK plus structured trace info.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / 'monitor_report_latest.json'
HISTORY_PATH = ROOT / 'monitor_report_history.jsonl'
CONSTRAINTS_PATH = ROOT / 'active_constraints.json'


try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def now_iso():
    return datetime.now().isoformat()


def load_constraints():
    try:
        return json.loads(CONSTRAINTS_PATH.read_text(encoding='utf-8')).get('constraints', [])
    except Exception:
        return []


def classify(task: str, channel_checked: bool, is_subsession: bool):
    lowered = (task or '').lower()
    violations = []
    level = 'PASS'
    constraints = load_constraints()

    slow = any(k in lowered for k in ['scan', 'crawl', 'collect', 'scrape', '整轮', '全量', '扫描', '抓取', '浏览器', 'gemini', 'chatgpt'])
    external = any(k in lowered for k in ['browser', 'gemini', 'chatgpt', 'acp', 'gateway', '浏览器', '外部'])

    for item in constraints:
        match_any = [x.lower() for x in item.get('match_any', [])]
        if not any(x in lowered for x in match_any):
            continue
        reqs = set(item.get('requires', []))
        if 'valid_probe_token' in reqs and not channel_checked:
            violations.append(f"CONSTRAINT::{item['id']}")
            level = 'BLOCK'
        if 'is_subsession' in reqs and not is_subsession:
            violations.append(f"CONSTRAINT::{item['id']}")
            if level != 'BLOCK':
                level = 'WARN'

    if external and not channel_checked:
        violations.append('PROBE_MISSING')
        level = 'BLOCK'

    if slow and not is_subsession:
        violations.append('SLOW_TASK_IN_MAIN_SESSION')
        if level != 'BLOCK':
            level = 'WARN'

    return {
        'level': level,
        'slow_task': slow,
        'external_task': external,
        'violations': violations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--channel-checked', action='store_true')
    parser.add_argument('--is-subsession', action='store_true')
    parser.add_argument('--memory-checked', action='store_true')
    parser.add_argument('--reflection-logged', action='store_true')
    args = parser.parse_args()

    gate = classify(args.task, args.channel_checked, args.is_subsession)

    if not args.memory_checked:
        gate['violations'].append('MEMORY_NOT_CHECKED')
        gate['level'] = 'BLOCK'

    if gate['level'] == 'PASS' and not args.reflection_logged:
        gate['violations'].append('REFLECTION_NOT_LOGGED_YET')
        gate['level'] = 'WARN'

    payload = {
        'trace_id': f"sentinel-{int(datetime.now().timestamp())}",
        'generated_at': now_iso(),
        'task': args.task,
        'status': gate['level'],
        'memory_checked': args.memory_checked,
        'reflection_logged': args.reflection_logged,
        'channel_checked': args.channel_checked,
        'is_subsession': args.is_subsession,
        'violations': gate['violations'],
        'intercept': gate['level'] == 'BLOCK',
        'remedy_instruction': (
            'STOP. Run memory/preflight first, verify external channel, and dispatch slow tasks to a subsession.'
            if gate['level'] == 'BLOCK' else
            'Review warnings before continuing.'
        )
    }

    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    with HISTORY_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(payload, ensure_ascii=False) + '\n')
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
