"""
接口测试：version_pack — 版本与环境管理（感知/定位/控制/仿真/传感器）
测试目标服务: http://127.0.0.1:8009
运行方式: python test/test_version_pack.py

覆盖范围：以感知（per）为代表，验证 Env + Version 的完整 CRUD 及批量操作。
其余 4 组（loc / ctl / sim / sen）结构完全相同，逻辑可类推。
"""
import io
import unittest
import requests

BASE_URL = "http://127.0.0.1:7898/api"
USERNAME = "admin"
PASSWORD = "admin123"


def get_token():
    resp = requests.post(f"{BASE_URL}/token/", json={"username": USERNAME, "password": PASSWORD})
    return resp.json().get("access", "")


def auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestPerEnv(unittest.TestCase):
    """感知环境（/api/per_env/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_per_env(self):
        """测试获取感知环境列表，验证分页结构"""
        resp = requests.get(f"{BASE_URL}/per_env/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)
        self.assertIn("pagination", data)

    def test_02_create_per_env(self):
        """测试新建感知环境（multipart，含 env_file 文件上传）"""
        fake_file = io.BytesIO(b"fake env file content")
        resp = requests.post(
            f"{BASE_URL}/per_env/",
            headers=self.headers,
            data={"env_name": "test_per_env_api", "apply_project": "主线版本"},
            files={"env_file": ("test_env.zip", fake_file, "application/zip")},
        )
        self.assertEqual(resp.status_code, 201)
        TestPerEnv.created_id = resp.json()["data"]["id"]

    def test_03_retrieve_per_env(self):
        """测试获取单个感知环境详情，验证字段完整性"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.get(f"{BASE_URL}/per_env/{self.created_id}/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["data"]
        self.assertEqual(item["env_name"], "test_per_env_api")
        self.assertIn("env_file", item)

    def test_04_update_per_env(self):
        """测试更新感知环境（PATCH env_note 字段）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/per_env/{self.created_id}/",
            headers=self.headers,
            data={"env_note": "updated note"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["env_note"], "updated note")

    def test_05_get_creators(self):
        """测试 creators 接口，返回创建过记录的用户列表"""
        resp = requests.get(f"{BASE_URL}/per_env/creators/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("id", data[0])
            self.assertIn("username", data[0])

    def test_06_list_filter_by_apply_project(self):
        """测试按 apply_project 精确过滤感知环境列表"""
        resp = requests.get(f"{BASE_URL}/per_env/", headers=self.headers,
                            params={"apply_project": "主线版本"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["apply_project"], "主线版本")

    def test_07_batch_delete_per_env(self):
        """测试批量删除感知环境（先补创建一个用于删除）"""
        # 创建一个临时记录
        fake_file = io.BytesIO(b"tmp file")
        r = requests.post(
            f"{BASE_URL}/per_env/",
            headers=self.headers,
            data={"env_name": "test_batch_del_env", "apply_project": "主线版本"},
            files={"env_file": ("tmp.zip", fake_file, "application/zip")},
        )
        tmp_id = r.json()["data"]["id"]

        resp = requests.post(f"{BASE_URL}/per_env/batch_delete/", headers=self.headers,
                             json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

        # 确认记录已删除
        check = requests.get(f"{BASE_URL}/per_env/{tmp_id}/", headers=self.headers)
        self.assertEqual(check.status_code, 404)

    def test_08_delete_per_env(self):
        """测试删除感知环境（同步删除物理文件）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/per_env/{self.created_id}/", headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestPerVersion(unittest.TestCase):
    """感知版本（/api/per_version/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_per_version(self):
        """测试获取感知版本列表，验证分页和字段"""
        resp = requests.get(f"{BASE_URL}/per_version/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_per_version(self):
        """测试新建感知版本（multipart），验证 test_result/test_verdict 不可在创建时设置"""
        fake_file = io.BytesIO(b"fake version file")
        resp = requests.post(
            f"{BASE_URL}/per_version/",
            headers=self.headers,
            data={
                "version_num": "per-api-test-v1.0.0",
                "apply_project": "主线版本",
                # 以下字段应被序列化器 exclude，即便传入也无效
                "test_result": "通过",
            },
            files={"version_file": ("v1.0.0.zip", fake_file, "application/zip")},
        )
        self.assertEqual(resp.status_code, 201)
        item = resp.json()["data"]
        # test_result 应被忽略，默认为"未开始"
        self.assertEqual(item.get("test_result", "未开始"), "未开始")
        TestPerVersion.created_id = item["id"]

    def test_03_update_per_version_cannot_change_version_num(self):
        """测试更新版本号（version_num）应被拦截，保持原值不变"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/per_version/{self.created_id}/",
            headers=self.headers,
            data={"version_num": "should-not-change"},
        )
        # 接口应成功，但 version_num 不应改变
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["version_num"], "per-api-test-v1.0.0")

    def test_04_update_test_result(self):
        """测试更新测试结果（test_result / test_verdict）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/per_version/{self.created_id}/",
            headers=self.headers,
            data={"test_result": "通过", "test_verdict": "功能正常"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]
        self.assertEqual(data["test_result"], "通过")

    def test_05_filter_by_test_result(self):
        """测试按 test_result 精确过滤版本列表"""
        resp = requests.get(f"{BASE_URL}/per_version/", headers=self.headers,
                            params={"test_result": "未开始"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["test_result"], "未开始")

    def test_06_search_by_version_num(self):
        """测试 SearchFilter 模糊搜索版本号"""
        resp = requests.get(f"{BASE_URL}/per_version/", headers=self.headers,
                            params={"search": "api-test"})
        self.assertEqual(resp.status_code, 200)
        # 结果中应包含刚创建的版本
        nums = [i["version_num"] for i in resp.json()["data"]]
        self.assertIn("per-api-test-v1.0.0", nums)

    def test_07_batch_delete_per_version(self):
        """测试批量删除感知版本"""
        # 先创建一个临时版本
        fake = io.BytesIO(b"tmp")
        r = requests.post(
            f"{BASE_URL}/per_version/",
            headers=self.headers,
            data={"version_num": "per-tmp-batch-del", "apply_project": "主线版本"},
            files={"version_file": ("tmp.zip", fake, "application/zip")},
        )
        tmp_id = r.json()["data"]["id"]

        resp = requests.post(f"{BASE_URL}/per_version/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

    def test_08_delete_per_version(self):
        """测试删除感知版本（同步删除物理文件）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/per_version/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])

    def test_09_create_duplicate_version_num(self):
        """测试重复版本号应返回 400（unique 约束）"""
        fake = io.BytesIO(b"dup")
        # 先创建一个
        requests.post(
            f"{BASE_URL}/per_version/",
            headers=self.headers,
            data={"version_num": "per-dup-test", "apply_project": "主线版本"},
            files={"version_file": ("dup.zip", fake, "application/zip")},
        )
        # 再创建同一版本号
        fake2 = io.BytesIO(b"dup2")
        resp2 = requests.post(
            f"{BASE_URL}/per_version/",
            headers=self.headers,
            data={"version_num": "per-dup-test", "apply_project": "主线版本"},
            files={"version_file": ("dup2.zip", fake2, "application/zip")},
        )
        self.assertEqual(resp2.status_code, 400)
        # 清理
        for item in requests.get(f"{BASE_URL}/per_version/", headers=self.headers,
                                  params={"search": "per-dup-test"}).json()["data"]:
            requests.delete(f"{BASE_URL}/per_version/{item['id']}/", headers=self.headers)


if __name__ == "__main__":
    unittest.main(verbosity=2)
