import api from '@/plugins/axios'

export default {
  // 用户注册
  register(data) {
    return api.post('/auth/register', data)
  },

  // 用户登录
  login(data) {
    return api.post('/auth/login', data)
  },

  // 刷新令牌
  refreshToken(refreshToken) {
    return api.post('/auth/refresh', { refresh_token: refreshToken })
  },

  // 获取当前用户信息
  getMe() {
    return api.get('/auth/me')
  },

  // 获取当前用户详细资料
  getMyProfile() {
    return api.get('/users/me')
  },

  // 更新当前用户信息
  updateMyProfile(data) {
    return api.put('/users/me', data)
  },

  // 获取指定用户详细资料
  getUserProfile(userId) {
    return api.get(`/users/${userId}`)
  },

  // 关注用户
  followUser(userId) {
    return api.post(`/users/${userId}/follow`)
  },

  // 取消关注
  unfollowUser(userId) {
    return api.delete(`/users/${userId}/follow`)
  },

  // 获取粉丝列表
  getFollowers(userId, params) {
    return api.get(`/users/${userId}/followers`, { params })
  },

  // 获取关注列表
  getFollowing(userId, params) {
    return api.get(`/users/${userId}/following`, { params })
  },
}
