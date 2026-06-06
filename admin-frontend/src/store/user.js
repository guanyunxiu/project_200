import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginApi, getUserInfoApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const login = async (loginForm) => {
    const res = await loginApi(loginForm)
    token.value = res.access
    userInfo.value = res.user
    localStorage.setItem('token', res.access)
    localStorage.setItem('userInfo', JSON.stringify(res.user))
    localStorage.setItem('refreshToken', res.refresh)
    return res
  }

  const getUserInfo = async () => {
    const res = await getUserInfoApi()
    userInfo.value = res
    localStorage.setItem('userInfo', JSON.stringify(res))
    return res
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('refreshToken')
  }

  return {
    token,
    userInfo,
    login,
    getUserInfo,
    logout
  }
})
