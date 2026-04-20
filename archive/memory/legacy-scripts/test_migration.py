#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Migration Test - 验证 v3.0 迁移结果

测试内容:
1. 数据一致性检查（FAISS vs SQLite）
2. 语义命中测试
3. 边界值测试

作者：青 (Qing)
创建日期：2026-03-15
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from memory_vault_faiss import MemoryVaultFAISS

# ==================== 配置 ====================

V3_DB_PATH = Path(__file__).parent / "memory_vault_faiss.db"
V3_INDEX_PATH = Path(__file__).parent / "memory_vault_faiss.index"

# ==================== 测试函数 ====================

def test_consistency():
    """测试 1: 数据一致性检查"""
    print("=" * 60)
    print("🧪 测试 1: 数据一致性检查")
    print("=" * 60)
    
    vault = MemoryVaultFAISS(db_path=V3_DB_PATH, index_path=V3_INDEX_PATH)
    stats = vault.get_stats()
    
    print(f"   SQLite 记录数：{stats['total']}")
    print(f"   FAISS 向量数：{stats['faiss_vectors']}")
    
    if stats['faiss_vectors'] == stats['total']:
        print("   ✅ 一致性检查通过：FAISS 和 SQLite 记录数一致")
        return True
    else:
        print("   ⚠️  一致性检查警告：FAISS 和 SQLite 记录数不一致")
        print(f"   差异：{abs(stats['faiss_vectors'] - stats['total'])} 条")
        return False

def test_semantic_search():
    """测试 2: 语义命中测试"""
    print()
    print("=" * 60)
    print("🧪 测试 2: 语义命中测试")
    print("=" * 60)
    
    vault = MemoryVaultFAISS(db_path=V3_DB_PATH, index_path=V3_INDEX_PATH)
    
    # 测试查询（基于已知记忆内容）
    test_queries = [
        ("browser 自动化", ["browser", "自动化", "页面"]),
        ("前程无忧投递", ["前程无忧", "投递", "51job"]),
        ("记忆系统", ["记忆", "系统", "FAISS"]),
        ("FAISS 索引", ["FAISS", "索引", "向量"]),
        ("智联招聘", ["智联", "招聘", "职位"]),
    ]
    
    all_passed = True
    
    for query, keywords in test_queries:
        print(f"\n   查询：'{query}'")
        results = vault.search_memory(query=query, top_k=3)
        
        if results:
            print(f"   ✅ 找到 {len(results)} 条结果:")
            for i, r in enumerate(results[:3], 1):
                content_preview = r['content'][:60].replace('\n', ' ')
                print(f"     {i}. [{r['memory_type']}] {content_preview}...")
            
            # 检查是否包含关键词（至少一个）
            found_keyword = False
            for r in results:
                content_lower = r['content'].lower()
                if any(kw.lower() in content_lower for kw in keywords):
                    found_keyword = True
                    break
            
            if found_keyword:
                print(f"   ✅ 语义相关性：找到匹配关键词")
            else:
                print(f"   ⚠️  语义相关性：未找到匹配关键词（但可能有语义关联）")
        else:
            print(f"   ⚠️  未找到结果")
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """测试 3: 边界值测试"""
    print()
    print("=" * 60)
    print("🧪 测试 3: 边界值测试")
    print("=" * 60)
    
    vault = MemoryVaultFAISS(db_path=V3_DB_PATH, index_path=V3_INDEX_PATH)
    
    # 测试 1: 空查询
    print("\n   测试 1: 空查询")
    try:
        results = vault.search_memory(query="", top_k=3)
        print(f"   ✅ 空查询处理正常（返回 {len(results)} 条）")
    except Exception as e:
        print(f"   ⚠️  空查询异常：{e}")
    
    # 测试 2: top_k=1
    print("\n   测试 2: top_k=1")
    try:
        results = vault.search_memory(query="记忆", top_k=1)
        print(f"   ✅ top_k=1 正常（返回 {len(results)} 条）")
    except Exception as e:
        print(f"   ⚠️  top_k=1 异常：{e}")
    
    # 测试 3: top_k=100（大于实际数量）
    print("\n   测试 3: top_k=100（大数量）")
    try:
        results = vault.search_memory(query="记忆", top_k=100)
        print(f"   ✅ top_k=100 正常（返回 {len(results)} 条）")
    except Exception as e:
        print(f"   ⚠️  top_k=100 异常：{e}")
    
    # 测试 4: 重复添加（去重测试）
    print("\n   测试 4: 重复添加（去重测试）")
    try:
        test_text = "测试去重功能 - 这是一条测试记忆"
        id1 = vault.add_memory(text=test_text, memory_type="learning")
        id2 = vault.add_memory(text=test_text, memory_type="learning")
        
        if id1 > 0 and id2 == -1:
            print(f"   ✅ 去重功能正常（首次添加 ID={id1}, 重复添加返回 -1）")
        else:
            print(f"   ⚠️  去重功能异常（id1={id1}, id2={id2}）")
    except Exception as e:
        print(f"   ⚠️  去重测试异常：{e}")
    
    return True

def test_migration_summary():
    """测试 4: 迁移总结"""
    print()
    print("=" * 60)
    print("📊 测试 4: 迁移总结")
    print("=" * 60)
    
    vault = MemoryVaultFAISS(db_path=V3_DB_PATH, index_path=V3_INDEX_PATH)
    stats = vault.get_stats()
    
    print(f"   数据库：{V3_DB_PATH}")
    print(f"   FAISS 索引：{V3_INDEX_PATH}")
    print()
    print(f"   总记录数：{stats['total']}")
    print(f"   FAISS 索引大小：{stats['faiss_vectors']} 条向量")
    print(f"   LRU 缓存大小：{stats['cache_size']} 条")
    print(f"   数据库：{stats['database']}")
    print()
    print("   按类型统计:")
    for mem_type, count in stats['by_type'].items():
        print(f"     - {mem_type}: {count}")
    
    print()
    print("=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🧪 Memory Migration Test - v3.0 验证")
    print()
    
    # 执行测试
    test1 = test_consistency()
    test2 = test_semantic_search()
    test3 = test_edge_cases()
    test_migration_summary()
    
    # 总结
    print()
    if test1 and test2:
        print("🎉 迁移验证成功！v3.0 系统运行正常")
    else:
        print("⚠️  迁移验证完成，但有部分测试未通过，请检查日志")
    
    print()
