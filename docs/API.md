# 后端接口文档

> 所有接口前缀：`/api/`  
> 认证方式：`Authorization: Bearer <access_token>`  
> 统一响应格式：`{ "code": 0, "msg": "success", "data": ... }`  
> 分页响应格式：`{ "code": 0, "msg": "success", "data": [...], "pagination": { "count", "page", "page_size", "total_pages" } }`  
> 接口文档（Swagger UI）：`/swagger/`

---

## 认证接口

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/api/login/` | 无需认证 | 手机号+密码登录，返回 `access`、`refresh`、`user` |
| POST | `/api/token/` | 无需认证 | DRF SimpleJWT 标准登录（用户名+密码） |
| POST | `/api/token/refresh/` | 无需认证 | 刷新 access token，body: `{ "refresh": "..." }` |
| POST | `/api/change_pwd/` | 已登录 | 修改密码，body: `{ "old_password", "new_password" }` |
| GET | `/api/me/` | 已登录 | 当前登录用户信息（含角色列表、权限列表） |

---

## App: back_stage — 用户与权限管理

### 用户管理  `/api/users/`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/users/` | 已登录 | 用户列表，支持过滤：`username`(icontains)、`phone_number`(icontains)、`is_staff`、`is_active` |
| POST | `/api/users/` | is_staff 或以上 | 新建用户，密码默认 `Test123456` |
| GET | `/api/users/{id}/` | 已登录 | 用户详情 |
| PATCH | `/api/users/{id}/` | is_staff 或以上 | 更新用户（非超管不可修改 is_staff/is_superuser） |
| DELETE | `/api/users/{id}/` | is_staff 或以上 | 删除用户 |

### 角色（权限组）管理  `/api/groups/`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/api/groups/` | is_staff 或以上 | 角色列表（含权限详情、成员数） |
| POST | `/api/groups/` | 超级管理员 | 新建角色 |
| PATCH | `/api/groups/{id}/` | 超级管理员 | 更新角色（可批量设置权限 IDs） |
| DELETE | `/api/groups/{id}/` | 超级管理员 | 删除角色 |
| GET | `/api/groups/all_permissions/` | 已登录 | 返回所有业务 app 的权限列表（供角色配置使用） |

---

## App: version_pack — 版本/环境管理

所有接口均需 `已登录 + HasModelPermission`（超级管理员例外）。

### 通用 Env 接口（5组：per_env / loc_env / ctl_env / sim_env / sen_env）

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/{prefix}_env/` | `view_{model}` | 环境列表，支持过滤：`apply_project`(exact)、`created_by`(id)、`create_time_after/before`；搜索：`env_name` |
| POST | `/api/{prefix}_env/` | `add_{model}` | 新建环境（multipart，含 env_file） |
| GET | `/api/{prefix}_env/{id}/` | `view_{model}` | 环境详情 |
| PATCH | `/api/{prefix}_env/{id}/` | `change_{model}` | 更新环境 |
| DELETE | `/api/{prefix}_env/{id}/` | `delete_{model}` | 删除环境（同步删文件） |
| POST | `/api/{prefix}_env/batch_delete/` | `delete_{model}` | 批量删除，body: `{ "ids": [1,2,...] }` |
| GET | `/api/{prefix}_env/creators/` | `view_{model}` | 返回创建过记录的用户列表 `[{id, username}]` |

> 以 `per_env` 为例，权限码为 `version_pack.view_perenv`、`version_pack.add_perenv` 等

### 通用 Version 接口（5组：per_version / loc_version / ctl_version / sim_version / sen_version）

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/{prefix}_version/` | `view_{model}` | 版本列表，过滤：`versions_type`(JSON contains)、`apply_project`、`env`(id)、`test_result`、`created_by`；搜索：`version_num` |
| POST | `/api/{prefix}_version/` | `add_{model}` | 新建版本（multipart），`test_result`/`test_verdict` 不可在创建时设置 |
| GET | `/api/{prefix}_version/{id}/` | `view_{model}` | 版本详情 |
| PATCH | `/api/{prefix}_version/{id}/` | `change_{model}` | 更新版本（不可修改 `version_num` 和 `version_file`） |
| DELETE | `/api/{prefix}_version/{id}/` | `delete_{model}` | 删除版本（同步删文件） |
| POST | `/api/{prefix}_version/batch_delete/` | `delete_{model}` | 批量删除 |
| GET | `/api/{prefix}_version/creators/` | `view_{model}` | 创建过记录的用户列表 |

