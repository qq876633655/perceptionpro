import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由白名单（无需登录）
const WHITE_LIST = ['/login']

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layout/BasicLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'HomeFilled' },
      },
      {
        path: 'versions',
        name: 'Versions',
        component: () => import('@/views/version/VersionList.vue'),
        meta: {
          title: '版本管理',
          icon: 'Document',
          // 需要以下任一权限
          permissions: ['version:view'],
        },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── 全局前置守卫 ──────────────────────────────────────────────────
router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - PerceptionPro` : 'PerceptionPro'

  const authStore = useAuthStore()

  // 未登录且不在白名单 → 跳转登录
  if (!authStore.isLoggedIn && !WHITE_LIST.includes(to.path)) {
    return next('/login')
  }

  // 已登录但未加载用户信息 → 先拉取
  if (authStore.isLoggedIn && !authStore.userInfo) {
    try {
      await authStore.fetchUserInfo()
    } catch {
      authStore.logout()
      return next('/login')
    }
  }

  // 已登录访问登录页 → 跳首页
  if (authStore.isLoggedIn && to.path === '/login') {
    return next('/')
  }

  // 路由级权限校验
  const requiredPermissions = to.meta.permissions
  if (requiredPermissions?.length) {
    const hasAll = requiredPermissions.every((p) => authStore.hasPermission(p))
    if (!hasAll) {
      return next('/') // 权限不足，跳回首页（可换 403 页面）
    }
  }

  next()
})

export default router
