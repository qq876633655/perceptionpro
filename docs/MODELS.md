# 数据模型文档

> 数据库：MySQL，默认主键类型：`BigAutoField`（id），时区：`Asia/Shanghai`  
> 自定义用户模型：`back_stage.User`（`AUTH_USER_MODEL`）

---

## 公共抽象基类

### `CommonDatetime`（`apps/common_views/models.py`）

所有业务模型的父类，**abstract = True**，不生成独立数据表。

| 字段 | 类型 | 说明 |
|------|------|------|
| `created_by` | FK → `back_stage.User` | 创建人，`SET_NULL`，可空 |
| `updated_by` | FK → `back_stage.User` | 更新人，`SET_NULL`，可空 |
| `create_time` | DateTimeField | 创建时间，`auto_now_add=True` |
| `update_time` | DateTimeField | 更新时间，`auto_now=True` |

---

## App: back_stage

### `User`（继承 `AbstractUser` + `CommonDatetime`）

自定义用户模型，替换 Django 默认 User。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | 自增主键 |
| `username` | CharField | unique | 继承自 AbstractUser |
| `password` | CharField | — | 继承自 AbstractUser |
| `is_staff` | BooleanField | default=False | 管理员标识 |
| `is_superuser` | BooleanField | default=False | 超级管理员 |
| `is_active` | BooleanField | default=True | 是否启用 |
| `phone_number` | CharField(16) | unique | 手机号，用于登录 |
| `dd_user_id` | CharField(128) | null, blank | 钉钉 userId |
| `avatar` | URLField | null, blank | 头像 URL，存储到 `media/avatar/{id}.{ext}` |
| `is_default_password` | BooleanField | default=False | 是否使用默认密码，钉钉创建新用户时置 `True`，修改密码后自动置 `False` |
| `department` | CharField(128) | null, blank | 部门，由用户在申请角色时填写 |
| `created_by` + `updated_by` | FK → User | 继承自 CommonDatetime |
| `create_time` / `update_time` | DateTimeField | 继承自 CommonDatetime |

> 登录方式：手机号 + 密码（`PhoneBackend`）或用户名 + 密码（`ModelBackend`），或钉钉 OAuth2（`/dd/no_sign_in/`）

---

## App: version_pack

### 公共抽象基类

#### `BaseEnv`（abstract）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `env_name` | CharField(128) | unique | 环境名称 |
| `apply_project` | CharField(16) | default='主线版本' | 适用专项 |
| `env_note` | TextField | null, blank | 环境描述 |
| + CommonDatetime 字段 | | | |

#### `BaseVersion`（abstract）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `version_num` | CharField(128) | unique | 版本号 |
| `versions_type` | JSONField | — | 版本类型（数组），如 `["feature","test"]` |
| `apply_project` | CharField(16) | default='主线版本' | 适用专项 |
| `dev_test_result` | TextField | null, blank | 研发提测内容 |
| `test_result` | CharField(32) | choices，default='未开始' | 测试结果：未开始/测试中/通过/失败/中断 |
| `test_verdict` | TextField | null, blank | 测试总结 |
| + CommonDatetime 字段 | | | |

### 具体模型（5 组，结构完全一致，仅前缀不同）

| 前缀 | 模块 | Env 模型 | Version 模型 |
|------|------|----------|--------------|
| `per_` | 感知 | `PerEnv` | `PerVersion` |
| `loc_` | 定位 | `LocEnv` | `LocVersion` |
| `ctl_` | 控制 | `CtlEnv` | `CtlVersion` |
| `sim_` | 仿真 | `SimEnv` | `SimVersion` |
| `sen_` | 传感器 | `SenEnv` | `SenVersion` |

#### `XxxEnv` 扩展字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `env_file` | FileField | — | 环境文件，路径：`{prefix}_env/{env_name}/{filename}` |

#### `XxxVersion` 扩展字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `version_file` | FileField | — | 版本文件，路径：`{prefix}_versions/{version_num}/{filename}` |
| `env` | FK → XxxEnv | `SET_NULL`，null | 关联环境 |
| `database_file` | FileField | null, blank，仅 `PerVersion` | 数据库文件，限 `.db` 扩展名 |

