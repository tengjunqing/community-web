"""私信数据模型"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, SmallInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Conversation(Base):
    """会话模型"""

    __tablename__ = "conversations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user1_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_message_id = Column(BigInteger, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # 关系
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    messages = relationship("Message", back_populates="conversation", lazy="dynamic")

    # 唯一约束
    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="uq_conversation"),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id})>"


class Message(Base):
    """私信模型"""

    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=True)
    message_type = Column(SmallInteger, default=1, comment="1:文字 2:图片 3:文件")
    media_url = Column(String(255), nullable=True)
    is_read = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=func.now())

    # 关系
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id})>"
