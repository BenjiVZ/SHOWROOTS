import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)
  const isTalent = computed(() => user.value?.role === 'talent')
  const isClient = computed(() => user.value?.role === 'client')
  const isPartner = computed(() => user.value?.role === 'partner')
  const isAdmin = computed(() => user.value?.role === 'admin')
  // True si Partner es el rol primario O si el usuario lo activó como rol secundario
  const hasPartnerRole = computed(() => user.value?.role === 'partner' || !!user.value?.is_partner_active)

  const roleLabel = computed(() => {
    const map = { talent: 'Talento', client: 'Cliente', partner: 'Aliado', admin: 'Admin' }
    return map[user.value?.role] || ''
  })

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    user.value = data.user
    accessToken.value = data.tokens.access
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('access_token', data.tokens.access)
    localStorage.setItem('refresh_token', data.tokens.refresh)
    return data
  }

  async function register(userData) {
    const { data } = await api.post('/auth/register/', userData)
    user.value = data.user
    accessToken.value = data.tokens.access
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('access_token', data.tokens.access)
    localStorage.setItem('refresh_token', data.tokens.refresh)
    return data
  }

  async function fetchMe() {
    const { data } = await api.get('/auth/me/')
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user, accessToken, isLoggedIn,
    isTalent, isClient, isPartner, isAdmin, hasPartnerRole, roleLabel,
    login, register, fetchMe, logout
  }
})
