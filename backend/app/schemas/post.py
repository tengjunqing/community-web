"""动态相关模式"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TopicBase(BaseModel):
    """话题基础模式"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class TopicCreate(TopicBase):
    """创建话题请求"""
    pass


class TopicResponse(TopicBase):
    """话题响应"""
    id: int
    cover: Optional[str] = None
    post_count: int = 0

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    """动态基础模式"""
    content: str = Field(..., min_length=1, max_length=5000)
    images: Optional[List[str]] = None
    topic_id: Optional[int] = None


class PostCreate(PostBase):
    """创建动态请求"""
    pass


class PostUpdate(BaseModel):
    """更新动态请求"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    images: Optional[List[str]] = None


class CommentBase(BaseModel):
    """评论基础模式"""
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    """创建评论请求"""
    pass


class CommentResponse(CommentBase):
    """评论响应"""
    id: int
    user_id: int
    post_id: int
    like_count: int = 0
    created_at: datetime
    user: Optional["UserBrief"] = None

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    """用户简要信息"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class PostResponse(PostBase):
    """动态响应"""
    id: int
    user_id: int
    like_count: int = 0
    comment_count: int = 0
    status: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserBrief] = None
    topic: Optional[TopicResponse] = None
    is_liked: bool = False

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """动态列表响应"""
    total: int
    items: List[PostResponse]


class CommentListResponse(BaseModel):
    """评论列表响应"""
    total: int
    items: List[CommentResponse]
