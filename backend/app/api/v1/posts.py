"""动态相关接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, PostListResponse,
    CommentCreate, CommentResponse, CommentListResponse,
    TopicResponse
)
from app.services.post_service import PostService
from app.models.user import User
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("", response_model=PostListResponse)
async def get_posts(
    user_id: Optional[int] = Query(None, description="用户ID"),
    topic_id: Optional[int] = Query(None, description="话题ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取动态列表"""
    posts, total = await PostService.get_posts(db, user_id, topic_id, skip, limit)

    # 检查是否点赞
    post_responses = []
    for post in posts:
        is_liked = await PostService.check_liked(db, current_user.id, post.id)
        post_dict = {
            "id": post.id,
            "user_id": post.user_id,
            "content": post.content,
            "images": post.images,
            "topic_id": post.topic_id,
            "like_count": post.like_count,
            "comment_count": post.comment_count,
            "status": post.status,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "user": post.user,
            "topic": post.topic,
            "is_liked": is_liked,
        }
        post_responses.append(post_dict)

    return PostListResponse(total=total, items=post_responses)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发布动态"""
    post = await PostService.create_post(db, current_user.id, post_data)
    return post


@router.get("/topics", response_model=list[TopicResponse])
async def get_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取话题列表"""
    topics = await PostService.get_topics(db, skip, limit)
    return topics


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取动态详情"""
    post = await PostService.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )

    is_liked = await PostService.check_liked(db, current_user.id, post_id)
    post_dict = {
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "images": post.images,
        "topic_id": post.topic_id,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "status": post.status,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "user": post.user,
        "topic": post.topic,
        "is_liked": is_liked,
    }
    return post_dict


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新动态"""
    post = await PostService.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此动态"
        )

    updated_post = await PostService.update_post(db, post, post_data)
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除动态"""
    post = await PostService.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此动态"
        )

    await PostService.delete_post(db, post)
    return {"message": "删除成功"}


@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """点赞动态"""
    success = await PostService.like_post(db, current_user.id, post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="点赞失败，可能已经点赞"
        )
    return {"message": "点赞成功"}


@router.delete("/{post_id}/like", status_code=status.HTTP_200_OK)
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """取消点赞"""
    success = await PostService.unlike_post(db, current_user.id, post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="取消点赞失败，可能尚未点赞"
        )
    return {"message": "取消点赞成功"}


@router.get("/{post_id}/comments", response_model=CommentListResponse)
async def get_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取评论列表"""
    comments, total = await PostService.get_comments(db, post_id, skip, limit)
    return CommentListResponse(total=total, items=comments)


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发表评论"""
    # 检查动态是否存在
    post = await PostService.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="动态不存在"
        )

    comment = await PostService.create_comment(db, current_user.id, post_id, comment_data)
    return comment
