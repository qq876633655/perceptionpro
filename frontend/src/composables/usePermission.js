import { useAuthStore } from '@/stores/auth'

/**
 * 权限判断 composable
 *
 * 使用 Django permission 格式：'app_label.action_modelname'
 * 例：hasPermission('version_pack.add_perversion')
 *
 * 超级管理员始终返回 true；其余用户按角色分配的权限判断。
 */
export function usePermission() {
  const authStore = useAuthStore()

  // 超级管理员跳过所有权限检查
  const isSuperUser = authStore.isSuperUser

  /** 判断是否拥有指定 Django 权限（如 'version_pack.add_perversion'） */
  const hasPermission = (perm) => isSuperUser || authStore.hasPermission(perm)

  const hasRole = (role) => authStore.hasRole(role)

  /** 按钮级：支持 string | string[]，任一匹配即可 */
  const canDo = (permOrPerms) => {
    if (isSuperUser) return true
    const perms = Array.isArray(permOrPerms) ? permOrPerms : [permOrPerms]
    return perms.some((p) => authStore.hasPermission(p))
  }

  return { isSuperUser, hasPermission, hasRole, canDo }
}
