<template>
  <div class="version-list">
    <!-- 搜索筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline>
        <el-form-item label="版本号">
          <el-input
            v-model="filters.version_num"
            placeholder="版本号关键词"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="测试结果">
          <el-select
            v-model="filters.test_result"
            placeholder="全部"
            clearable
            style="width: 140px"
          >
            <el-option label="未开始" value="未开始" />
            <el-option label="测试中" value="测试中" />
            <el-option label="通过" value="通过" />
            <el-option label="不通过" value="不通过" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用专项">
          <el-input
            v-model="filters.apply_project"
            placeholder="适用专项"
            clearable
            style="width: 140px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="resetAndFetch(filters)">
            搜索
          </el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card shadow="never" style="margin-top: 12px">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            v-permission="'version:create'"
            type="primary"
            :icon="Plus"
            @click="openCreateDialog"
          >
            新建版本
          </el-button>
          <el-button
            v-permission="'version:delete'"
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
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%; margin-top: 12px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="version_num" label="版本号" min-width="140" />
        <el-table-column prop="versions_type" label="版本类型" width="130">
          <template #default="{ row }">
            <span>{{ formatVersionsType(row.versions_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="apply_project" label="适用专项" width="120" />
        <el-table-column prop="test_result" label="测试结果" width="100">
          <template #default="{ row }">
            <el-tag :type="testResultTagType(row.test_result)">{{ row.test_result ?? '未开始' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dev_test_result" label="研发提测" min-width="180" show-overflow-tooltip />
        <el-table-column prop="env" label="关联环境" width="130">
          <template #default="{ row }">
            {{ row.env_detail?.env_name ?? (row.env ? `#${row.env}` : '-') }}
          </template>
        </el-table-column>
        <el-table-column prop="version_file" label="版本文件" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.version_file" type="success" size="small">已上传</el-tag>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-permission="'version:edit'"
              type="primary"
              link
              @click="openEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              v-permission="'version:upload'"
              type="success"
              link
              @click="openUploadDialog(row)"
            >
              上传文件
            </el-button>
            <el-popconfirm
              title="确认删除该版本？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button v-permission="'version:delete'" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新建 / 编辑弹窗 -->
    <VersionFormDialog
      v-model:visible="formDialogVisible"
      :edit-data="editRow"
      @success="fetchData()"
    />

    <!-- 文件上传弹窗 -->
    <VersionUploadDialog
      v-model:visible="uploadDialogVisible"
      :row="uploadRow"
      @success="fetchData()"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { getVersionList, batchDeleteVersions, deleteVersion } from '@/api/version'
import { usePagination } from '@/composables/usePagination'
import VersionFormDialog from './VersionFormDialog.vue'
import VersionUploadDialog from './VersionUploadDialog.vue'

// ── 分页 + 列表 ────────────────────────────────────────────────────
const {
  loading,
  tableData,
  pagination,
  filters,
  fetchData,
  handlePageChange,
  handleSizeChange,
  resetAndFetch,
} = usePagination(getVersionList)

fetchData() // 初始加载

// ── 筛选重置 ────────────────────────────────────────────────────────
function handleReset() {
  filters.version_num = ''
  filters.test_result = ''
  filters.apply_project = ''
  resetAndFetch({})
}

// ── 多选 ────────────────────────────────────────────────────────────
const selectedIds = ref([])
function handleSelectionChange(rows) {
  selectedIds.value = rows.map((r) => r.id)
}

// ── 批量删除 ────────────────────────────────────────────────────────
async function handleBatchDelete() {
  await ElMessageBox.confirm(
    `确认删除选中的 ${selectedIds.value.length} 个版本？`,
    '批量删除',
    { type: 'warning' },
  )
  await batchDeleteVersions(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

// ── 单条删除 ────────────────────────────────────────────────────────
async function handleDelete(id) {
  await deleteVersion(id)
  ElMessage.success('删除成功')
  fetchData()
}

// ── 新建 / 编辑弹窗 ────────────────────────────────────────────────
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

// ── 文件上传弹窗 ────────────────────────────────────────────────────
const uploadDialogVisible = ref(false)
const uploadRow = ref(null)

function openUploadDialog(row) {
  uploadRow.value = row
  uploadDialogVisible.value = true
}

// ── 工具函数 ────────────────────────────────────────────────────────
const TEST_RESULT_TYPE = {
  '未开始': 'info',
  '测试中': 'warning',
  '通过': 'success',
  '不通过': 'danger',
}

function testResultTagType(val) {
  return TEST_RESULT_TYPE[val] ?? 'info'
}

function formatVersionsType(val) {
  if (!val) return '-'
  if (Array.isArray(val)) return val.join('、')
  if (typeof val === 'object') return Object.values(val).join('、')
  return val
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.version-list {
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
</style>
