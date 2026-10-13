import { defineStore } from 'pinia'
import api from '@/api'

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
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    isAdmin: (s) => s.user?.role_id === 1,
    // Array id OPD (id_sub_pd) yang boleh diakses; kosong = semua (Admin).
    allowedOpds: (s) => (s.user?.role_id === 1 ? [] : s.user?.opds || []),
    displayName: (s) => s.user?.display_name || s.user?.username || '',
  },
  actions: {
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
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
