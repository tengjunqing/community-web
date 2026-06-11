"""群组服务"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.models.group import Group, GroupMember, GroupPost, GroupAnnouncement
from app.models.post import Post
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate, GroupAnnouncementCreate
from app.schemas.post import PostCreate


class GroupService:
    """群组服务类"""

    @staticmethod
    async def create_group(db: AsyncSession, creator_id: int, group_data: GroupCreate) -> Group:
        """创建群组"""
        group = Group(
            name=group_data.name,
            description=group_data.description,
            category=group_data.category,
            is_public=group_data.is_public,
            creator_id=creator_id,
        )
        db.add(group)
        await db.flush()

        # 添加创建者为群主
        member = GroupMember(
            group_id=group.id,
            user_id=creator_id,
            role=3,  # 群主
        )
        db.add(member)
        await db.flush()
        await db.commit()
        await db.refresh(group)

        return group

    @staticmethod
    async def get_group_by_id(db: AsyncSession, group_id: int) -> Optional[Group]:
        """获取群组详情"""
        result = await db.execute(
            select(Group)
            .options(selectinload(Group.creator))
            .where(Group.id == group_id, Group.status == 1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_groups(
        db: AsyncSession,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Group], int]:
        """获取群组列表"""
        query = select(Group).options(selectinload(Group.creator)).where(Group.status == 1, Group.is_public == 1)

        if category:
            query = query.where(Group.category == category)
        if keyword:
            query = query.where(Group.name.ilike(f"%{keyword}%"))

        # 获取总数
        count_query = select(func.count(Group.id)).where(Group.status == 1, Group.is_public == 1)
        if category:
            count_query = count_query.where(Group.category == category)
        if keyword:
            count_query = count_query.where(Group.name.ilike(f"%{keyword}%"))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取列表
        query = query.order_by(desc(Group.member_count)).offset(skip).limit(limit)
        result = await db.execute(query)
        groups = result.scalars().all()

        return groups, total

    @staticmethod
    async def update_group(db: AsyncSession, group: Group, group_data: GroupUpdate) -> Group:
        """更新群组信息"""
        update_data = group_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)

        await db.flush()
        await db.commit()
        await db.refresh(group)
        return group

    @staticmethod
    async def delete_group(db: AsyncSession, group: Group) -> bool:
        """删除群组（软删除）"""
        group.status = 0
        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def join_group(db: AsyncSession, group_id: int, user_id: int) -> bool:
        """加入群组"""
        # 检查是否已是成员
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )
        if result.scalar_one_or_none():
            return False

        member = GroupMember(group_id=group_id, user_id=user_id)
        db.add(member)

        # 更新群组成员数
        group_result = await db.execute(select(Group).where(Group.id == group_id))
        group = group_result.scalar_one_or_none()
        if group:
            group.member_count += 1

        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def leave_group(db: AsyncSession, group_id: int, user_id: int) -> bool:
        """退出群组"""
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return False

        # 群主不能退出
        if member.role == 3:
            return False

        await db.delete(member)

        # 更新群组成员数
        group_result = await db.execute(select(Group).where(Group.id == group_id))
        group = group_result.scalar_one_or_none()
        if group and group.member_count > 0:
            group.member_count -= 1

        await db.flush()
        await db.commit()
        return True

    @staticmethod
    async def get_members(
        db: AsyncSession,
        group_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[GroupMember], int]:
        """获取群组成员列表"""
        # 获取总数
        count_result = await db.execute(
            select(func.count(GroupMember.id)).where(GroupMember.group_id == group_id)
        )
        total = count_result.scalar() or 0

        # 获取成员列表
        result = await db.execute(
            select(GroupMember)
            .options(selectinload(GroupMember.user))
            .where(GroupMember.group_id == group_id)
            .order_by(GroupMember.role.desc(), GroupMember.joined_at)
            .offset(skip)
            .limit(limit)
        )
        members = result.scalars().all()

        return members, total

    @staticmethod
    async def check_member(db: AsyncSession, group_id: int, user_id: int) -> Optional[GroupMember]:
        """检查是否是成员"""
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_group_post(
        db: AsyncSession,
        group_id: int,
        user_id: int,
        post_data: PostCreate
    ) -> GroupPost:
        """创建群组动态"""
        # 先创建动态
        post = Post(
            user_id=user_id,
            content=post_data.content,
            images=post_data.images,
            topic_id=post_data.topic_id,
        )
        db.add(post)
        await db.flush()

        # 创建群组动态关联
        group_post = GroupPost(
            group_id=group_id,
            user_id=user_id,
            post_id=post.id,
        )
        db.add(group_post)
        await db.flush()
        await db.commit()
        await db.refresh(group_post)

        return group_post

    @staticmethod
    async def get_group_posts(
        db: AsyncSession,
        group_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[dict], int]:
        """获取群组动态列表"""
        # 获取总数
        count_result = await db.execute(
            select(func.count(GroupPost.id)).where(GroupPost.group_id == group_id)
        )
        total = count_result.scalar() or 0

        # 获取动态列表
        result = await db.execute(
            select(GroupPost)
            .options(selectinload(GroupPost.post).selectinload(Post.user))
            .where(GroupPost.group_id == group_id)
            .order_by(GroupPost.is_pinned.desc(), desc(GroupPost.created_at))
            .offset(skip)
            .limit(limit)
        )
        group_posts = result.scalars().all()

        return group_posts, total

    @staticmethod
    async def create_announcement(
        db: AsyncSession,
        group_id: int,
        creator_id: int,
        announcement_data: GroupAnnouncementCreate
    ) -> GroupAnnouncement:
        """创建群组公告"""
        announcement = GroupAnnouncement(
            group_id=group_id,
            title=announcement_data.title,
            content=announcement_data.content,
            creator_id=creator_id,
        )
        db.add(announcement)
        await db.flush()
        await db.commit()
        await db.refresh(announcement)

        return announcement

    @staticmethod
    async def get_announcements(
        db: AsyncSession,
        group_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[GroupAnnouncement], int]:
        """获取群组公告列表"""
        # 获取总数
        count_result = await db.execute(
            select(func.count(GroupAnnouncement.id)).where(
                GroupAnnouncement.group_id == group_id,
                GroupAnnouncement.is_active == 1
            )
        )
        total = count_result.scalar() or 0

        # 获取公告列表
        result = await db.execute(
            select(GroupAnnouncement)
            .options(selectinload(GroupAnnouncement.creator))
            .where(
                GroupAnnouncement.group_id == group_id,
                GroupAnnouncement.is_active == 1
            )
            .order_by(desc(GroupAnnouncement.created_at))
            .offset(skip)
            .limit(limit)
        )
        announcements = result.scalars().all()

        return announcements, total
