<template>
  <div class="user-management">
    <!-- 筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="用户名">
          <el-input
            v-model="filters.username"
            placeholder="用户名关键词"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input
            v-model="filters.phone_number"
            placeholder="手机号关键词"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item label="账号类型">
          <el-select v-model="filters.is_staff" placeholder="全部" clearable style="width: 120px">
            <el-option label="管理员" :value="true" />
            <el-option label="普通用户" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="账号状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable style="width: 110px">
            <el-option label="正常" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="resetAndFetch(filters)">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 + 表格 -->
    <el-card shadow="never" style="margin-top: 12px">
      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建用户</el-button>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%; margin-top:12px">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="phone_number" label="手机号" width="140" />
        <el-table-column label="角色" min-width="160">
          <template #default="{ row }">
            <el-tag
              v-for="name in row.group_names"
              :key="name"
              size="small"
              style="margin-right: 4px"
            >{{ name }}</el-tag>
            <span v-if="!row.group_names?.length">-</span>
          </template>
        </el-table-column>
        <el-table-column label="账号类型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_staff ? 'warning' : 'info'" size="small">
              {{ row.is_staff ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="超级管理员" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_superuser ? 'danger' : 'info'" size="small">
              {{ row.is_superuser ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="账号状态" width="100">
          <template #default="{ row }">
            <el-button
              :type="row.is_active ? 'success' : 'danger'"
              size="small"
              :loading="!!toggling[row.id]"
              @click="toggleActive(row)"
            >
              {{ row.is_active ? '正常' : '禁用' }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110">
          <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <template v-if="canModify(row)">
              <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-popconfirm title="确认删除该用户？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-button type="danger" link>删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <UserFormDialog
      v-model:visible="dialogVisible"
      :edit-data="editRow"
      :group-options="groupOptions"
      :is-super-user="isSuperUser"
      @success="fetchData()"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getUserList, deleteUser, updateUser, getGroupList } from '@/api/admin'
import { usePagination } from '@/composables/usePagination'
import { useAuthStore } from '@/stores/auth'
import UserFormDialog from './UserFormDialog.vue'

const authStore = useAuthStore()
const isSuperUser = authStore.isSuperUser
const isStaff = authStore.isStaff

function canModify(row) {
  if (isSuperUser) return true
  if (isStaff && !row.is_superuser) return true
  return false
}

const {
  loading, tableData, pagination, filters,
  fetchData, handlePageChange, handleSizeChange, resetAndFetch,
} = usePagination(getUserList)

fetchData()

function handleReset() {
  Object.assign(filters, {
    username: '', phone_number: '', is_staff: '', is_active: '',
  })
  resetAndFetch({})
}

// ── 角色选项（用于弹窗） ──────────────────────────────────────────
const groupOptions = ref([])

onMounted(async () => {
  try {
    const res = await getGroupList({ page_size: 999 })
    groupOptions.value = res.data ?? []
  } catch {
    // 加载失败不影响主界面
  }
})

// ── 删除 ────────────────────────────────────────────────────────────
async function handleDelete(id) {
  try {
    await deleteUser(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {
    // 错误已在拦截器中统一提示
  }
}

// ── 弹窗 ────────────────────────────────────────────────────────────
const dialogVisible = ref(false)
const editRow = ref(null)

function openCreateDialog() {
  editRow.value = null
  dialogVisible.value = true
}

function openEditDialog(row) {
  editRow.value = { ...row }
  dialogVisible.value = true
}

// 账号状态切换
const toggling = reactive({})
async function toggleActive(row) {
  if (toggling[row.id]) return
  toggling[row.id] = true
  try {
    await updateUser(row.id, { is_active: !row.is_active })
    row.is_active = !row.is_active
  } catch {
    // 错误已在拦截器中统一提示
  } finally {
    toggling[row.id] = false
  }
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.user-management {
  max-width: 1400px;
}

.filter-card :deep(.el-card__body) {
  padding: 16px 20px 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
