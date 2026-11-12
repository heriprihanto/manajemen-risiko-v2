import { defineStore } from 'pinia'
import api from '@/api'

let initialization

const TOKEN_KEY = 'mr_token'
const USER_KEY = 'mr_user'

function loadUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY)) || null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || null,
    user: loadUser(),
    ssoEnabled: false,
    loginUrl: '',
  }),
  getters: {
    isAuthenticated: (s) => s.ssoEnabled ? !!s.user : !!s.token,
    isAdmin: (s) => s.user?.role_id === 1,
    // Array id OPD (id_sub_pd) yang boleh diakses; kosong = semua (Admin).
    allowedOpds: (s) => (s.user?.role_id === 1 ? [] : s.user?.opds || []),
    displayName: (s) => s.user?.display_name || s.user?.username || '',
  },
  actions: {
    async initialize() {
      if (!initialization) initialization = api.get('/auth/config').then(({ data }) => {
        this.ssoEnabled = data.sso_enabled
        this.loginUrl = data.login_url
        if (this.ssoEnabled) this.clearSession()
      }).catch((error) => { initialization = null; throw error })
      await initialization
    },
    async refreshSession() {
      try {
        const { data } = await api.get('/auth/me')
        this.user = data
        return true
      } catch (error) {
        this.clearSession()
        if (error.response?.status === 401) return false
        throw error
      }
    },
    redirectToLogin(path = '/') {
      const target = new URL(this.loginUrl, window.location.origin)
      target.searchParams.set('return_to', new URL(import.meta.env.BASE_URL + path.replace(/^\//, ''), window.location.origin).href)
      window.location.replace(target.href)
    },
    async login(username, password, captcha = {}) {
      const { data } = await api.post('/auth/login', {
        username,
        password,
        captcha_id: captcha.id,
        captcha_answer: captcha.answer,
      })
      this.setSession(data.access_token, data.user)
      return data.user
    },
    setSession(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    async logout() {
      if (this.ssoEnabled) await api.post('/auth/logout')
      this.clearSession()
    },
    clearSession() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
