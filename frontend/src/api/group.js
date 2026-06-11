import api from '@/plugins/axios'

export default {
  // 获取群组列表
  getGroups(params) {
    return api.get('/groups', { params })
  },

  // 创建群组
  createGroup(data) {
    return api.post('/groups', data)
  },

  // 获取群组详情
  getGroup(groupId) {
    return api.get(`/groups/${groupId}`)
  },

  // 更新群组信息
  updateGroup(groupId, data) {
    return api.put(`/groups/${groupId}`, data)
  },

  // 删除群组
  deleteGroup(groupId) {
    return api.delete(`/groups/${groupId}`)
  },

  // 加入群组
  joinGroup(groupId) {
    return api.post(`/groups/${groupId}/join`)
  },

  // 退出群组
  leaveGroup(groupId) {
    return api.delete(`/groups/${groupId}/join`)
  },

  // 获取成员列表
  getMembers(groupId, params) {
    return api.get(`/groups/${groupId}/members`, { params })
  },

  // 获取群组动态
  getGroupPosts(groupId, params) {
    return api.get(`/groups/${groupId}/posts`, { params })
  },

  // 发布群组动态
  createGroupPost(groupId, data) {
    return api.post(`/groups/${groupId}/posts`, data)
  },

  // 获取公告列表
  getAnnouncements(groupId, params) {
    return api.get(`/groups/${groupId}/announcements`, { params })
  },

  // 发布公告
  createAnnouncement(groupId, data) {
    return api.post(`/groups/${groupId}/announcements`, data)
  },
}
