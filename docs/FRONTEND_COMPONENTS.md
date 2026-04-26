# 前端可复用组件与 Composable

> 本文档描述项目中所有可复用的组件和 composable，新增页面时优先查阅此文档。

---

## 一、`FileUploader.vue`（`src/components/FileUploader.vue`）

拖拽/点击上传组件，封装 `el-upload`，**不自动上传**，由父组件在提交时手动 append 到 FormData。

### Props

| Prop | 类型 | 默认 | 说明 |
|------|------|------|------|
| `accept` | String | `''` | 允许的文件类型，如 `'.zip,.yaml'` |
| `tip` | String | `''` | 上传区下方提示文字 |

### Events

| 事件 | 回调参数 | 说明 |
|------|----------|------|
| `change` | `File \| null` | 选中/移除文件时触发，参数为原生 File 对象或 null |

### Expose（父组件通过 ref 调用）

| 方法 | 说明 |
|------|------|
| `reset()` | 清空已选文件，通常在 Dialog closed 时调用 |
| `setProgress(val)` | 设置进度条百分比（0-100） |

### 使用示例

```vue
<FileUploader
  ref="fileRef"
  accept=".zip,.yaml"
  tip="请上传配置文件（必填）"
  @change="f => { selectedFile = f; form.file_guard = f?.name ?? null }"
/>
```

**文件上传提交流程**（含文件字段必须用 FormData）：

```js
const fd = new FormData()
fd.append('name', form.name)
if (selectedFile) fd.append('file_field', selectedFile)
await createXxx(fd)  // API 函数直接传 FormData，axios 自动设置 multipart
```

**新建必填 / 编辑可选** 的校验守卫写法：

```js
// 在 form 中增加一个守卫字段
form.file_guard = null

const rules = {
  file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedFile) cb(new Error('请上传文件'))
      else cb()
    },
    trigger: 'change',
  }],
}
```

---

## 二、`usePagination`（`src/composables/usePagination.js`）

通用列表分页 composable，封装了分页状态、加载状态、过滤参数、翻页逻辑。

### 签名

```js
const {
  loading,          // Ref<boolean>  - 请求中 loading 状态
  tableData,        // Ref<Array>    - 当前页数据
  pagination,       // Reactive      - { page, page_size, total, total_pages }
  filters,          // Reactive      - 查询参数（可直接 v-model 绑定）
  fetchData,        // (extraParams?) => void  - 用当前 pagination+filters 拉数据
  handlePageChange, // (page) => void          - 切换页码
  handleSizeChange, // (size) => void          - 切换每页大小（重置到第1页）
  resetAndFetch,    // (newFilters?) => void   - 覆盖 filters 并重置到第1页拉数据
} = usePagination(apiFn, defaultParams?)
```

### 参数

| 参数 | 说明 |
|------|------|
| `apiFn` | API 函数，接受 `params` 对象，返回 Promise。响应需符合 `{ data: [], pagination: { count, page, page_size, total_pages } }` |
| `defaultParams` | 可选，初始过滤参数（会合并进 `filters`） |

### 使用示例

```vue
<script setup>
import { usePagination } from '@/composables/usePagination'
import { getVersionList } from '@/api/version'

const { loading, tableData, pagination, filters, fetchData,
        handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getVersionList)

fetchData()  // 初始加载

// 搜索按钮
function handleSearch() {
  resetAndFetch(filters)  // 用当前 filters 重置并拉取
}

// 重置按钮
function handleReset() {
  Object.assign(filters, { search: '', created_by: '' })
  resetAndFetch({})
}
</script>

<template>
  <el-table v-loading="loading" :data="tableData" />
  <el-pagination
    v-model:current-page="pagination.page"
    v-model:page-size="pagination.page_size"
    :total="pagination.total"
    @current-change="handlePageChange"
    @size-change="handleSizeChange"
  />
</template>
```

---

## 三、`useFormErrors`（`src/composables/useFormErrors.js`）

处理后端字段级校验错误，将 `code: 1001` 的错误数组映射到表单项。

### 后端错误格式

```json
{
  "code": 1001,
  "msg": "参数校验失败",
  "data": [
    { "field": "version_num", "message": "该版本号已存在" },
    { "field": "env", "message": "关联环境不存在" }
  ]
}
```

### 使用示例

```vue
<script setup>
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

async function handleSubmit() {
  try {
    await createXxx(payload)
  } catch (err) {
    if (err?.response?.data) applyServerErrors(err.response.data)
    else ElMessage.error('操作失败')
  }
}
</script>

<template>
  <!-- :error 绑定 serverErrors 对应字段，有值时显示红色提示 -->
  <el-form-item label="版本号" prop="version_num" :error="serverErrors.version_num">
    <el-input v-model="form.version_num" />
  </el-form-item>
</template>
```

## 五、`NotFound.vue`（`src/views/NotFound.vue`）

404 页面，嵌套在 `BasicLayout` 下，保留侧边栏和顶栏。

- 显示品牌红大字 **404** + 说明文字
- 提供「返回首页」按钮，跳转到 `/`
- 由路由 `/:pathMatch(.*)*` 兜底匹配自动展示，无需手动引用

