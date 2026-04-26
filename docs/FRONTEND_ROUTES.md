# 前端路由结构与模块 API 映射

> 路由模式：`createWebHistory`（无 `#` 的 HTML5 history 模式）  
> 布局：除 `/login` 外所有路由均嵌套在 `BasicLayout.vue` 下  
> 守卫：全局前置守卫处理登录检查、用户信息懒加载、`is_staff` 限制

---

## 一、全局前置守卫逻辑（`src/router/index.js`）

```
访问任意路由
  ├─ 未登录 且 非白名单 → 跳 /login
  ├─ 已登录 但 userInfo 未加载 → 先 fetchUserInfo()（失败则强制登出）
  ├─ 已登录 访问 /login → 跳 /dashboard
  ├─ meta.permissions 存在 → 检查全部权限，不满足跳 /
  └─ meta.requireStaff = true 且 非 is_staff → 跳 /dashboard
```

白名单（无需登录）：`['/login', '/dd-callback']`

---

## 二、路由表

### 独立路由

| 路径 | 组件 | meta.title |
|------|------|------------|
| `/login` | `views/Login.vue` | 登录 |
| `/dd-callback` | `views/DingTalkCallback.vue` | 钉钉登录中... |

### 嵌套在 `BasicLayout` 下

#### 公共

| 路径 | 名称 | 组件 | 标题 |
|------|------|------|------|
| `/dashboard` | Dashboard | `views/Dashboard.vue` | 仪表盘 |

#### 系统管理（`meta.requireStaff: true`，侧边栏 `v-if="is_staff"`）

| 路径 | 名称 | 组件 | 标题 |
|------|------|------|------|
| `/system/users` | UserManagement | `views/system/UserManagement.vue` | 用户管理 |
| `/system/roles` | RoleManagement | `views/system/RoleManagement.vue` | 角色管理 |

#### 版本管理

| 路径 | 名称 | 组件 | 标题 |
|------|------|------|------|
| `/versions/perception` | PerceptionVersions | `views/versions/perception/PerceptionVersionList.vue` | 感知版本 |
| `/envs/perception` | PerceptionEnvs | `views/versions/perception/PerceptionEnvList.vue` | 感知环境 |
| `/versions/loc` | LocVersions | `views/versions/loc/LocVersionList.vue` | 定位版本 |
| `/envs/loc` | LocEnvs | `views/versions/loc/LocEnvList.vue` | 定位环境 |
| `/versions/ctl` | CtlVersions | `views/versions/ctl/CtlVersionList.vue` | 控制版本 |
| `/envs/ctl` | CtlEnvs | `views/versions/ctl/CtlEnvList.vue` | 控制环境 |
| `/versions/sim` | SimVersions | `views/versions/sim/SimVersionList.vue` | 仿真版本 |
| `/envs/sim` | SimEnvs | `views/versions/sim/SimEnvList.vue` | 仿真环境 |
| `/versions/sen` | SenVersions | `views/versions/sen/SenVersionList.vue` | 传感器版本 |
| `/envs/sen` | SenEnvs | `views/versions/sen/SenEnvList.vue` | 传感器环境 |

#### 数据管理

| 路径 | 名称 | 组件 | 标题 |
|------|------|------|------|
| `/data/sim_project_property` | SimProjectProperty | `views/data_manage/sim_project_property/SimProjectPropertyList.vue` | 仿真项目数据 |
| `/data/sim_common_property` | SimCommonProperty | `views/data_manage/sim_common_property/SimCommonPropertyList.vue` | 仿真通用数据 |

#### 整车仿真测试

| 路径 | 名称 | 组件 | 标题 |
|------|------|------|------|
| `/agv-sim/versions` | AgvSimVersions | `views/sim_test_agv/AutoTestVersionsList.vue` | 自动化版本 |
| `/agv-sim/case-map` | AgvSimCaseMap | `views/sim_test_agv/CaseMapList.vue` | 地图管理 |
| `/agv-sim/case-property` | AgvSimCaseProperty | `views/sim_test_agv/CasePropertyList.vue` | 资产管理 |
| `/agv-sim/common-parameter` | AgvSimCommonParameter | `views/sim_test_agv/SchemeCommonParameterList.vue` | 通用参数 |
| `/agv-sim/case-template` | AgvSimCaseTemplate | `views/sim_test_agv/CaseTemplateList.vue` | 用例模版 |
| `/agv-sim/test-task` | AgvSimTestTask | `views/sim_test_agv/AgvTestTaskList.vue` | 测试任务 |

#### 感知取货测试（侧边栏 `v-if="is_staff"`）

| 路径 | 名称 | 组件 | 标题 |
|------|------|------|------|
| `/get-test/target` | GetTestTarget | `views/sim_test_get/GetTestTargetList.vue` | 物体数据 |
| `/get-test/agv-body` | GetTestAgvBody | `views/sim_test_get/AgvBodyList.vue` | 车体数据 |
| `/get-test/common-param` | GetTestCommonParam | `views/sim_test_get/GetTestCommonParamList.vue` | 测试通参 |

> 未匹配路由（`/:pathMatch(.*)*`）在 `BasicLayout` 内展示 `views/NotFound.vue`，保留侧边栏和顶栏，并显示返回首页按钮。

---

## 三、路由 meta 字段约定

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 页面标题（写入 `document.title`）和面包屑当前项 |
| `parentTitle` | string | 面包屑父级文字 |
| `parentPath` | string | 面包屑父级链接 |
| `requireStaff` | boolean | `true` 时非 `is_staff` 用户跳转 `/dashboard` |
| `permissions` | string[] | 路由级权限校验（需全部满足，当前较少使用） |

