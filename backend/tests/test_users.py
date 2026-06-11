"""用户接口测试"""

from helpers import create_test_user, register_user, login_user


class TestUsers:
    """用户测试类"""

    def test_get_my_profile(self, client):
        """测试获取当前用户详细资料"""
        headers = create_test_user(client)
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert "post_count" in response.json()

    def test_update_my_profile(self, client):
        """测试更新当前用户信息"""
        headers = create_test_user(client)
        response = client.put("/api/v1/users/me", headers=headers, json={"nickname": "新昵称", "bio": "简介"})
        assert response.status_code == 200
        assert response.json()["nickname"] == "新昵称"

    def test_update_profile_long_nickname(self, client):
        """测试更新超长昵称（边界条件）"""
        headers = create_test_user(client)
        long_nickname = "a" * 51
        response = client.put("/api/v1/users/me", headers=headers, json={"nickname": long_nickname})
        assert response.status_code == 422

    def test_update_profile_special_characters(self, client):
        """测试更新特殊字符昵称"""
        headers = create_test_user(client)
        response = client.put("/api/v1/users/me", headers=headers, json={"nickname": "用户@#$%"})
        assert response.status_code == 200

    def test_get_user_profile(self, client):
        """测试获取指定用户详细资料"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        response = client.get(f"/api/v1/users/{user2_id}", headers=headers)
        assert response.status_code == 200

    def test_get_nonexistent_user_profile(self, client):
        """测试获取不存在的用户资料"""
        headers = create_test_user(client)
        response = client.get("/api/v1/users/99999", headers=headers)
        assert response.status_code == 404

    def test_follow_user(self, client):
        """测试关注用户"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        response = client.post(f"/api/v1/users/{user2_id}/follow", headers=headers)
        assert response.status_code == 200

    def test_follow_self(self, client):
        """测试关注自己"""
        headers = create_test_user(client)
        me_resp = client.get("/api/v1/auth/me", headers=headers)
        my_id = me_resp.json()["id"]
        response = client.post(f"/api/v1/users/{my_id}/follow", headers=headers)
        assert response.status_code == 400

    def test_follow_already_followed(self, client):
        """测试重复关注"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        client.post(f"/api/v1/users/{user2_id}/follow", headers=headers)
        response = client.post(f"/api/v1/users/{user2_id}/follow", headers=headers)
        assert response.status_code == 400

    def test_unfollow_user(self, client):
        """测试取消关注"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        client.post(f"/api/v1/users/{user2_id}/follow", headers=headers)
        response = client.delete(f"/api/v1/users/{user2_id}/follow", headers=headers)
        assert response.status_code == 200

    def test_unfollow_not_followed(self, client):
        """测试取消未关注的用户"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        response = client.delete(f"/api/v1/users/{user2_id}/follow", headers=headers)
        assert response.status_code == 400

    def test_get_followers(self, client):
        """测试获取粉丝列表"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post(f"/api/v1/users/1/follow", headers=headers2)
        response = client.get("/api/v1/users/1/followers", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_following(self, client):
        """测试获取关注列表"""
        headers = create_test_user(client)
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        user2_id = login_resp.json().get("user_id") or 2
        client.post(f"/api/v1/users/{user2_id}/follow", headers=headers)
        response = client.get("/api/v1/users/1/following", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1
