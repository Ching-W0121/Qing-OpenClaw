# OpenViking 安装配置指南

**配置时间：** 2026-03-08 16:15  
**更新时间：** 2026-03-08 16:20  
**VLM 模型：** qwen3.5-plus (通过 DashScope/阿里云)  
**安装状态：** ✅ 已完成

---

## 一、系统要求

- **Python:** 3.10 或更高
- **Go:** 1.22+ (构建 AGFS 组件需要)
- **C++ 编译器：** GCC 9+ 或 Clang 11+
- **操作系统：** Windows (当前环境)
- **网络：** 稳定网络连接

---

## 二、安装步骤

### 1. 安装 Python 包

```powershell
pip install openviking --upgrade --force-reinstall
```

### 2. 安装 VikingBot (可选，用于 AI Agent 功能)

```powershell
pip install openviking[bot]
```

### 3. 创建配置目录

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.openviking"
```

---

## 三、服务器配置 (ov.conf)

### 配置文件位置
`C:\Users\TR\.openviking\ov.conf`

### 配置模板 (使用阿里云 DashScope - Qwen3.5-Plus)

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
      "api_key": "<你的阿里云 DashScope API Key>",
      "provider": "openai",
      "dimension": 1536,
      "model": "text-embedding-v3",
      "max_concurrent": 10
    }
  },
  "vlm": {
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "<你的阿里云 DashScope API Key>",
    "provider": "litellm",
    "model": "dashscope/qwen3.5-plus",
    "max_concurrent": 100
  }
}
```

### 配置说明

| 配置项 | 说明 | 当前值 |
|--------|------|--------|
| **workspace** | 工作空间路径 | `C:/Users/TR/.openviking/workspace` |
| **embedding.model** | Embedding 模型 | `text-embedding-v3` (阿里云) |
| **embedding.provider** | Embedding 提供商 | `openai` (兼容模式) |
| **vlm.model** | VLM 模型 | `dashscope/qwen3.5-plus` |
| **vlm.provider** | VLM 提供商 | `litellm` (支持多种模型) |

---

## 四、CLI 客户端配置 (ovcli.conf)

### 配置文件位置
`C:\Users\TR\.openviking\ovcli.conf`

### 配置模板

```json
{
  "url": "http://localhost:1933",
  "timeout": 60.0,
  "output": "table"
}
```

---

## 五、设置环境变量

### PowerShell

```powershell
$env:OPENVIKING_CONFIG_FILE = "$HOME\.openviking\ov.conf"
$env:OPENVIKING_CLI_CONFIG_FILE = "$HOME\.openviking\ovcli.conf"
```

### 永久设置 (系统环境变量)

```powershell
[System.Environment]::SetEnvironmentVariable("OPENVIKING_CONFIG_FILE", "$HOME\.openviking\ov.conf", "User")
[System.Environment]::SetEnvironmentVariable("OPENVIKING_CLI_CONFIG_FILE", "$HOME\.openviking\ovcli.conf", "User")
```

---

## 六、启动服务

### 启动 OpenViking Server

```powershell
openviking-server
```

### 后台运行

```powershell
Start-Process -FilePath "openviking-server" -ArgumentList "--with-bot" -WindowStyle Hidden
```

### 启动 VikingBot (交互式聊天)

```powershell
ov chat
```

---

## 七、基本命令

### 查看状态

```powershell
ov status
```

### 添加资源

```powershell
ov add-resource https://github.com/volcengine/OpenViking
```

### 列出资源

```powershell
ov ls viking://resources/
```

### 查找内容

```powershell
ov find "什么是 OpenViking"
```

### 搜索内容

```powershell
ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs
```

---

## 八、API Key 获取

### 阿里云 DashScope (Qwen 模型)

1. 访问：https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 创建/获取 API Key
4. 确保开通以下服务：
   - 通义千问 (Qwen) - 用于 VLM
   - 文本嵌入 (Text Embedding) - 用于 Embedding

---

## 九、模型配置说明

### VLM 模型：qwen3.5-plus

**LiteLLM 格式：** `dashscope/qwen3.5-plus`

**支持的功能：**
- 文本理解
- 图像理解
- 代码理解
- 长上下文处理

### Embedding 模型：text-embedding-v3

**维度：** 1536  
**提供商：** 阿里云 DashScope  
**兼容模式：** OpenAI 兼容 API

---

## 十、验证安装

### 1. 检查服务器状态

```powershell
ov status
```

### 2. 测试连接

```powershell
ov ls viking://resources/
```

### 3. 测试聊天 (如果安装了 Bot)

```powershell
ov chat
```

---

## 十一、故障排查

### 常见问题

**1. 找不到 openviking-server 命令**
```powershell
# 重新安装
pip install openviking --upgrade --force-reinstall
```

**2. API Key 无效**
- 检查 DashScope 控制台 API Key 是否正确
- 确保账户有足够余额
- 确保服务已开通

**3. 连接超时**
- 检查网络连接
- 增加 timeout 值：编辑 ovcli.conf，设置 `"timeout": 120.0`

**4. 模型调用失败**
- 确认 LiteLLM 格式正确：`dashscope/qwen3.5-plus`
- 检查 API Key 权限
- 查看服务器日志

---

## 十二、已完成步骤

- ✅ Python 包安装 (openviking 0.2.5)
- ✅ 配置目录创建 (C:\Users\TR\.openviking)
- ✅ 服务器配置 (ov.conf)
- ✅ CLI 配置 (ovcli.conf)
- ✅ 环境变量设置
- ✅ 版本验证 (ov --version = 0.2.1)

## 十三、下一步

1. ⏳ 获取阿里云 DashScope API Key
2. ⏳ 更新 ov.conf 中的 API Key
3. ⏳ 启动服务器 (openviking-server)
4. ⏳ 运行第一个示例

---

**参考文档：**
- GitHub: https://github.com/volcengine/OpenViking
- 官方文档：https://www.openviking.ai/docs
- LiteLLM  providers: https://docs.litellm.ai/docs/providers
