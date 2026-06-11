import { defineStore } from 'pinia'
import { ref } from 'vue'
import { postApi } from '@/api'

export const usePostStore = defineStore('post', () => {
  // 状态
  const posts = ref([])
  const currentPost = ref(null)
  const comments = ref([])
  const topics = ref([])
  const total = ref(0)
  const loading = ref(false)

  // 获取动态列表
  async function fetchPosts(params = {}) {
    loading.value = true
    try {
      const result = await postApi.getPosts(params)
      if (params.skip === 0) {
        posts.value = result.items
      } else {
        posts.value = [...posts.value, ...result.items]
      }
      total.value = result.total
      return result
    } catch (error) {
      console.error('获取动态列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 发布动态
  async function createPost(data) {
    const result = await postApi.createPost(data)
    posts.value.unshift(result)
    total.value++
    return result
  }

  // 获取动态详情
  async function fetchPost(postId) {
    loading.value = true
    try {
      const result = await postApi.getPost(postId)
      currentPost.value = result
      return result
    } catch (error) {
      console.error('获取动态详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新动态
  async function updatePost(postId, data) {
    const result = await postApi.updatePost(postId, data)
    currentPost.value = result

    // 更新列表中的动态
    const index = posts.value.findIndex(p => p.id === postId)
    if (index !== -1) {
      posts.value[index] = result
    }

    return result
  }

  // 删除动态
  async function deletePost(postId) {
    await postApi.deletePost(postId)

    // 从列表中移除
    posts.value = posts.value.filter(p => p.id !== postId)
    total.value--
  }

  // 点赞动态
  async function likePost(postId) {
    await postApi.likePost(postId)

    // 更新当前动态
    if (currentPost.value?.id === postId) {
      currentPost.value.like_count++
      currentPost.value.is_liked = true
    }

    // 更新列表中的动态
    const post = posts.value.find(p => p.id === postId)
    if (post) {
      post.like_count++
      post.is_liked = true
    }
  }

  // 取消点赞
  async function unlikePost(postId) {
    await postApi.unlikePost(postId)

    // 更新当前动态
    if (currentPost.value?.id === postId) {
      currentPost.value.like_count--
      currentPost.value.is_liked = false
    }

    // 更新列表中的动态
    const post = posts.value.find(p => p.id === postId)
    if (post) {
      post.like_count--
      post.is_liked = false
    }
  }

  // 获取评论列表
  async function fetchComments(postId, params = {}) {
    const result = await postApi.getComments(postId, params)
    if (params.skip === 0) {
      comments.value = result.items
    } else {
      comments.value = [...comments.value, ...result.items]
    }
    return result
  }

  // 发表评论
  async function createComment(postId, data) {
    const result = await postApi.createComment(postId, data)
    comments.value.unshift(result)

    // 更新当前动态的评论数
    if (currentPost.value?.id === postId) {
      currentPost.value.comment_count++
    }

    // 更新列表中的动态
    const post = posts.value.find(p => p.id === postId)
    if (post) {
      post.comment_count++
    }

    return result
  }

  // 获取话题列表
  async function fetchTopics(params = {}) {
    const result = await postApi.getTopics(params)
    topics.value = result
    return result
  }

  // 重置状态
  function reset() {
    posts.value = []
    currentPost.value = null
    comments.value = []
    total.value = 0
  }

  return {
    posts,
    currentPost,
    comments,
    topics,
    total,
    loading,
    fetchPosts,
    createPost,
    fetchPost,
    updatePost,
    deletePost,
    likePost,
    unlikePost,
    fetchComments,
    createComment,
    fetchTopics,
    reset,
  }
})
