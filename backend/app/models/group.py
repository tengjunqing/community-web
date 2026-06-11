"""群组数据模型"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, SmallInteger, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Group(Base):
    """群组模型"""

    __tablename__ = "groups"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    avatar = Column(String(255), nullable=True)
    cover = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)
    creator_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    member_count = Column(Integer, default=1)
    is_public = Column(SmallInteger, default=1, comment="0:私密 1:公开")
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    creator = relationship("User", backref="created_groups")
    members = relationship("GroupMember", back_populates="group", lazy="dynamic")
    posts = relationship("GroupPost", back_populates="group", lazy="dynamic")
    announcements = relationship("GroupAnnouncement", back_populates="group", lazy="dynamic")

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class GroupMember(Base):
    """群组成员模型"""

    __tablename__ = "group_members"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SmallInteger, default=1, comment="1:成员 2:管理员 3:群主")
    joined_at = Column(DateTime, default=func.now())

    # 关系
    group = relationship("Group", back_populates="members")
    user = relationship("User", backref="group_memberships")

    # 唯一约束
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
    )

    def __repr__(self):
        return f"<GroupMember(group_id={self.group_id}, user_id={self.user_id})>"


class GroupPost(Base):
    """群组动态模型"""

    __tablename__ = "group_posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    is_pinned = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=func.now())

    # 关系
    group = relationship("Group", back_populates="posts")
    user = relationship("User")
    post = relationship("Post")

    def __repr__(self):
        return f"<GroupPost(group_id={self.group_id}, post_id={self.post_id})>"


class GroupAnnouncement(Base):
    """群组公告模型"""

    __tablename__ = "group_announcements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    creator_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=func.now())

    # 关系
    group = relationship("Group", back_populates="announcements")
    creator = relationship("User")

    def __repr__(self):
        return f"<GroupAnnouncement(id={self.id}, group_id={self.group_id})>"
