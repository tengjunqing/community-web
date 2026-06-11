"""群组相关模式"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GroupBase(BaseModel):
    """群组基础模式"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    is_public: int = Field(1, description="0:私密 1:公开")


class GroupCreate(GroupBase):
    """创建群组请求"""
    pass


class GroupUpdate(BaseModel):
    """更新群组请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    avatar: Optional[str] = None
    cover: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[int] = None


class GroupMemberResponse(BaseModel):
    """群组成员响应"""
    id: int
    user_id: int
    group_id: int
    role: int
    joined_at: datetime
    user: Optional["UserBrief"] = None

    class Config:
        from_attributes = True


class GroupAnnouncementBase(BaseModel):
    """群组公告基础模式"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)


class GroupAnnouncementCreate(GroupAnnouncementBase):
    """创建群组公告请求"""
    pass


class GroupAnnouncementResponse(GroupAnnouncementBase):
    """群组公告响应"""
    id: int
    group_id: int
    creator_id: int
    is_active: int
    created_at: datetime
    creator: Optional["UserBrief"] = None

    class Config:
        from_attributes = True


class GroupResponse(GroupBase):
    """群组响应"""
    id: int
    avatar: Optional[str] = None
    cover: Optional[str] = None
    creator_id: int
    member_count: int = 0
    status: int
    created_at: datetime
    creator: Optional["UserBrief"] = None
    is_member: bool = False
    member_role: Optional[int] = None

    class Config:
        from_attributes = True


class GroupListResponse(BaseModel):
    """群组列表响应"""
    total: int
    items: List[GroupResponse]


class GroupMemberListResponse(BaseModel):
    """群组成员列表响应"""
    total: int
    items: List[GroupMemberResponse]


class GroupAnnouncementListResponse(BaseModel):
    """群组公告列表响应"""
    total: int
    items: List[GroupAnnouncementResponse]


# 解决前向引用
from app.schemas.post import UserBrief
GroupMemberResponse.model_rebuild()
GroupAnnouncementResponse.model_rebuild()
GroupResponse.model_rebuild()
