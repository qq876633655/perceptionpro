<template>
  <div class="role-management">
    <!-- 操作栏 + 表格 -->
    <el-card shadow="never">
      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建角色</el-button>
        <el-button :icon="Refresh" circle @click="fetchData()" />
      </div>

      <el-table v-loading="loading" :data="tableData" stripe border style="width:100%; margin-top:12px">
        <el-table-column prop="name" label="角色名称" min-width="160" />
        <el-table-column label="权限数量" width="110">
          <template #default="{ row }">
            {{ row.permissions_detail?.length ?? row.permission_ids?.length ?? 0 }} 个
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="成员数量" width="110">
          <template #default="{ row }">{{ row.user_count ?? 0 }} 人</template>
        </el-table-column>
        <el-table-column label="权限预览" min-width="240">
          <template #default="{ row }">
            <template v-if="row.permissions_detail?.length">
              <el-tag
                v-for="p in row.permissions_detail.slice(0, 4)"
                :key="p.id"
                size="small"
                type="info"
                style="margin-right: 4px; margin-bottom: 2px"
              >{{ p.codename }}</el-tag>
              <span v-if="row.permissions_detail.length > 4" style="font-size:12px; color:#909399">
                +{{ row.permissions_detail.length - 4 }} 更多
              </span>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确认删除该角色？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <RoleFormDialog
      v-model:visible="dialogVisible"
      :edit-data="editRow"
      @success="fetchData()"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'
import { getGroupList, deleteGroup } from '@/api/admin'
import { usePagination } from '@/composables/usePagination'
import RoleFormDialog from './RoleFormDialog.vue'

const {
  loading, tableData, pagination,
  fetchData, handlePageChange, handleSizeChange,
} = usePagination(getGroupList)

fetchData()

async function handleDelete(id) {
  await deleteGroup(id)
  ElMessage.success('删除成功')
  fetchData()
}

const dialogVisible = ref(false)
const editRow = ref(null)

function openCreateDialog() {
  editRow.value = null
  dialogVisible.value = true
}

function openEditDialog(row) {
  editRow.value = { ...row }
  dialogVisible.value = true
}
</script>

<style scoped>
.role-management {
  max-width: 1200px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
