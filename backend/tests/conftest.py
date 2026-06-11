"""测试配置 - 使用 FastAPI TestClient 进行进程内测试"""

import sys
import os
import pytest
import sqlalchemy
from starlette.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 将 tests 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base, get_db
from app.main import app

# 同步引擎（用于 DDL 操作）
SYNC_DB_URL = "mysql+pymysql://root:Qq987654321@host.docker.internal:3306/social_network_test"
sync_engine = create_engine(SYNC_DB_URL, echo=False)

# 异步引擎（用于测试会话）
ASYNC_DB_URL = "mysql+aiomysql://root:Qq987654321@host.docker.internal:3306/social_network_test"
test_async_engine = create_async_engine(ASYNC_DB_URL, echo=False, pool_pre_ping=False)
TestAsyncSession = async_sessionmaker(test_async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
def _setup_db():
    """每个测试前创建表并清理数据"""
    Base.metadata.create_all(sync_engine)
    with sync_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"TRUNCATE TABLE `{table.name}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    yield


async def _get_test_db():
    """获取测试数据库会话（异步）"""
    async with TestAsyncSession() as session:
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
