#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Vault 测试脚本

测试所有功能：
1. 数据库初始化
2. 添加记忆
3. 语义搜索
4. MemoryVault 集成
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from memory_vault import (
    init_database,
    add_memory,
    search_memory,
    get_memory_stats,
    MemoryVault,
    DB_PATH
)

def test_all():
    """运行所有测试"""
    print("=" * 60)
    print("Memory Vault 功能测试")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n[测试 1] 数据库初始化...")
    db_path = init_database()
    assert db_path.exists(), "❌ 数据库文件未创建"
    print(f"✅ 数据库已创建：{db_path}")
    
    # 2. 添加记忆
    print("\n[测试 2] 添加记忆...")
    
    test_memories = [
        ("动态网页操作必须等待 10 秒+snapshot 后立即使用 + 验证结果", "error"),
        ("browser 操作前必须检索记忆", "learning"),
        ("失败 3 次必须停止并换方法", "learning"),
        ("PostgreSQL 配置完成 5 张表已创建", "episodic"),
        ("GPT 页面是 React 应用会持续重新渲染", "semantic"),
    ]
    
    for text, mem_type in test_memories:
        mem_id = add_memory(text, mem_type)
        if mem_id > 0:
            print(f"  ✅ 已添加：{mem_type} (ID: {mem_id})")
    
    # 3. 语义搜索
    print("\n[测试 3] 语义搜索...")
    
    test_queries = [
        ("browser 操作失败怎么办", 3),
        ("React 页面注意事项", 2),
        ("失败多次如何处理", 3),
    ]
    
    for query, top_k in test_queries:
        print(f"\n  查询：{query}")
        results = search_memory(query, top_k=top_k)
        
        if results:
            print(f"  ✅ 找到 {len(results)} 条相关记忆：")
            for i, mem in enumerate(results, 1):
                print(f"    {i}. [{mem['memory_type']}] 相似度：{mem['similarity']:.2f}")
                print(f"       {mem['memory_text'][:60]}...")
        else:
            print(f"  ⚠️  未找到相关记忆")
    
    # 4. 统计信息
    print("\n[测试 4] 统计信息...")
    stats = get_memory_stats()
    print(f"  数据库：{stats['database']}")
    print(f"  总记忆数：{stats['total']}")
    print(f"  已访问：{stats['accessed']}")
    print(f"  按类型:")
    for mem_type, count in stats['by_type'].items():
        print(f"    - {mem_type}: {count}")
    
    # 5. MemoryVault 集成测试
    print("\n[测试 5] MemoryVault 集成测试...")
    vault = MemoryVault()
    
    # 行动前检索
    print("\n  行动前检索测试:")
    memories = vault.before_action("browser_act", {"target": "GPT 输入框", "page_type": "React"})
    
    # 行动后记录
    print("\n  行动后记录测试:")
    vault.after_action("success", "browser_act", {"method": "标准流程"})
    vault.after_action("failed", "git_push", {"error": "连接被重置"})
    
    # 反思记录
    print("\n  反思记录测试:")
    vault.reflect(
        trigger_type="error",
        trigger_data={"action": "browser_act", "error": "元素失效"},
        analysis={
            "result": {"root_cause": "等待时间不足"},
            "lessons": ["必须等待 10 秒让 React 完全加载"]
        }
    )
    
    # 最终统计
    print("\n[测试 6] 最终统计...")
    final_stats = get_memory_stats()
    print(f"  总记忆数：{final_stats['total']}")
    print(f"  新增记忆：{final_stats['total'] - len(test_memories)}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)

if __name__ == '__main__':
    test_all()
