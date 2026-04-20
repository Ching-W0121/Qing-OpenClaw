"""
飞书机器人 - 长连接事件接收
基于飞书 SDK (lark-oapi) 实现 WebSocket 长连接

运行方式：python feishu_bot.py
"""

import os
from dotenv import load_dotenv
import lark_oapi as lark

# 加载环境变量
load_dotenv()


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    """
    处理接收消息事件 (v2.0)
    当机器人收到消息时触发
    """
    print(f'[收到消息 v2.0], data: {lark.JSON.marshal(data, indent=4)}')
    
    # 获取消息内容
    event = data.event
    message = event.message
    sender = event.sender
    
    print(f"发送者：{sender.sender_id.user_id}")
    print(f"消息 ID: {message.message_id}")
    print(f"聊天 ID: {message.chat_id}")
    print(f"消息内容：{message.content}")
    
    # TODO: 在这里添加你的消息处理逻辑
    # 例如：自动回复、命令解析等


def do_message_event(data: lark.CustomizedEvent) -> None:
    """
    处理自定义事件 (v1.0)
    用于接收 v1.0 版本的事件
    """
    print(f'[收到自定义事件 v1.0], data: {lark.JSON.marshal(data, indent=4)}')


def main():
    """
    主函数：初始化并启动长连接客户端
    """
    # 从环境变量读取 App ID 和 App Secret
    APP_ID = os.getenv("APP_ID")
    APP_SECRET = os.getenv("APP_SECRET")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    
    # 验证配置
    if not APP_ID or not APP_SECRET:
        print("❌ 错误：请在 .env 文件中配置 APP_ID 和 APP_SECRET")
        print("   或设置环境变量 APP_ID 和 APP_SECRET")
        return
    
    # 构建事件处理器
    event_handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
        .register_p1_customized_event("im.message.receive_v1", do_message_event) \
        .build()
    
    # 创建长连接客户端
    cli = lark.ws.Client(
        APP_ID, 
        APP_SECRET,
        event_handler=event_handler,
        log_level=getattr(lark.LogLevel, LOG_LEVEL, lark.LogLevel.DEBUG)
    )
    
    print("🌿 正在连接飞书长连接...")
    print("⚠️ 按 Ctrl+C 停止服务")
    
    # 启动客户端（阻塞）
    try:
        cli.start()
    except KeyboardInterrupt:
        print("\n👋 正在断开连接...")
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        raise


if __name__ == "__main__":
    main()
