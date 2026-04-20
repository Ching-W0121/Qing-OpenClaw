# 记忆系统 v3.0 - 三层认知架构

**基于 ChatGPT 咨询 (2026-03-11) 设计**

---

## 🧠 核心架构

```
Working Memory → Episodic Memory → Semantic Memory
     (RAM)           (日志)           (知识)
       ↓               ↓                ↓
   In-memory      SQLite/JSONL     Vector DB
```

---

## 📁 目录结构

```
memory/
├── working/                    # 工作记忆（会话级）
│   └── session_current.json    # 当前会话上下文
│
├── episodic/                   # 情景记忆（事件级）
│   ├── 2026-03-11.jsonl        # 用户请求日志
│   └── ...
│
├── semantic/                   # 语义记忆（长期知识）
│   ├── user_profile.json       # 用户画像
│   ├── preferences.json        # 偏好设置
│   └── knowledge_base.json     # 领域知识
│
├── summaries/                  # 归档总结
│   └── 2026-W10.json           # 周总结
│
├── memory_index.json           # 记忆索引（快速查询）
└── README.md                   # 本文档
```

---

## 🔍 各层说明

### 1. Working Memory（工作记忆）

**文件**: `memory/working/session_current.json`

**用途**: 当前会话的临时上下文

**特点**:
- 会话结束时自动清空（或压缩后转入 Episodic）
- 只保留最近 20 条消息
- 极快访问速度

**内容**:
```json
{
  "session_id": "agent:main:main-20260311-142100",
  "current_goal": "重构三层记忆系统",
  "recent_messages": [...],
  "active_entities": [...],
  "scratchpad": "当前推理信息"
}
```

---

### 2. Episodic Memory（情景记忆）

**文件**: `memory/episodic/YYYY-MM-DD.jsonl`

**用途**: 记录"发生了什么"——用户请求、任务执行、对话历史

**特点**:
- JSONL 格式（append only，只追加不修改）
- 按日期分文件
- 每周压缩为总结

**内容**:
```jsonl
{"timestamp":"2026-03-11T14:01:00","type":"user_request","user":"...","result":"...","tags":[...]}
{"timestamp":"2026-03-11T13:56:00","type":"user_request","user":"...","result":"...","tags":[...]}
```

---

### 3. Semantic Memory（语义记忆）

**文件**: `memory/semantic/*.json`

**用途**: 记录"是什么"——稳定的知识、概念、用户画像

**特点**:
- 长期稳定（不随会话变化）
- 结构化存储（便于推理）
- 每月清理（时间衰减）

**文件**:
- `user_profile.json` - 用户基本信息、职业目标、项目
- `preferences.json` - 沟通风格、偏好设置
- `knowledge_base.json` - 领域知识、系统配置

---

## 🔄 记忆流动

```
会话进行中
    ↓
Working Memory（临时上下文）
    ↓ (会话结束)
Episodic Memory（固化日志）
    ↓ (每日提炼)
Semantic Memory（抽象知识）
```

---

## 🔎 查询策略

| 问题类型 | 检索层 | 示例 |
|----------|--------|------|
| "刚才做了什么" | Working | 当前会话上下文 |
| "今天做了什么" | Episodic | 时间范围查询 |
| "我的偏好是什么" | Semantic | user_profile / preferences |
| "以前讨论过这个吗" | Episodic + Vector | 语义搜索 |

---

## 🧹 遗忘机制

| 层级 | 策略 | 周期 |
|------|------|------|
| Working | 删除（超出 20 条） | 实时 |
| Episodic | 压缩（周总结） | 每周 |
| Semantic | 衰减（frequency × recency） | 每月 |

---

## 📊 当前状态

- **Working**: 1 个活跃会话
- **Episodic**: 13 条请求（2026-03-11）
- **Semantic**: 3 个核心文件
- **Summaries**: 1 个周总结（2026-W10）

---

## 🚀 待实现功能

- [ ] 自动抽象（Episodic → Semantic）
- [ ] 记忆重要性评分
- [ ] 每周自动压缩任务
- [ ] 查询路由优化（memory gating）
- [ ] Vector DB 集成（语义搜索）

---

**最后更新**: 2026-03-11 14:55  
**架构版本**: v3.0  
**设计来源**: ChatGPT 咨询
