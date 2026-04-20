#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify that request / event / step runtime memory entry points all flow into the unified memory layer.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r'C:\Users\TR\.openclaw\workspace')


def configure_stdio():
    for stream_name in ('stdout', 'stderr'):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')


def run(cmd):
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return {
        'cmd': cmd,
        'code': res.returncode,
        'stdout': res.stdout.strip(),
        'stderr': res.stderr.strip(),
    }


def safe_print_json(data):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))


def main():
    configure_stdio()
    results = []
    results.append(run(['python', 'memory/record_runtime_event.py', '--type', 'operation', '--title', 'verify-chain-event', '--content', 'verify unified runtime event entry', '--tags', 'memory,verify,event']))
    results.append(run(['python', 'memory/record_runtime_event.py', '--type', 'operation', '--title', 'verify-chain-step', '--content', 'verify unified runtime step entry', '--tags', 'memory,verify,step']))
    results.append(run(['python', '-c', "import sys; sys.path.insert(0, r'C:\\Users\\TR\\.openclaw\\workspace\\scripts'); from request_tracker import RequestTracker; t=RequestTracker(); rid=t.log_request('verify-chain-request-entry', request_type='verify'); print(rid)"]))
    results.append(run(['python', 'memory/memory_search.py', '--query', 'verify-chain unified runtime request entry']))
    safe_print_json(results)


if __name__ == '__main__':
    main()
