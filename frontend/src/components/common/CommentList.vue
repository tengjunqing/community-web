<template>
  <div class="comment-list">
    <!-- 评论输入框 -->
    <div class="comment-input">
      <el-input
        v-model="commentContent"
        type="textarea"
        :rows="2"
        placeholder="写下你的评论..."
        maxlength="1000"
        show-word-limit
      />
      <el-button
        type="primary"
        :disabled="!commentContent.trim()"
        @click="handleSubmit"
      >
        发表评论
      </el-button>
    </div>

    <!-- 评论列表 -->
    <div class="comments">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <UserAvatar :user="comment.user" :size="32" />
        <div class="comment-content">
          <div class="comment-header">
            <span class="comment-user">{{ comment.user?.nickname || comment.user?.username }}</span>
            <span class="comment-time">{{ formatDateTime(comment.created_at) }}</span>
          </div>
          <div class="comment-text">{{ comment.content }}</div>
          <div class="comment-actions">
            <span class="action-btn" @click="handleReply(comment)">
              <el-icon><ChatDotRound /></el-icon>
              回复
            </span>
            <span class="action-btn">
              <el-icon><Star /></el-icon>
              {{ comment.like_count || '' }}
            </span>
          </div>

          <!-- 回复列表 -->
          <div v-if="comment.replies?.length" class="replies">
            <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <UserAvatar :user="reply.user" :size="24" />
              <div class="reply-content">
                <span class="reply-user">{{ reply.user?.nickname || reply.user?.username }}</span>
                <span class="reply-text">{{ reply.content }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more">
        <el-button text @click="loadMore">加载更多评论</el-button>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="comments.length === 0" description="暂无评论" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePostStore } from '@/stores/post'
import { formatDateTime } from '@/utils/helpers'
import UserAvatar from './UserAvatar.vue'
import { ChatDotRound, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  postId: {
    type: [Number, String],
    required: true,
  },
})

const postStore = usePostStore()
const commentContent = ref('')
const replyTo = ref(null)
const page = ref(1)

const comments = computed(() => postStore.comments)
const hasMore = computed(() => comments.value.length < postStore.total)

async function handleSubmit() {
  if (!commentContent.value.trim()) return

  try {
    await postStore.createComment(props.postId, {
      content: commentContent.value,
      parent_id: replyTo.value?.id,
    })
    commentContent.value = ''
    replyTo.value = null
    ElMessage.success('评论成功')
  } catch (error) {
    console.error('评论失败:', error)
  }
}

function handleReply(comment) {
  replyTo.value = comment
  commentContent.value = `@${comment.user?.nickname || comment.user?.username} `
}

async function loadMore() {
  page.value++
  await postStore.fetchComments(props.postId, {
    skip: (page.value - 1) * 20,
    limit: 20,
  })
}
</script>

<style lang="scss" scoped>
.comment-list {
  .comment-input {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;

    .el-textarea {
      flex: 1;
    }

    .el-button {
      align-self: flex-end;
    }
  }
}

.comments {
  .comment-item {
    display: flex;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }
  }

  .comment-content {
    flex: 1;

    .comment-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;

      .comment-user {
        font-size: 14px;
        font-weight: 500;
        color: #333;
      }

      .comment-time {
        font-size: 12px;
        color: #999;
      }
    }

    .comment-text {
      font-size: 14px;
      line-height: 1.6;
      color: #333;
      margin-bottom: 8px;
    }

    .comment-actions {
      display: flex;
      gap: 16px;

      .action-btn {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #999;
        cursor: pointer;

        &:hover {
          color: #409eff;
        }
      }
    }
  }

  .replies {
    margin-top: 12px;
    padding: 12px;
    background: #f9f9f9;
    border-radius: 4px;

    .reply-item {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;

      &:last-child {
        margin-bottom: 0;
      }

      .reply-content {
        flex: 1;

        .reply-user {
          font-size: 13px;
          font-weight: 500;
          color: #333;
          margin-right: 8px;
        }

        .reply-text {
          font-size: 13px;
          color: #666;
        }
      }
    }
  }

  .load-more {
    text-align: center;
    padding: 16px 0;
  }
}
</style>
