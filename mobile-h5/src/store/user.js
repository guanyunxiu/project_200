import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, getCurrentUserApi } from '@/api/auth'
import { getStudentDetailApi } from '@/api/student'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  const studentInfo = ref(JSON.parse(localStorage.getItem('studentInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  const setToken = (accessToken, refresh) => {
    token.value = accessToken
    refreshToken.value = refresh
    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', refresh)
  }

  const setUserInfo = (info) => {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  const setStudentInfo = (info) => {
    studentInfo.value = info
    localStorage.setItem('studentInfo', JSON.stringify(info))
  }

  const login = async (username, password) => {
    const res = await loginApi(username, password)
    setToken(res.access, res.refresh)
    setUserInfo(res.user)
    if (res.user.student_id) {
      const student = await getStudentDetailApi(res.user.student_id)
      setStudentInfo(student)
    }
    return res
  }

  const fetchUserInfo = async () => {
    const res = await getCurrentUserApi()
    setUserInfo(res)
    if (res.student_id) {
      const student = await getStudentDetailApi(res.student_id)
      setStudentInfo(student)
    }
    return res
  }

  const logout = () => {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    studentInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('studentInfo')
  }

  return {
    token,
    refreshToken,
    userInfo,
    studentInfo,
    isLoggedIn,
    setToken,
    setUserInfo,
    setStudentInfo,
    login,
    fetchUserInfo,
    logout
  }
})
