"""动态服务"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.models.post import Post, Like, Comment, Topic
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, CommentCreate


class PostService:
    """动态服务类"""

    @staticmethod
    async def create_post(db: AsyncSession, user_id: int, post_data: PostCreate) -> Post:
        """创建动态"""
        post = Post(
            user_id=user_id,
            content=post_data.content,
            images=post_data.images,
            topic_id=post_data.topic_id,
        )
        db.add(post)

        # 更新话题动态数
        if post_data.topic_id:
            result = await db.execute(select(Topic).where(Topic.id == post_data.topic_id))
            topic = result.scalar_one_or_none()
            if topic:
                topic.post_count += 1

        await db.flush()
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def get_post_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
        """获取动态详情"""
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.user), selectinload(Post.topic))
            .where(Post.id == post_id, Post.status == 1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_posts(
        db: AsyncSession,
        user_id: Optional[int] = None,
        topic_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Post], int]:
        """获取动态列表"""
        query = select(Post).options(selectinload(Post.user), selectinload(Post.topic)).where(Post.status == 1)

        if user_id:
            query = query.where(Post.user_id == user_id)
        if topic_id:
            query = query.where(Post.topic_id == topic_id)

        # 获取总数
        count_query = select(func.count(Post.id)).where(Post.status == 1)
        if user_id:
            count_query = count_query.where(Post.user_id == user_id)
        if topic_id:
            count_query = count_query.where(Post.topic_id == topic_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取列表
        query = query.order_by(desc(Post.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        posts = result.scalars().all()

        return posts, total

    @staticmethod
    async def update_post(db: AsyncSession, post: Post, post_data: PostUpdate) -> Post:
        """更新动态"""
        update_data = post_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        await db.flush()
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def delete_post(db: AsyncSession, post: Post) -> bool:
        """删除动态（软删除）"""
        post.status = 0
        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def like_post(db: AsyncSession, user_id: int, post_id: int) -> bool:
        """点赞动态"""
        # 检查是否已点赞
        result = await db.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        if result.scalar_one_or_none():
            return False

        like = Like(user_id=user_id, post_id=post_id)
        db.add(like)

        # 更新动态点赞数
        post_result = await db.execute(select(Post).where(Post.id == post_id))
        post = post_result.scalar_one_or_none()
        if post:
            post.like_count += 1

        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def unlike_post(db: AsyncSession, user_id: int, post_id: int) -> bool:
        """取消点赞"""
        result = await db.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        like = result.scalar_one_or_none()
        if not like:
            return False

        await db.delete(like)

        # 更新动态点赞数
        post_result = await db.execute(select(Post).where(Post.id == post_id))
        post = post_result.scalar_one_or_none()
        if post and post.like_count > 0:
            post.like_count -= 1

        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def check_liked(db: AsyncSession, user_id: int, post_id: int) -> bool:
        """检查是否已点赞"""
        result = await db.execute(
            select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def create_comment(db: AsyncSession, user_id: int, post_id: int, comment_data: CommentCreate) -> Comment:
        """创建评论"""
        comment = Comment(
            user_id=user_id,
            post_id=post_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
        )
        db.add(comment)

        # 更新动态评论数
        post_result = await db.execute(select(Post).where(Post.id == post_id))
        post = post_result.scalar_one_or_none()
        if post:
            post.comment_count += 1

        await db.flush()
        await db.commit()
        # 重新查询以加载 user 关系
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.id == comment.id)
        )
        comment = result.scalar_one()
        return comment

    @staticmethod
    async def get_comments(
        db: AsyncSession,
        post_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Comment], int]:
        """获取评论列表"""
        # 获取总数
        count_result = await db.execute(
            select(func.count(Comment.id)).where(Comment.post_id == post_id, Comment.status == 1)
        )
        total = count_result.scalar() or 0

        # 获取评论列表
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.post_id == post_id, Comment.status == 1, Comment.parent_id.is_(None))
            .order_by(desc(Comment.created_at))
            .offset(skip)
            .limit(limit)
        )
        comments = result.scalars().all()

        return comments, total

    @staticmethod
    async def get_topics(db: AsyncSession, skip: int = 0, limit: int = 20) -> List[Topic]:
        """获取话题列表"""
        result = await db.execute(
            select(Topic)
            .where(Topic.is_active == 1)
            .order_by(desc(Topic.post_count))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
