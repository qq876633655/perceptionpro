<template>
  <div class="get-test-common-param-list">
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
          <el-select v-model="filters.sim_test_vehicle" placeholder="全部" clearable filterable style="width: 130px">
            <el-option v-for="v in choices.sim_test_vehicle" :key="v" :label="v" :value="v" />
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
          <el-button v-permission="'sim_test_get.add_gettestcommonparameter'" type="primary" :icon="Plus"
            @click="openCreateDialog">新建通参</el-button>
          <el-button v-permission="'sim_test_get.delete_gettestcommonparameter'" type="danger" :icon="Delete"
            :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%;margin-top:12px"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="common_parameter_name" label="通参名称" min-width="160" />
        <el-table-column prop="sim_test_version" label="资产版本" min-width="130" />
        <el-table-column prop="sim_test_vehicle" label="测试车型" min-width="120" />
        <el-table-column prop="common_parameter_file" label="通参文件" width="90">
          <template #default="{ row }">
            <a v-if="row.common_parameter_file" :href="row.common_parameter_file" download
              class="download-link">下载</a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="parameter_desc" label="通参描述" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.parameter_desc || '-' }}</template>
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
            <el-button v-permission="'sim_test_get.change_gettestcommonparameter'" type="primary" link
              @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除该通参？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button v-permission="'sim_test_get.delete_gettestcommonparameter'" type="danger" link>删除</el-button>
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

    <GetTestCommonParamFormDialog v-model:visible="formDialogVisible" :edit-data="editRow" @success="fetchData()" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import {
  getGetTestCommonParamList, deleteGetTestCommonParam,
  batchDeleteGetTestCommonParams, getGetTestCommonParamCreators, getGetTestCommonParamChoices,
} from '@/api/sim_test_get'
import { usePagination } from '@/composables/usePagination'
import GetTestCommonParamFormDialog from './GetTestCommonParamFormDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getGetTestCommonParamList)

fetchData()

function handleReset() {
  Object.assign(filters, {
    common_parameter_name: '', sim_test_version: '', sim_test_vehicle: '',
    created_by: '', create_time_after: '', create_time_before: '',
  })
  resetAndFetch({})
}

const creators = ref([])
const choices = ref({ sim_test_version: [], sim_test_vehicle: [] })
onMounted(async () => {
  const [creatorsRes, choicesRes] = await Promise.all([
    getGetTestCommonParamCreators(),
    getGetTestCommonParamChoices(),
  ])
  creators.value = Array.isArray(creatorsRes) ? creatorsRes : (creatorsRes.data || [])
  const c = Array.isArray(choicesRes) ? {} : (choicesRes.data ?? choicesRes)
  choices.value = { sim_test_version: c.sim_test_version ?? [], sim_test_vehicle: c.sim_test_vehicle ?? [] }
})

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

async function handleDelete(id) {
  await deleteGetTestCommonParam(id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteGetTestCommonParams(selectedIds.value)
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
.download-link { color: #409eff; text-decoration: none; }
.download-link:hover { text-decoration: underline; }
</style>
