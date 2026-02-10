@echo off
REM 屏幕录制软件启动脚本
REM Windows批处理文件，用于方便地启动应用程序

echo ====================================
echo    屏幕录制软件 - 启动脚本
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] Python已安装
python --version
echo.

REM 检查依赖是否安装
echo [信息] 检查依赖包...
pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖包未安装，正在自动安装...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
    echo.
    echo [信息] 依赖包安装完成
    echo.
)

REM 启动应用程序
echo [信息] 正在启动屏幕录制软件...
echo.
python main.py

REM 如果程序异常退出，暂停以便查看错误信息
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)
