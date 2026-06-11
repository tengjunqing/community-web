"""私信接口测试"""

from helpers import create_test_user, register_user, login_user


class TestMessages:
    """私信测试类"""

    def test_create_conversation(self, client):
        """测试创建会话"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        response = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        assert response.status_code == 200

    def test_create_conversation_with_self(self, client):
        """测试与自己创建会话（边界条件）"""
        headers = create_test_user(client)
        me_resp = client.get("/api/v1/auth/me", headers=headers)
        my_id = me_resp.json()["id"]
        response = client.post(f"/api/v1/messages/conversations/{my_id}", headers=headers)
        assert response.status_code == 400

    def test_create_conversation_nonexistent_user(self, client):
        """测试与不存在的用户创建会话"""
        headers = create_test_user(client)
        response = client.post("/api/v1/messages/conversations/99999", headers=headers)
        assert response.status_code in [400, 404]

    def test_create_conversation_unauthorized(self, client):
        """测试未登录创建会话"""
        response = client.post("/api/v1/messages/conversations/2")
        assert response.status_code == 401

    def test_send_message(self, client):
        """测试发送消息"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        response = client.post(
            f"/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": "你好，测试消息"},
        )
        assert response.status_code == 201

    def test_send_message_empty_content(self, client):
        """测试发送空消息（边界条件）"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        response = client.post(
            f"/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": ""},
        )
        assert response.status_code == 422

    def test_send_message_long_content(self, client):
        """测试发送超长消息（边界条件）"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        long_content = "a" * 5001
        response = client.post(
            f"/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": long_content},
        )
        assert response.status_code == 422

    def test_send_message_special_characters(self, client):
        """测试发送特殊字符消息"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        response = client.post(
            f"/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": "特殊字符：<>&\"'!@#$%^&*()"},
        )
        assert response.status_code == 201

    def test_get_messages(self, client):
        """测试获取消息列表"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        for i in range(3):
            client.post(
                f"/api/v1/messages/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": f"消息 {i+1}"},
            )
        response = client.get(f"/api/v1/messages/conversations/{conversation_id}/messages", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3

    def test_get_messages_pagination(self, client):
        """测试消息列表分页"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        for i in range(15):
            client.post(
                f"/api/v1/messages/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": f"消息 {i+1}"},
            )
        response = client.get(
            f"/api/v1/messages/conversations/{conversation_id}/messages?skip=5&limit=5",
            headers=headers,
        )
        assert response.status_code == 200
        assert len(response.json()["items"]) == 5

    def test_get_conversations(self, client):
        """测试获取会话列表"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        response = client.get("/api/v1/messages/conversations", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_conversations_pagination(self, client):
        """测试会话列表分页"""
        headers = create_test_user(client)
        for i in range(10):
            register_user(client, f"user{i+2}", f"user{i+2}@example.com", "password123")
            login_resp = login_user(client, f"user{i+2}", "password123")
            user_id = login_resp.json().get("user_id") or (i + 2)
            client.post(f"/api/v1/messages/conversations/{user_id}", headers=headers)
        response = client.get("/api/v1/messages/conversations?skip=3&limit=3", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) == 3

    def test_mark_as_read(self, client):
        """测试标记消息已读"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        client.post(
            f"/api/v1/messages/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": "测试消息"},
        )
        response = client.put(f"/api/v1/messages/conversations/{conversation_id}/read", headers=headers)
        assert response.status_code == 200

    def test_mark_as_read_empty_conversation(self, client):
        """测试标记空会话已读"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        conv_resp = client.post(f"/api/v1/messages/conversations/{user2_id}", headers=headers)
        conversation_id = conv_resp.json()["id"]
        response = client.put(f"/api/v1/messages/conversations/{conversation_id}/read", headers=headers)
        assert response.status_code == 200
