import { defineStore } from 'pinia'
import { ref } from 'vue'
import { groupApi } from '@/api'

export const useGroupStore = defineStore('group', () => {
  // 状态
  const groups = ref([])
  const currentGroup = ref(null)
  const members = ref([])
  const groupPosts = ref([])
  const announcements = ref([])
  const total = ref(0)
  const loading = ref(false)

  // 获取群组列表
  async function fetchGroups(params = {}) {
    loading.value = true
    try {
      const result = await groupApi.getGroups(params)
      if (params.skip === 0) {
        groups.value = result.items
      } else {
        groups.value = [...groups.value, ...result.items]
      }
      total.value = result.total
      return result
    } catch (error) {
      console.error('获取群组列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建群组
  async function createGroup(data) {
    const result = await groupApi.createGroup(data)
    groups.value.unshift(result)
    total.value++
    return result
  }

  // 获取群组详情
  async function fetchGroup(groupId) {
    loading.value = true
    try {
      const result = await groupApi.getGroup(groupId)
      currentGroup.value = result
      return result
    } catch (error) {
      console.error('获取群组详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新群组信息
  async function updateGroup(groupId, data) {
    const result = await groupApi.updateGroup(groupId, data)
    currentGroup.value = result

    // 更新列表中的群组
    const index = groups.value.findIndex(g => g.id === groupId)
    if (index !== -1) {
      groups.value[index] = result
    }

    return result
  }

  // 删除群组
  async function deleteGroup(groupId) {
    await groupApi.deleteGroup(groupId)

    // 从列表中移除
    groups.value = groups.value.filter(g => g.id !== groupId)
    total.value--
  }

  // 加入群组
  async function joinGroup(groupId) {
    await groupApi.joinGroup(groupId)

    // 更新当前群组
    if (currentGroup.value?.id === groupId) {
      currentGroup.value.is_member = true
      currentGroup.value.member_count++
    }

    // 更新列表中的群组
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.is_member = true
      group.member_count++
    }
  }

  // 退出群组
  async function leaveGroup(groupId) {
    await groupApi.leaveGroup(groupId)

    // 更新当前群组
    if (currentGroup.value?.id === groupId) {
      currentGroup.value.is_member = false
      currentGroup.value.member_count--
    }

    // 更新列表中的群组
    const group = groups.value.find(g => g.id === groupId)
    if (group) {
      group.is_member = false
      group.member_count--
    }
  }

  // 获取成员列表
  async function fetchMembers(groupId, params = {}) {
    const result = await groupApi.getMembers(groupId, params)
    members.value = result.items
    return result
  }

  // 获取群组动态
  async function fetchGroupPosts(groupId, params = {}) {
    loading.value = true
    try {
      const result = await groupApi.getGroupPosts(groupId, params)
      if (params.skip === 0) {
        groupPosts.value = result.items
      } else {
        groupPosts.value = [...groupPosts.value, ...result.items]
      }
      return result
    } catch (error) {
      console.error('获取群组动态失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 发布群组动态
  async function createGroupPost(groupId, data) {
    const result = await groupApi.createGroupPost(groupId, data)
    groupPosts.value.unshift(result)
    return result
  }

  // 获取公告列表
  async function fetchAnnouncements(groupId, params = {}) {
    const result = await groupApi.getAnnouncements(groupId, params)
    announcements.value = result.items
    return result
  }

  // 发布公告
  async function createAnnouncement(groupId, data) {
    const result = await groupApi.createAnnouncement(groupId, data)
    announcements.value.unshift(result)
    return result
  }

  // 重置状态
  function reset() {
    groups.value = []
    currentGroup.value = null
    members.value = []
    groupPosts.value = []
    announcements.value = []
    total.value = 0
  }

  return {
    groups,
    currentGroup,
    members,
    groupPosts,
    announcements,
    total,
    loading,
    fetchGroups,
    createGroup,
    fetchGroup,
    updateGroup,
    deleteGroup,
    joinGroup,
    leaveGroup,
    fetchMembers,
    fetchGroupPosts,
    createGroupPost,
    fetchAnnouncements,
    createAnnouncement,
    reset,
  }
})
