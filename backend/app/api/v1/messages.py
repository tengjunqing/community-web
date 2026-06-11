"""私信相关接口"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.message import (
    MessageCreate, MessageResponse, MessageListResponse,
    ConversationResponse, ConversationListResponse
)
from app.schemas.post import UserBrief
from app.services.message_service import MessageService
from app.models.user import User
from app.api.deps import get_current_active_user
from app.core.websocket import manager
from app.core.security import verify_token

router = APIRouter()


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取会话列表"""
    conversations, total = await MessageService.get_conversations(db, current_user.id, skip, limit)
    return ConversationListResponse(total=total, items=conversations)


@router.post("/conversations/{user_id}", response_model=ConversationResponse)
async def create_conversation(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建或获取会话"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能与自己创建会话"
        )

    conversation = await MessageService.get_or_create_conversation(db, current_user.id, user_id)
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取消息列表"""
    messages, total = await MessageService.get_messages(db, conversation_id, current_user.id, skip, limit)
    return MessageListResponse(total=total, items=messages)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """发送消息"""
    message = await MessageService.send_message(db, conversation_id, current_user.id, message_data)

    # 通过 WebSocket 推送消息
    await manager.send_personal_message(
        {
            "type": "new_message",
            "data": {
                "id": message.id,
                "conversation_id": conversation_id,
                "sender_id": current_user.id,
                "content": message.content,
                "message_type": message.message_type,
                "created_at": message.created_at.isoformat(),
            }
        },
        current_user.id
    )

    # 手动构造响应以避免 lazy loading
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        message_type=message.message_type,
        media_url=message.media_url,
        is_read=message.is_read,
        created_at=message.created_at,
        sender=UserBrief(
            id=current_user.id,
            username=current_user.username,
            nickname=current_user.nickname,
            avatar=current_user.avatar,
        ) if current_user else None,
    )


@router.put("/conversations/{conversation_id}/read", status_code=status.HTTP_200_OK)
async def mark_as_read(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """标记消息已读"""
    await MessageService.mark_as_read(db, conversation_id, current_user.id)
    return {"message": "标记成功"}


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket 连接端点"""
    # 验证 token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001, reason="无效的令牌")
        return

    user_id = int(payload.get("sub"))
    await manager.connect(websocket, user_id)

    try:
        while True:
            # 保持连接
            data = await websocket.receive_text()
            # 处理客户端消息（如心跳）
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
