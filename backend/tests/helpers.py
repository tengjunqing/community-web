"""测试辅助函数"""


def register_user(client, username, email, password, nickname=None):
    """注册用户"""
    data = {"username": username, "email": email, "password": password}
    if nickname:
        data["nickname"] = nickname
    return client.post("/api/v1/auth/register", json=data)


def login_user(client, username, password):
    """登录用户"""
    return client.post("/api/v1/auth/login", json={"username": username, "password": password})


def create_test_user(client, username="testuser", email="test@example.com", password="testpassword123"):
    """创建测试用户并返回认证头"""
    register_user(client, username, email, password, username)
    response = login_user(client, username, password)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
