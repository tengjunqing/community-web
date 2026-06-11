import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { messageApi } from '@/api'

export const useMessageStore = defineStore('message', () => {
  // 状态
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const total = ref(0)
  const loading = ref(false)

  // 计算属性
  const unreadCount = computed(() => {
    return conversations.value.reduce((sum, conv) => sum + conv.unread_count, 0)
  })

  // 获取会话列表
  async function fetchConversations(params = {}) {
    loading.value = true
    try {
      const result = await messageApi.getConversations(params)
      conversations.value = result.items
      total.value = result.total
      return result
    } catch (error) {
      console.error('获取会话列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建或获取会话
  async function createConversation(userId) {
    const result = await messageApi.createConversation(userId)
    currentConversation.value = result
    return result
  }

  // 获取消息列表
  async function fetchMessages(conversationId, params = {}) {
    loading.value = true
    try {
      const result = await messageApi.getMessages(conversationId, params)
      if (params.skip === 0) {
        messages.value = result.items
      } else {
        messages.value = [...messages.value, ...result.items]
      }
      return result
    } catch (error) {
      console.error('获取消息列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 发送消息
  async function sendMessage(conversationId, data) {
    const result = await messageApi.sendMessage(conversationId, data)
    messages.value.push(result)

    // 更新会话列表
    const conv = conversations.value.find(c => c.id === conversationId)
    if (conv) {
      conv.last_message = result
      conv.last_message_at = result.created_at
    }

    return result
  }

  // 标记消息已读
  async function markAsRead(conversationId) {
    await messageApi.markAsRead(conversationId)

    // 更新会话列表
    const conv = conversations.value.find(c => c.id === conversationId)
    if (conv) {
      conv.unread_count = 0
    }
  }

  // 添加新消息（WebSocket）
  function addMessage(message) {
    // 如果是当前会话的消息
    if (currentConversation.value?.id === message.conversation_id) {
      messages.value.push(message)
    }

    // 更新会话列表
    const conv = conversations.value.find(c => c.id === message.conversation_id)
    if (conv) {
      conv.last_message = message
      conv.last_message_at = message.created_at
      if (currentConversation.value?.id !== message.conversation_id) {
        conv.unread_count++
      }
    }
  }

  // 设置当前会话
  function setCurrentConversation(conversation) {
    currentConversation.value = conversation
    messages.value = []
  }

  // 重置状态
  function reset() {
    conversations.value = []
    currentConversation.value = null
    messages.value = []
    total.value = 0
  }

  return {
    conversations,
    currentConversation,
    messages,
    total,
    loading,
    unreadCount,
    fetchConversations,
    createConversation,
    fetchMessages,
    sendMessage,
    markAsRead,
    addMessage,
    setCurrentConversation,
    reset,
  }
})
