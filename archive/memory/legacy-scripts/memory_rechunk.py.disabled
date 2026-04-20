#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Re-chunking Script - 重新分块迁移脚本

将现有大文件记忆重新解析，按块分割批量插入 SQLite
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_vault_v2 import (
    init_optimized_database,
    chunk_and_store_file,
    search_memory_optimized,
    get_memory_stats
)

# 需要重新分块的文件列表
FILES_TO_RECHUNK = [
    # memory 目录
    ("memory/episodic/2026-03-11.jsonl", "episodic"),
    ("memory/episodic/2026-03-12.jsonl", "episodic"),
    ("memory/episodic/2026-03-13.jsonl", "episodic"),
    ("memory/episodic/2026-03-14.jsonl", "episodic"),
    ("memory/semantic/lessons.json", "semantic"),
    ("memory/semantic/strategies.json", "semantic"),
    ("memory/semantic/mistakes.json", "semantic"),
    ("memory/semantic/patterns.json", "semantic"),
    
    # learnings 目录
    (".learnings/LEARNINGS.md", "learning"),
    (".learnings/ERRORS.md", "error"),
    
    # 重要文档
    ("MEMORY.md", "semantic"),
    ("AGENTS.md", "semantic"),
    ("TOOLS.md", "semantic"),
    ("SOUL.md", "semantic"),
    ("USER.md", "episodic"),
    ("HEARTBEAT.md", "episodic"),
]

def rechunk_all():
    """重新分块所有重要文件"""
    print("=" * 60)
    print("Memory Re-chunking - 重新分块迁移")
    print("=" * 60)
    
    # 初始化数据库
    init_optimized_database()
    
    total_inserted = 0
    
    # 处理每个文件
    workspace = Path(__file__).parent.parent
    
    for file_rel_path, memory_type in FILES_TO_RECHUNK:
        file_path = workspace / file_rel_path
        
        if file_path.exists():
            count = chunk_and_store_file(file_path, memory_type)
            total_inserted += count
        else:
            print(f"\n⚠️  文件不存在：{file_rel_path}")
    
    print("\n" + "=" * 60)
    print(f"重新分块完成!")
    print(f"  总插入：{total_inserted} 条记忆")
    print("=" * 60)
    
    # 显示统计
    stats = get_memory_stats()
    print(f"\n📊 当前数据库状态:")
    print(f"   总数：{stats['total']} 条")
    print(f"   类型分布:")
    for mem_type, count in stats['by_type'].items():
        print(f"     - {mem_type}: {count}")
    
    return total_inserted

def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    # 测试搜索
    test_queries = [
        ("2026-03-12 求职 Agent", 3),
        ("2026-03-13 智联招聘", 3),
        ("browser 操作 失败", 3),
        ("lessons.json semantic", 2),
    ]
    
    for query, top_k in test_queries:
        print(f"\n  查询：{query}")
        results = search_memory_optimized(query, top_k=top_k)
        
        if results:
            print(f"  ✅ 找到 {len(results)} 条")
        else:
            print(f"  ⚠️  未找到")

if __name__ == '__main__':
    rechunk_all()
    verify_migration()
