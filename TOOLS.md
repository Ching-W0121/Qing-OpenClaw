# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## 🧠 Memory System (v4.0)

### 当前主线（2026-03-19 收口更新）

- **唯一主库**: `memory/database/optimized_memory.db`
- **统一写入器**: `memory/unified_memory.py`
- **统一检索器**: `memory/memory_search.py`
- **语义检索层**: `memory/vector_memory.py`
- **Embedding 模型**: `doubao-embedding-vision-251215`
- **默认读取规则**: 先查主库 / `memory_search.py`，再看兼容视图；不再 `md-first`
- **文件层角色**: `working/`、`episodic/`、`semantic/` 仅作兼容备份/交换视图，不再是事实主库
- **Markdown 层角色**: `memory/*.md` 与 `MEMORY.md` 只作人工摘要 / 长期蒸馏，不再作为默认事实入口


### ⚠️ 强制检索规则（2026-03-14 新增）

**每次 browser 操作前必须检索**：
```python
errors = memory_search("browser automation dynamic page")
if errors:
    print("⚠️ 记忆中有相关错误：")
    print(errors[:3])
```

**不检索 = 禁止操作**

### Quick Commands

```bash
# 默认主入口：智能查询（优先主库 + 语义召回）
python memory/memory_search.py --query "今天做了什么"
python memory/memory_search.py --query "昨天做了什么"
python memory/memory_search.py --query "最近完成了什么"

# Working View (current session snapshot)
python memory/memory_search.py --layer working

# Episodic Backup View (only when you need date-bounded backup records)
python memory/memory_search.py --layer episodic
python memory/memory_search.py --layer episodic --date 2026-03-11

# Semantic View (profile/preferences)
python memory/memory_search.py --layer semantic --type profile

# Force-import markdown/reference views into SQLite + vector layer
python memory/import_reference_memories.py
```

### Hard Rule: No md-first execution

- `memory/*.md` / `MEMORY.md` / `.learnings/*.md` are **not** the primary runtime source of truth.
- Runtime decisions must read from `memory/memory_search.py` / SQLite / vector layer first.
- Markdown files are compatibility views and reflection outputs; they must be imported into the main memory system, not treated as the only memory path.
- If a recurring workflow still depends on reading daily markdown directly before main memory, treat that workflow as legacy and retire or rewrite it.

### Hard Rule: Reuse the last-known-good path

- Once a task type has a verified working method, keep using the same method and the same code path by default.
- If the signal changes or results become abnormal, stop immediately and run reflection / validation before trying again.
- Do **not** improvise a new path mid-task unless the old path is clearly broken and that break has been explicitly verified.

### Layer Roles

| Layer | Path | Role |
|-------|------|------|
| Primary Fact Store | `memory/database/optimized_memory.db` | 唯一事实源 |
| Retrieval Entry | `memory/memory_search.py` | 默认读取入口 |
| Working View | `memory/working/session_current.json` | 当前会话投影视图 |
| Episodic Backup | `memory/episodic/YYYY-MM-DD.jsonl` | 兼容备份 / 交换格式 |
| Semantic Exchange | `memory/semantic/*.json` | 兼容导出 / 交换视图 |
| Summary Views | `memory/*.md`, `MEMORY.md` | 人工摘要 / 长期蒸馏 |
| Vector Recall | `memory/database/memory_faiss.index`, `memory_vectors` | 语义召回层，不是事实层 |
| Archive | `memory/archive/old_markdown/` | 历史归档 |

### Memory Sync

- **Schedule**: Hourly (0 * * * *)
- **Target**: GitHub `Qing-OpenClaw-memory`
- **Content**: `memory/`, `.learnings/`

### 🚨 重大任务即时记录（2026-03-17 新增）

**原则**：重大任务一完成，必须立刻写入 `memory/database/optimized_memory.db`，不能只停留在对话上下文。

**统一命令**：
```bash
python memory/record_task_completion.py --title "任务标题" --summary "一句话总结" --details "关键结果/异常/验证信息" --tags critical,realtime-memory
```

**执行后必须验证**：
1. `memory/working/session_current.json` 已更新
2. 当日 `memory/episodic/YYYY-MM-DD.jsonl` 有新增记录
3. 再向庆汇报“已完成”

**典型场景**：
- 求职 Agent 跑完一轮
- 真实投递结果产生
- 大规模重构 / 数据迁移完成
- 用户明确说“这个必须实时记录”

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## 工作习惯

- **任务完成后必须汇报**：告诉庆任务已完成，并简述做了什么

---

## 📸 飞书发图片（重要！）

**问题**: OpenClaw 的 `message` 工具在飞书上发图有 bug，飞书收到的是文件路径文本，不是真正的图片。

**正确方法**: 用 `exec` 工具执行 curl 调用飞书 API，分三步：

### Step 1: 获取 tenant_access_token

```powershell
# 从 openclaw.json 读取 appSecret
$CONFIG = Get-Content "$env:APPDATA\openclaw\openclaw.json" | ConvertFrom-Json
$APP_ID = $CONFIG.channels.feishu.appId
$APP_SECRET = $CONFIG.channels.feishu.appSecret

# 获取 token
$TOKEN_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -Method Post -ContentType 'application/json' -Body (@{app_id=$APP_ID;app_secret=$APP_SECRET} | ConvertTo-Json)
$TOKEN = $TOKEN_RESPONSE.tenant_access_token
```

### Step 2: 上传图片获取 image_key

