# 记忆系统 v4.0 - 统一主库架构

**当前唯一主线**：
- **主库**：`memory/database/optimized_memory.db`（SQLite）
- **统一写入器**：`memory/unified_memory.py`
- **统一检索器**：`memory/memory_search.py`
- **语义检索层**：`memory/vector_memory.py`（豆包 embedding）
- **文件层**：`working/`、`episodic/`、`semantic/` 仅作兼容备份/交换格式

---

## 核心原则

1. **SQLite 是唯一事实源（source of truth）**
2. **新记忆优先写入主库**
3. **豆包 embedding 只负责语义召回，不负责事实存储**
4. **JSON/JSONL 文件保留为兼容备份，不再是主记忆库**

---

## 当前架构

```text
用户消息 / 系统事件
        ↓
unified_memory.py
        ↓
optimized_memory.db  ← 唯一主库
        ↓
memory_search.py     ← 统一查询入口
        ↓
vector_memory.py     ← 豆包 embedding 语义召回层
```

---

## 主库表

- `episodes`：对话/请求/事件记录
- `knowledge`：语义知识、偏好、领域知识
- `conversation_summaries`：摘要
- `user_profile`：用户画像
- `memory_vectors`：向量索引（由豆包 embedding 生成）

---

## 主要脚本

### 1) 统一写入
```bash
python memory/unified_memory.py
```

### 2) 统一查询
```bash
python memory/memory_search.py --query "今天做了什么"
python memory/memory_search.py --layer semantic --type profile
```

### 3) 向量索引同步
```bash
python memory/vector_memory.py sync
```

### 4) 语义检索
```bash
python memory/vector_memory.py search 记忆系统 设计 思路
```

---

## 角色分层（2026-03-19 收口版）

### 1. 唯一事实源
- `memory/database/optimized_memory.db`

### 2. 默认检索入口
- `memory/memory_search.py`
- 规则：先查主库，再决定是否需要 working / episodic / semantic / vector

### 3. 语义召回层
- `memory/vector_memory.py`
- `memory_vectors + FAISS`
- 规则：只负责语义召回，不负责事实存储
- 约束：默认只保留当前主链需要的向量来源（episode / coarse knowledge / summary / profile）；历史导入的 `memory_file.*`、`scattered_file.*`、`recent_memory_file.*` 之类旧碎片索引不应继续常驻主召回空间

### 4. 兼容视图 / 交换视图
- `memory/working/session_current.json`
- `memory/episodic/YYYY-MM-DD.jsonl`
- `memory/semantic/*.json`
- 规则：这些文件可保留、查看、导出，但**不再视为主库**

### 5. 摘要视图
- `memory/YYYY-MM-DD.md`
- `MEMORY.md`
- 规则：它们是人工摘要 / 长期蒸馏视图，不再作为默认事实入口

---

## 当前目标

- 主库唯一化 ✅
- 写入路径唯一化 ✅
- 检索路径统一化 ✅
- 豆包 embedding 语义层接入 ✅
- 清理旧并行记忆系统 ✅（大部分）

---

**最后更新**: 2026-03-17
**架构版本**: v4.0
