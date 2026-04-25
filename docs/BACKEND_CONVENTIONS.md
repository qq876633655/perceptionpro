# 后端约定与规范

---

## 一、全局配置分析

### 1.1 已安装的第三方 App（`INSTALLED_APPS`）

| 包名 | 作用 |
|------|------|
| `django_filters` | 提供 `FilterSet` 和 `DjangoFilterBackend`，支持对 QuerySet 按字段精确/模糊/范围过滤 |
| `rest_framework` | DRF 核心，提供 ViewSet、Serializer、Router、权限体系等 REST API 基础设施 |
| `rest_framework_simplejwt` | JWT 认证方案，提供 `JWTAuthentication`、token 生成/刷新/黑名单机制 |
| `drf_yasg` | 自动生成 Swagger/OpenAPI 文档，挂载路径 `/swagger/` |
| `django_celery_results` | Celery 任务结果持久化到 Django 数据库（`django_celery_results_taskresult` 表） |
| `django_celery_beat` | Celery 定时任务调度，将 beat 调度计划存到数据库（可通过 Admin 管理） |

### 1.2 DRF 全局配置（`REST_FRAMEWORK`）

| 配置项 | 值 | 作用 |
|--------|----|------|
| `DEFAULT_AUTHENTICATION_CLASSES` | `JWTAuthentication` | 所有接口默认使用 Bearer JWT 认证，token 从 `Authorization` 头读取 |
| `DEFAULT_PERMISSION_CLASSES` | `IsAuthenticated` | 所有接口默认要求登录，单个 ViewSet 可通过 `permission_classes` 覆盖 |
| `DEFAULT_FILTER_BACKENDS` | `DjangoFilterBackend` + `SearchFilter` + `OrderingFilter` | 全局启用三类过滤后端；各 ViewSet 通过 `filterset_class`、`search_fields`、`ordering_fields` 声明具体规则 |
| `DEFAULT_PAGINATION_CLASS` | `apps.common_views.response.CustomPagination` | 自定义分页，默认每页 10 条，支持 `page`/`page_size` 参数，响应带 `pagination` 元信息 |
| `PAGE_SIZE` | `10` | 默认分页大小（可被 `page_size` 查询参数覆盖） |
| `EXCEPTION_HANDLER` | `apps.common_views.response.custom_exception_handler` | 统一异常格式：`{ code, msg, data }`，详见 §3.4 |
| `DEFAULT_RENDERER_CLASSES` | `apps.common_views.response.CustomJSONRenderer` | 统一响应格式包装：普通响应自动包装为 `{ code:0, msg:"success", data:... }`，分页响应同时附加 `pagination`；blob 流和已有 `code` 字段的响应直接透传 |

### 1.3 SimpleJWT 配置

| 配置项 | 值 | 说明 |
|--------|----|------|
| `ACCESS_TOKEN_LIFETIME` | 24 小时 | access token 有效期 |
| `REFRESH_TOKEN_LIFETIME` | 7 天 | refresh token 有效期 |
| `AUTH_HEADER_TYPES` | `Bearer` | 请求头格式：`Authorization: Bearer <token>` |
| `ROTATE_REFRESH_TOKENS` | `True` | 每次刷新时生成新的 refresh token |
| `BLACKLIST_AFTER_ROTATION` | `True` | 旧 refresh token 刷新后立即失效，防止重放 |

### 1.4 其他重要配置

| 配置项 | 值 | 说明 |
|--------|----|------|
| `AUTH_USER_MODEL` | `back_stage.User` | 自定义用户模型，扩展了手机号、钉钉ID、头像字段 |
| `AUTHENTICATION_BACKENDS` | `PhoneBackend` + `ModelBackend` | 支持手机号登录和用户名登录两种方式 |
| `LANGUAGE_CODE` | `zh-Hans` | 后端校验错误消息使用中文 |
| `TIME_ZONE` | `Asia/Shanghai` | 数据库存储和日志均使用东八区 |
| `DEFAULT_AUTO_FIELD` | `BigAutoField` | 所有模型主键默认为 64 位整数 |
| `MEDIA_ROOT` | `{BASE_DIR}/media` | 文件上传的物理根目录 |
| `MEDIA_URL` | `/media/` | 文件访问的 URL 前缀 |
| `DATA_UPLOAD_MAX_NUMBER_FILES` | `200` | 单次请求最多上传文件数（文件夹上传场景需要） |
| `CORS_ALLOW_ALL_ORIGINS` | `True` | 允许所有跨域访问（开发环境） |
| `DATABASES` | MySQL, host 来自 `config/perceptionpro_cfg.py` | 生产配置独立管理，避免硬编码 |
| `CACHES` | LocMemCache，TTL=300s，max 300条 | 本地内存缓存，不跨进程 |

---

## 二、项目结构约定

