"""用户相关接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserProfile, UserListResponse
from app.services.user_service import UserService
from app.models.user import User
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户详细资料"""
    profile = await UserService.get_user_profile(db, current_user.id, current_user.id)
    return profile


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    user = await UserService.update_user(db, current_user, user_data)
    return user


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取指定用户详细资料"""
    profile = await UserService.get_user_profile(db, user_id, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return profile


@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """关注用户"""
    success = await UserService.follow_user(db, current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="关注失败，可能已经关注或不能关注自己"
        )
    return {"message": "关注成功"}


@router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """取消关注"""
    success = await UserService.unfollow_user(db, current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="取消关注失败，可能尚未关注"
        )
    return {"message": "取消关注成功"}


@router.get("/{user_id}/followers", response_model=UserListResponse)
async def get_followers(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取粉丝列表"""
    followers = await UserService.get_followers(db, user_id, skip, limit)
    return UserListResponse(
        total=len(followers),
        items=followers
    )


@router.get("/{user_id}/following", response_model=UserListResponse)
async def get_following(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取关注列表"""
    following = await UserService.get_following(db, user_id, skip, limit)
    return UserListResponse(
        total=len(following),
        items=following
    )
