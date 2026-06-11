"""群组接口测试"""

from helpers import create_test_user, register_user, login_user


class TestGroups:
    """群组测试类"""

    def test_create_group(self, client):
        """测试创建群组"""
        headers = create_test_user(client)
        response = client.post(
            "/api/v1/groups",
            headers=headers,
            json={"name": "测试群组", "description": "测试描述", "category": "兴趣"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "测试群组"

    def test_create_group_empty_name(self, client):
        """测试创建空名称群组（边界条件）"""
        headers = create_test_user(client)
        response = client.post("/api/v1/groups", headers=headers, json={"name": ""})
        assert response.status_code == 422

    def test_create_group_long_name(self, client):
        """测试创建超长名称群组（边界条件）"""
        headers = create_test_user(client)
        long_name = "a" * 101
        response = client.post("/api/v1/groups", headers=headers, json={"name": long_name})
        assert response.status_code == 422

    def test_create_group_unauthorized(self, client):
        """测试未登录创建群组"""
        response = client.post("/api/v1/groups", json={"name": "测试群组"})
        assert response.status_code == 401

    def test_get_groups(self, client):
        """测试获取群组列表"""
        headers = create_test_user(client)
        client.post("/api/v1/groups", headers=headers, json={"name": "列表测试", "is_public": 1})
        response = client.get("/api/v1/groups", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_groups_pagination(self, client):
        """测试群组列表分页"""
        headers = create_test_user(client)
        for i in range(15):
            client.post("/api/v1/groups", headers=headers, json={"name": f"群组 {i+1}", "is_public": 1})
        response = client.get("/api/v1/groups?skip=5&limit=5", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) == 5

    def test_get_groups_search(self, client):
        """测试群组搜索"""
        headers = create_test_user(client)
        client.post("/api/v1/groups", headers=headers, json={"name": "Python学习群", "is_public": 1})
        client.post("/api/v1/groups", headers=headers, json={"name": "Java学习群", "is_public": 1})
        response = client.get("/api/v1/groups?keyword=Python", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_groups_by_category(self, client):
        """测试按分类筛选群组"""
        headers = create_test_user(client)
        client.post("/api/v1/groups", headers=headers, json={"name": "学习群", "category": "学习", "is_public": 1})
        client.post("/api/v1/groups", headers=headers, json={"name": "游戏群", "category": "游戏", "is_public": 1})
        response = client.get("/api/v1/groups?category=学习", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_group_detail(self, client):
        """测试获取群组详情"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "详情测试"})
        group_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/groups/{group_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "详情测试"

    def test_get_nonexistent_group(self, client):
        """测试获取不存在的群组"""
        headers = create_test_user(client)
        response = client.get("/api/v1/groups/99999", headers=headers)
        assert response.status_code == 404

    def test_update_group(self, client):
        """测试更新群组"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "原始名称"})
        group_id = create_resp.json()["id"]
        response = client.put(f"/api/v1/groups/{group_id}", headers=headers, json={"name": "新名称"})
        assert response.status_code == 200

    def test_update_group_not_admin(self, client):
        """测试非管理员更新群组（权限测试）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "测试群组"})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        response = client.put(f"/api/v1/groups/{group_id}", headers=headers2, json={"name": "尝试修改"})
        assert response.status_code == 403

    def test_delete_group(self, client):
        """测试删除群组"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "要删除的"})
        group_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/groups/{group_id}", headers=headers)
        assert response.status_code == 200

    def test_delete_group_not_creator(self, client):
        """测试非群主删除群组（权限测试）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "测试群组"})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        response = client.delete(f"/api/v1/groups/{group_id}", headers=headers2)
        assert response.status_code == 403

    def test_join_group(self, client):
        """测试加入群组"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "加入测试", "is_public": 1})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        assert response.status_code == 200

    def test_join_group_already_member(self, client):
        """测试重复加入群组"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "重复加入测试", "is_public": 1})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        response = client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        assert response.status_code == 400

    def test_join_nonexistent_group(self, client):
        """测试加入不存在的群组"""
        headers = create_test_user(client)
        response = client.post("/api/v1/groups/99999/join", headers=headers)
        assert response.status_code == 404

    def test_leave_group(self, client):
        """测试退出群组"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "退出测试", "is_public": 1})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        response = client.delete(f"/api/v1/groups/{group_id}/join", headers=headers2)
        assert response.status_code == 200

    def test_leave_group_not_member(self, client):
        """测试非成员退出群组"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "非成员退出测试", "is_public": 1})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = client.delete(f"/api/v1/groups/{group_id}/join", headers=headers2)
        assert response.status_code == 400

    def test_get_members(self, client):
        """测试获取成员列表"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "成员列表测试"})
        group_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/groups/{group_id}/members", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_create_group_post(self, client):
        """测试发布群组动态"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "动态测试"})
        group_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/groups/{group_id}/posts", headers=headers, json={"content": "群组动态"})
        assert response.status_code == 201

    def test_create_group_post_not_member(self, client):
        """测试非成员发布群组动态（权限测试）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "非成员动态测试"})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = client.post(f"/api/v1/groups/{group_id}/posts", headers=headers2, json={"content": "尝试发布"})
        assert response.status_code == 403

    def test_get_group_posts(self, client):
        """测试获取群组动态列表"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "群组动态列表测试"})
        group_id = create_resp.json()["id"]
        for i in range(3):
            client.post(f"/api/v1/groups/{group_id}/posts", headers=headers, json={"content": f"群组动态 {i+1}"})
        response = client.get(f"/api/v1/groups/{group_id}/posts", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3

    def test_create_announcement(self, client):
        """测试发布公告"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "公告测试"})
        group_id = create_resp.json()["id"]
        response = client.post(
            f"/api/v1/groups/{group_id}/announcements",
            headers=headers,
            json={"title": "测试公告", "content": "公告内容"},
        )
        assert response.status_code == 201

    def test_create_announcement_not_admin(self, client):
        """测试非管理员发布公告（权限测试）"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "非管理员公告测试"})
        group_id = create_resp.json()["id"]
        register_user(client, "user2", "user2@example.com", "password123")
        login_resp = login_user(client, "user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        client.post(f"/api/v1/groups/{group_id}/join", headers=headers2)
        response = client.post(
            f"/api/v1/groups/{group_id}/announcements",
            headers=headers2,
            json={"title": "尝试发布公告", "content": "公告内容"},
        )
        assert response.status_code == 403

    def test_get_announcements(self, client):
        """测试获取公告列表"""
        headers = create_test_user(client)
        create_resp = client.post("/api/v1/groups", headers=headers, json={"name": "公告列表测试"})
        group_id = create_resp.json()["id"]
        for i in range(3):
            client.post(
                f"/api/v1/groups/{group_id}/announcements",
                headers=headers,
                json={"title": f"公告 {i+1}", "content": f"公告内容 {i+1}"},
            )
        response = client.get(f"/api/v1/groups/{group_id}/announcements", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 3
