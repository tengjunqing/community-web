"""动态接口测试"""

from helpers import create_test_user


class TestPosts:
    """动态测试类"""

    def test_create_post(self, client):
        """测试发布动态"""
        headers = create_test_user(client)
        response = client.post("/api/v1/posts", headers=headers, json={"content": "测试动态"})
        assert response.status_code == 201
        assert response.json()["content"] == "测试动态"

    def test_get_posts(self, client):
        """测试获取动态列表"""
        headers = create_test_user(client)
        for i in range(3):
            client.post("/api/v1/posts", headers=headers, json={"content": f"动态 {i+1}"})
        response = client.get("/api/v1/posts", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3

    def test_get_post_detail(self, client):
        """测试获取动态详情"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "详情测试"})
        post_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/posts/{post_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["content"] == "详情测试"

    def test_delete_post(self, client):
        """测试删除动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "要删除的"})
        post_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/posts/{post_id}", headers=headers)
        assert response.status_code == 200

    def test_like_post(self, client):
        """测试点赞动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "点赞测试"})
        post_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 200
        get_resp = client.get(f"/api/v1/posts/{post_id}", headers=headers)
        assert get_resp.json()["like_count"] == 1

    def test_unlike_post(self, client):
        """测试取消点赞"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "取消点赞测试"})
        post_id = create_resp.json()["id"]
        client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        response = client.delete(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert response.status_code == 200

    def test_create_comment(self, client):
        """测试发表评论"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/posts", headers=headers, json={"content": "评论测试"})
        post_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/posts/{post_id}/comments", headers=headers, json={"content": "测试评论"})
        assert response.status_code == 201

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
