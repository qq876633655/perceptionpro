import { useAuthStore } from '@/stores/auth'

/**
 * 权限判断 composable
 *
 * 使用：
 *   const { hasPermission, hasRole, isAdmin } = usePermission()
 *   if (hasPermission('version:delete')) { ... }
 */
export function usePermission() {
  const authStore = useAuthStore()

  const isAdmin = authStore.hasRole('admin')

  const hasPermission = (perm) => isAdmin || authStore.hasPermission(perm)

  const hasRole = (role) => authStore.hasRole(role)

  /** 按钮级：同时支持 string | string[] */
  const canDo = (permOrPerms) => {
    if (isAdmin) return true
    const perms = Array.isArray(permOrPerms) ? permOrPerms : [permOrPerms]
    return perms.some((p) => authStore.hasPermission(p))
  }

  return { isAdmin, hasPermission, hasRole, canDo }
}
