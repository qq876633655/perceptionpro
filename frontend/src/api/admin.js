import request from '@/utils/request'

// ════════════════════════════════════════════════════════════════════
// 用户管理  /api/users/
// ════════════════════════════════════════════════════════════════════

/** 用户列表（分页 + 筛选） */
export function getUserList(params) {
  return request({ url: '/users/', method: 'get', params })
}

/** 创建用户 */
export function createUser(data) {
  return request({ url: '/users/', method: 'post', data })
}

/** 更新用户 */
export function updateUser(id, data) {
  return request({ url: `/users/${id}/`, method: 'patch', data })
}

/** 删除用户 */
export function deleteUser(id) {
  return request({ url: `/users/${id}/`, method: 'delete' })
}

// ════════════════════════════════════════════════════════════════════
// 角色管理  /api/groups/
// ════════════════════════════════════════════════════════════════════

/** 角色列表（分页） */
export function getGroupList(params) {
  return request({ url: '/groups/', method: 'get', params })
}

/** 创建角色 */
export function createGroup(data) {
  return request({ url: '/groups/', method: 'post', data })
}

/** 更新角色（含权限） */
export function updateGroup(id, data) {
  return request({ url: `/groups/${id}/`, method: 'patch', data })
}

/** 删除角色 */
export function deleteGroup(id) {
  return request({ url: `/groups/${id}/`, method: 'delete' })
}

/** 获取所有可用权限列表（用于角色权限选择器） */
export function getAllPermissions() {
  return request({ url: '/groups/all_permissions/', method: 'get' })
}
