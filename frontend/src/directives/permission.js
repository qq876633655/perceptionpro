/**
 * 全局权限指令
 *
 * 用法：
 *   <el-button v-permission="'version:create'">新建</el-button>
 *   <el-button v-permission="['version:create', 'version:edit']">操作</el-button>
 *
 * 当用户不具备所需权限时，该元素会从 DOM 中移除。
 */
import { useAuthStore } from '@/stores/auth'

export const permissionDirective = {
  mounted(el, binding) {
    const authStore = useAuthStore()
    const required = binding.value

    const check = (perm) => authStore.isSuperUser || authStore.hasPermission(perm)

    const allowed = Array.isArray(required)
      ? required.some(check)  // 有其中一个即可
      : check(required)

    if (!allowed) {
      el.parentNode?.removeChild(el)
    }
  },
}
