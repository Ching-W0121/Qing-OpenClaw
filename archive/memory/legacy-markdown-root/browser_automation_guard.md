# Browser 自动化操作强制检查系统

**创建日期**: 2026-03-14 18:10  
**状态**: ✅ 已激活

---

## 🚨 强制执行规则

### 规则 1: 操作前必须检索记忆

```python
# 每次 browser 操作前
BEFORE_BROWSER_ACTION:
    errors = memory_search("browser automation")
    if errors:
        print("⚠️ 记忆中有相关错误：")
        print(errors[:3])  # 显示前 3 条
```

### 规则 2: 失败计数器

```python
FAILURE_LIMIT = 3

failure_tracker = {
    "browser_snapshot": 0,
    "browser_act": 0,
    "browser_open": 0,
    "git_push": 0,
    "file_operation": 0
}

if failure_tracker[action_type] >= FAILURE_LIMIT:
    STOP_AND_ASK_USER()
```

### 规则 3: 操作后必须验证

```python
AFTER_BROWSER_ACTION:
    verify_result()
    if failed:
        log_error(ERRORS.md)
        failure_tracker[action_type] += 1
        
        if failure_tracker[action_type] >= 3:
            trigger_immediate_reflection()
```

---

## 📋 动态网页操作规范（React/Vue）

### 正确流程

```
1. browser.open(url)
2. await sleep(10)  # 等页面完全加载
3. snapshot = browser.snapshot()  # 获取新 DOM
4. browser.act(ref=snapshot.ref)  # 立即使用，不等待
5. verify = browser.snapshot()  # 验证结果
6. if failed: log_error() + failure_count++
```

### 错误流程（禁止）

```
❌ snapshot() → 等待 → 用旧 ref → 失败 → 假设成功
```

---

## 🔴 已记录的错误模式

| 错误 ID | 错误类型 | 发生次数 | 解决方案 |
|---------|----------|----------|----------|
| ERR-20260314-001 | 数据编造 | 1 | 实事求是，不验证不报告 |
| ERR-20260314-002 | 动态页面元素失效 | 2 | 等待加载 + snapshot 后立即使用 + 验证 |
| ERR-20260314-003 | 死循环等待 | 1 | 设置超时 + 失败 3 次停止 |

---

## ⚡ 实时反思触发条件

**立即触发反思**（不等 6 小时）：
1. 同一错误发生 3 次
2. 用户明确纠正
3. 关键任务失败（投递、推送）

**反思流程**：
```
触发 → 读取最近 50 条记录 → LLM 分析 → 更新 lessons.json → 追加 LEARNINGS.md
```

---

## 📊 失败计数器状态

| 操作类型 | 当前计数 | 阈值 | 状态 |
|----------|----------|------|------|
| browser_snapshot | 0 | 3 | ✅ 正常 |
| browser_act | 0 | 3 | ✅ 正常 |
| browser_open | 0 | 3 | ✅ 正常 |
| git_push | 0 | 3 | ✅ 正常 |
| file_operation | 0 | 3 | ✅ 正常 |

---

**激活时间**: 2026-03-14 18:10  
**下次检查**: 每次 browser 操作前
