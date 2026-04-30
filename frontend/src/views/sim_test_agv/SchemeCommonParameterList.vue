<template>
  <div class="common-param-list">
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="通参名称">
          <el-input v-model="filters.common_parameter_name" placeholder="模糊查询" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="资产版本">
          <el-select v-model="filters.sim_test_version" placeholder="全部" clearable filterable style="width: 130px">
            <el-option v-for="v in choices.sim_test_version" :key="v" :label="v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试车型">
          <el-select v-model="filters.sim_test_vehicle" placeholder="全部" clearable filterable style="width: 120px">
            <el-option v-for="v in choices.sim_test_vehicle" :key="v" :label="v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试模块">
          <el-select v-model="filters.test_module" placeholder="全部" clearable filterable style="width: 120px">
            <el-option v-for="v in choices.test_module" :key="v" :label="v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="通参状态">
          <el-select v-model="filters.common_parameter_status" placeholder="全部" clearable style="width: 100px">
            <el-option label="正常" value="正常" />
            <el-option label="维护" value="维护" />
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
          <el-button v-permission="'sim_test_agv.add_schemecommonparameter'" type="primary" :icon="Plus"
            @click="openCreateDialog">新建通参</el-button>
          <el-button v-permission="'sim_test_agv.delete_schemecommonparameter'" type="danger" :icon="Delete"
            :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
          <el-button v-permission="'sim_test_agv.add_schemecommonparameter'" type="warning"
            :disabled="!selectedIds.length" @click="copyDialogVisible = true">
            批量复制{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%;margin-top:12px"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="common_parameter_name" label="通参名称" min-width="160" />
        <el-table-column prop="sim_test_version" label="资产版本" min-width="130" />
        <el-table-column prop="sim_test_vehicle" label="测试车型" min-width="110" />
        <el-table-column prop="test_module" label="测试模块" min-width="110" />
        <el-table-column prop="common_parameter_file" label="通参文件" width="90">
          <template #default="{ row }">
            <a v-if="row.common_parameter_file" :href="row.common_parameter_file" download class="download-link">下载</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="parameter_desc" label="通参描述" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.parameter_desc || '-' }}</template>
        </el-table-column>
        <el-table-column prop="common_parameter_status" label="通参状态" width="100">
          <template #default="{ row }">
            <el-button :type="row.common_parameter_status === '正常' ? 'success' : 'warning'" size="small"
              :loading="!!cycling[row.id]" @click="cycleStatus(row)">
              {{ row.common_parameter_status || '正常' }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110">
          <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="update_time" label="更新时间" width="170">
          <template #default="{ row }">{{ formatTime(row.update_time) }}</template>
        </el-table-column>
        <el-table-column prop="updated_by_name" label="更新人" width="110">
          <template #default="{ row }">{{ row.updated_by_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'sim_test_agv.change_schemecommonparameter'" type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除该通参记录？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button v-permission="'sim_test_agv.delete_schemecommonparameter'" type="danger" link>删除</el-button>
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

    <SchemeCommonParameterFormDialog v-model:visible="formDialogVisible" :edit-data="editRow" @success="fetchData()" />
    <CommonParameterBatchCopyDialog v-model:visible="copyDialogVisible" :rows="selectedRows" @success="fetchData()" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import {
  getCommonParameterList, deleteCommonParameter, batchDeleteCommonParameters,
  getCommonParameterCreators, updateCommonParameter, getCommonParameterChoices,
} from '@/api/sim_test_agv'
import { usePagination } from '@/composables/usePagination'
import SchemeCommonParameterFormDialog from './SchemeCommonParameterFormDialog.vue'
import CommonParameterBatchCopyDialog from './CommonParameterBatchCopyDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getCommonParameterList)

fetchData()

function handleReset() {
  Object.assign(filters, {
    common_parameter_name: '', sim_test_version: '', sim_test_vehicle: '',
    test_module: '', common_parameter_status: '', created_by: '',
    create_time_after: '', create_time_before: '',
  })
  resetAndFetch({})
}

const creators = ref([])
const choices = reactive({ sim_test_version: [], sim_test_vehicle: [], test_module: [] })
onMounted(async () => {
  const [crRes, chRes] = await Promise.all([getCommonParameterCreators(), getCommonParameterChoices()])
  creators.value = Array.isArray(crRes) ? crRes : (crRes.data || [])
  const ch = chRes.data ?? chRes
  Object.assign(choices, ch)
})

const selectedIds = ref([])
const selectedRows = ref([])
function handleSelectionChange(rows) {
  selectedIds.value = rows.map(r => r.id)
  selectedRows.value = rows
}

async function handleDelete(id) {
  await deleteCommonParameter(id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteCommonParameters(selectedIds.value)
  ElMessage.success('删除成功')
  fetchData()
}

const cycling = reactive({})
const STATUS_CYCLE = ['正常', '维护']
async function cycleStatus(row) {
  if (cycling[row.id]) return
  const next = STATUS_CYCLE[(STATUS_CYCLE.indexOf(row.common_parameter_status || '正常') + 1) % STATUS_CYCLE.length]
  cycling[row.id] = true
  try {
    await updateCommonParameter(row.id, { common_parameter_status: next })
    row.common_parameter_status = next
  } finally {
    cycling[row.id] = false
  }
}

const formDialogVisible = ref(false)
const copyDialogVisible = ref(false)
const editRow = ref(null)
function openCreateDialog() { editRow.value = null; formDialogVisible.value = true }
function openEditDialog(row) { editRow.value = row; formDialogVisible.value = true }

function formatTime(t) { return t ? t.replace('T', ' ').slice(0, 19) : '-' }
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
.download-link { color: #409eff; text-decoration: none; }
.download-link:hover { text-decoration: underline; }
</style>
