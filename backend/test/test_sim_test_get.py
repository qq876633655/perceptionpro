"""
接口测试：sim_test_get — 感知取货测试
测试目标服务: http://127.0.0.1:8009
运行方式: python test/test_sim_test_get.py

覆盖范围：
  - GetTestTarget（物体数据）：CRUD + 批量删除 + 创建人 + node_params JSON 校验
  - AgvBody（车体数据）：CRUD + 批量删除 + 创建人
  - GetTestCommonParameter（测试通参）：CRUD + 批量删除 + 创建人 + choices
"""
import io
import json
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


class TestGetTestTarget(unittest.TestCase):
    """物体数据（/api/gt_test_target/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.headers_json = {**auth(cls.token), "Content-Type": "application/json"}
        cls.created_id = None

    def test_01_list_get_test_target(self):
        """测试获取物体数据列表，验证分页和统一响应格式"""
        resp = requests.get(f"{BASE_URL}/gt_test_target/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIsInstance(data["data"], list)
        self.assertIn("pagination", data)

    def test_02_create_get_test_target(self):
        """测试新建物体数据（JSON body，包含 node_params JSONField）"""
        payload = {
            "target_name": "api_test_pallet_001",
            "target_type": "pallet",
            "texture": "plastic",
            "color": "white",
            "length": 1.2,
            "width": 0.8,
            "height": 0.15,
            "model_name": "pallet_model_api",
            "extern_proto_path": "protos/PalletApi.proto",
            "node_params": {"key1": "value1", "size": 3},
            # 卡板参数（有默认值）
            "pallet": "100,100,100",
            "hole": "80,80",
            "pallet_height": 0.12,
        }
        resp = requests.post(f"{BASE_URL}/gt_test_target/", headers=self.headers_json,
                             data=json.dumps(payload))
        self.assertEqual(resp.status_code, 201)
        item = resp.json()["data"]
        self.assertEqual(item["target_name"], "api_test_pallet_001")
        # node_params 应以 dict 形式存储
        self.assertIsInstance(item["node_params"], dict)
        TestGetTestTarget.created_id = item["id"]

    def test_03_retrieve_get_test_target(self):
        """测试获取单条物体数据详情，验证所有字段存在"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.get(f"{BASE_URL}/gt_test_target/{self.created_id}/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["data"]
        for field in ["target_name", "target_type", "texture", "color",
                      "length", "width", "height", "model_name", "node_params",
                      "created_by_name", "updated_by_name"]:
            self.assertIn(field, item, f"缺少字段: {field}")

    def test_04_update_get_test_target(self):
        """测试更新物体数据（PATCH），修改 texture 和 node_params"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/gt_test_target/{self.created_id}/",
            headers=self.headers_json,
            data=json.dumps({"texture": "metal", "node_params": {"updated": True}}),
        )
        self.assertEqual(resp.status_code, 200)
        item = resp.json()["data"]
        self.assertEqual(item["texture"], "metal")
        self.assertEqual(item["node_params"], {"updated": True})

    def test_05_duplicate_target_name_should_fail(self):
        """测试重复 target_name（unique 约束）应返回 400"""
        payload = {
            "target_name": "api_test_pallet_001",  # 与 test_02 重名
            "target_type": "pallet",
            "texture": "metal",
            "color": "black",
            "length": 1.0,
            "width": 0.8,
            "height": 0.1,
            "model_name": "dup_model",
            "extern_proto_path": "protos/Dup.proto",
            "node_params": {},
        }
        resp = requests.post(f"{BASE_URL}/gt_test_target/", headers=self.headers_json,
                             data=json.dumps(payload))
        self.assertEqual(resp.status_code, 400)

    def test_06_filter_by_target_type(self):
        """测试按 target_type 精确过滤（pallet/cage）"""
        resp = requests.get(f"{BASE_URL}/gt_test_target/", headers=self.headers,
                            params={"target_type": "pallet"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["target_type"], "pallet")

    def test_07_filter_by_target_name_icontains(self):
        """测试 target_name 模糊过滤"""
        resp = requests.get(f"{BASE_URL}/gt_test_target/", headers=self.headers,
                            params={"target_name": "api_test"})
        self.assertEqual(resp.status_code, 200)

    def test_08_get_creators(self):
        """测试 creators 接口，返回 [{id, username}]"""
        resp = requests.get(f"{BASE_URL}/gt_test_target/creators/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json()["data"], list)

    def test_09_batch_delete(self):
        """测试批量删除物体数据"""
        payload = {
            "target_name": "api_batch_del_target",
            "target_type": "cage",
            "texture": "wood",
            "color": "yellow",
            "length": 1.0, "width": 0.6, "height": 0.2,
            "model_name": "cage_del", "extern_proto_path": "protos/Cage.proto",
            "node_params": {},
        }
        r = requests.post(f"{BASE_URL}/gt_test_target/", headers=self.headers_json,
                          data=json.dumps(payload))
        tmp_id = r.json()["data"]["id"]

        resp = requests.post(f"{BASE_URL}/gt_test_target/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

        check = requests.get(f"{BASE_URL}/gt_test_target/{tmp_id}/", headers=self.headers)
        self.assertEqual(check.status_code, 404)

    def test_10_delete_get_test_target(self):
        """测试删除物体数据"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/gt_test_target/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestAgvBody(unittest.TestCase):
    """车体数据（/api/gt_agv_body/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.headers_json = {**auth(cls.token), "Content-Type": "application/json"}
        cls.created_id = None

    def _body_payload(self, agv_type="api_test_vehicle_X1"):
        return {
            "agv_type": agv_type,
            "left_width": 0.35,
            "right_width": 0.35,
            "front_length": 1.2,
            "back_length": 0.6,
            "fork_length": 1.0,
            "fork_inner_width": 0.28,
            "fork_width": 0.1,
            "fork_thickness": 0.04,
            "load_position_x": 0.5,
            "sensor_extrinsic": "[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]",
            "agv_node": "<agv_node>test</agv_node>",
        }

    def test_01_list_agv_body(self):
        """测试获取车体数据列表"""
        resp = requests.get(f"{BASE_URL}/gt_agv_body/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["code"], 0)

    def test_02_create_agv_body(self):
        """测试新建车体数据（JSON body，agv_type 唯一约束）"""
        resp = requests.post(f"{BASE_URL}/gt_agv_body/", headers=self.headers_json,
                             data=json.dumps(self._body_payload()))
        self.assertEqual(resp.status_code, 201)
        TestAgvBody.created_id = resp.json()["data"]["id"]

    def test_03_duplicate_agv_type_should_fail(self):
        """测试重复 agv_type 应返回 400（unique 约束）"""
        resp = requests.post(f"{BASE_URL}/gt_agv_body/", headers=self.headers_json,
                             data=json.dumps(self._body_payload("api_test_vehicle_X1")))
        self.assertEqual(resp.status_code, 400)

    def test_04_update_agv_body(self):
        """测试更新车体数据（PATCH），修改 fork_length"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.patch(
            f"{BASE_URL}/gt_agv_body/{self.created_id}/",
            headers=self.headers_json,
            data=json.dumps({"fork_length": 1.1}),
        )
        self.assertEqual(resp.status_code, 200)
        self.assertAlmostEqual(resp.json()["data"]["fork_length"], 1.1)

    def test_05_filter_by_agv_type(self):
        """测试按 agv_type 模糊过滤车体数据列表"""
        resp = requests.get(f"{BASE_URL}/gt_agv_body/", headers=self.headers,
                            params={"agv_type": "api_test_vehicle"})
        self.assertEqual(resp.status_code, 200)

    def test_06_get_creators(self):
        """测试 creators 接口"""
        resp = requests.get(f"{BASE_URL}/gt_agv_body/creators/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json()["data"], list)

    def test_07_batch_delete(self):
        """测试批量删除车体数据"""
        r = requests.post(f"{BASE_URL}/gt_agv_body/", headers=self.headers_json,
                          data=json.dumps(self._body_payload("api_batch_del_vehicle")))
        tmp_id = r.json()["data"]["id"]
        resp = requests.post(f"{BASE_URL}/gt_agv_body/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

    def test_08_delete_agv_body(self):
        """测试删除车体数据"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/gt_agv_body/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


class TestGetTestCommonParameter(unittest.TestCase):
    """测试通参（/api/gt_common_param/）接口测试"""

    @classmethod
    def setUpClass(cls):
        cls.token = get_token()
        cls.headers = auth(cls.token)
        cls.created_id = None

    def test_01_list_common_param(self):
        """测试获取测试通参列表"""
        resp = requests.get(f"{BASE_URL}/gt_common_param/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["code"], 0)

    def test_02_create_common_param(self):
        """测试新建测试通参（multipart，含文件上传），验证 uid 自动生成"""
        fake = io.BytesIO(b"common parameter file content")
        resp = requests.post(
            f"{BASE_URL}/gt_common_param/",
            headers=self.headers,
            data={
                "common_parameter_name": "gt_api_param_001",
                "sim_test_version": "gt_v1",
                "sim_test_vehicle": "vehicle_A",
                "parameter_desc": "api测试通参",
            },
            files={"common_parameter_file": ("param.yaml", fake, "text/plain")},
        )
        self.assertEqual(resp.status_code, 201)
        item = resp.json()["data"]
        self.assertEqual(item["common_parameter_name"], "gt_api_param_001")
        # uid 应自动生成
        self.assertIn("uid", item)
        self.assertTrue(item["uid"])
        # 文件路径应包含 uid
        self.assertIn(item["uid"], item["common_parameter_file"])
        TestGetTestCommonParameter.created_id = item["id"]

    def test_03_retrieve_common_param(self):
        """测试获取单条通参详情，验证 created_by_name 字段"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.get(f"{BASE_URL}/gt_common_param/{self.created_id}/",
                            headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("created_by_name", resp.json()["data"])

    def test_04_update_common_param_replace_file(self):
        """测试更新通参并替换文件（pre_save 信号应删除旧文件）"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        new_file = io.BytesIO(b"new param content")
        resp = requests.patch(
            f"{BASE_URL}/gt_common_param/{self.created_id}/",
            headers=self.headers,
            data={"parameter_desc": "updated desc"},
            files={"common_parameter_file": ("new_param.yaml", new_file, "text/plain")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["data"]["parameter_desc"], "updated desc")

    def test_05_duplicate_name_should_fail(self):
        """测试 common_parameter_name 唯一约束，重复创建应返回 400"""
        fake = io.BytesIO(b"dup")
        resp = requests.post(
            f"{BASE_URL}/gt_common_param/",
            headers=self.headers,
            data={
                "common_parameter_name": "gt_api_param_001",
                "sim_test_version": "gt_v1",
                "sim_test_vehicle": "vehicle_A",
            },
            files={"common_parameter_file": ("dup.yaml", fake, "text/plain")},
        )
        self.assertEqual(resp.status_code, 400)

    def test_06_filter_by_sim_test_version(self):
        """测试按 sim_test_version 精确过滤（exact）"""
        resp = requests.get(f"{BASE_URL}/gt_common_param/", headers=self.headers,
                            params={"sim_test_version": "gt_v1"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["sim_test_version"], "gt_v1")

    def test_07_filter_by_sim_test_vehicle(self):
        """测试按 sim_test_vehicle 精确过滤（exact）"""
        resp = requests.get(f"{BASE_URL}/gt_common_param/", headers=self.headers,
                            params={"sim_test_vehicle": "vehicle_A"})
        self.assertEqual(resp.status_code, 200)
        for item in resp.json()["data"]:
            self.assertEqual(item["sim_test_vehicle"], "vehicle_A")

    def test_08_get_choices(self):
        """测试 choices 接口，返回数据库中已有的 sim_test_version 和 sim_test_vehicle 去重列表"""
        resp = requests.get(f"{BASE_URL}/gt_common_param/choices/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        ch = resp.json()["data"]
        self.assertIn("sim_test_version", ch)
        self.assertIn("sim_test_vehicle", ch)
        # 刚创建的数据应出现在 choices 中
        self.assertIn("gt_v1", ch["sim_test_version"])
        self.assertIn("vehicle_A", ch["sim_test_vehicle"])

    def test_09_get_creators(self):
        """测试 creators 接口，返回有数据的用户"""
        resp = requests.get(f"{BASE_URL}/gt_common_param/creators/", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json()["data"], list)

    def test_10_batch_delete(self):
        """测试批量删除通参（post_delete 信号应同步删除物理文件）"""
        fake = io.BytesIO(b"tmp")
        r = requests.post(
            f"{BASE_URL}/gt_common_param/",
            headers=self.headers,
            data={
                "common_parameter_name": "gt_batch_del_tmp",
                "sim_test_version": "gt_v1",
                "sim_test_vehicle": "vehicle_A",
            },
            files={"common_parameter_file": ("tmp.yaml", fake, "text/plain")},
        )
        tmp_id = r.json()["data"]["id"]

        resp = requests.post(f"{BASE_URL}/gt_common_param/batch_delete/",
                             headers=self.headers, json={"ids": [tmp_id]})
        self.assertEqual(resp.status_code, 200)

        check = requests.get(f"{BASE_URL}/gt_common_param/{tmp_id}/", headers=self.headers)
        self.assertEqual(check.status_code, 404)

    def test_11_delete_common_param(self):
        """测试删除单条通参，post_delete 信号触发物理文件清理"""
        if not self.created_id:
            self.skipTest("依赖 test_02 先执行")
        resp = requests.delete(f"{BASE_URL}/gt_common_param/{self.created_id}/",
                               headers=self.headers)
        self.assertIn(resp.status_code, [200, 204])


if __name__ == "__main__":
    unittest.main(verbosity=2)
