<template>
  <div class="dashboard">
    <!-- 访客提示条 -->
    <el-alert
      v-if="isVisitorOnly"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px"
    >
      <template #title>
        <span>当前账号仅有访客权限，无法操作数据。如需更多权限，请向管理员申请。</span>
        <el-button
          type="primary"
          size="small"
          style="margin-left: 16px"
          @click="roleDialogVisible = true"
        >申请角色权限</el-button>
      </template>
    </el-alert>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>欢迎回来，{{ authStore.userInfo?.username }}</span>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="手机号">
              {{ authStore.userInfo?.phone_number ?? '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag
                v-for="role in authStore.roles"
                :key="role"
                type="success"
                style="margin-right: 4px"
              >
                {{ role }}
              </el-tag>
              <span v-if="!authStore.roles.length" style="color:#909399">无角色</span>
            </el-descriptions-item>
            <el-descriptions-item label="权限数量">
              {{ authStore.permissions.length }} 项
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>

  <!-- 申请角色弹框 -->
  <el-dialog
    v-model="roleDialogVisible"
    title="申请角色权限"
    width="440px"
    :close-on-click-modal="false"
    @closed="resetRoleForm"
  >
    <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-width="80px">
      <el-form-item label="部门" prop="department">
        <el-input v-model="roleForm.department" placeholder="请输入您的部门" clearable />
      </el-form-item>
      <el-form-item label="申请角色" prop="roles">
        <el-checkbox-group v-model="roleForm.roles">
          <el-checkbox
            v-for="g in availableGroups"
            :key="g.id"
            :label="g.name"
          >{{ g.name }}</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="roleDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleRoleRequest">提交申请</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { getGroups, roleRequest } from '@/api/auth'

const authStore = useAuthStore()

// 是否仅有 visitor 角色或无角色
const isVisitorOnly = computed(() => {
  const roles = authStore.roles
  return roles.length === 0 || (roles.length === 1 && roles[0] === 'visitor')
})

const roleDialogVisible = ref(false)
const roleFormRef = ref(null)
const submitting = ref(false)
const availableGroups = ref([])

const roleForm = reactive({
  department: authStore.userInfo?.department || '',
  roles: [...authStore.roles],
})

const roleRules = {
  department: [{ required: true, message: '请输入部门', trigger: 'blur' }],
  roles: [{ type: 'array', min: 1, message: '请至少选择一个角色', trigger: 'change' }],
}

onMounted(async () => {
  try {
    const res = await getGroups()
    availableGroups.value = res.data ?? []
  } catch {
    // 加载失败不影响主页面
  }
})

async function handleRoleRequest() {
  const valid = await roleFormRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const res = await roleRequest({
      department: roleForm.department,
      roles: roleForm.roles,
    })
    ElMessage.success(res.msg || '申请已提交，请等待管理员审核')
    roleDialogVisible.value = false
  } catch {
    // 错误已由拦截器一并处理
  } finally {
    submitting.value = false
  }
}

function resetRoleForm() {
  roleFormRef.value?.resetFields()
  roleForm.roles = [...authStore.roles]
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}
</style>
