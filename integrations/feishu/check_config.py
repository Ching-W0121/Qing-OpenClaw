"""
飞书机器人配置检查工具

运行方式：python check_config.py
"""

import os
import sys
from dotenv import load_dotenv

def check_env():
    """检查环境变量配置"""
    print("=" * 50)
    print("🔍 检查环境变量配置")
    print("=" * 50)
    
    load_dotenv()
    
    app_id = os.getenv("APP_ID")
    app_secret = os.getenv("APP_SECRET")
    log_level = os.getenv("LOG_LEVEL", "DEBUG")
    
    # 检查 APP_ID
    if not app_id:
        print("❌ APP_ID: 未设置")
        print("   请在 .env 文件中设置 APP_ID")
        return False
    elif not app_id.startswith("cli_"):
        print(f"⚠️  APP_ID: {app_id[:10]}... (格式可能不正确，应以 cli_ 开头)")
    else:
        print(f"✅ APP_ID: {app_id[:10]}...{app_id[-5:]}")
    
    # 检查 APP_SECRET
    if not app_secret:
        print("❌ APP_SECRET: 未设置")
        print("   请在 .env 文件中设置 APP_SECRET")
        return False
    elif len(app_secret) < 20:
        print(f"⚠️  APP_SECRET: 长度过短 ({len(app_secret)} 字符)")
    else:
        print(f"✅ APP_SECRET: 已设置 ({len(app_secret)} 字符)")
    
    # 检查 LOG_LEVEL
    print(f"✅ LOG_LEVEL: {log_level}")
    
    return True


def check_sdk():
    """检查 SDK 安装"""
    print("\n" + "=" * 50)
    print("🔍 检查 SDK 安装")
    print("=" * 50)
    
    try:
        import lark_oapi
        print(f"✅ lark-oapi: 已安装")
        return True
    except ImportError:
        print("❌ lark-oapi: 未安装")
        print("   运行以下命令安装：")
        print("   pip install lark-oapi -U")
        return False


def check_dotenv():
    """检查 python-dotenv 安装"""
    print("\n" + "=" * 50)
    print("🔍 检查依赖")
    print("=" * 50)
    
    try:
        import dotenv
        print(f"✅ python-dotenv: 已安装")
        return True
    except ImportError:
        print("❌ python-dotenv: 未安装")
        print("   运行以下命令安装：")
        print("   pip install python-dotenv")
        return False


def check_files():
    """检查必要文件"""
    print("\n" + "=" * 50)
    print("🔍 检查文件结构")
    print("=" * 50)
    
    files = {
        "feishu_bot.py": "主程序",
        ".env": "配置文件",
        ".env.example": "配置示例",
        "requirements.txt": "依赖列表",
        "README.md": "使用文档"
    }
    
    all_exist = True
    for filename, description in files.items():
        if os.path.exists(filename):
            print(f"✅ {filename}: {description}")
        else:
            print(f"❌ {filename}: {description} (缺失)")
            all_exist = False
    
    return all_exist


def main():
    """主函数"""
    print("\n🌿 飞书机器人配置检查工具\n")
    
    results = []
    
    # 执行检查
    results.append(("环境变量", check_env()))
    results.append(("SDK 安装", check_sdk()))
    results.append(("依赖", check_dotenv()))
    results.append(("文件结构", check_files()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 检查结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ 所有检查通过！可以启动机器人了")
        print("\n运行以下命令启动：")
        print("  python feishu_bot.py")
        print("或双击 start.bat")
    else:
        print("⚠️  部分检查未通过，请先修复上述问题")
        print("\n修复后再次运行：")
        print("  python check_config.py")
    
    print("=" * 50 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
