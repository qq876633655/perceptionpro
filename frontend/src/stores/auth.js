import { defineStore } from 'pinia'
import { login as loginApi, getCurrentUser, refreshToken as refreshTokenApi } from '@/api/auth'

const TOKEN_KEY = 'pp_token'
const REFRESH_KEY = 'pp_refresh_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    refreshTokenVal: localStorage.getItem(REFRESH_KEY) || '',
    userInfo: null, // { id, username, phone_number, roles, permissions }
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,

    /** 当前用户角色列表，如 ['admin', 'developer'] */
    roles: (state) => state.userInfo?.roles ?? [],

    /** 当前用户权限码列表，如 ['version:create', 'version:delete'] */
    permissions: (state) => state.userInfo?.permissions ?? [],

    /** 判断是否拥有某角色 */
    hasRole: (state) => (role) => state.userInfo?.roles?.includes(role) ?? false,

    /** 判断是否拥有某权限码 */
    hasPermission: (state) => (perm) => state.userInfo?.permissions?.includes(perm) ?? false,
  },

  actions: {
    /** 登录：POST /api/login/ → 存储 access + refresh token */
    async loginAction(credentials) {
      const res = await loginApi(credentials)
      this._saveTokens(res.data.access, res.data.refresh)
      await this.fetchUserInfo()
    },

    /** 刷新 access token：POST /api/token/refresh/ */
    async refreshTokenAction() {
      if (!this.refreshTokenVal) throw new Error('no refresh token')
      const res = await refreshTokenApi(this.refreshTokenVal)
      const newAccess = res.data.access
      this.token = newAccess
      localStorage.setItem(TOKEN_KEY, newAccess)
      return newAccess
    },

    /** 拉取当前用户信息 */
    async fetchUserInfo() {
      const res = await getCurrentUser()
      this.userInfo = res.data
    },

    /** 登出：清除所有本地状态 */
    logout() {
      this.token = ''
      this.refreshTokenVal = ''
      this.userInfo = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_KEY)
    },

    _saveTokens(access, refresh) {
      this.token = access
      this.refreshTokenVal = refresh ?? ''
      localStorage.setItem(TOKEN_KEY, access)
      if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
    },
  },
})
