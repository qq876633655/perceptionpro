import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const service = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// ── token 刷新队列（处理并发 401 时只刷新一次）──────────────────────
let isRefreshing = false
let failedQueue = []

function processQueue(error, token = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  failedQueue = []
}

// ── 请求拦截器：自动携带 JWT Token ──────────────────────────────────
service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── 响应拦截器：统一处理后端返回格式 + 自动刷新 token ───────────────
service.interceptors.response.use(
  (response) => {
    // 204 No Content（DELETE 成功无返回体）
    if (response.status === 204) {
      return { code: 0, msg: 'success', data: null }
    }
    const res = response.data
    // 后端统一格式：{ code, msg, data }
    if (res.code !== 0) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(res)
    }
    return res
  },
  async (error) => {
    const status = error.response?.status
    const originalRequest = error.config

    // ── 401：尝试用 refresh token 换新 access token ────────────────
    if (status === 401 && !originalRequest._retry) {
      // refresh 接口本身 401 → 直接登出，不再重试
      if (originalRequest.url?.includes('/token/refresh/')) {
        _forceLogout()
        return Promise.reject(error)
      }

      // 如果正在刷新，将当前请求加入等待队列
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((newToken) => {
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`
            return service(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const authStore = useAuthStore()
      try {
        const newToken = await authStore.refreshTokenAction()
        processQueue(null, newToken)
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        return service(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        _forceLogout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // ── 其他错误 ──────────────────────────────────────────────────
    if (status === 403) {
      ElMessage.error(error.response?.data?.msg || '权限不足')
    } else if (status === 500) {
      ElMessage.error('服务器错误，请稍后重试')
    } else if (status !== 401) {
      ElMessage.error(error.response?.data?.msg || error.message || '网络错误')
    }

    return Promise.reject(error.response?.data || error)
  },
)

function _forceLogout() {
  const authStore = useAuthStore()
  ElMessage.error('登录已过期，请重新登录')
  authStore.logout()
  router.push('/login')
}

export default service

