<template>
  <div class="at-version-list">
    <!-- 搜索筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="版本号">
          <el-input v-model="filters.search" placeholder="版本号模糊查询" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="版本类型">
          <el-select v-model="filters.versions_type" placeholder="全部" clearable style="width: 120px">
            <el-option label="feature" value="feature" />
            <el-option label="dev" value="dev" />
            <el-option label="test" value="test" />
            <el-option label="hotfix" value="hotfix" />
            <el-option label="release" value="release" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用专项">
          <el-input v-model="filters.apply_project" placeholder="适用专项" clearable style="width: 130px" />
        </el-form-item>
        <el-form-item label="关联环境">
          <el-select v-model="filters.env" placeholder="全部" clearable filterable style="width: 150px">
            <el-option v-for="env in envFilterOptions" :key="env.id" :label="env.env_name" :value="env.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试结果">
          <el-select v-model="filters.test_result" placeholder="全部" clearable style="width: 110px">
            <el-option label="未开始" value="未开始" />
            <el-option label="测试中" value="测试中" />
            <el-option label="通过" value="通过" />
            <el-option label="失败" value="失败" />
            <el-option label="中断" value="中断" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建人">
          <el-select v-model="filters.created_by" placeholder="全部" clearable filterable style="width: 130px">
            <el-option v-for="u in userFilterOptions" :key="u.id" :label="u.username" :value="u.id" />
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

    <!-- 操作栏 -->
    <el-card shadow="never" style="margin-top: 12px">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button v-if="canAdd" type="primary" :icon="Plus" @click="openCreateDialog">新建版本</el-button>
          <el-button v-if="canDelete" type="danger" :icon="Delete" :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
          </el-button>
          <el-button @click="$router.push('/envs/at')">版本环境</el-button>
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
        <el-table-column prop="version_num" label="版本号" min-width="140" />
        <el-table-column prop="versions_type" label="版本类型" min-width="190">
          <template #default="{ row }">
            <template v-if="Array.isArray(row.versions_type) && row.versions_type.length">
              <el-tag v-for="t in row.versions_type" :key="t" :type="versionTypeTagType(t)" size="small" style="margin-right: 4px; margin-bottom: 2px">{{ t }}</el-tag>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="apply_project" label="适用专项" width="120" />
        <el-table-column prop="env_name" label="关联环境" width="130">
          <template #default="{ row }">{{ row.env_name ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="version_file" label="版本文件" width="90">
          <template #default="{ row }">
            <a v-if="row.version_file" :href="row.version_file" target="_blank" class="download-link">下载</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="dev_test_result" label="研发提测" width="90">
          <template #default="{ row }">
            <el-button v-if="row.dev_test_result" type="primary" link @click="openDetail('研发提测', row.dev_test_result)">展示</el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="test_result" label="测试结果" width="110">
          <template #default="{ row }">
            <el-button :type="testResultTagType(row.test_result)" size="small" :loading="!!cycling[row.id]" :disabled="!canChange" @click="cycleTestResult(row)">
              {{ row.test_result ?? '未开始' }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="test_verdict" label="测试总结" width="90">
          <template #default="{ row }">
            <el-button v-if="row.test_verdict" type="primary" link @click="openDetail('测试总结', row.test_verdict)">展示</el-button>
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
            <el-popconfirm v-if="canDelete" title="确认删除该版本？" @confirm="handleDelete(row.id)">
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

    <AtVersionFormDialog v-model:visible="formDialogVisible" :edit-data="editRow" @success="fetchData()" />

    <el-dialog v-model="detailVisible" :title="detailTitle" width="600px">
      <pre class="detail-content">{{ detailContent }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { atApi } from '@/api/version'
import { usePagination } from '@/composables/usePagination'
import { usePermission } from '@/composables/usePermission'
import AtVersionFormDialog from './AtVersionFormDialog.vue'

const { hasPermission } = usePermission()
const canView   = hasPermission('version_pack.view_atversion')
const canAdd    = hasPermission('version_pack.add_atversion')
const canChange = hasPermission('version_pack.change_atversion')
const canDelete = hasPermission('version_pack.delete_atversion')

const {
  loading, tableData, pagination, filters,
  fetchData, handlePageChange, handleSizeChange, resetAndFetch,
} = usePagination(atApi.getVersionList)

if (canView) fetchData()

function handleReset() {
  Object.assign(filters, {
    search: '', versions_type: '', apply_project: '', env: '',
    test_result: '', created_by: '', create_time_after: '', create_time_before: '',
  })
  resetAndFetch({})
}

const envFilterOptions = ref([])
const userFilterOptions = ref([])

onMounted(async () => {
  if (!canView) return
  try {
    const [envRes, creatorsRes] = await Promise.all([
      atApi.getEnvList({ page_size: 999 }),
      atApi.getVersionCreators(),
    ])
    envFilterOptions.value = envRes.data ?? []
    userFilterOptions.value = creatorsRes.data ?? []
  } catch {}
})

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map((r) => r.id) }

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 个版本？`, '批量删除', { type: 'warning' })
  await atApi.batchDeleteVersions(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleDelete(id) {
  await atApi.deleteVersion(id)
  ElMessage.success('删除成功')
  fetchData()
}

const formDialogVisible = ref(false)
const editRow = ref(null)
function openCreateDialog() { editRow.value = null; formDialogVisible.value = true }
function openEditDialog(row) { editRow.value = { ...row }; formDialogVisible.value = true }

const detailVisible = ref(false)
const detailTitle = ref('')
const detailContent = ref('')
function openDetail(title, content) { detailTitle.value = title; detailContent.value = content; detailVisible.value = true }

const TEST_RESULT_ORDER = ['未开始', '测试中', '通过', '失败', '中断']
const cycling = reactive({})
async function cycleTestResult(row) {
  if (cycling[row.id]) return
  cycling[row.id] = true
  const idx = TEST_RESULT_ORDER.indexOf(row.test_result ?? '未开始')
  const next = TEST_RESULT_ORDER[(idx + 1) % TEST_RESULT_ORDER.length]
  try {
    await atApi.updateVersion(row.id, { test_result: next })
    row.test_result = next
  } catch {} finally { delete cycling[row.id] }
}

const TEST_RESULT_TYPE = { '未开始': 'info', '测试中': 'primary', '通过': 'success', '失败': 'danger', '中断': 'warning' }
function testResultTagType(val) { return TEST_RESULT_TYPE[val] ?? 'info' }
const VERSION_TYPE_COLOR = { feature: '', dev: 'warning', test: 'info', hotfix: 'danger', release: 'success' }
function versionTypeTagType(val) { return VERSION_TYPE_COLOR[val] ?? '' }
function formatTime(t) { if (!t) return '-'; return new Date(t).toLocaleString('zh-CN', { hour12: false }) }
</script>

<style scoped>
.at-version-list { max-width: 1400px; }
.filter-card :deep(.el-card__body) { padding: 16px 20px 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
.download-link { color: #409eff; text-decoration: none; }
.download-link:hover { text-decoration: underline; }
.detail-content { white-space: pre-wrap; word-break: break-all; font-size: 13px; line-height: 1.6; }
</style>
