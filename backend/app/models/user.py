"""用户数据模型"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, SmallInteger, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# 用户兴趣标签关联表
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("tag_id", BigInteger, ForeignKey("interest_tags.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, default=func.now()),
)


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    status = Column(SmallInteger, default=1, comment="0:禁用 1:正常 2:待验证")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    interests = relationship("InterestTag", secondary=user_interests, back_populates="users", lazy="selectin")
    posts = relationship("Post", back_populates="user", lazy="dynamic")
    comments = relationship("Comment", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class InterestTag(Base):
    """兴趣标签模型"""

    __tablename__ = "interest_tags"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    category = Column(String(50), nullable=True)
    icon = Column(String(255), nullable=True)
    sort_order = Column(BigInteger, default=0)
    is_active = Column(SmallInteger, default=1)

    # 关系
    users = relationship("User", secondary=user_interests, back_populates="interests", lazy="selectin")

    def __repr__(self):
        return f"<InterestTag(id={self.id}, name={self.name})>"