> `PerVersion` 额外有 `database_file` 字段（FileField，可选，限 .db 扩展名）

---

## App: data_manage — 仿真数据管理

所有接口均需 `已登录 + HasModelPermission`。

### 仿真项目数据  `/api/sim_project_property/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/sim_project_property/` | `data_manage.view_simprojectproperty` | 列表，过滤：`apply_project`(icontains)、`property_tag`(icontains)、`created_by`、`create_time_after/before`；搜索：`apply_project` |
| POST | `/api/sim_project_property/` | `data_manage.add_simprojectproperty` | 新建（multipart） |
| GET | `/api/sim_project_property/{id}/` | `view_` | 详情 |
| PATCH | `/api/sim_project_property/{id}/` | `change_` | 更新 |
| DELETE | `/api/sim_project_property/{id}/` | `delete_` | 删除（同步删文件） |
| POST | `/api/sim_project_property/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/sim_project_property/creators/` | `view_` | 创建人列表 |

### 仿真通用数据  `/api/sim_common_property/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/sim_common_property/` | `data_manage.view_simcommonproperty` | 列表，过滤：`property_tag`(icontains)、`created_by`、`create_time_after/before`；搜索：`versions` |
| POST | `/api/sim_common_property/` | `data_manage.add_simcommonproperty` | 新建 |
| PATCH | `/api/sim_common_property/{id}/` | `change_` | 更新 |
| DELETE | `/api/sim_common_property/{id}/` | `delete_` | 删除 |
| POST | `/api/sim_common_property/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/sim_common_property/creators/` | `view_` | 创建人列表 |

---

## App: sim_test_agv — 整车仿真自动化测试

所有接口均需 `已登录 + HasModelPermission`。

### 自动化测试版本  `/api/at_versions/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/at_versions/` | `sim_test_agv.view_autotestversions` | 列表，过滤：`versions`(icontains)、`created_by`、`create_time_after/before`；搜索：`versions` |
| POST | `/api/at_versions/` | `sim_test_agv.add_autotestversions` | 新建版本（multipart，含 versions_file） |
| PATCH | `/api/at_versions/{id}/` | `sim_test_agv.change_autotestversions` | 更新（可更新 release_note） |
| DELETE | `/api/at_versions/{id}/` | `sim_test_agv.delete_autotestversions` | 删除 |
| POST | `/api/at_versions/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/at_versions/creators/` | `view_` | 创建人列表 |

### 地图管理  `/api/at_case_map/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/at_case_map/` | `sim_test_agv.view_casemap` | 过滤：`map_name`(icontains)、`created_by`、时间范围 |
| POST | `/api/at_case_map/` | `sim_test_agv.add_casemap` | 新建（multipart，含 map_file） |
| PATCH | `/api/at_case_map/{id}/` | `change_` | 更新 |
| DELETE | `/api/at_case_map/{id}/` | `delete_` | 删除 |
| POST | `/api/at_case_map/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/at_case_map/creators/` | `view_` | 创建人列表 |

### 资产管理  `/api/at_case_property/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/at_case_property/` | `sim_test_agv.view_caseproperty` | 过滤：`sim_test_version`/`sim_test_vehicle`/`sim_scheme_name`/`test_module`(icontains)、`property_status`(exact)、`created_by`、时间范围 |
| POST | `/api/at_case_property/` | `add_` | 新建（multipart，至少含 backup_file） |
| PATCH | `/api/at_case_property/{id}/` | `change_` | 更新主字段（文件夹路径字段通过专用 action 更新） |
| DELETE | `/api/at_case_property/{id}/` | `delete_` | 删除 |
| POST | `/api/at_case_property/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/at_case_property/creators/` | `view_` | 创建人列表 |
| GET | `/api/at_case_property/sim_test_versions/` | `view_` | 返回 sim_test_version 去重列表（供 AgvTestTask 新建下拉） |
| **POST** | `/api/at_case_property/{id}/upload_folder_field/` | `change_` | 上传文件夹到指定路径字段（见下方详情） |
| **GET** | `/api/at_case_property/{id}/download_folder_field/` | `view_` | 下载指定路径字段的文件夹（zip 流，见下方详情） |
| **POST** | `/api/at_case_property/batch_copy/` | `add_` | 批量复制资产到新版本，body: `{ "ids": [...], "sim_test_version": "新版本" }`；会同步复制物理文件并重映射路径 |