```
backend/
├── apps/
│   ├── back_stage/        # 用户、权限、认证
│   ├── common_views/      # 公共基类（BaseModelViewSet、CommonDatetime、响应格式）
│   ├── version_pack/      # 版本/环境管理（5个模块）
│   ├── data_manage/       # 仿真数据管理
│   ├── sim_test_agv/      # 整车仿真自动化测试
│   └── sim_test_get/      # 感知取货测试
├── common/                # 工具函数（log.py 等）
├── config/
│   └── perceptionpro_cfg.py  # 外部配置（DB地址、环境变量等）
├── dev_perceptionpro/     # Django 项目入口（settings, urls, wsgi, celery）
├── media/                 # 上传文件物理存储根目录
└── test/                  # 接口测试脚本（按 app 分文件）
```

`apps/` 目录通过 `sys.path.insert` 加入路径，因此各 app 内可以用 `from apps.xxx` 直接导入。

---

## 三、核心公共组件

### 3.1 `BaseModelViewSet`（`apps/common_views/views.py`）

继承自 `ModelViewSet`，覆盖两个方法：

```python
def perform_create(self, serializer):
    serializer.save(created_by=self.request.user)

def perform_update(self, serializer):
    serializer.save(updated_by=self.request.user)
```

**所有业务 ViewSet 均以此为父类**，确保 `created_by` 和 `updated_by` 自动写入当前请求用户。

### 3.2 `HasModelPermission`（`apps/back_stage/permissions.py`）

基于 Django 内置模型权限的动态鉴权，**超级管理员无限制**。

Action → 权限类型映射：

| ViewSet action | 所需权限 |
|---------------|----------|
| `list`、`retrieve`、`creators` | `view_{model}` |
| `create` | `add_{model}` |
| `update`、`partial_update` | `change_{model}` |
| `destroy`、`batch_delete` | `delete_{model}` |
| `batch_copy` | `add_{model}` |
| `cancel` | `change_{model}` |
| 其他自定义 action（如 `upload_folder_field`、`sim_test_versions`、`choices`） | **默认放行**（`perm_type is None → return True`） |

权限字符串格式：`{app_label}.{type}_{model_name}`  
示例：`sim_test_agv.add_caseproperty`、`version_pack.delete_perenv`

> **注意**：新增自定义 action 若需要权限控制，需在 `_action_to_perm` 字典中显式声明，否则默认放行。

> **`BUSINESS_APPS`**：`back_stage/views.py` 中维护了一个集合 `{'back_stage', 'version_pack', 'common_views', 'data_manage', 'sim_test_agv', 'sim_test_get'}`，`/api/groups/all_permissions/` 接口仅返回这些 app 的权限，过滤掉 Django 内置权限。

### 3.3 `OverwriteStorage`（`apps/version_pack/models.py`）

```python
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
```

**作用**：上传同名文件时直接覆盖，不追加随机后缀。  
**使用场景**：所有需要稳定文件路径的字段（如版本文件、备份文件）均使用此存储。

### 3.4 统一响应格式（`apps/common_views/response.py`）

#### 成功响应（`CustomJSONRenderer` 自动包装）

