#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified execution gate: runs preflight + sentinel and returns a single allow/deny decision.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def run_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    raw = result.stdout or result.stderr
    try:
        return json.loads(raw), result.returncode
    except Exception:
        return {'raw': raw, 'returncode': result.returncode}, result.returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', required=True)
    parser.add_argument('--channel-checked', action='store_true')
    parser.add_argument('--probe-token', default='')
    parser.add_argument('--probe-channel', default='external')
    parser.add_argument('--is-subsession', action='store_true')
    parser.add_argument('--reflection-logged', action='store_true')
    args = parser.parse_args()

    preflight_cmd = [sys.executable, str(ROOT / 'preflight_guard.py'), '--task', args.task]
    sentinel_cmd = [sys.executable, str(ROOT / 'sentinel_monitor.py'), '--task', args.task, '--memory-checked']

    if args.channel_checked:
        preflight_cmd.append('--channel-checked')
        sentinel_cmd.append('--channel-checked')
    if args.probe_token:
        preflight_cmd.extend(['--probe-token', args.probe_token, '--probe-channel', args.probe_channel])
        sentinel_cmd.append('--channel-checked')
    if args.is_subsession:
        preflight_cmd.append('--is-subsession')
        sentinel_cmd.append('--is-subsession')
    if args.reflection_logged:
        preflight_cmd.append('--reflection-logged')
        sentinel_cmd.append('--reflection-logged')

    preflight, _ = run_json(preflight_cmd)
    sentinel, _ = run_json(sentinel_cmd)

    allow = bool(preflight.get('ready')) and sentinel.get('status') != 'BLOCK'
    payload = {
        'task': args.task,
        'allow': allow,
        'status': 'READY' if allow else 'BLOCKED',
        'preflight': preflight,
        'sentinel': sentinel,
        'remedy_instruction': sentinel.get('remedy_instruction') or 'Review preflight/sentinel violations.'
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not allow:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
