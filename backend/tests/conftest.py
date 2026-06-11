"""测试配置 - 使用 FastAPI TestClient + SQLite 内存数据库进行进程内测试"""

import sys
import os
import pytest
import asyncio
from starlette.testclient import TestClient
from sqlalchemy import BigInteger, create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 将 tests 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

# SQLite 不支持 BigInteger 自动递增，需要让 BigInteger 编译为 INTEGER
from sqlalchemy.ext.compiler import compiles


@compiles(BigInteger, "sqlite")
def bi_c(element, compiler, **kw):
    return "INTEGER"


# 在导入 app 模块之前，替换 database.py 中的引擎为 SQLite
import app.database as _db_module

TEST_ASYNC_URL = "sqlite+aiosqlite:///:memory:"
_test_engine = create_async_engine(TEST_ASYNC_URL, echo=False)
_TestSession = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)

# 替换模块级引擎和会话工厂（lifespan 中 init_db 使用的是 app.database.engine）
_db_module.engine = _test_engine
_db_module.AsyncSessionLocal = _TestSession

from app.database import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def _setup_db():
    """每个测试前创建表，测试后删除所有表"""
    loop = asyncio.new_event_loop()

    async def _create():
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(_create())

    yield

    async def _drop():
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    loop.run_until_complete(_drop())
    loop.close()


async def _get_test_db():
    """获取测试数据库会话（异步）"""
    async with _TestSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
def client():
    """测试客户端"""
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