> **信号（工厂模式统一注册）**：`pre_save` 更新时删旧文件；`post_delete` 删除记录时清理物理文件。  
> 对所有 10 个模型（5 × Env + 5 × Version）均已通过 `_FILE_SIGNAL_REGISTRY` 循环注册。

---

## App: data_manage

### `SimProjectProperty`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `uid` | UUIDField | unique, editable=False | 用于文件路径隔离 |
| `apply_project` | CharField(64) | — | 适用项目 |
| `project_property` | FileField | max_length=256 | 项目资产文件，路径：`sim_project_property/{uid}/{filename}` |
| `property_desc` | TextField | null, blank | 资产说明 |
| `property_tag` | CharField(128) | null, blank | 标签 |
| + CommonDatetime 字段 | | | |

> **信号**：`pre_save` 替换文件时删除旧文件；`post_delete` 删除记录时删物理文件

### `SimCommonProperty`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `uid` | UUIDField | unique, editable=False | 用于文件路径隔离 |
| `versions` | CharField(128) | unique | 版本号 |
| `common_property` | FileField | max_length=256 | 通用资产文件，路径：`sim_common_property/{uid}/{filename}` |
| `property_desc` | TextField | null, blank | 资产说明 |
| `property_tag` | CharField(128) | null, blank | 标签 |
| + CommonDatetime 字段 | | | |

> **信号**：`pre_save` 替换文件时删除旧文件；`post_delete` 删除记录时删物理文件

---

## App: sim_test_agv

### `CaseMap`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `district_name` | CharField(255) | unique | 分区名称 |
| `map_file` | FileField | max_length=255 | 路径：`sim_res_bak/map/{filename}` |
| + CommonDatetime 字段 | | | |

### `CaseProperty`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `sim_test_version` | CharField(255) | — | 资产版本 |
| `sim_test_vehicle` | CharField(255) | — | 测试车型 |
| `sim_scheme_name` | CharField(255) | — | 测试方案 |
| `test_module` | CharField(255) | — | 测试模块 |
| `backup_file` | FileField | max_length=255 | robotune备份，路径：`sim_res_bak/{ver}/{vehicle}/{scheme}/{filename}` |
| `lastagvpose_path` | CharField(128) | **required** | lastagvpose 文件夹路径 |
| `wbt_file` | FileField | max_length=255 | wbt文件，同上路径 |
| `map` | FK → CaseMap | `SET_NULL`，null | 分区名称 |
| `mapping_ecal_path` | CharField(255) | null, blank | 自动建图ecal文件夹路径 |
| `extend_mapping_ecal_path` | CharField(255) | null, blank | 扩展建图ecal文件夹路径 |
| `ply_path` | CharField(255) | null, blank | 感知模版文件夹路径 |
| `property_status` | CharField(32) | choices，default='正常' | 资产状态：正常/维护 |
| + CommonDatetime 字段 | | | |

> **unique_together**: `(sim_test_version, sim_test_vehicle, sim_scheme_name)`  
> **4 个路径字段**（`lastagvpose_path`、`mapping_ecal_path`、`extend_mapping_ecal_path`、`ply_path`）存储文件夹相对路径（相对于 `MEDIA_ROOT`），通过专用 API 上传整个文件夹后回填，路径格式：`sim_res_bak/{ver}/{vehicle}/{scheme}/{field_name}/{folder_root}/`

### `SchemeCommonParameter`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `common_parameter_name` | CharField(255) | unique | 通参名称 |
| `sim_test_version` | CharField(255) | — | 资产版本 |
| `sim_test_vehicle` | CharField(255) | — | 测试车型 |
| `test_module` | CharField(255) | **required** | 测试模块 |
| `common_parameter_status` | CharField(32) | choices，default='正常' | 通参状态：正常/维护 |
| `parameter_desc` | TextField | null, blank | 通参描述 |
| `common_parameter_file` | FileField | max_length=255 | 路径：`sim_res_bak/{ver}/{vehicle}/通用参数/{filename}` |
| + CommonDatetime 字段 | | | |

### `CaseTemplate`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `uid` | UUIDField | unique, editable=False | 文件路径隔离 |
| `sim_test_version` | CharField(255) | — | 资产版本 |
| `case_desc` | TextField | — | 用例说明（必填） |
| `test_module` | CharField(255) | **required** | 测试模块 |
| `case_file` | FileField | max_length=255 | 路径：`sim_res_bak/case_template/{uid}/{filename}` |
| + CommonDatetime 字段 | | | |

