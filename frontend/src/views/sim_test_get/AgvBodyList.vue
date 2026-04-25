<template>
  <div class="agv-body-list">
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="测试车型">
          <el-input v-model="filters.agv_type" placeholder="模糊查询" clearable style="width: 150px" />
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
          <el-button v-permission="'sim_test_get.add_agvbody'" type="primary" :icon="Plus"
            @click="openCreateDialog">新建车体</el-button>
          <el-button v-permission="'sim_test_get.delete_agvbody'" type="danger" :icon="Delete"
            :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%;margin-top:12px"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="agv_type" label="测试车型" min-width="130" />
        <el-table-column prop="left_width" label="左边车宽" width="90" />
        <el-table-column prop="right_width" label="右边车宽" width="90" />
        <el-table-column prop="front_length" label="前方车长" width="90" />
        <el-table-column prop="back_length" label="后方车长" width="90" />
        <el-table-column prop="fork_length" label="货叉长度" width="90" />
        <el-table-column prop="fork_inner_width" label="货叉内宽" width="90" />
        <el-table-column prop="fork_width" label="货叉宽度" width="90" />
        <el-table-column prop="fork_thickness" label="货叉厚度" width="90" />
        <el-table-column prop="load_position_x" label="原车前悬距" width="100" />
        <el-table-column prop="create_time" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110">
          <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'sim_test_get.change_agvbody'" type="primary" link
              @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除该车体数据？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button v-permission="'sim_test_get.delete_agvbody'" type="danger" link>删除</el-button>
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

    <AgvBodyFormDialog v-model:visible="formDialogVisible" :edit-data="editRow" @success="fetchData()" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import {
  getAgvBodyList, deleteAgvBody,
  batchDeleteAgvBodies, getAgvBodyCreators,
} from '@/api/sim_test_get'
import { usePagination } from '@/composables/usePagination'
import AgvBodyFormDialog from './AgvBodyFormDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getAgvBodyList)

fetchData()

function handleReset() {
  Object.assign(filters, { agv_type: '', created_by: '', create_time_after: '', create_time_before: '' })
  resetAndFetch({})
}

const creators = ref([])
onMounted(async () => {
  const res = await getAgvBodyCreators()
  creators.value = Array.isArray(res) ? res : (res.data || [])
})

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

async function handleDelete(id) {
  await deleteAgvBody(id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteAgvBodies(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

const formDialogVisible = ref(false)
const editRow = ref(null)
function openCreateDialog() { editRow.value = null; formDialogVisible.value = true }
function openEditDialog(row) { editRow.value = row; formDialogVisible.value = true }

function formatTime(t) {
  if (!t) return '-'
  return t.replace('T', ' ').slice(0, 19)
}
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
