#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Issue and verify short-lived probe tokens for external channels."""

import argparse
import json
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKENS_PATH = ROOT / 'probe_tokens.json'
TTL_MINUTES = 5

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def now():
    return datetime.now()


def load_tokens():
    if not TOKENS_PATH.exists():
        return []
    try:
        return json.loads(TOKENS_PATH.read_text(encoding='utf-8'))
    except Exception:
        return []


def save_tokens(tokens):
    TOKENS_PATH.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding='utf-8')


def prune(tokens):
    current = now()
    return [t for t in tokens if datetime.fromisoformat(t['expires_at']) > current]


def issue(channel):
    tokens = prune(load_tokens())
    token = secrets.token_hex(16)
    payload = {
        'token': token,
        'channel': channel,
        'issued_at': now().isoformat(),
        'expires_at': (now() + timedelta(minutes=TTL_MINUTES)).isoformat()
    }
    tokens.append(payload)
    save_tokens(tokens)
    return payload


def verify(token, channel=''):
    tokens = prune(load_tokens())
    save_tokens(tokens)
    for item in tokens:
        if item['token'] == token and (not channel or item['channel'] == channel):
            return {'ok': True, 'token': token, 'channel': item['channel'], 'expires_at': item['expires_at']}
    return {'ok': False, 'token': token, 'channel': channel}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['issue', 'verify'])
    parser.add_argument('--channel', default='external')
    parser.add_argument('--token', default='')
    args = parser.parse_args()

    if args.action == 'issue':
        result = issue(args.channel)
    else:
        result = verify(args.token, args.channel)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
