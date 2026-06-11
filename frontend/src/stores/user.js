import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(null)
  const userProfile = ref(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userId = computed(() => userInfo.value?.id)

  // 设置令牌
  function setTokens(accessToken, refresh) {
    token.value = accessToken
    refreshToken.value = refresh
    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', refresh)
  }

  // 清除令牌
  function clearTokens() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    userProfile.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  // 用户注册
  async function register(data) {
    const result = await userApi.register(data)
    return result
  }

  // 用户登录
  async function login(username, password) {
    const result = await userApi.login({ username, password })
    setTokens(result.access_token, result.refresh_token)

    // 获取用户信息
    await fetchUserInfo()

    return result
  }

  // 刷新令牌
  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('没有刷新令牌')
    }

    const result = await userApi.refreshToken(refreshToken.value)
    setTokens(result.access_token, result.refresh_token)

    return result
  }

  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const result = await userApi.getMe()
      userInfo.value = result
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  // 获取用户详细资料
  async function fetchUserProfile(userId) {
    try {
      const result = userId
        ? await userApi.getUserProfile(userId)
        : await userApi.getMyProfile()
      userProfile.value = result
      return result
    } catch (error) {
      console.error('获取用户资料失败:', error)
      throw error
    }
  }

  // 更新用户信息
  async function updateProfile(data) {
    const result = await userApi.updateMyProfile(data)
    userInfo.value = result
    return result
  }

  // 关注用户
  async function followUser(userId) {
    await userApi.followUser(userId)
  }

  // 取消关注
  async function unfollowUser(userId) {
    await userApi.unfollowUser(userId)
  }

  // 登出
  function logout() {
    clearTokens()
  }

  return {
    token,
    refreshToken,
    userInfo,
    userProfile,
    isAuthenticated,
    userId,
    setTokens,
    clearTokens,
    register,
    login,
    refreshAccessToken,
    fetchUserInfo,
    fetchUserProfile,
    updateProfile,
    followUser,
    unfollowUser,
    logout,
  }
})
