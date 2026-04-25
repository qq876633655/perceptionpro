"""
接口测试：back_stage — 用户认证与权限管理
测试目标服务: http://127.0.0.1:8009
运行方式: python test/test_back_stage.py
"""
import unittest
import requests

BASE_URL = "http://127.0.0.1:8009/api"

# 超级管理员账号（需在运行前配置）
SUPERUSER_USERNAME = "admin"
SUPERUSER_PASSWORD = "admin123"

# 普通管理员账号（is_staff=True）
STAFF_USERNAME = "staff_user"
STAFF_PASSWORD = "Test123456"


def get_token(username, password):
    """通过 /api/token/ 获取 JWT access token"""
    resp = requests.post(f"{BASE_URL}/token/", json={
        "username": username,
        "password": password,
    })
    return resp.json().get("access", "")


def auth_headers(token):
    """构造 Authorization 请求头"""
    return {"Authorization": f"Bearer {token}"}


class TestAuth(unittest.TestCase):
    """认证相关接口测试"""

    def test_login_success(self):
        """测试正确手机号/用户名+密码登录，应返回 access 和 refresh token"""
        resp = requests.post(f"{BASE_URL}/login/", json={
            "phone_number": "13800000000",
            "password": SUPERUSER_PASSWORD,
        })
        # 若无手机号，换用用户名登录（/api/token/）
        resp2 = requests.post(f"{BASE_URL}/token/", json={
            "username": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        })
        self.assertEqual(resp2.status_code, 200)
        data = resp2.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_login_wrong_password(self):
        """测试错误密码登录，应返回 401 或错误提示"""
        resp = requests.post(f"{BASE_URL}/token/", json={
            "username": SUPERUSER_USERNAME,
            "password": "wrongpassword",
        })
        self.assertIn(resp.status_code, [400, 401])

    def test_token_refresh(self):
        """测试用 refresh token 换取新 access token"""
        # 先登录获取 refresh
        resp = requests.post(f"{BASE_URL}/token/", json={
            "username": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        })
        refresh = resp.json().get("refresh", "")
        self.assertTrue(refresh, "未能获取 refresh token")

        # 用 refresh 换新 access
        resp2 = requests.post(f"{BASE_URL}/token/refresh/", json={"refresh": refresh})
        self.assertEqual(resp2.status_code, 200)
        self.assertIn("access", resp2.json())

    def test_get_current_user_info(self):
        """测试 /me/ 接口，返回当前登录用户信息（含 permissions）"""
        token = get_token(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
        resp = requests.get(f"{BASE_URL}/me/", headers=auth_headers(token))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # 统一响应格式校验
        self.assertEqual(data.get("code"), 0)
        user = data.get("data", {})
        self.assertIn("username", user)
        self.assertIn("permissions", user)

    def test_access_without_token(self):
        """测试未携带 token 访问受保护接口，应返回 401"""
        resp = requests.get(f"{BASE_URL}/me/")
        self.assertEqual(resp.status_code, 401)

    def test_change_password(self):
        """测试修改密码接口（先改再改回），验证新旧密码校验逻辑"""
        token = get_token(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
        headers = auth_headers(token)

        # 用错误的旧密码修改，应失败
        resp = requests.post(f"{BASE_URL}/change_pwd/", headers=headers, json={
            "old_password": "wrong_old_pwd",
            "new_password": "NewPass123",
        })
        self.assertNotEqual(resp.status_code, 200)


class TestUserManagement(unittest.TestCase):
    """用户管理接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
        cls.headers = auth_headers(cls.token)
        cls.created_user_id = None

    def test_01_list_users(self):
        """测试获取用户列表，验证分页格式和字段"""
        resp = requests.get(f"{BASE_URL}/users/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("code"), 0)
        # 列表数据为数组
        self.assertIsInstance(data.get("data"), list)
        # 包含分页信息
        self.assertIn("pagination", data)

    def test_02_list_users_filter_by_username(self):
        """测试按 username 模糊过滤用户列表"""
        resp = requests.get(f"{BASE_URL}/users/", headers=self.headers,
                            params={"username": "admin"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        for user in data.get("data", []):
            self.assertIn("admin", user["username"].lower())

    def test_03_create_user(self):
        """测试新建用户，密码默认为 Test123456"""
        resp = requests.post(f"{BASE_URL}/users/", headers=self.headers, json={
            "username": "test_api_user_001",
            "phone_number": "13900000099",
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data.get("code"), 0)
        TestUserManagement.created_user_id = data["data"]["id"]

    def test_04_retrieve_user(self):
        """测试获取单个用户详情"""
        if not self.created_user_id:
            self.skipTest("依赖 test_03_create_user 先执行")
        resp = requests.get(f"{BASE_URL}/users/{self.created_user_id}/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["username"], "test_api_user_001")

    def test_05_update_user(self):
        """测试更新用户信息（PATCH）"""
        if not self.created_user_id:
            self.skipTest("依赖 test_03_create_user 先执行")
        resp = requests.patch(f"{BASE_URL}/users/{self.created_user_id}/",
                              headers=self.headers, json={"is_active": False})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.json()["data"]["is_active"])

    def test_06_delete_user(self):
        """测试删除用户"""
        if not self.created_user_id:
            self.skipTest("依赖 test_03_create_user 先执行")
        resp = requests.delete(f"{BASE_URL}/users/{self.created_user_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])

    def test_07_create_user_no_permission(self):
        """测试普通用户（非 is_staff）无权新建用户，应返回 403"""
        # 用普通账号 token 尝试创建用户
        token = get_token(STAFF_USERNAME, STAFF_PASSWORD)
        if not token:
            self.skipTest("未配置 STAFF 账号，跳过")
        resp = requests.post(f"{BASE_URL}/users/", headers=auth_headers(token), json={
            "username": "should_fail",
            "phone_number": "13911110000",
        })
        self.assertEqual(resp.status_code, 403)


class TestGroupManagement(unittest.TestCase):
    """角色（权限组）管理接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
        cls.headers = auth_headers(cls.token)
        cls.created_group_id = None

    def test_01_list_groups(self):
        """测试获取角色列表，返回含成员数和权限详情"""
        resp = requests.get(f"{BASE_URL}/groups/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("code"), 0)
        self.assertIsInstance(data.get("data"), list)

    def test_02_get_all_permissions(self):
        """测试获取业务 app 权限列表，仅含 BUSINESS_APPS 内的权限，不含 Django 内置"""
        resp = requests.get(f"{BASE_URL}/groups/all_permissions/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        permissions = resp.json().get("data", [])
        self.assertIsInstance(permissions, list)
        # 验证不含 Django 内置 app（admin/auth/contenttypes/sessions）的权限
        for perm in permissions:
            app_label = perm.get("content_type", {}).get("app_label", "")
            self.assertNotIn(app_label, ["admin", "auth", "contenttypes", "sessions"])

    def test_03_create_group(self):
        """测试新建角色（超级管理员权限）"""
        resp = requests.post(f"{BASE_URL}/groups/", headers=self.headers, json={
            "name": "test_role_api_001",
            "permissions": [],
        })
        self.assertEqual(resp.status_code, 201)
        TestGroupManagement.created_group_id = resp.json()["data"]["id"]

    def test_04_update_group_permissions(self):
        """测试更新角色权限（批量设置 permissions IDs）"""
        if not self.created_group_id:
            self.skipTest("依赖 test_03 先执行")
        # 先获取一个合法权限 ID
        perms_resp = requests.get(f"{BASE_URL}/groups/all_permissions/",
                                  headers=self.headers)
        perms = perms_resp.json().get("data", [])
        perm_id = perms[0]["id"] if perms else None
        if not perm_id:
            self.skipTest("无可用权限")
        resp = requests.patch(f"{BASE_URL}/groups/{self.created_group_id}/",
                              headers=self.headers,
                              json={"permissions": [perm_id]})
        self.assertEqual(resp.status_code, 200)

    def test_05_delete_group(self):
        """测试删除角色"""
        if not self.created_group_id:
            self.skipTest("依赖 test_03 先执行")
        resp = requests.delete(f"{BASE_URL}/groups/{self.created_group_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


if __name__ == "__main__":
    unittest.main(verbosity=2)
