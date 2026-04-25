<template>
  <div class="not-found">
    <div class="not-found-code">404</div>
    <div class="not-found-title">页面不存在</div>
    <div class="not-found-desc">你访问的页面可能已被删除或路径有误</div>
    <el-button type="primary" @click="router.push('/')">返回首页</el-button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  gap: 12px;
  color: #909399;
}

.not-found-code {
  font-size: 96px;
  font-weight: 700;
  line-height: 1;
  color: #E8312A;
  letter-spacing: -4px;
}

.not-found-title {
  font-size: 22px;
  color: #303133;
  font-weight: 600;
}

.not-found-desc {
  font-size: 14px;
  margin-bottom: 8px;
}
</style>
