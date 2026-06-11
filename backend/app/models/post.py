"""动态数据模型"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, SmallInteger, Integer, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Topic(Base):
    """话题模型"""

    __tablename__ = "topics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    cover = Column(String(255), nullable=True)
    post_count = Column(Integer, default=0)
    is_active = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())

    # 关系
    posts = relationship("Post", back_populates="topic", lazy="dynamic")

    def __repr__(self):
        return f"<Topic(id={self.id}, name={self.name})>"


class Post(Base):
    """动态模型"""

    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True, comment="图片URL数组")
    topic_id = Column(BigInteger, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    status = Column(SmallInteger, default=1, comment="0:删除 1:正常 2:审核中")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="posts")
    topic = relationship("Topic", back_populates="posts")
    likes = relationship("Like", back_populates="post", lazy="dynamic")
    comments = relationship("Comment", back_populates="post", lazy="dynamic")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id})>"


class Like(Base):
    """点赞模型"""

    __tablename__ = "likes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # 关系
    user = relationship("User")
    post = relationship("Post", back_populates="likes")

    # 唯一约束
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_like"),
    )

    def __repr__(self):
        return f"<Like(user_id={self.user_id}, post_id={self.post_id})>"


class Comment(Base):
    """评论模型"""

    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())

    # 关系
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="children")
    children = relationship("Comment", back_populates="parent")

    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id})>"
