"""群组相关接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.group import (
    GroupCreate, GroupUpdate, GroupResponse, GroupListResponse,
    GroupMemberResponse, GroupMemberListResponse,
    GroupAnnouncementCreate, GroupAnnouncementResponse, GroupAnnouncementListResponse
)
from app.schemas.post import PostCreate, PostResponse
from app.services.group_service import GroupService
from app.models.user import User
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=GroupListResponse)
async def get_groups(
    category: Optional[str] = Query(None, description="分类"),
    keyword: Optional[str] = Query(None, description="关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取群组列表"""
    groups, total = await GroupService.get_groups(db, category, keyword, skip, limit)

    # 检查是否是成员
    group_responses = []
    for group in groups:
        member = await GroupService.check_member(db, group.id, current_user.id)
        group_dict = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "category": group.category,
            "is_public": group.is_public,
            "avatar": group.avatar,
            "cover": group.cover,
            "creator_id": group.creator_id,
            "member_count": group.member_count,
            "status": group.status,
            "created_at": group.created_at,
            "creator": group.creator,
            "is_member": member is not None,
            "member_role": member.role if member else None,
        }
        group_responses.append(group_dict)

    return GroupListResponse(total=total, items=group_responses)


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建群组"""
    group = await GroupService.create_group(db, current_user.id, group_data)
    return group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取群组详情"""
    group = await GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    member = await GroupService.check_member(db, group_id, current_user.id)
    group_dict = {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "category": group.category,
        "is_public": group.is_public,
        "avatar": group.avatar,
        "cover": group.cover,
        "creator_id": group.creator_id,
        "member_count": group.member_count,
        "status": group.status,
        "created_at": group.created_at,
        "creator": group.creator,
        "is_member": member is not None,
        "member_role": member.role if member else None,
    }
    return group_dict


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新群组信息"""
    group = await GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    # 检查权限（群主或管理员）
    member = await GroupService.check_member(db, group_id, current_user.id)
    if not member or member.role < 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改群组信息"
        )

    updated_group = await GroupService.update_group(db, group, group_data)
    return updated_group


@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除群组"""
    group = await GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    # 只有群主可以删除
    if group.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群主可以删除群组"
        )

    await GroupService.delete_group(db, group)
    return {"message": "删除成功"}


@router.post("/{group_id}/join", status_code=status.HTTP_200_OK)
async def join_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """加入群组"""
    # 检查群组是否存在
    group = await GroupService.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群组不存在"
        )

    success = await GroupService.join_group(db, group_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="加入失败，可能已经是成员"
        )
    return {"message": "加入成功"}


@router.delete("/{group_id}/join", status_code=status.HTTP_200_OK)
async def leave_group(
    group_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """退出群组"""
    success = await GroupService.leave_group(db, group_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="退出失败，可能不是成员或是群主"
        )
    return {"message": "退出成功"}


@router.get("/{group_id}/members", response_model=GroupMemberListResponse)
async def get_members(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取成员列表"""
    members, total = await GroupService.get_members(db, group_id, skip, limit)
    return GroupMemberListResponse(total=total, items=members)


@router.get("/{group_id}/posts")
async def get_group_posts(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取群组动态"""
    group_posts, total = await GroupService.get_group_posts(db, group_id, skip, limit)
    return {"total": total, "items": group_posts}


@router.post("/{group_id}/posts", status_code=status.HTTP_201_CREATED)
async def create_group_post(
    group_id: int,
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发布群组动态"""
    # 检查是否是成员
    member = await GroupService.check_member(db, group_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群成员可以发布动态"
        )

    group_post = await GroupService.create_group_post(db, group_id, current_user.id, post_data)
    return group_post


@router.get("/{group_id}/announcements", response_model=GroupAnnouncementListResponse)
async def get_announcements(
    group_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取公告列表"""
    announcements, total = await GroupService.get_announcements(db, group_id, skip, limit)
    return GroupAnnouncementListResponse(total=total, items=announcements)


@router.post("/{group_id}/announcements", response_model=GroupAnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    group_id: int,
    announcement_data: GroupAnnouncementCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发布公告"""
    # 检查权限（群主或管理员）
    member = await GroupService.check_member(db, group_id, current_user.id)
    if not member or member.role < 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以发布公告"
        )

    announcement = await GroupService.create_announcement(db, group_id, current_user.id, announcement_data)
    return announcement
