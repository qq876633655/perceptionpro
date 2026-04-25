<template>
  <div class="login-page">
    <!-- 左侧视频区 -->
    <div class="login-video-side">
      <video
        class="bg-video"
        src="/login_bg-6ef8a3fb.mp4"
        autoplay
        loop
        muted
        playsinline
      />
      <!-- 半透明遮罩 + 品牌文字 -->
      <div class="video-overlay">
        <h1 class="brand-title">PerceptionPro</h1>
        <p class="brand-subtitle">测试管理平台</p>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="login-form-side">
      <div class="login-card">
        <div class="login-header">
          <h2 class="login-title">欢迎登录</h2>
          <p class="login-subtitle">请使用手机号或钉钉账号登录</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item label="手机号" prop="phone_number">
            <el-input
              v-model="form.phone_number"
              placeholder="请输入手机号"
              prefix-icon="Phone"
              clearable
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>

          <div class="divider-text"><span>或</span></div>

          <el-form-item>
            <el-button
              class="login-btn dingtalk-btn"
              @click="handleDingTalkLogin"
            >
              钉钉登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  phone_number: '',
  password: '',
})

// 前端表单校验规则
const rules = {
  phone_number: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

function handleDingTalkLogin() {
  const url =
    'https://login.dingtalk.com/oauth2/auth?redirect_uri=' +
    encodeURIComponent('http://' + window.location.hostname + ':' + 7898 + '/dd/no_sign_in/') +
    '&response_type=code&scope=openid&client_id=dingnnpn4oajxevomvwj&prompt=consent'
  window.location.href = url
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.loginAction({
      phone_number: form.phone_number,
      password: form.password,
    })
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err) {
    // 后端字段错误（格式：data 数组）
    if (Array.isArray(err?.data)) {
      const msg = err.data.map((e) => e.message).join('；')
      ElMessage.error(msg)
    }
    // 其他错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── 整体容器 ── */
.login-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── 左侧视频区 ── */
.login-video-side {
  position: relative;
  width: 50%;
  overflow: hidden;
  background: #111;
}

.bg-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px;
}

.brand-title {
  font-size: 34px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 3px;
  margin: 0 0 12px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.brand-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  letter-spacing: 2px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
}

/* ── 右侧表单区 ── */
.login-form-side {
  width: 50%;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 380px;
  background: #fff;
  border-radius: 12px;
  padding: 48px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.login-subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  letter-spacing: 2px;
}

.dingtalk-btn {
  background-color: #1a6de0;
  border-color: #1a6de0;
  color: #fff;
}

.dingtalk-btn:hover,
.dingtalk-btn:focus {
  background-color: #1559c0;
  border-color: #1559c0;
  color: #fff;
}

/* 或 分隔线 */
.divider-text {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  margin: -4px 0 8px;
  position: relative;
}
.divider-text::before,
.divider-text::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 38%;
  height: 1px;
  background: #e4e7ed;
}
.divider-text::before { left: 0; }
.divider-text::after  { right: 0; }
</style>
