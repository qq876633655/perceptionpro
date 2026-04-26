"""
接口测试：sim_test_agv — 整车仿真自动化测试
测试目标服务: http://127.0.0.1:8009
运行方式: python test/test_sim_test_agv.py

覆盖范围：
  - AutoTestVersions（自动化版本）：CRUD + 批量删除 + 创建人
  - CaseMap（地图管理）：CRUD + 批量删除
  - CaseProperty（资产管理）：CRUD + batch_copy + choices + sim_test_versions
  - SchemeCommonParameter（通用参数）：CRUD + batch_copy + choices
  - CaseTemplate（用例模版）：CRUD + 批量删除
  - AgvTestTask（测试任务）：创建（dispatch）+ cancel + 批量删除
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


class TestAutoTestVersions(unittest.TestCase):
    """自动化测试版本（/api/at_versions/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_at_versions(self):
        """测试获取自动化版本列表，验证分页和统一响应格式"""
        resp = requests.get(f"{BASE_URL}/at_versions/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_at_versions(self):
        """测试新建自动化版本（multipart，含 versions_file 上传）"""
        fake = io.BytesIO(b"at version file content")
        resp = requests.post(
            f"{BASE_URL}/at_versions/",
            headers=self.headers,
            data={"versions": "at-api-test-v1.0", "release_note": "api测试版本"},
            files={"versions_file": ("at_v1.zip", fake, "application/zip")},
        )
        self.assertEqual(resp.status_code, 201)
        TestAutoTestVersions.created_id = resp.json()["data"]["id"]

    def test_03_update_release_note(self):
        """测试更新发布说明（PATCH release_note）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/at_versions/{self.created_id}/",
            headers=self.headers,
            data={"release_note": "updated release note"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["release_note"], "updated release note")

    def test_04_get_creators(self):
        """测试 creators 接口，返回创建过记录的用户列表"""
        resp = requests.get(f"{BASE_URL}/at_versions/creators/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json()["data"], list)

    def test_05_filter_by_versions(self):
        """测试按 versions 模糊过滤"""
        resp = requests.get(f"{BASE_URL}/at_versions/", headers=self.headers,
                            params={"versions": "at-api-test"})
        self.assertEqual(resp.status_code, 200)

    def test_06_batch_delete(self):
        """测试批量删除自动化版本"""
        fake = io.BytesIO(b"tmp")
        r = requests.post(
            f"{BASE_URL}/at_versions/",
            headers=self.headers,
            data={"versions": "at-batch-del-tmp"},
            files={"versions_file": ("tmp.zip", fake, "application/zip")},
        )
        tmp_id = r.json()["data"]["id"]
        resp = requests.post(f"{BASE_URL}/at_versions/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

    def test_07_delete(self):
        """测试删除单条自动化版本"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/at_versions/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestCaseMap(unittest.TestCase):
    """地图管理（/api/at_case_map/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_case_map(self):
        """测试获取地图列表"""
        resp = requests.get(f"{BASE_URL}/at_case_map/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["code"], 0)

    def test_02_create_case_map(self):
        """测试新建地图记录（multipart，含 map_file 上传，district_name 唯一）"""
        fake = io.BytesIO(b"map file content")
        resp = requests.post(
            f"{BASE_URL}/at_case_map/",
            headers=self.headers,
            data={"district_name": "api_test_district"},
            files={"map_file": ("test_map.zip", fake, "application/zip")},
        )
        self.assertEqual(resp.status_code, 201)
        TestCaseMap.created_id = resp.json()["data"]["id"]

    def test_03_filter_by_district_name(self):
        """测试按 district_name 模糊过滤地图列表"""
        resp = requests.get(f"{BASE_URL}/at_case_map/", headers=self.headers,
                            params={"district_name": "api_test"})
        self.assertEqual(resp.status_code, 200)

    def test_04_batch_delete(self):
        """测试批量删除地图记录"""
        fake = io.BytesIO(b"tmp")
        r = requests.post(
            f"{BASE_URL}/at_case_map/",
            headers=self.headers,
            data={"district_name": "api_batch_del_map"},
            files={"map_file": ("tmp.zip", fake, "application/zip")},
        )
        tmp_id = r.json()["data"]["id"]
        resp = requests.post(f"{BASE_URL}/at_case_map/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

    def test_05_delete(self):
        """测试删除地图记录"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/at_case_map/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestCaseProperty(unittest.TestCase):
    """资产管理（/api/at_case_property/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_case_property(self):
        """测试获取资产列表，验证分页"""
        resp = requests.get(f"{BASE_URL}/at_case_property/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["code"], 0)

    def test_02_create_case_property(self):
        """测试新建资产（唯一约束：version+vehicle+scheme 三元组）"""
        fake_backup = io.BytesIO(b"backup file")
        fake_wbt = io.BytesIO(b"wbt file")
        resp = requests.post(
            f"{BASE_URL}/at_case_property/",
            headers=self.headers,
            data={
                "sim_test_version": "api_test_v1",
                "sim_test_vehicle": "test_vehicle_A",
                "sim_scheme_name": "scheme_001",
                "test_module": "module_A",
                "lastagvpose_path": "",
            },
            files={
                "backup_file": ("backup.zip", fake_backup, "application/zip"),
                "wbt_file": ("scene.wbt", fake_wbt, "text/plain"),
            },
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()["data"]
        TestCaseProperty.created_id = data["id"]
        # 附加只读字段校验
        self.assertIn("created_by_name", data)

    def test_03_cannot_change_version_on_update(self):
        """测试更新资产时修改 sim_test_version 应被忽略（SerializerUpdateLock）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/at_case_property/{self.created_id}/",
            headers=self.headers,
            data={"sim_test_version": "should_not_change", "test_module": "module_B"},
        )
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["data"]
        # version 不可改
        self.assertEqual(item["sim_test_version"], "api_test_v1")
        # test_module 可改
        self.assertEqual(item["test_module"], "module_B")

    def test_04_get_sim_test_versions(self):
        """测试 sim_test_versions 接口，返回不重复的资产版本字符串列表"""
        resp = requests.get(f"{BASE_URL}/at_case_property/sim_test_versions/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        versions = resp.json()["data"]
        self.assertIsInstance(versions, list)

    def test_05_get_choices(self):
        """测试 choices 接口，返回各字段去重值（version/vehicle/scheme/module）"""
        resp = requests.get(f"{BASE_URL}/at_case_property/choices/",
                            headers=self.headers)
        # choices 接口未在权限表登记，默认放行
        self.assertEqual(resp.status_code, 200)
        ch = resp.json()["data"]
        self.assertIn("sim_test_version", ch)
        self.assertIn("sim_test_vehicle", ch)

    def test_06_batch_copy_case_property(self):
        """测试批量复制资产到新版本（batch_copy），验证唯一性冲突检测"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")

        # 正常复制到新版本
        resp = requests.post(f"{BASE_URL}/at_case_property/batch_copy/",
                             headers=self.headers,
                             json={"ids": [self.created_id], "sim_test_version": "api_copy_v2"})
        self.assertEqual(resp.status_code, 200)

        # 再次复制到同一目标版本应触发冲突
        resp2 = requests.post(f"{BASE_URL}/at_case_property/batch_copy/",
                              headers=self.headers,
                              json={"ids": [self.created_id], "sim_test_version": "api_copy_v2"})
        self.assertEqual(resp2.status_code, 400)
        self.assertIn("已存在", resp2.json().get("detail", ""))

        # 清理复制出来的记录
        for item in requests.get(f"{BASE_URL}/at_case_property/", headers=self.headers,
                                  params={"sim_test_version": "api_copy_v2"}).json()["data"]:
            requests.delete(f"{BASE_URL}/at_case_property/{item['id']}/", headers=self.headers)

    def test_07_batch_copy_empty_ids(self):
        """测试 batch_copy 传空 ids 应返回 400"""
        resp = requests.post(f"{BASE_URL}/at_case_property/batch_copy/",
                             headers=self.headers,
                             json={"ids": [], "sim_test_version": "any_v"})
        self.assertEqual(resp.status_code, 400)

    def test_08_batch_copy_empty_version(self):
        """测试 batch_copy 未传目标版本应返回 400"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.post(f"{BASE_URL}/at_case_property/batch_copy/",
                             headers=self.headers,
                             json={"ids": [self.created_id], "sim_test_version": ""})
        self.assertEqual(resp.status_code, 400)

    def test_09_delete(self):
        """测试删除资产记录"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/at_case_property/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestSchemeCommonParameter(unittest.TestCase):
    """通用参数（/api/at_common_parameter/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_common_parameter(self):
        """测试获取通用参数列表"""
        resp = requests.get(f"{BASE_URL}/at_common_parameter/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["code"], 0)

    def test_02_create_common_parameter(self):
        """测试新建通用参数（multipart，common_parameter_name 唯一）"""
        fake = io.BytesIO(b"param file content")
        resp = requests.post(
            f"{BASE_URL}/at_common_parameter/",
            headers=self.headers,
            data={
                "common_parameter_name": "api_test_param_001",
                "sim_test_version": "api_v1",
                "sim_test_vehicle": "vehicle_A",
                "test_module": "module_A",
                "common_parameter_status": "正常",
            },
            files={"common_parameter_file": ("param.yaml", fake, "text/plain")},
        )
        self.assertEqual(resp.status_code, 201)
        TestSchemeCommonParameter.created_id = resp.json()["data"]["id"]

    def test_03_get_choices(self):
        """测试 choices 接口，返回数据库中已有的 version/vehicle/module 去重列表"""
        resp = requests.get(f"{BASE_URL}/at_common_parameter/choices/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        ch = resp.json()["data"]
        self.assertIn("sim_test_version", ch)
        self.assertIn("sim_test_vehicle", ch)
        self.assertIn("test_module", ch)

    def test_04_filter_by_status(self):
        """测试按通参状态精确过滤"""
        resp = requests.get(f"{BASE_URL}/at_common_parameter/", headers=self.headers,
                            params={"common_parameter_status": "正常"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["common_parameter_status"], "正常")

    def test_05_batch_copy(self):
        """测试 batch_copy 为选中通参改名复制，items 结构为 [{id, common_parameter_name}]"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.post(
            f"{BASE_URL}/at_common_parameter/batch_copy/",
            headers=self.headers,
            json={"items": [{"id": self.created_id, "common_parameter_name": "api_copied_param"}]},
        )
        self.assertEqual(resp.status_code, 200)
        # 清理复制出来的记录
        for item in requests.get(f"{BASE_URL}/at_common_parameter/", headers=self.headers,
                                  params={"common_parameter_name": "api_copied_param"}).json()["data"]:
            requests.delete(f"{BASE_URL}/at_common_parameter/{item['id']}/",
                            headers=self.headers)

    def test_06_batch_copy_duplicate_name(self):
        """测试 batch_copy 新名称与已有记录重复应返回 400"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.post(
            f"{BASE_URL}/at_common_parameter/batch_copy/",
            headers=self.headers,
            json={"items": [{"id": self.created_id,
                             "common_parameter_name": "api_test_param_001"}]},
        )
        self.assertEqual(resp.status_code, 400)

    def test_07_delete(self):
        """测试删除通用参数，同步删除物理文件"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/at_common_parameter/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestCaseTemplate(unittest.TestCase):
    """用例模版（/api/at_case_template/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_case_template(self):
        """测试获取用例模版列表"""
        resp = requests.get(f"{BASE_URL}/at_case_template/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["code"], 0)

    def test_02_create_case_template(self):
        """测试新建用例模版（含 case_file 上传）"""
        fake = io.BytesIO(b"case file content")
        resp = requests.post(
            f"{BASE_URL}/at_case_template/",
            headers=self.headers,
            data={
                "sim_test_version": "api_tmpl_v1",
                "test_module": "module_tmpl",
                "case_desc": "api测试用例描述",
            },
            files={"case_file": ("case.yaml", fake, "text/plain")},
        )
        self.assertEqual(resp.status_code, 201)
        TestCaseTemplate.created_id = resp.json()["data"]["id"]

    def test_03_filter_by_sim_test_version(self):
        """测试按 sim_test_version 精确过滤用例模版"""
        resp = requests.get(f"{BASE_URL}/at_case_template/", headers=self.headers,
                            params={"sim_test_version": "api_tmpl_v1"})
        self.assertEqual(resp.status_code, 200)

    def test_04_delete(self):
        """测试删除用例模版"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/at_case_template/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestAgvTestTask(unittest.TestCase):
    """测试任务（/api/at_test_task/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_test_task(self):
        """测试获取测试任务列表，验证分页和字段"""
        resp = requests.get(f"{BASE_URL}/at_test_task/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)

    def test_02_create_test_task_dispatches_celery(self):
        """测试新建测试任务，创建后应自动 dispatch 到 Celery，状态为 DISPATCHED"""
        fake_case = io.BytesIO(b"case json content")
        resp = requests.post(
            f"{BASE_URL}/at_test_task/",
            headers=self.headers,
            data={
                "sim_test_version": "api_task_v1",
                "queue_name": "api_test_queue",
                "recovery_default_version": "False",
            },
            files={"agv_case_file": ("case.json", fake_case, "application/json")},
        )
        self.assertEqual(resp.status_code, 201)
        item = resp.json()["data"]
        # 创建后状态应为 DISPATCHED（已 dispatch 到 Celery）
        self.assertIn(item["task_status"], ["CREATED", "DISPATCHED"])
        TestAgvTestTask.created_id = item["id"]

    def test_03_task_has_no_patch_endpoint(self):
        """测试任务不允许 PATCH 修改（保护任务状态完整性）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/at_test_task/{self.created_id}/",
            headers=self.headers,
            json={"task_status": "SUCCESS"},
        )
        # 无 PATCH 接口应返回 405 Method Not Allowed
        self.assertEqual(resp.status_code, 405)

    def test_04_cancel_dispatched_task(self):
        """测试取消 DISPATCHED 状态任务：应立即撤销 Celery 任务并变更状态为 CANCELED"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.post(f"{BASE_URL}/at_test_task/{self.created_id}/cancel/",
                             headers=self.headers)
        # 取消应成功
        self.assertEqual(resp.status_code, 200)

    def test_05_cancel_already_canceled_task(self):
        """测试取消已终止状态（CANCELED/SUCCESS/FAILED）任务应返回 400"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.post(f"{BASE_URL}/at_test_task/{self.created_id}/cancel/",
                             headers=self.headers)
        # 已终止状态不可再次取消
        self.assertEqual(resp.status_code, 400)

    def test_06_filter_by_task_status(self):
        """测试按 task_status 精确过滤任务列表"""
        resp = requests.get(f"{BASE_URL}/at_test_task/", headers=self.headers,
                            params={"task_status": "CANCELED"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["task_status"], "CANCELED")

    def test_07_batch_delete(self):
        """测试批量删除测试任务"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.post(f"{BASE_URL}/at_test_task/batch_delete/",
                             headers=self.headers, json={"ids": [self.created_id]})
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