```powershell
# 上传图片（支持 JPEG, PNG, WEBP, GIF, TIFF, BMP, ICO）
$IMAGE_PATH = "C:/path/to/image.png"
$IMAGE_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/images' -Method Post -Headers @{Authorization="Bearer $TOKEN"} -Form @{image_type="message";image=(Get-Item $IMAGE_PATH)}
$IMAGE_KEY = $IMAGE_RESPONSE.data.image_key
```

### Step 3: 发送图片消息

```powershell
# 发送图片消息
$RECEIVE_ID = "ou_xxxxxxxx"  # 收信人 open_id
$CONTENT = (@{image_key=$IMAGE_KEY} | ConvertTo-Json -Compress)
Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' -Method Post -Headers @{Authorization="Bearer $TOKEN";'Content-Type'='application/json'} -Body (@{receive_id=$RECEIVE_ID;msg_type="image";content=$CONTENT} | ConvertTo-Json)
```

### 关键信息

| 配置项 | 值 |
|--------|-----|
| App ID | `cli_a93ba86cdfba5bcc` |
| 用户 open_id | 待获取（在飞书开发者后台查看） |
| 支持格式 | JPEG, PNG, WEBP, GIF, TIFF, BMP, ICO |
| 最大文件大小 | 10MB |

### 完整示例（PowerShell 脚本）

```powershell
# 飞书发图完整脚本
param(
    [string]$ImagePath,
    [string]$ReceiveId
)

# 读取配置
$CONFIG = Get-Content "$env:APPDATA\openclaw\openclaw.json" | ConvertFrom-Json
$APP_ID = $CONFIG.channels.feishu.appId
$APP_SECRET = $CONFIG.channels.feishu.appSecret

# Step 1: 获取 token
$TOKEN_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -Method Post -ContentType 'application/json' -Body (@{app_id=$APP_ID;app_secret=$APP_SECRET} | ConvertTo-Json)
$TOKEN = $TOKEN_RESPONSE.tenant_access_token

# Step 2: 上传图片
$IMAGE_RESPONSE = Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/images' -Method Post -Headers @{Authorization="Bearer $TOKEN"} -Form @{image_type="message";image=(Get-Item $ImagePath)}
$IMAGE_KEY = $IMAGE_RESPONSE.data.image_key

# Step 3: 发送消息
$CONTENT = (@{image_key=$IMAGE_KEY} | ConvertTo-Json -Compress)
Invoke-RestMethod -Uri 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' -Method Post -Headers @{Authorization="Bearer $TOKEN";'Content-Type'='application/json'} -Body (@{receive_id=$ReceiveId;msg_type="image";content=$CONTENT} | ConvertTo-Json)

Write-Host "图片发送成功！image_key: $IMAGE_KEY"
```

**使用方法**: 当用户要求发送图片时，执行上述 PowerShell 脚本，替换 `$ImagePath` 和 `$ReceiveId` 参数。

---

## 🧠 豆包向量模型配置（多模态）

| 配置项 | 值 |
|--------|-----|
| Base URL | `https://ark.cn-beijing.volces.com/api/v3` |
| API Key | `fddc1778-d04c-403e-8327-ab68ec1ec9dd` |
| 模型 ID | `doubao-embedding-vision-251215` |
| Embedding 维度 | 2048 |
| API Endpoint | `/embeddings/multimodal` |
| 支持类型 | text, image_url, video_url |

### 调用示例

```bash
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/embeddings/multimodal" \
  -H "Authorization: Bearer fddc1778-d04c-403e-8327-ab68ec1ec9dd" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-embedding-vision-251215",
    "encoding_format": "float",
    "input": [
      {"type": "text", "text": "文本内容"},
      {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}
    ]
  }'
```

### 响应格式

```json
{
  "created": 1743575029,
  "data": {
    "embedding": [-0.123, -0.355, ...],
    "object": "embedding"
  },
  "id": "021743575029461...",
  "model": "doubao-embedding-vision-251215",
  "usage": {
    "prompt_tokens": 13987,
    "total_tokens": 13987
  }
}
```

### 调用示例

```bash
curl -X POST "https://ark.cn-beijing.volces.com/api/v3/embeddings" \
  -H "Authorization: Bearer fddc1778-d04c-403e-8327-ab68ec1ec9dd" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Doubao-embedding-vision",
    "input": ["文本 1", "文本 2"]
  }'
```

### 响应格式

```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ],
  "model": "Doubao-embedding-vision",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

## 🌐 动态网页自动化操作指南

**适用**: React/Vue 应用（GPT、招聘网站、现代 Web 应用）

### 正确流程

```
1. browser.open(url)
2. await sleep(10)  # 等页面完全加载
3. snapshot = browser.snapshot()  # 获取新 DOM
4. browser.act(ref=snapshot.ref)  # 立即使用，不等待
5. verify = browser.snapshot()  # 验证结果
```

### 错误流程（避免）

```
1. snapshot = browser.snapshot()
2. await sleep(5)  # ❌ 等待导致 ref 失效
3. browser.act(ref=snapshot.ref)  # ❌ 用旧 ref
4. 假设成功  # ❌ 不验证
```

### 关键原则

1. **等待页面加载** - React 需要时间渲染
2. **snapshot 后立即使用** - ref 只在瞬间有效
3. **操作后验证** - 检查输入框/消息历史
4. **失败则重试** - 重新 snapshot 获取新 ref

### 常见失败场景

| 场景 | 原因 | 解决 |
|------|------|------|
| GPT 消息发送失败 | 用旧 ref 输入 | 等待 10 秒 + 立即输入 |
| 前程无忧点击失败 | 页面刷新中操作 | 等刷新完成 + 重新 snapshot |
| 智联招聘找不到元素 | 不等加载就操作 | 添加 sleep(10) |

---

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
