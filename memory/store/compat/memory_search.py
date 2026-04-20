#!/usr/bin/env python3
"""
兼容入口：转发到统一记忆检索器 memory/memory_search.py
"""

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'memory' / 'memory_search.py'

if __name__ == '__main__':
    runpy.run_path(str(TARGET), run_name='__main__')
