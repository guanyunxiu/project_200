import axios from 'axios'
import { showToast, showDialog } from 'vant'
import { useUserStore } from '@/store/user'
import router from '@/router'

const service = axios.create({
  baseURL: '/api',
  timeout: 15000
})

service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const userStore = useUserStore()
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        showDialog({
          title: '系统提示',
          message: '登录状态已过期，请重新登录',
          confirmButtonText: '重新登录',
          showCancelButton: false
        }).then(() => {
          userStore.logout()
          router.replace('/login')
        })
      } else if (status === 403) {
        showToast('没有操作权限')
      } else if (status === 400 || status === 500) {
        const msg = error.response.data?.detail || error.response.data?.error || '操作失败'
        showToast(msg)
      } else {
        showToast('服务器错误')
      }
    } else {
      showToast('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default service
