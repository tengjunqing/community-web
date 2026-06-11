"""用户服务"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import User, InterestTag
from app.models.follow import Follow
from app.schemas.user import UserCreate, UserUpdate, UserProfile
from app.core.security import get_password_hash, verify_password


class UserService:
    """用户服务类"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.interests))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.interests))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.interests))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """创建用户"""
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            nickname=user_data.nickname or user_data.username,
        )
        db.add(user)
        await db.flush()
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user: User, user_data: UserUpdate) -> User:
        """更新用户信息"""
        update_data = user_data.model_dump(exclude_unset=True)

        # 处理兴趣标签
        if "interest_ids" in update_data:
            interest_ids = update_data.pop("interest_ids")
            if interest_ids is not None:
                result = await db.execute(
                    select(InterestTag).where(InterestTag.id.in_(interest_ids))
                )
                interests = result.scalars().all()
                user.interests = list(interests)

        # 更新其他字段
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户"""
        # 尝试用户名或邮箱登录
        user = await UserService.get_user_by_username(db, username)
        if not user:
            user = await UserService.get_user_by_email(db, username)

        if not user or not verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int, current_user_id: Optional[int] = None) -> dict:
        """获取用户详细资料"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        # 获取动态数量
        from app.models.post import Post
        post_count_result = await db.execute(
            select(func.count(Post.id)).where(Post.user_id == user_id, Post.status == 1)
        )
        post_count = post_count_result.scalar() or 0

        # 获取粉丝数
        follower_count_result = await db.execute(
            select(func.count(Follow.id)).where(Follow.following_id == user_id)
        )
        follower_count = follower_count_result.scalar() or 0

        # 获取关注数
        following_count_result = await db.execute(
            select(func.count(Follow.id)).where(Follow.follower_id == user_id)
        )
        following_count = following_count_result.scalar() or 0

        # 检查是否关注
        is_following = False
        if current_user_id and current_user_id != user_id:
            follow_result = await db.execute(
                select(Follow).where(
                    Follow.follower_id == current_user_id,
                    Follow.following_id == user_id
                )
            )
            is_following = follow_result.scalar_one_or_none() is not None

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "bio": user.bio,
            "status": user.status,
            "created_at": user.created_at,
            "interests": user.interests,
            "post_count": post_count,
            "follower_count": follower_count,
            "following_count": following_count,
            "is_following": is_following,
        }

    @staticmethod
    async def follow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
        """关注用户"""
        if follower_id == following_id:
            return False

        # 检查是否已关注
        result = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id
            )
        )
        if result.scalar_one_or_none():
            return False

        follow = Follow(follower_id=follower_id, following_id=following_id)
        db.add(follow)
        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def unfollow_user(db: AsyncSession, follower_id: int, following_id: int) -> bool:
        """取消关注"""
        result = await db.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id
            )
        )
        follow = result.scalar_one_or_none()
        if not follow:
            return False

        await db.delete(follow)
        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def get_followers(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20) -> List[User]:
        """获取粉丝列表"""
        result = await db.execute(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.following_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_following(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20) -> List[User]:
        """获取关注列表"""
        result = await db.execute(
            select(User)
            .join(Follow, Follow.following_id == User.id)
            .where(Follow.follower_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
