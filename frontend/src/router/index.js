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
        path: 'versions/perception',
        name: 'PerceptionVersions',
        component: () => import('@/views/versions/perception/PerceptionVersionList.vue'),
        meta: { title: '感知版本', parentTitle: '版本管理', parentPath: '/versions/perception' },
      },
      {
        path: 'envs/perception',
        name: 'PerceptionEnvs',
        component: () => import('@/views/versions/perception/PerceptionEnvList.vue'),
        meta: { title: '感知环境', parentTitle: '版本管理', parentPath: '/versions/perception' },
      },
      {
        path: 'versions/loc',
        name: 'LocVersions',
        component: () => import('@/views/versions/loc/LocVersionList.vue'),
        meta: { title: '定位版本', parentTitle: '版本管理', parentPath: '/versions/loc' },
      },
      {
        path: 'envs/loc',
        name: 'LocEnvs',
        component: () => import('@/views/versions/loc/LocEnvList.vue'),
        meta: { title: '定位环境', parentTitle: '版本管理', parentPath: '/versions/loc' },
      },
      {
        path: 'versions/ctl',
        name: 'CtlVersions',
        component: () => import('@/views/versions/ctl/CtlVersionList.vue'),
        meta: { title: '控制版本', parentTitle: '版本管理', parentPath: '/versions/ctl' },
      },
      {
        path: 'envs/ctl',
        name: 'CtlEnvs',
        component: () => import('@/views/versions/ctl/CtlEnvList.vue'),
        meta: { title: '控制环境', parentTitle: '版本管理', parentPath: '/versions/ctl' },
      },
      {
        path: 'versions/sim',
        name: 'SimVersions',
        component: () => import('@/views/versions/sim/SimVersionList.vue'),
        meta: { title: '仿真版本', parentTitle: '版本管理', parentPath: '/versions/sim' },
      },
      {
        path: 'envs/sim',
        name: 'SimEnvs',
        component: () => import('@/views/versions/sim/SimEnvList.vue'),
        meta: { title: '仿真环境', parentTitle: '版本管理', parentPath: '/versions/sim' },
      },
      {
        path: 'versions/sen',
        name: 'SenVersions',
        component: () => import('@/views/versions/sen/SenVersionList.vue'),
        meta: { title: '传感器版本', parentTitle: '版本管理', parentPath: '/versions/sen' },
      },
      {
        path: 'envs/sen',
        name: 'SenEnvs',
        component: () => import('@/views/versions/sen/SenEnvList.vue'),
        meta: { title: '传感器环境', parentTitle: '版本管理', parentPath: '/versions/sen' },
      },
      // ── 系统管理（仅 is_staff 可访） ───────────────────────
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('@/views/system/UserManagement.vue'),
        meta: { title: '用户管理', parentTitle: '系统管理', requireStaff: true },
      },
      {
        path: 'system/roles',
        name: 'RoleManagement',
        component: () => import('@/views/system/RoleManagement.vue'),
        meta: { title: '角色管理', parentTitle: '系统管理', requireStaff: true },
      },
      // ── 数据管理 ────────────────────────────────────────────────
      {
        path: 'data/sim_project_property',
        name: 'SimProjectProperty',
        component: () => import('@/views/data_manage/sim_project_property/SimProjectPropertyList.vue'),
        meta: { title: '仿真项目数据', parentTitle: '数据管理', parentPath: '/data/sim_project_property' },
      },
      {
        path: 'data/sim_common_property',
        name: 'SimCommonProperty',
        component: () => import('@/views/data_manage/sim_common_property/SimCommonPropertyList.vue'),
        meta: { title: '仿真通用数据', parentTitle: '数据管理', parentPath: '/data/sim_common_property' },
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
      return next('/')
    }
  }

  // is_staff 页面限制
  if (to.meta.requireStaff && !authStore.userInfo?.is_staff) {
    return next('/dashboard')
  }

  next()
})

export default router
