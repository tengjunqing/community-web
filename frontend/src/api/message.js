import api from '@/plugins/axios'

export default {
  // 获取会话列表
  getConversations(params) {
    return api.get('/messages/conversations', { params })
  },

  // 创建或获取会话
  createConversation(userId) {
    return api.post(`/messages/conversations/${userId}`)
  },

  // 获取消息列表
  getMessages(conversationId, params) {
    return api.get(`/messages/conversations/${conversationId}/messages`, { params })
  },

  // 发送消息
  sendMessage(conversationId, data) {
    return api.post(`/messages/conversations/${conversationId}/messages`, data)
  },

  // 标记消息已读
  markAsRead(conversationId) {
    return api.put(`/messages/conversations/${conversationId}/read`)
  },
}