#### `upload_folder_field` 参数说明

- Content-Type: `multipart/form-data`
- `field_name`（必填）：目标路径字段名，必须为 `lastagvpose_path` / `mapping_ecal_path` / `extend_mapping_ecal_path` / `ply_path` 之一
- `files[]`：所有文件（FileField 列表，与 `paths[]` 一一对应）
- `paths[]`：每个文件的 `webkitRelativePath`（保留目录结构，如 `folder/sub/file.txt`）
- 效果：先删除旧文件夹，再按 `paths` 重建目录结构写入，最后将根文件夹路径回填到字段

#### `download_folder_field` 参数说明

- Query param: `field_name`（同上四选一）
- 返回：`application/zip` 流，自动命名为 `{folder_name}.zip`

### 通用参数  `/api/at_common_parameter/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/at_common_parameter/` | `sim_test_agv.view_schemecommonparameter` | 过滤：`common_parameter_name`/`sim_test_version`/`sim_test_vehicle`/`test_module`(icontains)、`common_parameter_status`(exact)、`created_by`、时间范围 |
| POST | `/api/at_common_parameter/` | `add_` | 新建（multipart） |
| PATCH | `/api/at_common_parameter/{id}/` | `change_` | 更新 |
| DELETE | `/api/at_common_parameter/{id}/` | `delete_` | 删除 |
| POST | `/api/at_common_parameter/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/at_common_parameter/creators/` | `view_` | 创建人列表 |
| GET | `/api/at_common_parameter/choices/` | `view_` | 返回各字段已有去重值：`sim_test_version`、`sim_test_vehicle`、`test_module` |
| **POST** | `/api/at_common_parameter/batch_copy/` | `add_` | 批量复制通参，body: `{ "items": [{"id": 1, "common_parameter_name": "新名称"}, ...] }`；同步复制物理文件 |

### 用例模版  `/api/at_case_template/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/at_case_template/` | `sim_test_agv.view_casetemplate` | 过滤：`sim_test_version`/`test_module`(icontains)、`created_by`、时间范围 |
| POST | `/api/at_case_template/` | `add_` | 新建 |
| PATCH | `/api/at_case_template/{id}/` | `change_` | 更新 |
| DELETE | `/api/at_case_template/{id}/` | `delete_` | 删除 |
| POST | `/api/at_case_template/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/at_case_template/creators/` | `view_` | 创建人列表 |

### 测试任务  `/api/at_test_task/`

