#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hard preflight guard: every serious task should pass memory + reflection checks first.
Usage:
  python memory/preflight_guard.py --task "describe task"
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

MEMORY_ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = MEMORY_ROOT / 'engine'
MONITOR_ROOT = MEMORY_ROOT / 'monitor'
ROOT = MEMORY_ROOT

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def run_memory_search(query: str):
    cmd = [sys.executable, str(ENGINE_ROOT / 'memory_search.py'), '--query', query]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        return {'ok': False, 'error': result.stderr.strip() or result.stdout.strip()}
    try:
        return {'ok': True, 'result': json.loads(result.stdout)}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'raw': result.stdout}


def classify_task(task: str):
    lowered = (task or '').lower()
    slow_keywords = [
        'scan', 'crawl', 'collect', 'scrape', 'browser', 'gemini', 'chatgpt',
        '整轮', '全量', '扫描', '抓取', '浏览器', '咨询', '分片'
    ]
    external_keywords = [
        'browser', 'gemini', 'chatgpt', 'acp', 'gateway', '外部', '浏览器', '咨询'
    ]
    return {
        'is_slow_task': any(k in lowered for k in slow_keywords),
        'needs_probe_first': any(k in lowered for k in external_keywords),
    }


def build_gate_status(task: str, memory: dict, channel_checked: bool = False, is_subsession: bool = False):
    task_flags = classify_task(task)
    violations = []

    if not memory.get('ok'):
        violations.append('memory_search_failed')

    if task_flags['is_slow_task'] and not is_subsession:
        violations.append('slow_task_requires_subsession')

    if task_flags['needs_probe_first'] and not channel_checked:
        violations.append('external_channel_requires_probe_first')

    status = 'READY' if not violations else 'BLOCKED'
    return {
        'status': status,
        'task_flags': task_flags,
        'violations': violations,
        'ready': status == 'READY',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--channel-checked', action='store_true')
    parser.add_argument('--probe-token', default='')
    parser.add_argument('--probe-channel', default='external')
    parser.add_argument('--is-subsession', action='store_true')
    parser.add_argument('--reflection-logged', action='store_true')
    args = parser.parse_args()

    probe_valid = False
    probe_data = {}
    if args.probe_token:
        try:
            verify = subprocess.run(
                [sys.executable, str(MONITOR_ROOT / 'probe_token.py'), 'verify', '--token', args.probe_token, '--channel', args.probe_channel],
                capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            probe_data = json.loads((verify.stdout or '').strip() or '{}')
            probe_valid = bool(probe_data.get('ok'))
        except Exception as e:
            probe_valid = False
            probe_data = {'ok': False, 'error': str(e)}

    effective_channel_checked = args.channel_checked or probe_valid

    memory = run_memory_search(args.task)
    gate = build_gate_status(args.task, memory, channel_checked=effective_channel_checked, is_subsession=args.is_subsession)

    if gate['task_flags']['needs_probe_first'] and not effective_channel_checked:
        gate['violations'].append('probe_not_confirmed')
        gate['status'] = 'BLOCKED'
        gate['ready'] = False

    try:
        subprocess.run(
            [sys.executable, str(MONITOR_ROOT / 'watchdog.py'), '--mode', 'mark', '--task', args.task],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

    output = {
        'ok': True,
        'task': args.task,
        'status': gate['status'],
        'ready': gate['ready'],
        'channel_checked': effective_channel_checked,
        'probe_token_used': bool(args.probe_token),
        'probe_channel': args.probe_channel,
        'probe_valid': probe_valid,
        'probe_result': probe_data,
        'is_subsession': args.is_subsession,
        'reflection_logged': args.reflection_logged,
        'memory_checked': memory['ok'],
        'memory_result': memory.get('result') if memory['ok'] else None,
        'memory_error': memory.get('error') if not memory['ok'] else None,
        'task_flags': gate['task_flags'],
        'violations': gate['violations'],
        'rules': [
            'memory-first',
            'reflection-before-action',
            'reuse-last-known-good-method',
            'stop-after-3-same-failures',
            'probe-before-external-channel',
            'slow-task-default-subsession'
        ],
        'watchdog_marked': True,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
