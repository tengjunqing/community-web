"""WebSocket 连接管理"""

from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 用户ID -> WebSocket连接集合
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """建立连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """断开连接"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # 连接已断开，移除
                    self.active_connections[user_id].discard(connection)

    async def broadcast(self, message: dict):
        """广播消息"""
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)

    def get_online_users(self) -> list:
        """获取在线用户列表"""
        return list(self.active_connections.keys())


# 全局连接管理器
manager = ConnectionManager()
