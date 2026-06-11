<template>
  <div class="post-detail" v-loading="loading">
    <div v-if="post" class="detail-content">
      <!-- 动态详情 -->
      <div class="post-card">
        <div class="post-header">
          <UserAvatar :user="post.user" :size="48" show-name />
          <div class="post-meta">
            <span class="post-time">{{ formatDateTime(post.created_at) }}</span>
            <span v-if="post.topic" class="post-topic">#{{ post.topic.name }}</span>
          </div>
        </div>

        <div class="post-content">
          <p>{{ post.content }}</p>
        </div>

        <div v-if="post.images?.length" class="post-images">
          <el-image
            v-for="(image, index) in post.images"
            :key="index"
            :src="image"
            :preview-src-list="post.images"
            :initial-index="index"
            fit="cover"
            class="post-image"
          />
        </div>

        <div class="post-actions">
          <div class="action-item" @click="handleLike">
            <el-icon :class="{ liked: post.is_liked }"><Star /></el-icon>
            <span>{{ post.like_count || '点赞' }}</span>
          </div>
          <div class="action-item">
            <el-icon><ChatDotRound /></el-icon>
            <span>{{ post.comment_count || '评论' }}</span>
          </div>
          <div class="action-item">
            <el-icon><Share /></el-icon>
            <span>分享</span>
          </div>
        </div>
      </div>

      <!-- 评论区 -->
      <div class="comment-section">
        <h3 class="section-title">评论 ({{ post.comment_count || 0 }})</h3>
        <CommentList :post-id="postId" />
      </div>
    </div>

    <el-empty v-else-if="!loading" description="动态不存在" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePostStore } from '@/stores/post'
import { formatDateTime } from '@/utils/helpers'
import UserAvatar from '@/components/common/UserAvatar.vue'
import CommentList from '@/components/common/CommentList.vue'
import { Star, ChatDotRound, Share } from '@element-plus/icons-vue'

const route = useRoute()
const postStore = usePostStore()

const postId = computed(() => route.params.id)
const post = computed(() => postStore.currentPost)
const loading = computed(() => postStore.loading)

onMounted(async () => {
  await fetchPost()
  await fetchComments()
})

async function fetchPost() {
  try {
    await postStore.fetchPost(postId.value)
  } catch (error) {
    console.error('获取动态详情失败:', error)
  }
}

async function fetchComments() {
  try {
    await postStore.fetchComments(postId.value, { skip: 0, limit: 20 })
  } catch (error) {
    console.error('获取评论列表失败:', error)
  }
}

async function handleLike() {
  try {
    if (post.value.is_liked) {
      await postStore.unlikePost(postId.value)
    } else {
      await postStore.likePost(postId.value)
    }
  } catch (error) {
    console.error('操作失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.post-detail {
  max-width: 680px;
  margin: 0 auto;
}

.post-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;

  .post-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .post-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #999;

      .post-topic {
        color: #409eff;
        cursor: pointer;
      }
    }
  }

  .post-content {
    margin-bottom: 16px;

    p {
      font-size: 16px;
      line-height: 1.8;
      color: #333;
      word-break: break-word;
    }
  }

  .post-images {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 16px;

    .post-image {
      width: 100%;
      height: 150px;
      border-radius: 4px;
      cursor: pointer;
    }
  }

  .post-actions {
    display: flex;
    align-items: center;
    gap: 40px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;

    .action-item {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #999;
      cursor: pointer;
      transition: color 0.2s;

      .el-icon {
        font-size: 20px;
      }

      &:hover {
        color: #409eff;
      }

      .liked {
        color: #ff6b6b;
      }
    }
  }
}

.comment-section {
  background: #fff;
  border-radius: 8px;
  padding: 24px;

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 20px;
  }
}
</style>
