import api from '@/plugins/axios'

export default {
  // 获取动态列表
  getPosts(params) {
    return api.get('/posts', { params })
  },

  // 发布动态
  createPost(data) {
    return api.post('/posts', data)
  },

  // 获取动态详情
  getPost(postId) {
    return api.get(`/posts/${postId}`)
  },

  // 更新动态
  updatePost(postId, data) {
    return api.put(`/posts/${postId}`, data)
  },

  // 删除动态
  deletePost(postId) {
    return api.delete(`/posts/${postId}`)
  },

  // 点赞动态
  likePost(postId) {
    return api.post(`/posts/${postId}/like`)
  },

  // 取消点赞
  unlikePost(postId) {
    return api.delete(`/posts/${postId}/like`)
  },

  // 获取评论列表
  getComments(postId, params) {
    return api.get(`/posts/${postId}/comments`, { params })
  },

  // 发表评论
  createComment(postId, data) {
    return api.post(`/posts/${postId}/comments`, data)
  },

  // 获取话题列表
  getTopics(params) {
    return api.get('/posts/topics', { params })
  },
}
