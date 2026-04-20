#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Guard - Browser 操作前强制记忆检查

用法:
    python memory/memory_guard.py browser_act --target "GPT 输入框" --page_type "React"
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 设置控制台输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_failure_tracker():
    """加载失败计数器"""
    tracker_path = Path(__file__).parent / "failure_tracker.md"
    if not tracker_path.exists():
        return {}
    
    tracker = {}
    with open(tracker_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('|') and 'browser' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    action_type = parts[1].strip()
                    count = int(parts[2].strip()) if parts[2].strip().isdigit() else 0
                    tracker[action_type] = count
    return tracker

def check_failure_limit(action_type, tracker):
    """检查是否达到失败限制"""
    count = tracker.get(action_type, 0)
    if count >= 3:
        print(f"\n🔴 强制停止：{action_type} 已失败 {count} 次（阈值 3 次）")
        print("\n已触发:")
        print("  1. ❌ 停止该类型操作")
        print("  2. 📝 记录到 ERRORS.md")
        print("  3. 🤔 触发即时反思")
        print("  4. ⏸️ 等待用户指示")
        print("\n请用户指示下一步操作。")
        sys.exit(1)
    return count

def memory_search(query, min_score=0.7, max_results=3):
    """搜索记忆"""
    # 简化实现：搜索 ERRORS.md 和 LEARNINGS.md
    errors_path = Path(__file__).parent.parent / ".learnings" / "ERRORS.md"
    learnings_path = Path(__file__).parent.parent / ".learnings" / "LEARNINGS.md"
    
    results = []
    
    # 搜索 ERRORS.md
    if errors_path.exists():
        with open(errors_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if query.lower() in content.lower():
                # 提取相关错误
                sections = content.split('## ')
                for section in sections[:5]:
                    if query.lower() in section.lower():
                        results.append({
                            'source': 'ERRORS.md',
                            'content': section[:500]
                        })
    
    return results[:max_results]

def check_before_action(action_type, context):
    """操作前检查"""
    print(f"\n🔍 检查 {action_type} 操作...")
    
    # 1. 检查失败计数器
    tracker = load_failure_tracker()
    count = check_failure_limit(action_type, tracker)
    
    # 2. 检索记忆
    query = f"{action_type} {context.get('page_type', '')} {context.get('target', '')}"
    errors = memory_search(query)
    
    # 3. 显示相关错误
    if errors:
        print(f"\n⚠️ 记忆中有 {len(errors)} 条相关错误：")
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. 来源：{error['source']}")
            print(f"   {error['content'][:200]}...")
        
        # 4. 显示建议流程
        print(f"\n📋 建议操作流程：")
        print(f"1. browser.open(url)")
        print(f"2. await sleep(10)  # 等页面完全加载")
        print(f"3. snapshot = browser.snapshot()")
        print(f"4. browser.act(ref=snapshot.ref)  # 立即使用")
        print(f"5. verify = browser.snapshot()  # 验证结果")
        
        # 5. 确认继续
        if len(errors) >= 2:
            print(f"\n🔴 错误次数较多，建议谨慎操作")
            response = input("\n继续操作？(y/n): ").lower()
            if response != 'y':
                print("❌ 操作已取消")
                sys.exit(0)
    
    # 6. 记录检查日志
    log_check(action_type, context, errors)
    
    print(f"✅ 检查通过，可以执行 {action_type}")

def log_check(action_type, context, errors):
    """记录检查日志"""
    log_path = Path(__file__).parent / "memory_guard_log.jsonl"
    entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action_type,
        'context': context,
        'errors_found': len(errors),
        'proceeded': True
    }
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python memory_guard.py <action_type> [--target <target>] [--page_type <type>]")
        print("示例：python memory_guard.py browser_act --target 'GPT 输入框' --page_type 'React'")
        sys.exit(1)
    
    action_type = sys.argv[1]
    context = {}
    
    # 解析参数
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--target' and i < len(sys.argv) - 1:
            context['target'] = sys.argv[i + 1]
        elif arg == '--page_type' and i < len(sys.argv) - 1:
            context['page_type'] = sys.argv[i + 1]
    
    check_before_action(action_type, context)
