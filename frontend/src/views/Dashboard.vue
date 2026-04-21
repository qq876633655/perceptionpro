<template>
  <div class="dashboard">
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
            </el-descriptions-item>
            <el-descriptions-item label="权限数量">
              {{ authStore.permissions.length }} 项
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}
</style>
