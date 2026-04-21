import request from '@/utils/request'
import axios from 'axios'

/**
 * 登录 - 使用 phone_number + password 换取 JWT token
 * 接口：POST /api/login/
 */
export function login(data) {
  return request({
    url: '/login/',
    method: 'post',
    data,
  })
}

/**
 * 获取 token pair（SimpleJWT 标准接口）
 * 接口：POST /api/token/
 */
export function obtainToken(data) {
  return request({
    url: '/token/',
    method: 'post',
    data,
  })
}

/**
 * 刷新 access token
 * 接口：POST /api/token/refresh/
 * 注意：直接用 axios 避免触发响应拦截器的刷新逻辑（防止死循环）
 */
export function refreshToken(refresh) {
  return axios.post('/api/token/refresh/', { refresh })
}

/**
 * 获取当前登录用户信息（含 roles & permissions）
 * 接口：GET /api/me/
 */
export function getCurrentUser() {
  return request({
    url: '/me/',
    method: 'get',
  })
}

/**
 * 修改密码
 * 接口：POST /api/change_pwd/
 */
export function changePassword(data) {
  return request({
    url: '/change_pwd/',
    method: 'post',
    data,
  })
}

// ── 用户管理 /api/users/ (RESTful CRUD) ─────────────────────────────
export function getUserList(params) {
  return request({ url: '/users/', method: 'get', params })
}

export function getUser(id) {
  return request({ url: `/users/${id}/`, method: 'get' })
}

export function createUser(data) {
  return request({ url: '/users/', method: 'post', data })
}

export function updateUser(id, data) {
  return request({ url: `/users/${id}/`, method: 'patch', data })
}

export function deleteUser(id) {
  return request({ url: `/users/${id}/`, method: 'delete' })
}
