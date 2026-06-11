# 小众兴趣社交平台

一个面向小众兴趣爱好者的社交平台，让用户能够找到志同道合的伙伴，分享兴趣内容，建立深度连接。

## 功能特性

- 🔐 **用户管理** - 注册登录、个人资料、兴趣标签
- 👤 **个人主页** - 动态展示、关注粉丝、成就徽章
- 📝 **动态系统** - 发布、点赞、评论、话题标签
- 💬 **私信系统** - 一对一聊天、实时推送、消息管理
- 👥 **群组系统** - 创建群组、群组动态、成员管理

## 技术栈

### 前端
- Vue 3
- Element Plus
- Pinia
- Vue Router
- Axios

### 后端
- Python FastAPI
- SQLAlchemy
- MySQL 8.0
- Redis
- WebSocket

### 部署
- Docker
- Docker Compose
- Nginx

## 快速开始

### 方式一：Docker 部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd social-network
```

2. 启动服务
```bash
docker-compose up -d
```

3. 访问应用
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 方式二：本地开发

#### 后端启动

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

5. 初始化数据库
```bash
# 执行 sql/init.sql 文件创建表结构
mysql -u root -p < ../sql/init.sql
```

6. 启动后端服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install --registry=https://registry.npmmirror.com
```

3. 启动开发服务器
```bash
npm run dev
```

4. 访问应用
- 前端：http://localhost:5173

## 项目结构

```
social-network/
├── backend/                # 后端项目
│   ├── app/               # 应用代码
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心功能
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试文件
│   ├── requirements.txt   # Python 依赖
│   └── Dockerfile         # Docker 配置
├── frontend/              # 前端项目
│   ├── src/               # 源代码
│   │   ├── api/           # API 请求
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面视图
│   ├── package.json       # 项目配置
│   └── Dockerfile         # Docker 配置
├── sql/                   # SQL 脚本
│   └── init.sql           # 初始化脚本
├── docker-compose.yml     # Docker Compose 配置
└── README.md              # 项目说明
```

## 测试

### 后端测试

```bash
cd backend
pytest tests/ -v --cov=app
```

### 测试覆盖率

```bash
pytest tests/ -v --cov=app --cov-report=html
```

## API 文档

启动后端服务后，访问以下地址查看 API 文档：

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接地址 | mysql+aiomysql://root:password@localhost:3306/social_network |
| REDIS_URL | Redis 连接地址 | redis://localhost:6379/0 |
| SECRET_KEY | JWT 密钥 | your-secret-key-change-in-production |
| ACCESS_TOKEN_EXPIRE_MINUTES | 访问令牌过期时间（分钟） | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | 刷新令牌过期时间（天） | 7 |

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发者。
