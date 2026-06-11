"""私信接口测试"""

import requests
from helpers import create_test_user, register_user, login_user

BASE_URL = "http://localhost:8000"


class TestMessages:
    """私信测试类"""

    def test_create_conversation(self):
        """测试创建会话"""
        headers = create_test_user()
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        response = requests.post(f"{BASE_URL}/api/v1/messages/conversations/{user2_id}", headers=headers)
        assert response.status_code == 200

    def test_send_message(self):
        """测试发送消息"""
        headers = create_test_user()
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = requests.post(f"{BASE_URL}/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        response = requests.post(
            f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": "你好，测试消息"},
        )
        assert response.status_code == 201

    def test_get_messages(self):
        """测试获取消息列表"""
        headers = create_test_user()
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = requests.post(f"{BASE_URL}/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        for i in range(3):
            requests.post(
                f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": f"消息 {i+1}"},
            )
        response = requests.get(f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3

    def test_get_conversations(self):
        """测试获取会话列表"""
        headers = create_test_user()
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        requests.post(f"{BASE_URL}/api/v1/messages/conversations/{user2_id}", headers=headers)
        response = requests.get(f"{BASE_URL}/api/v1/messages/conversations", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_mark_as_read(self):
        """测试标记消息已读"""
        headers = create_test_user()
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = requests.post(f"{BASE_URL}/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        requests.post(
            f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": "测试消息"},
        )
        response = requests.put(f"{BASE_URL}/api/v1/messages/conversations/{conversation_id}/read", headers=headers)
        assert response.status_code == 200