```json
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

分页场景额外带：

```json
{
  "pagination": {
    "count": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

#### 特殊透传场景

- HTTP 204（DELETE 成功）：返回空 body
- `responseType: blob` 的请求：直接透传，不包装
- 流式响应（`StreamingHttpResponse`）：不包装

#### 错误响应（`custom_exception_handler`）

| code | 触发条件 |
|------|----------|
| 1001 | `ValidationError`（字段校验失败），`data` 包含字段→错误列表映射 |
| 2001 | `AuthenticationFailed` / `NotAuthenticated` |
| 2003 | `PermissionDenied` |
| 5000 | 其他 DRF 异常 |

### 3.5 `CommonDatetime`（`apps/common_views/models.py`）

所有业务模型的公共抽象基类，注入 4 个字段：`created_by`、`updated_by`（FK → User）、`create_time`、`update_time`。  
`abstract = True`，不产生独立数据表。

---

## 四、序列化器约定

### 4.1 通用字段模式

所有 ListSerializer 均包含 `created_by_name` 只读字段：

```python
created_by_name = serializers.CharField(
    source='created_by.username', read_only=True, default=''
)
```

### 4.2 三段式 Serializer（version_pack 模式）

对于有"不可修改字段"的模型，拆分为三个 Serializer：

| 类型 | 说明 |
|------|------|
| `XxxCreateSerializer` | 新建时使用，`exclude` 掉 `test_result`/`test_verdict`（这两个字段由测试人员后续更新） |
| `XxxUpdateSerializer` | 更新时使用，全字段，但在 `validate()` 中拦截 `version_num` 和 `version_file` 的修改 |
| `XxxListSerializer` | 列表/详情展示，附加 `env_name`、`created_by_name` 等只读字段 |

ViewSet 中通过 `get_serializer_class()` 按 `action` 分发。

### 4.3 版本号校验规则

版本号仅允许：字母、数字、点 `.`、横线 `-`、下划线 `_`，禁止中文和其他特殊字符。

### 4.4 覆盖模型必填字段为可选（sim_test_agv 模式）

`CaseProperty.lastagvpose_path` 模型层定义为必填 CharField，但在序列化器中覆盖为可选（因为首次创建时文件夹尚未上传）：

```python
lastagvpose_path = serializers.CharField(allow_blank=True, required=False, default='')
```

---

## 五、过滤器约定

### 5.1 标准过滤参数命名

| 参数名 | 含义 | lookup |
|--------|------|--------|
| `created_by` | 创建人 ID | exact |
| `create_time_after` | 创建时间起始 | `gte` |
| `create_time_before` | 创建时间截止 | `lte` |
| `{field_name}` | 各业务字段精确匹配 | exact |
| `search` | SearchFilter 全文搜索 | 由 `search_fields` 决定 |

### 5.2 模糊查询字段

业务字符串字段多使用 `icontains`，通过显式声明 `CharFilter(lookup_expr='icontains')` 实现。

### 5.3 JSON 字段过滤

`versions_type` 是 JSONField（数组），过滤时用自定义方法：

```python
def filter_versions_type(self, queryset, name, value):
    return queryset.filter(versions_type__contains=value)
```

---

## 六、文件处理约定

### 6.1 FileField 路径函数

每个 FileField 对应一个独立的路径函数（非 lambda），确保路径可序列化（Django migration 要求）。路径通常包含业务主键或 uid 作为命名空间：

```python
def per_version_path(instance, filename):
    return os.path.join('per_versions', str(instance.version_num), filename)
```

### 6.2 文件删除信号

- **`post_delete`**：删除记录时触发，清理对应的物理文件
- **`pre_save`**（部分模型）：更新时若文件字段被替换，先删除旧文件

`version_pack` 统一在模块底部用工厂函数批量注册 `post_delete`，避免重复代码。

### 6.3 文件夹上传（`sim_test_agv`）

`CaseProperty` 的 4 个路径字段（`lastagvpose_path` 等）存储文件夹路径，上传流程：

1. 前端用 `<input webkitdirectory multiple>` 选择文件夹，获取所有文件及其 `webkitRelativePath`
2. 构造 `FormData`，字段 `field_name`（目标字段名）+ `files[]`（文件对象）+ `paths[]`（相对路径）
3. 调用 `POST /api/at_case_property/{id}/upload_folder_field/`
4. 后端先 `shutil.rmtree` 删除旧文件夹，再按 paths 重建目录结构写入，最后将根文件夹路径写入模型字段

文件夹路径格式：`sim_res_bak/{sim_test_version}/{sim_test_vehicle}/{sim_scheme_name}/{field_name}/{folder_root}/`

### 6.4 文件夹下载

调用 `GET /api/at_case_property/{id}/download_folder_field/?field_name=xxx`，后端用 `zipfile` 打包目录为内存 zip，以 `StreamingHttpResponse` 返回，Content-Type 为 `application/zip`。

---

## 七、批量删除约定

所有 ViewSet 均提供 `batch_delete` action：

```
POST /api/{prefix}/batch_delete/
Body: { "ids": [1, 2, 3] }
Response: { "code": 0, "msg": "删除成功", "data": null }
```

底层调用 `Model.objects.filter(id__in=ids).delete()`，会触发 `post_delete` 信号链式删除文件。

---

## 八、ViewSet 工厂模式（version_pack）

`version_pack` 中 `Loc/Ctl/Sim/Sen` 四套模块结构完全一致，使用工厂函数动态生成 ViewSet 和 Serializer，避免重复：

```python
LocVersionViewSet = make_version_viewset(
    LocVersion, LocEnv,
    LocVersionCreateSerializer, LocVersionUpdateSerializer, LocVersionListSerializer,
    LocVersionFilter
)
```

类名通过 `_XxxViewSet.__name__ = f'{model.__name__}ViewSet'` 显式设置，确保 DRF router 和文档能正确识别。

---

## 九、认证约定

### 9.1 登录方式

- 优先走 `PhoneBackend`：使用 `phone_number` 字段匹配
- 降级走 `ModelBackend`：使用 `username` 字段匹配（Django Admin 需要）

### 9.2 Token 刷新

- 前端 401 时调用 `POST /api/token/refresh/`，携带 `refresh` token
- 后端启用 `ROTATE_REFRESH_TOKENS=True`，每次刷新会返回新的 refresh token，旧 token 进黑名单
- 若 refresh 接口本身返回 401，前端强制登出

---

## 十、`BUSINESS_APPS` 权限过滤

`back_stage/views.py` 中定义：

```python
BUSINESS_APPS = {'back_stage', 'version_pack', 'common_views', 'data_manage', 'sim_test_agv'}
```

`GET /api/groups/all_permissions/` 仅返回这些 app 的权限，过滤掉 Django 内置 app（`admin`、`auth`、`contenttypes`、`sessions`）的权限，保持前端权限选择器的简洁。

> **新增 app 时**：必须将 app label 加入此集合，否则该 app 的权限不会出现在角色配置界面。
