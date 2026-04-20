# 飞书机器人配置指南

## 📋 配置步骤

### 步骤 1：创建飞书应用

1. 登录 [飞书开发者后台](https://open.feishu.cn/app)
2. 点击"创建企业自建应用"
3. 填写应用名称（如"庆的助手"）
4. 选择应用类型：**企业自建应用**
5. 点击"创建"

---

### 步骤 2：获取应用凭证

1. 进入应用详情页
2. 点击左侧菜单 **凭证与基础信息**
3. 找到 **应用凭证** 区域
4. 复制以下两个值：
   - **App ID** (格式：`cli_xxxxxxxxxxxxxxxxx`)
   - **App Secret** (随机字符串)

---

### 步骤 3：配置本地环境

1. 打开 `integrations/feishu/.env` 文件
2. 填入你的 App ID 和 App Secret：

```env
APP_ID=cli_xxxxxxxxxxxxxxxxx
APP_SECRET=xxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=DEBUG
```

---

### 步骤 4：添加机器人功能

1. 在应用详情页，点击左侧菜单 **机器人**
2. 点击"创建机器人"
3. 填写机器人名称和描述
4. 上传机器人头像（可选）
5. 点击"完成"

---

### 步骤 5：配置事件订阅

#### 5.1 进入事件订阅页面

1. 在应用详情页，点击左侧菜单 **事件与回调**
2. 进入 **事件配置** 页面

#### 5.2 设置订阅方式为长连接

1. 点击"编辑订阅方式"
2. 选择 **使用长连接接收事件**
3. 点击"保存"

⚠️ **注意**：必须先启动本地长连接客户端，才能保存成功！

#### 5.3 添加事件

1. 点击"添加事件"
2. 搜索并选择以下事件：
   - **接收消息 v2.0** (`im.message.receive_v1`)
3. 点击"确定"

---

### 步骤 6：启动长连接客户端

```bash
# 进入项目目录
cd feishu

# 安装依赖（如果还没安装）
pip install -r requirements.txt

# 启动机器人
python feishu_bot.py
```

**成功标志**：
```
🌿 正在连接飞书长连接...
⚠️ 按 Ctrl+C 停止服务
connected to wss://xxxxx
```

---

### 步骤 7：测试机器人

1. 在飞书中找到你的应用（或在开发者后台点击"预览"）
2. 发送一条消息给机器人
3. 查看控制台输出，应该能看到：
```
[收到消息 v2.0], data: {
    "event": {
        "message": {
            "message_id": "xxxxx",
            "content": "{\"text\":\"你好\"}"
        },
        "sender": {
            "sender_id": {
                "user_id": "xxxxx"
            }
        }
    }
}
```

---

## 🔧 代码说明

### 事件处理器

```python
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("im.message.receive_v1", do_message_event) \
    .build()
```

- `builder("", "")` - 两个参数必须填空字符串
- `register_p2_im_message_receive_v1` - 注册 v2.0 版本接收消息事件
- `register_p1_customized_event` - 注册 v1.0 版本自定义事件

### 事件处理函数

```python
def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    """处理接收消息事件 (v2.0)"""
    event = data.event
    message = event.message
    sender = event.sender
    
    # 获取消息内容
    print(f"发送者：{sender.sender_id.user_id}")
    print(f"消息 ID: {message.message_id}")
    print(f"聊天 ID: {message.chat_id}")
    print(f"消息内容：{message.content}")
```

---

## 📝 事件版本说明

### v2.0 事件
- **方法命名**: `register_p2_{业务域}_{事件类型}`
- **数据类型**: `lark.{业务域}.v1.P2{事件类型}`
- **示例**: `register_p2_im_message_receive_v1`

### v1.0 事件
- **方法命名**: `register_p1_customized_event("事件 key", handler)`
- **数据类型**: `lark.CustomizedEvent`
- **示例**: `register_p1_customized_event("im.message.receive_v1", handler)`

---

## ⚠️ 注意事项

1. **长连接仅支持企业自建应用** - 商店应用需要使用 Webhook 模式
2. **3 秒内处理完成** - 超时会导致重推
3. **最多 50 个连接** - 每个应用最多建立 50 个长连接
4. **集群模式** - 多个客户端部署时，消息只会被随机一个客户端收到
5. **无需公网 IP** - 长连接模式只需本地能访问公网即可

---

## 🚀 下一步：实现自动回复

在 `feishu_bot.py` 的 `do_p2_im_message_receive_v1` 函数中添加回复逻辑：

```python
def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    event = data.event
    message = event.message
    
    # 创建客户端（用于发送消息）
    cli = lark.Client(APP_ID, APP_SECRET)
    
    # 发送回复消息
    cli.im.v1.message.create(
        params={"receive_id_type": "chat_id"},
        data={
            "receive_id": message.chat_id,
            "msg_type": "text",
            "content": lark.JSON.marshal({"text": "收到你的消息！"})
        }
    )
```

---

## 📚 参考文档

- [飞书 SDK 文档](https://open.feishu.cn/document/ukTMukTMukTM/uETO1YjLxkTN24SM5UjN)
- [事件订阅指南](https://open.feishu.cn/document/server-docs/event-subscription-guide/overview)
- [事件列表](https://open.feishu.cn/document/server-docs/event-subscription-guide/event-list)
- [长连接配置案例](https://open.feishu.cn/document/server-docs/event-subscription-guide/event-subscription-configure-/request-url-configuration-case)

---

**最后更新**: 2026-03-11  
**SDK 版本**: lark-oapi 1.5.3
