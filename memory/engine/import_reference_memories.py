#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from unified_memory import upsert_knowledge
from vector_memory import upsert_vector

WORKSPACE = Path(r'C:\Users\TR\.openclaw\workspace')
TARGET_FILES = [
    'AGENTS.md',
    'SOUL.md',
    'TOOLS.md',
    'USER.md',
    'MEMORY.md',
]


def configure_stdio():
    for stream_name in ('stdout', 'stderr'):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')


def chunk_text(text: str, max_chars: int = 1200):
    text = text.strip()
    if not text:
        return []
    chunks = []
    current = []
    current_len = 0
    for para in text.split('\n\n'):
        para = para.strip()
        if not para:
            continue
        piece_len = len(para) + 2
        if current and current_len + piece_len > max_chars:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += piece_len
    if current:
        chunks.append('\n\n'.join(current))
    return chunks


def main():
    configure_stdio()
    imported_files = 0
    imported_chunks = 0
    updated_keys = 0

    for name in TARGET_FILES:
        path = WORKSPACE / name
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='replace')
        chunks = chunk_text(text)
        if not chunks:
            continue
        imported_files += 1
        for i, chunk in enumerate(chunks, start=1):
            key = f'reference_file.{name}#chunk{i}'
            value = f'FILE: {name}\nCHUNK: {i}/{len(chunks)}\n\n{chunk}'
            existed = upsert_knowledge(key, value)
            if existed:
                updated_keys += 1
            imported_chunks += 1
            try:
                upsert_vector('knowledge', key, value)
            except Exception:
                pass

    print(json.dumps({
        'imported_files': imported_files,
        'imported_chunks': imported_chunks,
        'updated_keys': updated_keys,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
