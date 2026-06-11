import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config

    // 如果是 401 错误且不是刷新令牌请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const userStore = useUserStore()

      // 尝试刷新令牌
      if (userStore.refreshToken) {
        try {
          await userStore.refreshAccessToken()
          // 重新发送原请求
          originalRequest.headers.Authorization = `Bearer ${userStore.token}`
          return api(originalRequest)
        } catch (refreshError) {
          // 刷新失败，跳转登录
          userStore.logout()
          router.push('/login')
          return Promise.reject(refreshError)
        }
      } else {
        // 没有刷新令牌，跳转登录
        userStore.logout()
        router.push('/login')
      }
    }

    // 显示错误消息
    const message = error.response?.data?.detail || '请求失败，请稍后重试'
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

export default api
