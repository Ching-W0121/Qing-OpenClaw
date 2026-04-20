# 记忆强制检索脚本

**用途**: 每次 browser 操作前强制检索相关错误记忆

---

## 🔧 使用方法

```python
# 在 browser 操作前调用
from memory_guard import check_before_action

# 检查
check_before_action("browser_act", {
    "target": "GPT 输入框",
    "page_type": "React",
    "url": "https://chatgpt.com"
})

# 输出：
# ⚠️ 记忆中有 2 条相关错误：
# 1. ERR-20260314-002: 动态页面元素失效
#    解决方案：等待 10 秒 + snapshot 后立即使用
# 2. ERR-20260313-001: 不等页面加载
#    解决方案：sleep(10) 后再 snapshot
```

---

## 📋 检索逻辑

```python
def check_before_action(action_type, context):
    """操作前强制检查记忆"""
    
    # 1. 构建搜索查询
    query = f"{action_type} {context.get('page_type', '')} {context.get('target', '')}"
    
    # 2. 检索记忆
    errors = memory_search(query, minScore=0.7)
    
    # 3. 显示相关错误
    if errors:
        print(f"⚠️ 记忆中有 {len(errors)} 条相关错误：")
        for i, error in enumerate(errors[:3], 1):
            print(f"{i}. {error.id}: {error.summary}")
            print(f"   解决方案：{error.solution}")
        
        # 4. 确认继续
        if len(errors) >= 3:
            print("\n🔴 错误次数过多，建议换方法或求助用户")
            confirm = input("继续操作？(y/n): ")
            if confirm.lower() != 'y':
                raise StopAction("用户取消操作")
    
    # 5. 记录检查日志
    log_check(action_type, context, errors)
```

---

## 📊 检索规则

| 操作类型 | 搜索关键词 | 最小匹配度 |
|----------|------------|------------|
| browser_act | browser automation | 0.7 |
| browser_snapshot | React Vue dynamic DOM | 0.7 |
| browser_open | page load wait | 0.6 |
| git_push | git network firewall | 0.7 |
| file_operation | file edit write | 0.6 |

---

## ✅ 输出示例

```
⚠️ 记忆中有 2 条相关错误：

1. ERR-20260314-002: 动态页面元素失效
   原因：React 页面重新渲染导致 ref 失效
   解决方案：等待 10 秒 + snapshot 后立即使用 + 验证结果
   
2. ERR-20260313-001: 不等页面加载
   原因：页面还在加载就操作
   解决方案：browser.open() 后 sleep(10)

📋 建议操作流程：
1. browser.open(url)
2. await sleep(10)
3. snapshot = browser.snapshot()
4. browser.act(ref=snapshot.ref)
5. verify = browser.snapshot()

继续操作？(y/n): 
```

---

**创建时间**: 2026-03-14 18:10  
**状态**: 待实现（需要编写 Python 脚本）
