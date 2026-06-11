@echo off
chcp 65001 >nul

echo ========================================
echo   小众兴趣社交平台 - 开发环境启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

REM 检查 MySQL 是否安装
mysql --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到 MySQL 命令行工具，请确保 MySQL 服务已启动
)

echo [1/4] 初始化后端环境...
cd backend

REM 创建虚拟环境
if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装后端依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

REM 创建环境变量文件
if not exist ".env" (
    echo 创建环境变量文件...
    copy .env.example .env
    echo 请编辑 backend\.env 文件配置数据库连接信息
)

cd ..

echo [2/4] 初始化前端环境...
cd frontend

REM 安装依赖
echo 安装前端依赖...
npm install --registry=https://registry.npmmirror.com --silent

cd ..

echo [3/4] 初始化数据库...
echo 请确保 MySQL 服务已启动，并执行以下命令初始化数据库：
echo mysql -u root -p ^< sql\init.sql
echo.

echo [4/4] 启动服务...
echo.
echo 正在启动后端服务...
start "后端服务" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo 正在启动前端服务...
start "前端服务" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo 前端地址：http://localhost:5173
echo 后端地址：http://localhost:8000
echo API 文档：http://localhost:8000/docs
echo.
echo 按任意键退出此窗口...
pause >nul