### `AgvTestTask`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `uid` | UUIDField | unique, editable=False | 文件路径隔离 |
| `per_version` | FileField | null, blank，max_length=255 | 感知测试版本包，路径：`sim_res_bak/agv_test_task/{uid}/{filename}` |
| `loc_version` | FileField | null, blank，max_length=255 | 定位测试版本包 |
| `ctl_version` | FileField | null, blank，max_length=255 | 控制测试版本包 |
| `agv_version` | FileField | null, blank，max_length=255 | 整车测试版本包 |
| `agv_case_file` | FileField | **必填**，max_length=255 | 测试用例文件 |
| `sim_test_version` | CharField(255) | — | 使用的资产版本（对应 CaseProperty.sim_test_version） |
| `queue_name` | CharField(255) | — | 任务队列 |
| `recovery_default_version` | CharField(16) | choices: True/False，default='False' | 是否恢复默认版本 |
| `base_version` | CharField(255) | null, blank | 待测基线版本 |
| `manual_error_handling` | CharField(16) | choices: True/False，default='True' | 是否手动处理错误 |
| `task_status` | CharField(16) | choices，default='CREATED'，null, blank | CREATED/DISPATCHED/RUNNING/CANCELING/CANCELED/SUCCESS/FAILED |
| `current_schedule` | CharField(32) | null, blank | 当前进度 |
| `celery_id` | CharField(255) | null, blank | 执行中的 Celery 任务 ID |
| `process_id` | CharField(255) | null, blank | 任务进程 ID |
| `worker_name` | CharField(128) | null, blank | 执行端名称 |
| `target_worker` | CharField(255) | null, blank | 指定 Worker hostname，空=广播到 queue_name，填写=只发给该 worker 专属队列 |
| `error_msg` | TextField | null, blank | 错误信息 |
| `cancel_requested` | BooleanField | default=False | 是否请求中止 |
| `auto_test_run_log` | FileField | null, blank，max_length=255 | 运行日志文件 |
| `test_result` | FileField | null, blank，max_length=255 | 测试结果文件 |
| + CommonDatetime 字段 | | | |

> **无编辑接口**：该模型不允许 PUT/PATCH，任务状态由 Celery Worker 回写

### `WorkerNode`

已注册的 Celery Worker 节点静态登记表，运行时状态（在线/离线/队列）通过 Celery inspect 动态获取。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `hostname` | CharField(255) | unique | Worker 名称，如 `celery@10.20.24.75_webotsC2` |
| `docker_type` | CharField(64) | blank, default='' | Docker 类型，如 `webotsC1`/`webotsC2`，供任务脚本 run_docker 使用 |
| `ip_address` | CharField(64) | blank, default='' | IP 地址 |
| `note` | TextField | blank, default='' | 备注 |
| + CommonDatetime 字段 | | | |

> **Meta**: `ordering = ['hostname']`

---

## 文件存储路径速查

| 模型 / 字段 | MEDIA_ROOT 相对路径 |
|------------|---------------------|
| PerEnv.env_file | `per_env/{env_name}/{filename}` |
| PerVersion.version_file | `per_versions/{version_num}/{filename}` |
| PerVersion.database_file | `per_versions/{version_num}/{filename}` |
| LocEnv.env_file | `loc_env/{env_name}/{filename}` |
| LocVersion.version_file | `loc_versions/{version_num}/{filename}` |
| CtlEnv / CtlVersion | `ctl_env/` / `ctl_versions/` |
| SimEnv / SimVersion | `sim_env/` / `sim_versions/` |
| SenEnv / SenVersion | `sen_env/` / `sen_versions/` |
| SimProjectProperty.project_property | `sim_project_property/{uid}/{filename}` |
| SimCommonProperty.common_property | `sim_common_property/{uid}/{filename}` |
| CaseMap.map_file | `sim_res_bak/map/{filename}` |
| CaseProperty.backup_file / wbt_file | `sim_res_bak/{ver}/{vehicle}/{scheme}/{filename}` |
| CaseProperty 路径字段（4个） | `sim_res_bak/{ver}/{vehicle}/{scheme}/{field_name}/{folder_root}/` |
| SchemeCommonParameter.common_parameter_file | `sim_res_bak/{ver}/{vehicle}/通用参数/{filename}` |
| CaseTemplate.case_file | `sim_res_bak/case_template/{uid}/{filename}` |
| AgvTestTask 所有 FileField | `sim_res_bak/agv_test_task/{uid}/{filename}` |
| GetTestCommonParameter.common_parameter_file | `sim_res_bak/common_parameter/{uid}/{filename}` |

