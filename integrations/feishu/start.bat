@echo off
echo 🌿 正在启动飞书机器人...
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import lark_oapi" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  检测到依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo ⚠️  未找到 .env 文件，从 .env.example 复制...
    copy .env.example .env
    echo.
    echo ❗ 请先编辑 .env 文件，填入你的 APP_ID 和 APP_SECRET
    echo   获取路径：飞书开发者后台 > 应用详情页 > 凭证与基础信息
    echo.
    pause
    exit /b 1
)

echo ✅ 启动中...
echo.
python feishu_bot.py

pause