---

## 四、侧边栏菜单与访问控制

| 菜单 | 可见条件 | 路由守卫额外限制 |
|------|----------|----------------|
| 仪表盘 | 所有登录用户 | 无 |
| 系统管理 | `is_staff = true` | `requireStaff: true` |
| 版本管理 | 所有登录用户 | 无（按钮级由 `v-permission` 控制） |
| 数据管理 | 所有登录用户 | 无 |
| 整车仿真测试 | 所有登录用户 | 无 |
| 感知取货测试 | `is_staff = true` | 无（路由无额外守卫） |

> **注意**：感知取货测试目前仅在侧边栏设了 `v-if="is_staff"`，路由本身没有 `requireStaff`，直接访问 URL 不会被拦截。如需强制阻止直接访问，需在路由 meta 中补充 `requireStaff: true`。

---

## 五、API 文件与后端接口映射

| API 文件 | 对应后端 app | URL 前缀 | 说明 |
|----------|-------------|---------|------|
| `src/api/auth.js` | `back_stage` | `/api/login/`、`/api/token/`、`/api/me/` | 登录、刷新 token、当前用户信息、修改密码 |
| `src/api/version.js` | `version_pack` | `/api/per_*/`、`/api/loc_*/`、`/api/ctl_*/`、`/api/sim_*/`、`/api/sen_*/` | 5 组版本+环境 CRUD |
| `src/api/sim_test_agv.js` | `sim_test_agv` | `/api/at_versions/`、`/api/at_case_map/`、`/api/at_case_property/`、`/api/at_common_parameter/`、`/api/at_case_template/`、`/api/at_test_task/` | 整车仿真测试全部接口 |
| `src/api/sim_test_get.js` | `sim_test_get` | `/api/gt_test_target/`、`/api/gt_agv_body/`、`/api/gt_common_param/` | 感知取货测试全部接口 |

### `src/api/sim_test_agv.js` 主要函数

| 函数 | 方法 | 路径 |
|------|------|------|
| `getAtVersionsList` | GET | `/at_versions/` |
| `createAtVersions` | POST | `/at_versions/` |
| `updateAtVersions(id, data)` | PATCH | `/at_versions/{id}/` |
| `deleteAtVersions(id)` | DELETE | `/at_versions/{id}/` |
| `batchDeleteAtVersions(ids)` | POST | `/at_versions/batch_delete/` |
| `getCasePropertyList` | GET | `/at_case_property/` |
| `batchCopyCaseProperties(ids, version)` | POST | `/at_case_property/batch_copy/` |
| `getCasePropertyChoices` | GET | `/at_case_property/choices/` |
| `uploadCasePropertyFolder(id, data)` | POST | `/at_case_property/{id}/upload_folder_field/` |
| `downloadCasePropertyFolder(id, field)` | GET (blob) | `/at_case_property/{id}/download_folder_field/` |
| `getCommonParameterChoices` | GET | `/at_common_parameter/choices/` |
| `batchCopyCommonParameters(items)` | POST | `/at_common_parameter/batch_copy/` |
| `cancelAgvTestTask(id)` | POST | `/at_test_task/{id}/cancel/` |

### `src/api/sim_test_get.js` 主要函数

| 函数 | 方法 | 路径 |
|------|------|------|
| `getGetTestTargetList` | GET | `/gt_test_target/` |
| `createGetTestTarget(data)` | POST | `/gt_test_target/` |
| `updateGetTestTarget(id, data)` | PATCH | `/gt_test_target/{id}/` |
| `deleteGetTestTarget(id)` | DELETE | `/gt_test_target/{id}/` |
| `batchDeleteGetTestTargets(ids)` | POST | `/gt_test_target/batch_delete/` |
| `getGetTestTargetCreators` | GET | `/gt_test_target/creators/` |
| `getAgvBodyList` | GET | `/gt_agv_body/` |
| `createAgvBody(data)` | POST | `/gt_agv_body/` |
| `updateAgvBody(id, data)` | PATCH | `/gt_agv_body/{id}/` |
| `deleteAgvBody(id)` | DELETE | `/gt_agv_body/{id}/` |
| `batchDeleteAgvBodies(ids)` | POST | `/gt_agv_body/batch_delete/` |
| `getGetTestCommonParamList` | GET | `/gt_common_param/` |
| `createGetTestCommonParam(data)` | POST | `/gt_common_param/` |
| `updateGetTestCommonParam(id, data)` | PATCH | `/gt_common_param/{id}/` |
| `deleteGetTestCommonParam(id)` | DELETE | `/gt_common_param/{id}/` |
| `batchDeleteGetTestCommonParams(ids)` | POST | `/gt_common_param/batch_delete/` |
| `getGetTestCommonParamChoices` | GET | `/gt_common_param/choices/` |

---

## 六、新增页面 Checklist

新增一个模块页时需要完成以下步骤：

1. **`src/api/xxx.js`** — 新建 API 文件，参考现有文件格式
2. **`src/views/xxx/XxxList.vue`** — 列表页（参考 `FRONTEND_COMPONENTS.md` ListPage 标准模式）
3. **`src/views/xxx/XxxFormDialog.vue`** — 表单弹框（参考 FormDialog 标准模式）
4. **`src/router/index.js`** — 在 `children` 中添加路由条目
5. **`src/layout/BasicLayout.vue`** — 在侧边栏添加 `el-menu-item` 或 `el-sub-menu`
6. 如需权限控制侧边栏可见性，在 `el-sub-menu` 加 `v-if="authStore.userInfo?.is_staff"`
7. 如需路由守卫阻止直接访问，在 `meta` 中加 `requireStaff: true`
