"""认证接口测试"""

from helpers import register_user, login_user, create_test_user


class TestAuth:
    """认证测试类"""

    def test_register(self, client):
        """测试用户注册"""
        response = register_user(client, "newuser", "new@example.com", "newpassword123", "新用户")
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data

    def test_register_duplicate_username(self, client):
        """测试重复用户名注册"""
        register_user(client, "testuser", "test@example.com", "password123")
        response = register_user(client, "testuser", "another@example.com", "password123")
        assert response.status_code == 400

    def test_register_duplicate_email(self, client):
        """测试重复邮箱注册"""
        register_user(client, "testuser", "test@example.com", "password123")
        response = register_user(client, "anotheruser", "test@example.com", "password123")
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """测试无效邮箱注册"""
        response = register_user(client, "newuser", "invalid-email", "password123")
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """测试短密码注册"""
        response = register_user(client, "newuser", "new@example.com", "123")
        assert response.status_code == 422

    def test_register_short_username(self, client):
        """测试短用户名注册（边界条件）"""
        response = register_user(client, "ab", "new@example.com", "password123")
        assert response.status_code == 422

    def test_register_long_username(self, client):
        """测试长用户名注册（边界条件）"""
        long_username = "a" * 51
        response = register_user(client, long_username, "new@example.com", "password123")
        assert response.status_code == 422

    def test_register_special_characters_username(self, client):
        """测试特殊字符用户名"""
        response = register_user(client, "user@#$%", "new@example.com", "password123")
        assert response.status_code in [201, 422]

    def test_register_empty_fields(self, client):
        """测试空字段注册"""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422

    def test_login(self, client):
        """测试用户登录"""
        register_user(client, "testuser", "test@example.com", "testpassword123")
        response = login_user(client, "testuser", "testpassword123")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_email(self, client):
        """测试邮箱登录"""
        register_user(client, "testuser", "test@example.com", "testpassword123")
        response = login_user(client, "test@example.com", "testpassword123")
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client):
        """测试错误密码登录"""
        register_user(client, "testuser", "test@example.com", "testpassword123")
        response = login_user(client, "testuser", "wrongpassword")
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """测试不存在的用户登录"""
        response = login_user(client, "nonexistent", "password123")
        assert response.status_code == 401

    def test_get_me(self, client):
        """测试获取当前用户信息"""
        headers = create_test_user(client)
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_get_me_unauthorized(self, client):
        """测试未认证获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """测试无效令牌获取用户信息"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_refresh_token(self, client):
        """测试刷新令牌"""
        register_user(client, "testuser", "test@example.com", "testpassword123")
        login_resp = login_user(client, "testuser", "testpassword123")
        refresh_token = login_resp.json()["refresh_token"]

        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_refresh_token_invalid(self, client):
        """测试无效刷新令牌"""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid-token"})
        assert response.status_code == 401
