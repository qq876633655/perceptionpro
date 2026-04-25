<template>
  <div class="agv-task-list">
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
        <el-table-column prop="worker_name" label="执行端" min-width="120">
          <template #default="{ row }">{{ row.worker_name || '-' }}</template>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { getAgvTestTaskList, deleteAgvTestTask, batchDeleteAgvTestTasks, getAgvTestTaskCreators, cancelAgvTestTask } from '@/api/sim_test_agv'
import { usePagination } from '@/composables/usePagination'
import AgvTestTaskFormDialog from './AgvTestTaskFormDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getAgvTestTaskList)

fetchData()

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
</style>
