"""私信服务"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload

from app.models.message import Conversation, Message
from app.models.user import User
from app.schemas.message import MessageCreate


class MessageService:
    """私信服务类"""

    @staticmethod
    async def get_or_create_conversation(db: AsyncSession, user1_id: int, user2_id: int) -> Conversation:
        """获取或创建会话"""
        # 确保 user1_id < user2_id 以避免重复
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id

        result = await db.execute(
            select(Conversation).where(
                Conversation.user1_id == user1_id,
                Conversation.user2_id == user2_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(
                user1_id=user1_id,
                user2_id=user2_id
            )
            db.add(conversation)
            await db.flush()
            await db.commit()
            await db.refresh(conversation)

        return conversation

    @staticmethod
    async def send_message(
        db: AsyncSession,
        conversation_id: int,
        sender_id: int,
        message_data: MessageCreate
    ) -> Message:
        """发送消息"""
        from datetime import datetime
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=message_data.content,
            message_type=message_data.message_type,
            media_url=message_data.media_url,
        )
        db.add(message)
        await db.flush()

        # 更新会话最后消息（使用原生 SQL 避免 lazy loading）
        now = datetime.utcnow()
        await db.execute(
            Conversation.__table__.update()
            .where(Conversation.id == conversation_id)
            .values(last_message_id=message.id, last_message_at=now)
        )
        await db.commit()

        # 重新查询以加载 sender 关系
        result = await db.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.id == message.id)
        )
        message = result.scalar_one()
        return message

    @staticmethod
    async def get_conversations(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20) -> tuple[List[dict], int]:
        """获取会话列表"""
        # 获取总数
        count_result = await db.execute(
            select(func.count(Conversation.id)).where(
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
        )
        total = count_result.scalar() or 0

        # 获取会话列表
        result = await db.execute(
            select(Conversation)
            .where(
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id
                )
            )
            .order_by(desc(Conversation.last_message_at))
            .offset(skip)
            .limit(limit)
        )
        conversations = result.scalars().all()

        # 构建响应数据
        conversation_list = []
        for conv in conversations:
            # 确定对方用户
            other_user_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
            other_user_result = await db.execute(select(User).where(User.id == other_user_id))
            other_user = other_user_result.scalar_one_or_none()

            # 获取最后一条消息
            last_message = None
            if conv.last_message_id:
                msg_result = await db.execute(
                    select(Message)
                    .options(selectinload(Message.sender))
                    .where(Message.id == conv.last_message_id)
                )
                last_message = msg_result.scalar_one_or_none()

            # 获取未读消息数
            unread_result = await db.execute(
                select(func.count(Message.id)).where(
                    Message.conversation_id == conv.id,
                    Message.sender_id != user_id,
                    Message.is_read == 0
                )
            )
            unread_count = unread_result.scalar() or 0

            conversation_list.append({
                "id": conv.id,
                "user1_id": conv.user1_id,
                "user2_id": conv.user2_id,
                "last_message_id": conv.last_message_id,
                "last_message_at": conv.last_message_at,
                "created_at": conv.created_at,
                "other_user": other_user,
                "last_message": last_message,
                "unread_count": unread_count,
            })

        return conversation_list, total

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Message], int]:
        """获取消息列表"""
        # 获取总数
        count_result = await db.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
        )
        total = count_result.scalar() or 0

        # 获取消息列表
        result = await db.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .offset(skip)
            .limit(limit)
        )
        messages = result.scalars().all()

        return messages, total

    @staticmethod
    async def mark_as_read(db: AsyncSession, conversation_id: int, user_id: int) -> bool:
        """标记消息已读"""
        result = await db.execute(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,
                Message.is_read == 0
            )
        )
        messages = result.scalars().all()

        for message in messages:
            message.is_read = 1

        await db.flush()
        await db.commit()
        return True
