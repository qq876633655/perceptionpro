<template>
  <div class="callback-page">
    <span>{{ message }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const message = ref('钉钉登录中...')

onMounted(async () => {
  const { access, refresh, error } = route.query

  if (error) {
    ElMessage.error(error)
    router.replace('/login')
    return
  }

  if (!access || !refresh) {
    ElMessage.error('登录失败，缺少凭证信息')
    router.replace('/login')
    return
  }

  try {
    authStore._saveTokens(access, refresh)
    await authStore.fetchUserInfo()
    router.replace('/')
  } catch {
    ElMessage.error('获取用户信息失败，请重试')
    authStore.logout()
    router.replace('/login')
  }
})
</script>

<style scoped>
.callback-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-size: 16px;
  color: #606266;
}
</style>
