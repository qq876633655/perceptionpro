"""
接口测试：data_manage — 仿真数据管理
测试目标服务: http://127.0.0.1:8009
运行方式: python test/test_data_manage.py

覆盖范围：
  - SimProjectProperty（仿真项目数据）：CRUD + 批量删除 + 创建人列表
  - SimCommonProperty（仿真通用数据）：CRUD + 批量删除 + 创建人列表
"""
import io
import unittest
import requests

BASE_URL = "http://127.0.0.1:8009/api"
USERNAME = "admin"
PASSWORD = "admin123"


def get_token():
    resp = requests.post(f"{BASE_URL}/token/", json={"username": USERNAME, "password": PASSWORD})
    return resp.json().get("access", "")


def auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestSimProjectProperty(unittest.TestCase):
    """仿真项目数据（/api/sim_project_property/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_sim_project_property(self):
        """测试获取仿真项目数据列表，验证分页和统一响应格式"""
        resp = requests.get(f"{BASE_URL}/sim_project_property/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)
        self.assertIn("pagination", data)

    def test_02_create_sim_project_property(self):
        """测试新建仿真项目数据（multipart，含文件上传）"""
        fake_file = io.BytesIO(b"fake project property content")
        resp = requests.post(
            f"{BASE_URL}/sim_project_property/",
            headers=self.headers,
            data={
                "apply_project": "api_test_project",
                "property_tag": "api_tag",
                "property_desc": "测试创建",
            },
            files={"project_property": ("test_prop.zip", fake_file, "application/zip")},
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        self.assertEqual(data["apply_project"], "api_test_project")
        # uid 字段应自动生成
        self.assertIn("uid", data)
        TestSimProjectProperty.created_id = data["id"]

    def test_03_retrieve_sim_project_property(self):
        """测试获取单条仿真项目数据详情"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.get(f"{BASE_URL}/sim_project_property/{self.created_id}/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["id"], self.created_id)

    def test_04_update_sim_project_property(self):
        """测试更新仿真项目数据（PATCH property_desc）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/sim_project_property/{self.created_id}/",
            headers=self.headers,
            data={"property_desc": "updated description"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["property_desc"], "updated description")

    def test_05_filter_by_apply_project(self):
        """测试按 apply_project 模糊过滤项目数据列表"""
        resp = requests.get(f"{BASE_URL}/sim_project_property/", headers=self.headers,
                            params={"apply_project": "api_test"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertIn("api_test", item["apply_project"])

    def test_06_filter_by_property_tag(self):
        """测试按 property_tag 模糊过滤"""
        resp = requests.get(f"{BASE_URL}/sim_project_property/", headers=self.headers,
                            params={"property_tag": "api_tag"})
        self.assertEqual(resp.status_code, 200)

    def test_07_get_creators(self):
        """测试 creators 接口，返回 [{id, username}] 格式"""
        resp = requests.get(f"{BASE_URL}/sim_project_property/creators/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertIsInstance(data, list)

    def test_08_batch_delete(self):
        """测试批量删除仿真项目数据（新建临时记录后删除）"""
        fake = io.BytesIO(b"tmp")
        r = requests.post(
            f"{BASE_URL}/sim_project_property/",
            headers=self.headers,
            data={"apply_project": "batch_del_test"},
            files={"project_property": ("tmp.zip", fake, "application/zip")},
        )
        tmp_id = r.json()["data"]["id"]

        resp = requests.post(f"{BASE_URL}/sim_project_property/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

        # 确认已删除
        check = requests.get(f"{BASE_URL}/sim_project_property/{tmp_id}/",
                             headers=self.headers)
        self.assertEqual(check.status_code, 404)

    def test_09_delete_sim_project_property(self):
        """测试删除记录，同时应清理物理文件（pre_save / post_delete 信号）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/sim_project_property/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestSimCommonProperty(unittest.TestCase):
    """仿真通用数据（/api/sim_common_property/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_sim_common_property(self):
        """测试获取仿真通用数据列表，验证分页格式"""
        resp = requests.get(f"{BASE_URL}/sim_common_property/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_sim_common_property(self):
        """测试新建仿真通用数据（versions 字段唯一约束）"""
        fake = io.BytesIO(b"common property file")
        resp = requests.post(
            f"{BASE_URL}/sim_common_property/",
            headers=self.headers,
            data={
                "versions": "sim_common_api_v1",
                "property_tag": "tag_api",
            },
            files={"common_property": ("common.zip", fake, "application/zip")},
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        self.assertEqual(data["versions"], "sim_common_api_v1")
        TestSimCommonProperty.created_id = data["id"]

    def test_03_create_duplicate_versions_should_fail(self):
        """测试 versions 字段唯一约束：重复创建应返回 400"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        fake = io.BytesIO(b"dup")
        resp = requests.post(
            f"{BASE_URL}/sim_common_property/",
            headers=self.headers,
            data={"versions": "sim_common_api_v1"},
            files={"common_property": ("dup.zip", fake, "application/zip")},
        )
        self.assertEqual(resp.status_code, 400)

    def test_04_update_sim_common_property(self):
        """测试更新仿真通用数据（property_desc）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/sim_common_property/{self.created_id}/",
            headers=self.headers,
            data={"property_desc": "updated common desc"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["property_desc"], "updated common desc")

    def test_05_search_by_versions(self):
        """测试 SearchFilter 按 versions 字段搜索"""
        resp = requests.get(f"{BASE_URL}/sim_common_property/", headers=self.headers,
                            params={"search": "sim_common_api"})
        self.assertEqual(resp.status_code, 200)
        nums = [i["versions"] for i in resp.json()["data"]]
        self.assertIn("sim_common_api_v1", nums)

    def test_06_get_creators(self):
        """测试 creators 接口"""
        resp = requests.get(f"{BASE_URL}/sim_common_property/creators/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json()["data"], list)

    def test_07_batch_delete(self):
        """测试批量删除仿真通用数据"""
        fake = io.BytesIO(b"tmp")
        r = requests.post(
            f"{BASE_URL}/sim_common_property/",
            headers=self.headers,
            data={"versions": "sim_common_batch_del_tmp"},
            files={"common_property": ("tmp.zip", fake, "application/zip")},
        )
        tmp_id = r.json()["data"]["id"]

        resp = requests.post(f"{BASE_URL}/sim_common_property/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

    def test_08_delete_sim_common_property(self):
        """测试删除单条仿真通用数据"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/sim_common_property/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


if __name__ == "__main__":
    unittest.main(verbosity=2)
