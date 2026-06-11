"""群组接口测试"""

import requests
from helpers import create_test_user, register_user, login_user

BASE_URL = "http://localhost:8000"


class TestGroups:
    """群组测试类"""

    def test_create_group(self):
        """测试创建群组"""
        headers = create_test_user()
        response = requests.post(
            f"{BASE_URL}/api/v1/groups",
            headers=headers,
            json={"name": "测试群组", "description": "测试描述", "category": "兴趣"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "测试群组"

    def test_get_groups(self):
        """测试获取群组列表"""
        headers = create_test_user()
        requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "列表测试", "is_public": 1})
        response = requests.get(f"{BASE_URL}/api/v1/groups", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_group_detail(self):
        """测试获取群组详情"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "详情测试"})
        group_id = create_resp.json()["id"]
        response = requests.get(f"{BASE_URL}/api/v1/groups/{group_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "详情测试"

    def test_update_group(self):
        """测试更新群组"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "原始名称"})
        group_id = create_resp.json()["id"]
        response = requests.put(f"{BASE_URL}/api/v1/groups/{group_id}", headers=headers, json={"name": "新名称"})
        assert response.status_code == 200

    def test_delete_group(self):
        """测试删除群组"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "要删除的"})
        group_id = create_resp.json()["id"]
        response = requests.delete(f"{BASE_URL}/api/v1/groups/{group_id}", headers=headers)
        assert response.status_code == 200

    def test_join_group(self):
        """测试加入群组"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "加入测试", "is_public": 1})
        group_id = create_resp.json()["id"]
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = requests.post(f"{BASE_URL}/api/v1/groups/{group_id}/join", headers=headers2)
        assert response.status_code == 200

    def test_leave_group(self):
        """测试退出群组"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "退出测试", "is_public": 1})
        group_id = create_resp.json()["id"]
        register_user("user2", "user2@example.com", "password123")
        login_resp = login_user("user2", "password123")
        headers2 = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        requests.post(f"{BASE_URL}/api/v1/groups/{group_id}/join", headers=headers2)
        response = requests.delete(f"{BASE_URL}/api/v1/groups/{group_id}/join", headers=headers2)
        assert response.status_code == 200

    def test_create_group_post(self):
        """测试发布群组动态"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "动态测试"})
        group_id = create_resp.json()["id"]
        response = requests.post(f"{BASE_URL}/api/v1/groups/{group_id}/posts", headers=headers, json={"content": "群组动态"})
        assert response.status_code == 201

    def test_create_announcement(self):
        """测试发布公告"""
        headers = create_test_user()
        create_resp = requests.post(f"{BASE_URL}/api/v1/groups", headers=headers, json={"name": "公告测试"})
        group_id = create_resp.json()["id"]
        response = requests.post(
            f"{BASE_URL}/api/v1/groups/{group_id}/announcements",
            headers=headers,
            json={"title": "测试公告", "content": "公告内容"},
        )
        assert response.status_code == 201