---

## App: sim_test_get

感知获取测试相关模型，包含测试目标参数、车体参数和通用参数。

### `GetTestTarget`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `target_name` | CharField(255) | unique | 载具名称 |
| `target_type` | CharField(64) | choices | 类型：pallet（托盘）/ cage（料笼） |
| `pallet` | CharField(256) | default="0,0,0" | 墩宽列表（逗号分隔） |
| `hole` | CharField(256) | default="0,0" | 孔宽列表 |
| `pallet_height` | FloatField | default=0 | 墩高 |
| `top_height` | FloatField | default=0 | 面板高度 |
| `bottom_height` | FloatField | default=0 | 底板高度 |
| `card_width_expand` | FloatField | default=0 | 面板相对墩y方向突出量 |
| `card_length_expand` | FloatField | default=0 | 面板相对墩x方向突出量 |
| `fork_in_bias_height` | FloatField | default=0 | 入叉高度相对横梁高度偏移量 |
| `adaption_z_reserve` | FloatField | default=0 | roi区域上下整体偏移距离 |
| `card_length` | FloatField | default=0 | 卡板长度 |
| `card_height` | FloatField | default=0 | 卡板高度 |
| `texture` | CharField(16) | choices | 模型材质：plastic/metal/wood/mirror_hollow/plastic_damaged/mirror |
| `color` | CharField(16) | choices | 模型颜色：white/yellow/blue/black/red/red_brown/silver/wood_color/black_hollow/silver_gray |
| `length` | FloatField | **required** | 入叉面长 |
| `width` | FloatField | **required** | 入叉面宽 |
| `height` | FloatField | **required** | 入叉面高 |
| `t_target_in_fork_center_x` | FloatField | default=0 | 物体坐标入叉面中心点x |
| `t_target_in_fork_center_y` | FloatField | default=0 | 物体坐标入叉面中心点y |
| `t_target_in_fork_center_z` | FloatField | default=0 | 物体坐标入叉面中心点z |
| `model_name` | CharField(256) | **required** | 模型名称 |
| `extern_proto_path` | CharField(256) | **required** | 引用路径 |
| `node_params` | JSONField | **required** | 节点参数 |
| + CommonDatetime 字段 | | | |

### `AgvBody`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `agv_type` | CharField(128) | unique | 测试车型 |
| `left_width` | FloatField | **required** | 左边车宽 |
| `right_width` | FloatField | **required** | 右边车宽 |
| `front_length` | FloatField | **required** | 前方车长 |
| `back_length` | FloatField | **required** | 后方车长 |
| `fork_length` | FloatField | **required** | 货叉长度 |
| `fork_inner_width` | FloatField | **required** | 货叉内宽 |
| `fork_width` | FloatField | **required** | 货叉宽度 |
| `fork_thickness` | FloatField | **required** | 货叉厚度 |
| `load_position_x` | FloatField | **required** | 原车前悬距 |
| `sensor_extrinsic` | TextField | **required** | 传感器外参 |
| `agv_node` | TextField | **required** | 车体节点 |
| + CommonDatetime 字段 | | | |

### `GetTestCommonParameter`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | BigAutoField | PK | |
| `uid` | UUIDField | unique, editable=False | 用于文件路径隔离 |
| `common_parameter_name` | CharField(255) | unique | 通参名称 |
| `sim_test_version` | CharField(255) | **required** | 资产版本 |
| `sim_test_vehicle` | CharField(255) | **required** | 测试车型 |
| `common_parameter_file` | FileField | max_length=255 | 通用参数文件，路径：`sim_res_bak/common_parameter/{uid}/{filename}` |
| `parameter_desc` | TextField | null, blank | 通参描述 |
| + CommonDatetime 字段 | | | |
