"""私信相关模式"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    """私信基础模式"""
    content: Optional[str] = Field(None, max_length=5000)
    message_type: int = Field(1, description="1:文字 2:图片 3:文件")
    media_url: Optional[str] = None


class MessageCreate(MessageBase):
    """创建私信请求"""
    pass


class MessageResponse(MessageBase):
    """私信响应"""
    id: int
    conversation_id: int
    sender_id: int
    is_read: int
    created_at: datetime
    sender: Optional["UserBrief"] = None

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """会话基础模式"""
    user1_id: int
    user2_id: int


class ConversationResponse(BaseModel):
    """会话响应"""
    id: int
    user1_id: int
    user2_id: int
    last_message_id: Optional[int] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime
    other_user: Optional["UserBrief"] = None
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """会话列表响应"""
    total: int
    items: List[ConversationResponse]


class MessageListResponse(BaseModel):
    """消息列表响应"""
    total: int
    items: List[MessageResponse]


# 解决前向引用
from app.schemas.post import UserBrief
MessageResponse.model_rebuild()
ConversationResponse.model_rebuild()
