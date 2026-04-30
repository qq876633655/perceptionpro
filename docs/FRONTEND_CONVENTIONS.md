# 前端架构与全局约定

> 框架：Vue 3 (Composition API) + Vite + Element Plus + Pinia + Axios  
> 项目目录：`frontend/`  
> 开发服务器：`npm run dev`（端口 5173，代理 `/api` → `http://10.20.24.62:8009`）

---

## 一、技术栈

| 依赖 | 版本 | 用途 |
|------|------|------|
| Vue 3 | latest | 核心框架（Composition API / `<script setup>`） |
| Vite | latest | 构建工具，支持 HMR |
| Element Plus | latest | UI 组件库 |
| Pinia | latest | 状态管理 |
| Vue Router 4 | latest | 路由（createWebHistory） |
| Axios | latest | HTTP 请求 |
| unplugin-auto-import | latest | Vue/Vue Router/Pinia API 自动导入（无需手动 import ref/computed 等） |
| unplugin-vue-components | latest | Element Plus 组件自动注册（无需手动 import ElButton 等） |

---

## 二、自动导入配置（`vite.config.js`）

```js
AutoImport({
  resolvers: [ElementPlusResolver()],
  imports: ['vue', 'vue-router', 'pinia'],  // ref/computed/watch/useRouter/defineStore 等全局可用
})
Components({
  resolvers: [ElementPlusResolver()],       // Element Plus 组件全局注册，无需 import
})
```

**影响**：
- `ref`、`reactive`、`computed`、`watch`、`onMounted` 等 **直接使用，无需 import**
- `ElButton`、`ElTable`、`ElDialog` 等 Element Plus 组件 **直接使用，无需 import**
- Element Plus 图标（`<HomeFilled />`、`<Setting />` 等）同样自动注册

---

## 三、路径别名

```js
// vite.config.js
resolve: { alias: { '@': '/frontend/src' } }
```

所有源码内用 `@/` 代替 `src/`，如 `import { useAuthStore } from '@/stores/auth'`。

---

## 四、`request.js` HTTP 封装（`src/utils/request.js`）

### 基础配置

```js
const service = axios.create({
  baseURL: '/api',   // 所有请求前缀为 /api，vite dev server 代理到后端
  timeout: 15000,
})
```

### 请求拦截器
自动从 `useAuthStore().token` 读取并注入 `Authorization: Bearer <token>` 头。

### 响应拦截器

| 场景 | 处理方式 |
|------|----------|
| HTTP 204 | 返回 `{ code: 0, msg: 'success', data: null }` |
| `responseType: 'blob'` | 直接返回 `response.data`（文件下载不包装） |
| `res.code === 0` | 直接返回整个 `res` 对象（`{ code, msg, data, pagination? }`） |
| `res.code !== 0` | `ElMessage.error(res.msg)` + `Promise.reject(res)` |
| HTTP 401（首次） | 自动用 refresh token 换新 access token，并重试原请求 |
| HTTP 401（并发） | 后续请求排队等待刷新完成后统一重试 |
| refresh token 失效 | 强制登出并跳转 `/login` |
| HTTP 403 | `ElMessage.error('权限不足')` |
| HTTP 500 | `ElMessage.error('服务器错误...')` |

### 调用方式

```js
// 普通请求
const res = await getVersionList({ page: 1, page_size: 10 })
// res = { code: 0, msg: 'success', data: [...], pagination: {...} }
const list = res.data ?? []

// 文件下载（blob流）
import { downloadBlob } from '@/utils/request'
await downloadBlob('/at_case_property/1/download_folder_field/?field_name=ply_path', 'folder.zip')
```

### 取数据惯用写法

```js
// 列表：后端分页时 data 直接是数组
tableData.value = res.data ?? []

// 创建人/choices 等非分页接口
creators.value = Array.isArray(res) ? res : (res.data || [])

// choices 接口（返回 { sim_test_version: [], ... }）
const c = res.data ?? res
choices.value = { sim_test_version: c.sim_test_version ?? [] }
```

---

## 五、Auth Store（`src/stores/auth.js`）

```js
const authStore = useAuthStore()
```

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `token` | string | access token（localStorage `pp_token`） |
| `refreshTokenVal` | string | refresh token（localStorage `pp_refresh_token`） |
| `userInfo` | object \| null | `{ id, username, phone_number, is_staff, is_superuser, roles, permissions }` |
| `isLoggedIn` | getter | `!!token` |
| `isStaff` | getter | `userInfo.is_staff` |
| `isSuperUser` | getter | `userInfo.is_superuser` |
| `permissions` | getter | `userInfo.permissions`（Django 权限码数组） |
| `hasPermission(perm)` | getter fn | 判断是否拥有某权限码 |
| `hasRole(role)` | getter fn | 判断是否拥有某角色 |
| `loginAction(credentials)` | action | 登录并保存 token |
| `fetchUserInfo()` | action | 拉取 `/api/me/` |
| `logout()` | action | 清除所有状态并清 localStorage |

---

## 六、权限系统

### 权限码格式

Django 格式：`'{app_label}.{action}_{model_name}'`

```
sim_test_agv.add_caseproperty
version_pack.delete_perversion
sim_test_get.change_gettesttarget
```

### `v-permission` 指令（`src/directives/permission.js`）

```html
<!-- 不具备权限时，元素从 DOM 移除 -->
<el-button v-permission="'sim_test_agv.add_caseproperty'">新建</el-button>

<!-- 多权限：任一满足即显示 -->
<el-button v-permission="['app.add_model', 'app.change_model']">操作</el-button>
```

超级管理员（`is_superuser`）始终通过，不受权限限制。

### `usePermission` composable（`src/composables/usePermission.js`）

```js
const { hasPermission, canDo, isSuperUser } = usePermission()

// 单权限
if (hasPermission('version_pack.add_perversion')) { ... }

// 多权限（任一满足）
if (canDo(['app.add_model', 'app.change_model'])) { ... }
```

### 侧边栏可见性控制

```html
<!-- 仅 is_staff 可见 -->
<el-sub-menu v-if="authStore.userInfo?.is_staff" index="/system">

<!-- 所有登录用户可见（无 v-if） -->
<el-sub-menu index="/versions">
```

---

## 七、项目目录结构

```
frontend/src/
├── api/                   # 各模块 API 函数（按后端 app 分文件）
│   ├── auth.js
│   ├── admin.js
│   ├── version.js
│   ├── data_manage.js
│   ├── sim_test_agv.js
│   └── sim_test_get.js
├── assets/                # 静态资源
├── components/            # 全局公共组件
│   ├── FileUploader.vue
│   └── ChangePasswordDialog.vue
├── composables/           # 可复用逻辑
│   ├── usePagination.js
│   ├── useFormErrors.js
│   └── usePermission.js
├── directives/
│   └── permission.js      # v-permission 指令
├── layout/
│   └── BasicLayout.vue    # 主布局（侧边栏+顶栏+面包屑）
├── router/
│   └── index.js           # 路由配置 + 全局前置守卫
├── stores/
│   └── auth.js            # Pinia Auth Store
├── utils/
│   └── request.js         # Axios 封装
├── views/                 # 页面组件（按模块目录组织）
│   ├── Login.vue
│   ├── Dashboard.vue
│   ├── system/
│   ├── versions/          # version_pack 相关页面
│   ├── data_manage/
│   ├── sim_test_agv/
│   └── sim_test_get/
├── App.vue
└── main.js
```
