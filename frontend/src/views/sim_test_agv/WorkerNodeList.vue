<template>
  <div class="worker-node-list">
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="filters.hostname" placeholder="模糊查询" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="IP 地址">
          <el-input v-model="filters.ip_address" placeholder="模糊查询" clearable style="width: 150px" />
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
          <el-button v-permission="'sim_test_agv.add_workernode'" type="primary" :icon="Plus"
            @click="openCreate">新建节点</el-button>
          <el-button v-permission="'sim_test_agv.delete_workernode'" type="danger" :icon="Delete"
            :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%;margin-top:12px"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="hostname" label="Worker 名称" min-width="220" show-overflow-tooltip />
        <el-table-column prop="docker_type" label="Docker 类型" width="110">
          <template #default="{ row }">{{ row.docker_type || '-' }}</template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP 地址" width="150">
          <template #default="{ row }">{{ row.ip_address || '-' }}</template>
        </el-table-column>
        <el-table-column prop="note" label="备注" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.note || '-' }}</template>
        </el-table-column>
        <el-table-column label="历史总量" width="90" align="center">
          <template #default="{ row }">
            <span>{{ historyStats[row.hostname]?.total ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="成功" width="70" align="center">
          <template #default="{ row }">
            <span style="color:#67c23a">{{ historyStats[row.hostname]?.success ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="失败" width="70" align="center">
          <template #default="{ row }">
            <span style="color:#f56c6c">{{ historyStats[row.hostname]?.failed ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110">
          <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'sim_test_agv.change_workernode'" type="primary" link
              @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确认删除该节点？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button v-permission="'sim_test_agv.delete_workernode'" type="danger" link>删除</el-button>
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

    <WorkerNodeFormDialog v-model:visible="dialogVisible" :row="editRow" @success="fetchData()" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { getWorkerNodeList, deleteWorkerNode, batchDeleteWorkerNodes, getWorkerHistoryStats } from '@/api/sim_test_agv'
import { usePagination } from '@/composables/usePagination'
import WorkerNodeFormDialog from './WorkerNodeFormDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getWorkerNodeList)

fetchData()

const historyStats = ref({})
async function loadHistoryStats() {
  try {
    const res = await getWorkerHistoryStats()
    historyStats.value = res.data ?? res ?? {}
  } catch { historyStats.value = {} }
}
onMounted(loadHistoryStats)

function handleReset() {
  Object.assign(filters, { hostname: '', ip_address: '' })
  resetAndFetch({})
}

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

async function handleDelete(id) {
  await deleteWorkerNode(id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteWorkerNodes(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

const dialogVisible = ref(false)
const editRow = ref(null)

function openCreate() { editRow.value = null; dialogVisible.value = true }
function openEdit(row) { editRow.value = row; dialogVisible.value = true }

function formatTime(t) { return t ? t.replace('T', ' ').slice(0, 19) : '-' }
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
