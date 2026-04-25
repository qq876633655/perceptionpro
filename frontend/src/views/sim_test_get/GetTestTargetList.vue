<template>
  <div class="get-test-target-list">
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline label-width="80px">
        <el-form-item label="载具名称">
          <el-input v-model="filters.target_name" placeholder="模糊查询" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="filters.model_name" placeholder="模糊查询" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.target_type" placeholder="全部" clearable style="width: 110px">
            <el-option label="托盘" value="pallet" />
            <el-option label="料笼" value="cage" />
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
          <el-button v-permission="'sim_test_get.add_gettesttarget'" type="primary" :icon="Plus"
            @click="openCreateDialog">新建载具</el-button>
          <el-button v-permission="'sim_test_get.delete_gettesttarget'" type="danger" :icon="Delete"
            :disabled="!selectedIds.length" @click="handleBatchDelete">
            批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </el-button>
        </div>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%;margin-top:12px"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="target_name" label="载具名称" min-width="140" />
        <el-table-column prop="target_type" label="类型" width="80">
          <template #default="{ row }">{{ row.target_type === 'pallet' ? '托盘' : '料笼' }}</template>
        </el-table-column>
        <el-table-column prop="texture" label="材质" width="90">
          <template #default="{ row }">{{ textureLabel(row.texture) }}</template>
        </el-table-column>
        <el-table-column prop="color" label="颜色" width="90">
          <template #default="{ row }">{{ colorLabel(row.color) }}</template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="length" label="长" width="70" />
        <el-table-column prop="width" label="宽" width="70" />
        <el-table-column prop="height" label="高" width="70" />
        <el-table-column prop="create_time" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="110">
          <template #default="{ row }">{{ row.created_by_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'sim_test_get.change_gettesttarget'" type="primary" link
              @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除该载具数据？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button v-permission="'sim_test_get.delete_gettesttarget'" type="danger" link>删除</el-button>
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

    <GetTestTargetFormDialog v-model:visible="formDialogVisible" :edit-data="editRow" @success="fetchData()" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import {
  getGetTestTargetList, deleteGetTestTarget,
  batchDeleteGetTestTargets, getGetTestTargetCreators,
} from '@/api/sim_test_get'
import { usePagination } from '@/composables/usePagination'
import GetTestTargetFormDialog from './GetTestTargetFormDialog.vue'

const { loading, tableData, pagination, filters, fetchData, handlePageChange, handleSizeChange, resetAndFetch } =
  usePagination(getGetTestTargetList)

fetchData()

function handleReset() {
  Object.assign(filters, {
    target_name: '', model_name: '', target_type: '',
    created_by: '', create_time_after: '', create_time_before: '',
  })
  resetAndFetch({})
}

const creators = ref([])
onMounted(async () => {
  const res = await getGetTestTargetCreators()
  creators.value = Array.isArray(res) ? res : (res.data || [])
})

const selectedIds = ref([])
function handleSelectionChange(rows) { selectedIds.value = rows.map(r => r.id) }

async function handleDelete(id) {
  await deleteGetTestTarget(id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleBatchDelete() {
  await ElMessageBox.confirm(`确认删除选中的 ${selectedIds.value.length} 条记录？`, '提示', { type: 'warning' })
  await batchDeleteGetTestTargets(selectedIds.value)
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

const TEXTURE_MAP = {
  plastic: '塑料', metal: '金属', wood: '木材',
  mirror_hollow: '镜面空洞', plastic_damaged: '塑料破损',
  mirror: '镜面',
}
const COLOR_MAP = {
  white: '白色', yellow: '黄色', blue: '蓝色', black: '黑色',
  red: '红色', red_brown: '红棕色', silver: '银色',
  wood_color: '原木色', black_hollow: '黑色空洞', silver_gray: '银灰色',
}
function textureLabel(v) { return TEXTURE_MAP[v] || v || '-' }
function colorLabel(v) { return COLOR_MAP[v] || v || '-' }
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; gap: 8px; }
.pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
