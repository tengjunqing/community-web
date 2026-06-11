<template>
  <div class="post-card">
    <!-- 用户信息 -->
    <div class="post-header">
      <UserAvatar :user="post.user" :size="40" show-name />
      <div class="post-meta">
        <span class="post-time">{{ formatDateTime(post.created_at) }}</span>
        <span v-if="post.topic" class="post-topic">#{{ post.topic.name }}</span>
      </div>
    </div>

    <!-- 内容 -->
    <div class="post-content" @click="goToDetail">
      <p>{{ post.content }}</p>
    </div>

    <!-- 图片 -->
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

    <!-- 操作栏 -->
    <div class="post-actions">
      <div class="action-item" @click="handleLike">
        <el-icon :class="{ liked: post.is_liked }"><Star /></el-icon>
        <span>{{ post.like_count || '' }}</span>
      </div>
      <div class="action-item" @click="goToDetail">
        <el-icon><ChatDotRound /></el-icon>
        <span>{{ post.comment_count || '' }}</span>
      </div>
      <div class="action-item">
        <el-icon><Share /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { usePostStore } from '@/stores/post'
import { formatDateTime } from '@/utils/helpers'
import UserAvatar from './UserAvatar.vue'
import { Star, ChatDotRound, Share } from '@element-plus/icons-vue'

const props = defineProps({
  post: {
    type: Object,
    required: true,
  },
})

const router = useRouter()
const postStore = usePostStore()

function goToDetail() {
  router.push(`/post/${props.post.id}`)
}

async function handleLike() {
  try {
    if (props.post.is_liked) {
      await postStore.unlikePost(props.post.id)
    } else {
      await postStore.likePost(props.post.id)
    }
  } catch (error) {
    console.error('操作失败:', error)
  }
}
</script>

<style lang="scss" scoped>
.post-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }
}

.post-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;

  .post-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #999;

    .post-topic {
      color: #409eff;
      cursor: pointer;

      &:hover {
        color: #66b1ff;
      }
    }
  }
}

.post-content {
  margin-bottom: 12px;
  cursor: pointer;

  p {
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    word-break: break-word;
  }
}

.post-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;

  .post-image {
    width: 100%;
    height: 120px;
    border-radius: 4px;
    cursor: pointer;
  }
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 40px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;

  .action-item {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #999;
    cursor: pointer;
    transition: color 0.2s;

    .el-icon {
      font-size: 18px;
    }

    &:hover {
      color: #409eff;
    }

    .liked {
      color: #ff6b6b;
    }
  }
}
</style>
