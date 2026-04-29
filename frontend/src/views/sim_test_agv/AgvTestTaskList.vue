<template>
  <div class="agv-task-list">
    <!-- Worker 状态面板 -->
    <el-card shadow="never" style="margin-bottom: 12px">
      <template #header>
        <div class="worker-panel-header">
          <span style="font-weight:600">Worker 节点状态</span>
          <div style="display:flex;align-items:center;gap:8px">
            <el-text size="small" type="info">每 10 秒自动刷新</el-text>
            <el-button :icon="Refresh" size="small" circle :loading="workerLoading" @click="fetchWorkers" />
            <el-button size="small" link @click="workerPanelExpanded = !workerPanelExpanded">
              {{ workerPanelExpanded ? '收起' : '展开' }}
            </el-button>
          </div>
        </div>
      </template>
      <div v-if="workerPanelExpanded">
        <div v-if="workerLoading && !workerList.length" class="worker-placeholder">加载中...</div>
        <div v-else-if="!workerList.length" class="worker-placeholder">暂无注册的 Worker 节点</div>
        <div v-else class="worker-cards">
          <div v-for="w in workerList" :key="w.id" class="worker-card"
            :class="'worker-' + w.status">
            <div class="worker-card-title">
              <el-tag :type="workerTagType(w.status)" size="small">{{ workerStatusLabel(w.status) }}</el-tag>
              <span class="worker-hostname">{{ w.hostname }}</span>
            </div>
            <div class="worker-card-info">
              <span v-if="w.ip_address">IP: {{ w.ip_address }}</span>
              <span v-if="w.queues.length">队列: {{ w.queues.join(', ') }}</span>
              <span v-if="w.active_tasks.length" style="color:#e6a23c">
                执行中: {{ w.active_tasks[0].args?.[0] ?? w.active_tasks[0].id }}
              </span>
              <span v-if="w.reserved_count > 0" style="color:#e6a23c">等待中: {{ w.reserved_count }} 个任务</span>
              <span v-if="w.status !== 'offline'">本次已完成: {{ w.session_total }} 个</span>
            </div>
            <div v-if="w.note" class="worker-card-note">{{ w.note }}</div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="资产版本">
          <el-input v-model="filters.sim_test_version" placeholder="模糊查询" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="任务队列">
          <el-input v-model="filters.queue_name" placeholder="模糊查询" clearable style="width: 130px" />
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="filters.task_status" placeholder="全部" clearable style="width: 110px">
            <el-option label="已创建" value="CREATED" />
            <el-option label="已下发" value="DISPATCHED" />
            <el-option label="执行中" value="RUNNING" />
            <el-option label="取消中" value="CANCELING" />
            <el-option label="已取消" value="CANCELED" />
            <el-option label="成功" value="SUCCESS" />
            <el-option label="失败" value="FAILED" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建人">
          <el-select v-model="filters.created_by" placeholder="全部" clearable filterable style="width: 120px">
            <el-option v-for="u in creators" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="filters.create_time_after" type="datetime" placeholder="开始日期"
            value-format="YYYY-MM-DD HH:mm:ss" style="width: 180px" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="filters.create_time_before" type="datetime" placeholder="结束日期"
            value-format="YYYY-MM-DD HH:mm:ss" style="width: 180px" />
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
          <el-button v-permission="'sim_test_agv.add_agvtesttask'" type="primary" :icon="Plus"
            @click="openCreateDialog">新建任务</el-button>
          <el-button v-permission="'sim_test_agv.delete_agvtesttask'" type="danger" :icon="Delete"
            :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%;margin-top:12px"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="sim_test_version" label="资产版本" min-width="130" />
        <el-table-column prop="queue_name" label="任务队列" min-width="130" />
        <el-table-column prop="task_status" label="任务状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.task_status)" size="small">
              {{ statusLabel(row.task_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_schedule" label="当前进度" width="110">
          <template #default="{ row }">{{ row.current_schedule || '-' }}</template>
        </el-table-column>
        <el-table-column prop="worker_name" label="执行端" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.worker_name || '-' }}</span>
            <el-tag v-if="row.target_worker" size="small" type="warning" style="margin-left:4px">已指定</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_worker" label="指定 Worker" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">​{{ row.target_worker || '-' }}</template>
        </el-table-column>
        <el-table-column prop="error_msg" label="错误信息" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">
            <span :style="row.error_msg ? 'color:#f56c6c' : ''">{{ row.error_msg || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="recovery_default_version" label="恢复默认版本" width="110" />
        <el-table-column prop="base_version" label="待测基线版本" min-width="130">
          <template #default="{ row }">{{ row.base_version || '-' }}</template>
        </el-table-column>
        <el-table-column prop="auto_test_run_log" label="运行日志" width="90">
          <template #default="{ row }">
            <a v-if="row.auto_test_run_log" :href="row.auto_test_run_log" target="_blank" class="download-link">下载</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="test_result" label="测试结果" width="90">
          <template #default="{ row }">
            <a v-if="row.test_result" :href="row.test_result" target="_blank" class="download-link">下载</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110">
          <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
        </el-table-column>
        <!-- 无编辑按钮 -->
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-permission="'sim_test_agv.change_agvtesttask'"
              type="warning" link
              :disabled="!['CREATED','DISPATCHED','RUNNING'].includes(row.task_status)"
              :loading="!!canceling[row.id]"
              @click="handleCancel(row)"
            >取消</el-button>
            <el-popconfirm title="确认删除该任务记录？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button v-permission="'sim_test_agv.delete_agvtesttask'" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.page_size"
          :total="pagination.total" :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper" background
          @current-change="handlePageChange" @size-change="handleSizeChange" />
      </div>
    </el-card>

    <AgvTestTaskFormDialog v-model:visible="formDialogVisible" @success="fetchData()" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { getAgvTestTaskList, deleteAgvTestTask, batchDeleteAgvTestTasks, getAgvTestTaskCreators, cancelAgvTestTask, getWorkerStatus } from '@/api/sim_test_agv'
import { usePagination } from '@/composables/usePagination'
import AgvTestTaskFormDialog from './AgvTestTaskFormDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getAgvTestTaskList)

fetchData()

// ── Worker 状态面板 ────────────────────────────────────────
const workerPanelExpanded = ref(true)
const workerLoading = ref(false)
const workerList = ref([])

async function fetchWorkers() {
  workerLoading.value = true
  try {
    const res = await getWorkerStatus()
    workerList.value = Array.isArray(res) ? res : (res.data || [])
  } catch {
    // 静默失败，不影响任务列表
  } finally {
    workerLoading.value = false
  }
}

fetchWorkers()
const workerTimer = setInterval(fetchWorkers, 10000)
onUnmounted(() => clearInterval(workerTimer))

const WORKER_STATUS = {
  online: { label: '空闲', type: 'success' },
  busy:   { label: '执行中', type: 'warning' },
  offline: { label: '离线', type: 'info' },
}
function workerStatusLabel(s) { return WORKER_STATUS[s]?.label ?? s }
function workerTagType(s) { return WORKER_STATUS[s]?.type ?? '' }

// ─────────────────────────────────────────────────────────

function handleReset() {
  Object.assign(filters, { sim_test_version: '', queue_name: '', task_status: '', created_by: '', create_time_after: '', create_time_before: '' })
  resetAndFetch({})
}

const creators = ref([])
onMounted(async () => {
  const res = await getAgvTestTaskCreators()
  creators.value = Array.isArray(res) ? res : (res.data || [])
})

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

async function handleDelete(id) {
  await deleteAgvTestTask(id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteAgvTestTasks(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

const canceling = reactive({})
async function handleCancel(row) {
  if (canceling[row.id]) return
  canceling[row.id] = true
  try {
    await cancelAgvTestTask(row.id)
    ElMessage.success('取消请求已发送')
    fetchData()
  } catch (err) {
    const detail = err?.response?.data?.detail || '取消失败'
    ElMessage.error(detail)
  } finally {
    canceling[row.id] = false
  }
}

const STATUS_MAP = {
  CREATED: { label: '已创建', type: 'info' },
  DISPATCHED: { label: '已下发', type: '' },
  RUNNING: { label: '执行中', type: 'warning' },
  CANCELING: { label: '取消中', type: 'warning' },
  CANCELED: { label: '已取消', type: 'info' },
  SUCCESS: { label: '成功', type: 'success' },
  FAILED: { label: '失败', type: 'danger' },
}
function statusLabel(s) { return STATUS_MAP[s]?.label ?? s ?? '-' }
function statusTagType(s) { return STATUS_MAP[s]?.type ?? '' }

const formDialogVisible = ref(false)
function openCreateDialog() { formDialogVisible.value = true }

function formatTime(t) { return t ? t.replace('T', ' ').slice(0, 19) : '-' }
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
.download-link { color: #409eff; text-decoration: none; }
.download-link:hover { text-decoration: underline; }

.worker-panel-header { display: flex; justify-content: space-between; align-items: center; }
.worker-placeholder { color: #909399; font-size: 13px; padding: 8px 0; }
.worker-cards { display: flex; flex-wrap: wrap; gap: 10px; }
.worker-card {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  padding: 10px 14px;
  min-width: 220px;
  max-width: 320px;
  background: #fff;
}
.worker-card.worker-offline { background: #f5f7fa; opacity: 0.75; }
.worker-card.worker-busy { border-color: #e6a23c; }
.worker-card.worker-online { border-color: #67c23a; }
.worker-card-title { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.worker-hostname { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.worker-card-info { font-size: 12px; color: #606266; display: flex; flex-direction: column; gap: 2px; }
.worker-card-note { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
