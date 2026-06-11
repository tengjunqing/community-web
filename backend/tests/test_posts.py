"""动态接口测试"""

from helpers import create_test_user, register_user, login_user


class TestPosts:
    """动态测试类"""

    def test_create_post(self, client):
        """测试发布动态"""
        headers = create_test_user(client)
        response = client.post("/api/v1/posts", headers=headers, json={"content": "测试动态"})
        assert response.status_code == 201
        assert response.json()["content"] == "测试动态"

    def test_create_post_empty_content(self, client):
        """测试发布空内容动态（边界条件）"""
        headers = create_test_user(client)
        response = client.post("/api/v1/posts", headers=headers, json={"content": ""})
        assert response.status_code == 422

    def test_create_post_long_content(self, client):
        """测试发布超长内容动态（边界条件）"""
        headers = create_test_user(client)
        long_content = "a" * 5001
        response = client.post("/api/v1/posts", headers=headers, json={"content": long_content})
        assert response.status_code == 422

    def test_create_post_special_characters(self, client):
        """测试发布特殊字符动态"""
        headers = create_test_user(client)
        response = client.post("/api/v1/posts", headers=headers, json={"content": "特殊字符：<>&\"'!@#$%^&*()"})
        assert response.status_code == 201

    def test_create_post_unauthorized(self, client):
        """测试未登录发布动态"""
        response = client.post("/api/v1/posts", json={"content": "测试动态"})
        assert response.status_code == 401

    def test_get_posts(self, client):
        """测试获取动态列表"""
        headers = create_test_user(client)
        for i in range(3):
            client.post("/api/v1/posts", headers=headers, json={"content": f"动态 {i+1}"})
        response = client.get("/api/v1/posts", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3

    def test_get_posts_pagination(self, client):
        """测试动态列表分页"""
        headers = create_test_user(client)
        for i in range(15):
            client.post("/api/v1/posts", headers=headers, json={"content": f"动态 {i+1}"})
        # 测试默认分页
        response1 = client.get("/api/v1/posts", headers=headers)
        assert response1.status_code == 200
        assert len(response1.json()["items"]) <= 20
        # 测试自定义分页
        response2 = client.get("/api/v1/posts?skip=5&limit=5", headers=headers)
        assert response2.status_code == 200
        assert len(response2.json()["items"]) == 5

    def test_get_posts_by_user(self, client):
        """测试按用户筛选动态"""
        headers = create_test_user(client)
        client.post("/api/v1/posts", headers=headers, json={"content": "用户1的动态"})
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post("/api/v1/posts", headers=headers2, json={"content": "用户2的动态"})
        response = client.get("/api/v1/posts?user_id=1", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_post_detail(self, client):
        """测试获取动态详情"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "详情测试"})
        post_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/posts/{post_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["content"] == "详情测试"

    def test_get_nonexistent_post(self, client):
        """测试获取不存在的动态"""
        headers = create_test_user(client)
        response = client.get("/api/v1/posts/99999", headers=headers)
        assert response.status_code == 404

    def test_update_post(self, client):
        """测试更新动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "原始内容"})
        post_id = create_resp.json()["id"]
        response = client.put(f"/api/v1/posts/{post_id}", headers=headers, json={"content": "更新内容"})
        assert response.status_code == 200
        assert response.json()["content"] == "更新内容"

    def test_update_other_user_post(self, client):
        """测试更新他人动态（权限测试）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "用户1的动态"})
        post_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = client.put(f"/api/v1/posts/{post_id}", headers=headers2, json={"content": "尝试修改"})
        assert response.status_code == 403

    def test_delete_post(self, client):
        """测试删除动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "要删除的"})
        post_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/posts/{post_id}", headers=headers)
        assert response.status_code == 200

    def test_delete_other_user_post(self, client):
        """测试删除他人动态（权限测试）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "用户1的动态"})
        post_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = client.delete(f"/api/v1/posts/{post_id}", headers=headers2)
        assert response.status_code == 403

    def test_like_post(self, client):
        """测试点赞动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "点赞测试"})
        post_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 200
        get_resp = client.get(f"/api/v1/posts/{post_id}", headers=headers)
        assert get_resp.json()["like_count"] == 1

    def test_like_post_twice(self, client):
        """测试重复点赞"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "重复点赞测试"})
        post_id = create_resp.json()["id"]
        client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        response = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 400

    def test_unlike_post(self, client):
        """测试取消点赞"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "取消点赞测试"})
        post_id = create_resp.json()["id"]
        client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        response = client.delete(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 200

    def test_unlike_post_not_liked(self, client):
        """测试取消未点赞的动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "未点赞测试"})
        post_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 400

    def test_create_comment(self, client):
        """测试发表评论"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "评论测试"})
        post_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/posts/{post_id}/comments", headers=headers, json={"content": "测试评论"})
        assert response.status_code == 201

    def test_create_comment_empty_content(self, client):
        """测试发表空评论（边界条件）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "评论测试"})
        post_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/posts/{post_id}/comments", headers=headers, json={"content": ""})
        assert response.status_code == 422

    def test_create_comment_long_content(self, client):
        """测试发表超长评论（边界条件）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "评论测试"})
        post_id = create_resp.json()["id"]
        long_content = "a" * 1001
        response = client.post(f"/api/v1/posts/{post_id}/comments", headers=headers, json={"content": long_content})
        assert response.status_code == 422

    def test_create_comment_nonexistent_post(self, client):
        """测试对不存在的动态评论"""
        headers = create_test_user(client)
        response = client.post("/api/v1/posts/99999/comments", headers=headers, json={"content": "测试评论"})
        assert response.status_code == 404

    def test_get_comments(self, client):
        """测试获取评论列表"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "评论列表测试"})
        post_id = create_resp.json()["id"]
        for i in range(3):
            client.post(f"/api/v1/posts/{post_id}/comments", headers=headers, json={"content": f"评论 {i+1}"})
        response = client.get(f"/api/v1/posts/{post_id}/comments", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3

    def test_get_comments_pagination(self, client):
        """测试评论列表分页"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "评论分页测试"})
        post_id = create_resp.json()["id"]
        for i in range(15):
            client.post(f"/api/v1/posts/{post_id}/comments", headers=headers, json={"content": f"评论 {i+1}"})
        response = client.get(f"/api/v1/posts/{post_id}/comments?skip=5&limit=5", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) == 5
