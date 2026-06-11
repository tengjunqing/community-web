"""用户相关模式"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class InterestTagBase(BaseModel):
    """兴趣标签基础模式"""
    name: str = Field(..., max_length=50)
    category: Optional[str] = Field(None, max_length=50)


class InterestTagResponse(InterestTagBase):
    """兴趣标签响应"""
    id: int
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户请求"""
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    avatar: Optional[str] = None
    interest_ids: Optional[List[int]] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    avatar: Optional[str] = None
    status: int
    created_at: datetime
    interests: List[InterestTagResponse] = []

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """用户详细资料"""
    post_count: int = 0
    follower_count: int = 0
    following_count: int = 0
    is_following: bool = False


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    items: List[UserResponse]
