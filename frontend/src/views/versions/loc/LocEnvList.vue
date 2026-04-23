<template>
  <div class="loc-env-list">
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline>
        <el-form-item label="环境名称">
          <el-input v-model="filters.search" placeholder="环境名称模糊查询" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="适用专项">
          <el-input v-model="filters.apply_project" placeholder="适用专项" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="创建人">
          <el-select v-model="filters.created_by" placeholder="全部" clearable filterable style="width: 130px">
            <el-option v-for="u in envCreatorOptions" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="filters.create_time_after" type="datetime" placeholder="开始日期" value-format="YYYY-MM-DD HH:mm:ss" style="width: 180px" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="filters.create_time_before" type="datetime" placeholder="结束日期" value-format="YYYY-MM-DD HH:mm:ss" style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="resetAndFetch(filters)">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 12px">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button v-if="canAdd" type="primary" :icon="Plus" @click="openCreateDialog">新建环境</el-button>
          <el-button v-if="canDelete" type="danger" :icon="Delete" :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-empty v-if="!canView" description="暂无数据查看权限" style="padding: 40px 0" />
      <el-table
        v-else
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%; margin-top: 12px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column v-if="canDelete" type="selection" width="50" />
        <el-table-column prop="env_name" label="环境名称" min-width="160" />
        <el-table-column prop="apply_project" label="适用专项" width="130" />
        <el-table-column prop="env_note" label="环境描述" width="100">
          <template #default="{ row }">
            <el-button v-if="row.env_note" type="primary" link @click="showDetail(row.env_note, '环境描述')">展示</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="env_file" label="环境文件" width="100">
          <template #default="{ row }">
            <a v-if="row.env_file" :href="row.env_file" target="_blank" class="download-link">下载</a>
            <span v-else>-</span>
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
            <el-button v-if="canChange" type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm v-if="canDelete" title="确认删除该环境？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="canView" class="pagination-wrapper">
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

    <LocEnvFormDialog v-model:visible="formDialogVisible" :edit-data="editRow" @success="fetchData()" />

    <el-dialog v-model="detailVisible" :title="detailTitle" width="600px">
      <pre class="detail-content">{{ detailContent }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { locApi } from '@/api/version'
import { usePagination } from '@/composables/usePagination'
import { usePermission } from '@/composables/usePermission'
import LocEnvFormDialog from './LocEnvFormDialog.vue'

const { hasPermission } = usePermission()
const canView   = hasPermission('version_pack.view_locenv')
const canAdd    = hasPermission('version_pack.add_locenv')
const canChange = hasPermission('version_pack.change_locenv')
const canDelete = hasPermission('version_pack.delete_locenv')

const {
  loading, tableData, pagination, filters,
  fetchData, handlePageChange, handleSizeChange, resetAndFetch,
} = usePagination(locApi.getEnvList)

if (canView) fetchData()

function handleReset() {
  Object.assign(filters, { search: '', apply_project: '', created_by: '', create_time_after: '', create_time_before: '' })
  resetAndFetch({})
}

const envCreatorOptions = ref([])
onMounted(async () => {
  if (!canView) return
  try {
    const res = await locApi.getEnvCreators()
    envCreatorOptions.value = res.data ?? []
  } catch {}
})

const detailVisible = ref(false)
const detailTitle = ref('')
const detailContent = ref('')
function showDetail(content, title) { detailTitle.value = title; detailContent.value = content; detailVisible.value = true }

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map((r) => r.id) }

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 个环境？`, '批量删除', { type: 'warning' })
  await locApi.batchDeleteEnvs(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleDelete(id) {
  await locApi.deleteEnv(id)
  ElMessage.success('删除成功')
  fetchData()
}

const formDialogVisible = ref(false)
const editRow = ref(null)
function openCreateDialog() { editRow.value = null; formDialogVisible.value = true }
function openEditDialog(row) { editRow.value = { ...row }; formDialogVisible.value = true }
function formatTime(t) { if (!t) return '-'; return new Date(t).toLocaleString('zh-CN', { hour12: false }) }
</script>

<style scoped>
.loc-env-list { max-width: 1400px; }
.filter-card :deep(.el-card__body) { padding: 16px 20px 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
.download-link { color: #409eff; text-decoration: none; }
.download-link:hover { text-decoration: underline; }
.detail-content { white-space: pre-wrap; word-break: break-all; font-size: 13px; line-height: 1.6; }
</style>