---

## 六、`BasicLayout.vue`（`src/layout/BasicLayout.vue`）

全局主布局，除登录/回调页外所有路由的父容器。

### 侧边栏

| 特性 | 说明 |
|------|------|
| 配色 | 背景 `#f0f2f5`，文字 `#303133`，边框 `#e0e3e8` |
| 激活高亮 | `:deep(.el-menu-item.is-active)` → `background-color: #1890ff` |
| 折叠 | `isCollapsed` ref 控制，宽度 `220px` ↔ `64px`，动画 0.3s |
| Logo 折叠过渡 | 文字用 `<Transition name="logo-fade">` 包裹，淡出 0.15s；折叠时 logo 区 padding 收为 0 使图标自动居中 |

### 顶栏（Header）

- `position: sticky; top: 0; z-index: 10`，页面内容滚动时始终可见
- 右侧头像点击触发隐藏 `<input type="file">` 实现头像上传（3MB 限制）
- 下拉菜单：修改密码 / 退出登录

### 面包屑

由路由 `meta.title`、`meta.parentTitle`、`meta.parentPath` 自动生成，无需手动维护。

### 自动弹出修改密码

```js
watch(() => authStore.userInfo?.is_default_password, (val) => {
  if (val) changePwdVisible.value = true
}, { immediate: true })
```

用户首次通过钉钉登录（默认密码 `Test123456`）时，进入主界面后自动弹出修改密码对话框。

---

在逻辑层（非模板）判断权限，通常用于条件性执行代码。

```js
const { hasPermission, canDo, isSuperUser } = usePermission()

// 单权限判断
if (hasPermission('sim_test_agv.add_caseproperty')) {
  // 执行需要权限的操作
}

// 多权限（任一满足）
if (canDo(['app.add_model', 'app.change_model'])) {
  showOperationMenu.value = true
}
```

> 模板中推荐直接用 `v-permission` 指令，逻辑层用此 composable。

---

## 五、FormDialog 标准模式

所有新建/编辑弹框遵循统一模式，关键要点如下：

### 模板结构

```vue
<el-dialog
  v-model="visible"
  :title="isEdit ? '编辑xxx' : '新建xxx'"
  width="600px"
  :close-on-click-modal="false"
  @closed="handleClosed"
>
  <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
    ...
  </el-form>
  <template #footer>
    <el-button @click="visible = false">取消</el-button>
    <el-button type="primary" :loading="submitting" @click="handleSubmit">
      {{ isEdit ? '保存' : '创建' }}
    </el-button>
  </template>
</el-dialog>
```

### Script 骨架

```js
const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])

// visible 双向绑定（v-model:visible）
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const submitting = ref(false)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()
const form = reactive({ field1: '', field2: '' })

// 弹框打开时初始化表单
watch(() => props.visible, val => {
  if (val) {
    clearServerErrors()
    if (props.editData) {
      Object.assign(form, props.editData)  // 编辑：回填数据
    } else {
      Object.assign(form, { field1: '', field2: '' })  // 新建：清空
    }
  }
})

// 提交
async function handleSubmit() {
  await formRef.value.validate()  // 前端校验
  submitting.value = true
  try {
    isEdit.value
      ? await updateXxx(props.editData.id, form)
      : await createXxx(form)
    ElMessage.success(isEdit.value ? '修改成功' : '创建成功')
    visible.value = false
    emit('success')
  } catch (err) {
    if (err?.response?.data) applyServerErrors(err.response.data)
    else ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// Dialog 关闭后（动画结束后）清理
function handleClosed() {
  formRef.value?.resetFields()
  clearServerErrors()
}
```

### 有文件字段的额外处理

```js
const fileRef = ref(null)
let selectedFile = null

// watch 中额外重置
fileRef.value?.reset?.()
selectedFile = null

// handleSubmit 中改用 FormData
const fd = new FormData()
Object.entries(form).forEach(([k, v]) => {
  if (k !== 'file_guard') fd.append(k, v ?? '')
})
if (selectedFile) fd.append('file_field', selectedFile)
```

---

## 六、ListPage 标准模式

所有列表页遵循统一结构：

```
filter-card（筛选区）
  └─ el-form inline（各过滤字段 + 搜索/重置按钮）
table-card（表格区）
  ├─ toolbar（新建 + 批量操作按钮 + 刷新按钮）
  ├─ el-table（含 selection 列、数据列、操作列）
  └─ pagination-wrapper（el-pagination）
FormDialog（v-model:visible）
```

**批量删除**惯用写法：

```js
const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteXxx(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}
```

**创建人下拉**惯用写法（`onMounted` 拉取）：

```js
const creators = ref([])
onMounted(async () => {
  const res = await getXxxCreators()
  creators.value = Array.isArray(res) ? res : (res.data || [])
})
```

```html
<el-select v-model="filters.created_by" placeholder="全部" clearable filterable>
  <el-option v-for="u in creators" :key="u.id" :label="u.username" :value="u.id" />
</el-select>
```
