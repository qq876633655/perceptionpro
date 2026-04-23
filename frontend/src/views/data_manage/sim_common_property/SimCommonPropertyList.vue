<template>
  <div class="sim-common-property-list">
    <!-- 搜索筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline>
        <el-form-item label="标签">
          <el-input
            v-model="filters.property_tag"
            placeholder="标签模糊查询"
            clearable
            style="width: 140px"
          />
        </el-form-item>
        <el-form-item label="创建人">
          <el-select
            v-model="filters.created_by"
            placeholder="全部"
            clearable
            filterable
            style="width: 130px"
          >
            <el-option
              v-for="u in creatorOptions"
              :key="u.id"
              :label="u.username"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="filters.create_time_after"
            type="datetime"
            placeholder="开始日期"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filters.create_time_before"
            type="datetime"
            placeholder="结束日期"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="resetAndFetch(filters)">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card shadow="never" style="margin-top: 12px">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button v-if="canAdd" type="primary" :icon="Plus" @click="openCreateDialog">
            新建数据
          </el-button>
          <el-button
            v-if="canDelete"
            type="danger"
            :icon="Delete"
            :disabled="!selectedIds.length"
            @click="handleBatchDelete"
          >
            批量删除 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <!-- 数据表格 -->
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
        <el-table-column prop="versions" label="版本号" width="120" />
        <el-table-column prop="property_tag" label="标签" width="120">
          <template #default="{ row }">{{ row.property_tag || '-' }}</template>
        </el-table-column>
        <el-table-column prop="property_desc" label="资产说明" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.property_desc || '-' }}</template>
        </el-table-column>
        <el-table-column prop="common_property" label="通用资产" width="100">
          <template #default="{ row }">
            <a v-if="row.common_property" :href="row.common_property" target="_blank" class="download-link">
              下载
            </a>
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
            <el-popconfirm v-if="canDelete" title="确认删除该数据？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新建 / 编辑弹窗 -->
    <SimCommonPropertyFormDialog
      v-model:visible="formDialogVisible"
      :edit-data="editRow"
      @success="fetchData()"
    />

    <!-- 详情展示弹窗 -->
    <el-dialog v-model="detailVisible" :title="detailTitle" width="600px">
      <pre class="detail-content">{{ detailContent }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import {
  getSimCommonPropertyList,
  getSimCommonPropertyCreators,
  deleteSimCommonProperty,
  batchDeleteSimCommonProperties,
} from '@/api/data_manage'
import { usePagination } from '@/composables/usePagination'
import { usePermission } from '@/composables/usePermission'
import SimCommonPropertyFormDialog from './SimCommonPropertyFormDialog.vue'

// ── 权限控制 ────────────────────────────────────────────────
const { hasPermission } = usePermission()
const canView   = hasPermission('data_manage.view_simcommonproperty')
const canAdd    = hasPermission('data_manage.add_simcommonproperty')
const canChange = hasPermission('data_manage.change_simcommonproperty')
const canDelete = hasPermission('data_manage.delete_simcommonproperty')

// ── 分页 + 列表 ──────────────────────────────────────────────
const {
  loading,
  tableData,
  pagination,
  filters,
  fetchData,
  handlePageChange,
  handleSizeChange,
  resetAndFetch,
} = usePagination(getSimCommonPropertyList, {
  property_tag: '',
  created_by: null,
  create_time_after: null,
  create_time_before: null,
})

// ── 创建人下拉选项 ────────────────────────────────────────────
const creatorOptions = ref([])

async function loadCreators() {
  try {
    const res = await getSimCommonPropertyCreators()
    creatorOptions.value = res.data ?? res
  } catch {
    // ignore
  }
}

// ── 批量删除 ─────────────────────────────────────────────────
const selectedIds = ref([])

function handleSelectionChange(rows) {
  selectedIds.value = rows.map((r) => r.id)
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条数据？`, '批量删除', {
    type: 'warning',
  })
  await batchDeleteSimCommonProperties(selectedIds.value)
  ElMessage.success('删除成功')
  selectedIds.value = []
  fetchData()
}

async function handleDelete(id) {
  await deleteSimCommonProperty(id)
  ElMessage.success('删除成功')
  fetchData()
}

// ── 弹窗 ───────────────────────────────────────────────────────
const formDialogVisible = ref(false)
const editRow = ref(null)

function openCreateDialog() {
  editRow.value = null
  formDialogVisible.value = true
}

function openEditDialog(row) {
  editRow.value = { ...row }
  formDialogVisible.value = true
}

// ── 搜索重置 ─────────────────────────────────────────────────
function handleReset() {
  Object.assign(filters, {
    property_tag: '',
    created_by: null,
    create_time_after: null,
    create_time_before: null,
  })
  pagination.page = 1
  fetchData()
}

// ── 详情弹窗 ─────────────────────────────────────────────────
const detailVisible = ref(false)
const detailTitle = ref('')
const detailContent = ref('')

function showDetail(content, title) {
  detailTitle.value = title
  detailContent.value = content
  detailVisible.value = true
}

// ── 工具函数 ─────────────────────────────────────────────────
function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchData()
  loadCreators()
})
</script>

<style scoped>
.sim-common-property-list {
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

.toolbar-left {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.download-link {
  color: #409eff;
  text-decoration: none;
}

.download-link:hover {
  text-decoration: underline;
}

.detail-content {
  white-space: pre-wrap;
  word-break: break-all;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}
</style>
