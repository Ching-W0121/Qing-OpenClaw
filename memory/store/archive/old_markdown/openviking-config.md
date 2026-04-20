# OpenViking 配置记录

**配置时间**: 2026-03-08 16:47 (Asia/Shanghai)
**更新时间**: 2026-03-08 16:48 - API Key 问题排查

---

## 📁 配置文件

**路径**: `C:\Users\TR\.openviking\ov.conf`

```json
{
  "storage": {
    "workspace": "C:/Users/TR/.openviking/workspace"
  },
  "log": {
    "level": "INFO",
    "output": "stdout"
  },
  "embedding": {
    "dense": {
      "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "api_key": "sk-sp-0bf579e5e655429b96b6d04911909aa7",
      "provider": "openai",
      "dimension": 1536,
      "model": "text-embedding-v3"
    }
  },
  "vlm": {
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "sk-sp-0bf579e5e655429b96b6d04911909aa7",
    "provider": "litellm",
    "model": "dashscope/qwen-plus"
  }
}
```

---

## 🔑 API Key 状态

### 当前配置
- **Key**: `sk-sp-0bf579e5e655429b96b6d04911909aa7`
- **来源**: OpenClaw `custom-coding-dashscope-aliyuncs-com` provider
- **状态**: ⚠️ **不适用于嵌入 API**

### 测试结果

| API Key | 测试接口 | 结果 |
|---------|----------|------|
| `sk-sp-0bf579e5e655429b96b6d04911909aa7` | dashscope.aliyuncs.com/embeddings | ❌ invalid_api_key |
| `sk-sp-0bf579e5e655429b96b6d04911909aa7` | coding.dashscope.aliyuncs.com/v1 | ❌ 404 Not Found |
| `sk-a12ee1048381403fa157e61e13fdcf35` | dashscope.aliyuncs.com/embeddings | ❌ Arrearage (欠费) |

---

## ⚠️ 问题说明

**核心问题**: 
- `sk-sp-` 开头的 Key 仅适用于 `coding.dashscope.aliyuncs.com` (代码专用接口)
- `sk-a12ee-` 开头的 Key 适用于主 API，但账户欠费

**影响**:
- ❌ 向量嵌入 (Embedding) 无法生成
- ❌ 语义搜索无法使用
- ✅ 文件存储/浏览功能正常

---

## 🔧 解决方案

### 方案 1: 充值阿里云账户 (推荐)
- 充值账户：`sk-a12ee1048381403fa157e61e13fdcf35` 对应的账户
- 充值后配置该 Key
- 重新导入记忆文件

### 方案 2: 使用免费嵌入服务
- 配置 Jina AI (需要申请免费 API Key)
- 或配置其他支持的 provider

### 方案 3: 暂时跳过嵌入
- 仅使用文件存储功能
- 等待账户充值后再启用语义搜索

---

## 🚀 服务器状态

**监听地址**: `http://127.0.0.1:1933`
**进程 ID**: 17876
**运行状态**: ✅ 正常运行

---

## 📋 已导入文件

**12 个记忆文件**已存储至 `viking://resources/memory/`:
- 2026-03-06.md
- 2026-03-06-boss-auto-apply.md
- 2026-03-07-boss-search.md
- 2026-03-08.md
- 2026-03-08-0821.md
- boss-job-search-2026-03-08.md
- desktop-docs-2026-03-08.md
- desktop-docs-summary-2026-03-08.md
- job-search-config.md
- job-search-history.md
- openviking-config.md
- openviking-setup-guide.md

---

## 📝 备注

- 文件已成功导入，可正常浏览和读取
- 语义搜索功能需解决 API Key 问题后启用
- 建议优先充值阿里云账户
