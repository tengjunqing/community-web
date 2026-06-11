#!/bin/bash

echo "========================================"
echo "  小众兴趣社交平台 - 开发环境启动脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Python，请先安装 Python 3.11+${NC}"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo -e "${RED}[错误] 未找到 Node.js，请先安装 Node.js 18+${NC}"
    exit 1
fi

echo -e "${GREEN}[1/4] 初始化后端环境...${NC}"
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装后端依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

# 创建环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo -e "${YELLOW}请编辑 backend/.env 文件配置数据库连接信息${NC}"
fi

cd ..

echo -e "${GREEN}[2/4] 初始化前端环境...${NC}"
cd frontend

# 安装依赖
echo "安装前端依赖..."
npm install --registry=https://registry.npmmirror.com --silent

cd ..

echo -e "${GREEN}[3/4] 初始化数据库...${NC}"
echo -e "${YELLOW}请确保 MySQL 服务已启动，并执行以下命令初始化数据库：${NC}"
echo "mysql -u root -p < sql/init.sql"
echo ""

echo -e "${GREEN}[4/4] 启动服务...${NC}"
echo ""

# 启动后端服务
echo "正在启动后端服务..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端服务
echo "正在启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  服务启动完成！"
echo "========================================"
echo ""
echo -e "${GREEN}前端地址：http://localhost:5173${NC}"
echo -e "${GREEN}后端地址：http://localhost:8000${NC}"
echo -e "${GREEN}API 文档：http://localhost:8000/docs${NC}"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# 等待子进程
wait