> **无 PUT/PATCH 接口**：任务创建后不可编辑，状态由 Celery Worker 回写。

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/at_test_task/` | `sim_test_agv.view_agvtesttask` | 过滤：`sim_test_version`/`queue_name`(icontains)、`task_status`(exact)、`created_by`、时间范围 |
| POST | `/api/at_test_task/` | `sim_test_agv.add_agvtesttask` | 新建任务（multipart，agv_case_file 必填），创建后自动 dispatch 到 Celery |
| DELETE | `/api/at_test_task/{id}/` | `sim_test_agv.delete_agvtesttask` | 删除 |
| POST | `/api/at_test_task/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/at_test_task/creators/` | `view_` | 创建人列表 |
| **POST** | `/api/at_test_task/{id}/cancel/` | `change_` | 取消任务；`DISPATCHED` 状态直接撤销 Celery 任务；`RUNNING` 状态设 `cancel_requested=True` 并发送撤销信号，Worker 轮询后自行终止 |

#### cancel 响应说明

| 任务状态 | 行为 |
|----------|------|
| `DISPATCHED` | 立即撤销 Celery 任务，状态改为 `CANCELED` |
| `RUNNING` | 设置 `cancel_requested=True`，并向 Worker 发送 revoke 信号，Worker 循环检测后终止进程 |
| 其他状态 | 返回 400 错误，不可取消 |

#### 新建任务可提交字段

| 字段 | 是否必填 | 说明 |
|------|----------|------|
| `sim_test_version` | 必填 | 使用的资产版本 |
| `queue_name` | 必填 | 任务队列 |
| `agv_case_file` | 必填 | 测试用例文件 |
| `per_version` | 可选 | 感知测试版本包 |
| `loc_version` | 可选 | 定位测试版本包 |
| `ctl_version` | 可选 | 控制测试版本包 |
| `agv_version` | 可选 | 整车测试版本包 |
| `recovery_default_version` | 可选 | default: `'False'` |
| `base_version` | 可选 | 待测基线版本 |

---

---

## App: sim_test_get — 感知取货测试

所有接口均需 `已登录 + HasModelPermission`。  
> **访问控制**：前端侧边栏仅 `is_staff=True` 的用户可见此模块（与系统管理一致）。

### 物体数据  `/api/gt_test_target/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/gt_test_target/` | `sim_test_get.view_gettesttarget` | 列表，过滤：`target_name`(icontains)、`model_name`(icontains)、`target_type`(exact)、`created_by`、时间范围；搜索：`target_name`、`model_name` |
| POST | `/api/gt_test_target/` | `add_` | 新建，body: JSON，`node_params` 为 JSON 对象 |
| GET | `/api/gt_test_target/{id}/` | `view_` | 详情 |
| PATCH | `/api/gt_test_target/{id}/` | `change_` | 更新 |
| DELETE | `/api/gt_test_target/{id}/` | `delete_` | 删除 |
| POST | `/api/gt_test_target/batch_delete/` | `delete_` | 批量删除，body: `{ "ids": [...] }` |
| GET | `/api/gt_test_target/creators/` | `view_` | 创建人列表 |

#### 字段约束

| 字段 | 值域 |
|------|------|
| `target_type` | `pallet`（托盘）/ `cage`（料笼） |
| `texture` | `plastic` / `metal` / `wood` / `mirror_hollow` / `plastic_damaged` / `mirror` |
| `color` | `white` / `yellow` / `blue` / `black` / `red` / `red_brown` / `silver` / `wood_color` / `black_hollow` / `silver_gray` |
| `node_params` | 任意 JSON 对象，不可为空 |

### 车体数据  `/api/gt_agv_body/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/gt_agv_body/` | `sim_test_get.view_agvbody` | 列表，过滤：`agv_type`(icontains)、`created_by`、时间范围；搜索：`agv_type` |
| POST | `/api/gt_agv_body/` | `add_` | 新建，body: JSON |
| GET | `/api/gt_agv_body/{id}/` | `view_` | 详情 |
| PATCH | `/api/gt_agv_body/{id}/` | `change_` | 更新 |
| DELETE | `/api/gt_agv_body/{id}/` | `delete_` | 删除 |
| POST | `/api/gt_agv_body/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/gt_agv_body/creators/` | `view_` | 创建人列表 |

### 测试通参  `/api/gt_common_param/`

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | `/api/gt_common_param/` | `sim_test_get.view_gettestcommonparameter` | 列表，过滤：`common_parameter_name`(icontains)、`sim_test_version`(exact)、`sim_test_vehicle`(exact)、`created_by`、时间范围；搜索：`common_parameter_name` |
| POST | `/api/gt_common_param/` | `add_` | 新建（multipart，含 `common_parameter_file`） |
| GET | `/api/gt_common_param/{id}/` | `view_` | 详情 |
| PATCH | `/api/gt_common_param/{id}/` | `change_` | 更新（如需换文件，重新上传） |
| DELETE | `/api/gt_common_param/{id}/` | `delete_` | 删除（同步删物理文件） |
| POST | `/api/gt_common_param/batch_delete/` | `delete_` | 批量删除 |
| GET | `/api/gt_common_param/creators/` | `view_` | 创建人列表 |
| GET | `/api/gt_common_param/choices/` | `view_` | 返回字段已有去重值：`sim_test_version`、`sim_test_vehicle`（供前端下拉筛选） |

> **文件信号**：`GetTestCommonParameter.common_parameter_file` 有 `pre_save` 信号（替换时删旧文件）和 `post_delete` 信号（删记录时清物理文件）。  
> 文件路径：`sim_res_bak/common_parameter/{uid}/{filename}`

---

## 错误响应码

| code | 说明 |
|------|------|
| 0 | 成功 |
| 1001 | 参数校验失败（data 字段包含具体字段错误） |
| 1002 | 手机号或密码错误 |
| 2001 | 未认证或登录已过期 |
| 2003 | 权限不足 |
| 5000 | 服务器异常 |
