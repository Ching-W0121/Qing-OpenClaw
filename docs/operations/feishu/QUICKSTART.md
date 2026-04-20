# 飞书机器人 - 快速开始指南

## ⚡ 5 分钟快速配置

### 第 1 步：获取应用凭证（2 分钟）

1. 打开 [飞书开发者后台](https://open.feishu.cn/app)
2. 创建或选择你的企业自建应用
3. 进入 **凭证与基础信息** > **应用凭证**
4. 复制 **App ID** 和 **App Secret**

---

### 第 2 步：配置本地环境（1 分钟）

1. 打开 `integrations/feishu/.env` 文件
2. 填入你的凭证：

```env
APP_ID=cli_xxxxxxxxxxxxxxxxx
APP_SECRET=xxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=DEBUG
```

---

### 第 3 步：配置飞书后台（2 分钟）

1. 在应用详情页，点击 **事件与回调**
2. 编辑订阅方式，选择 **使用长连接接收事件**
3. 点击 **添加事件**，搜索并添加：
   - `im.message.receive_v1` (接收消息 v2.0)
4. 保存配置

⚠️ **注意**：如果保存失败，请先启动本地客户端（见第 4 步）

---

### 第 4 步：启动机器人（30 秒）

**方式 1: 使用启动脚本（推荐）**
```bash
# 双击 start.bat
# 或命令行运行：
start.bat
```

**方式 2: 直接运行**
```bash
cd feishu
python feishu_bot.py
```

**成功标志**：
```
🌿 正在连接飞书长连接...
⚠️ 按 Ctrl+C 停止服务
connected to wss://xxxxx
```

---

### 第 5 步：测试（30 秒）

1. 在飞书中找到你的应用
2. 发送消息："你好"
3. 查看控制台输出：

```
[收到消息 v2.0], data: {
    "event": {
        "message": {
            "chat_id": "oc_xxxxx",
            "content": "{\"text\":\"你好\"}"
        }
    }
}
```

---

## 🔧 常见问题

### Q1: 保存订阅方式失败

**原因**: 长连接未建立

**解决**:
1. 先运行 `python feishu_bot.py`
2. 看到 "connected to wss://xxxxx" 后
3. 再回到飞书后台保存配置

---

### Q2: App ID 格式不对

**正确格式**: `cli_xxxxxxxxxxxxxxxxx` (cli_ 开头 + 17 位字符)

**获取位置**: 开发者后台 > 应用详情页 > 凭证与基础信息

---

### Q3: 收不到消息

**检查清单**:
- [ ] 事件订阅中是否添加了 `im.message.receive_v1`
- [ ] 长连接是否正常（控制台有 "connected" 日志）
- [ ] 机器人是否已添加到测试群

---

### Q4: 依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `feishu_bot.py` | 主程序 |
| `.env` | 配置文件（需填写凭证） |
| `.env.example` | 配置示例 |
| `check_config.py` | 配置检查工具 |
| `start.bat` | 快速启动脚本 |
| `README.md` | 完整文档 |

---

## 🚀 下一步

### 实现自动回复

编辑 `feishu_bot.py`，在 `do_p2_im_message_receive_v1` 函数中添加：

```python
# 创建客户端
cli = lark.Client(APP_ID, APP_SECRET)

# 发送回复
cli.im.v1.message.create(
    params={"receive_id_type": "chat_id"},
    data={
        "receive_id": message.chat_id,
        "msg_type": "text",
        "content": lark.JSON.marshal({"text": "收到！"})
    }
)
```

### 添加更多事件

在 `event_handler` 中注册新事件：

```python
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_member_union_changed(do_member_changed) \  # 成员变更事件
    .build()
```

---

## 📚 完整文档

- [README.md](README.md) - 完整配置指南
- [飞书 SDK 文档](https://open.feishu.cn/document/ukTMukTMukTM/uETO1YjLxkTN24SM5UjN)
- [事件列表](https://open.feishu.cn/document/server-docs/event-subscription-guide/event-list)

---

**需要帮助？** 运行配置检查：
```bash
python check_config.py
```
