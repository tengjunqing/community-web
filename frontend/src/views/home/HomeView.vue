<template>
  <div class="home-view">
    <div class="home-content">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <UserAvatar :user="userStore.userInfo" :size="60" show-name />
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-value">{{ userProfile?.post_count || 0 }}</span>
              <span class="stat-label">动态</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userProfile?.follower_count || 0 }}</span>
              <span class="stat-label">粉丝</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userProfile?.following_count || 0 }}</span>
              <span class="stat-label">关注</span>
            </div>
          </div>
        </div>

        <!-- 话题推荐 -->
        <div class="topics-card">
          <h3 class="card-title">热门话题</h3>
          <div class="topic-list">
            <div
              v-for="topic in topics"
              :key="topic.id"
              class="topic-item"
              @click="filterByTopic(topic)"
            >
              <span class="topic-name">#{{ topic.name }}</span>
              <span class="topic-count">{{ topic.post_count }}条动态</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <!-- 发布动态入口 -->
        <div class="create-post" @click="$router.push('/post/create')">
          <el-avatar :size="40" :src="userStore.userInfo?.avatar">
            {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
          </el-avatar>
          <div class="create-input">分享你的兴趣...</div>
        </div>

        <!-- 动态列表 -->
        <div class="post-list">
          <PostCard v-for="post in posts" :key="post.id" :post="post" />

          <!-- 加载更多 -->
          <div v-if="loading" class="loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>

          <div v-if="!loading && posts.length === 0" class="empty">
            <el-empty description="暂无动态" />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePostStore } from '@/stores/post'
import UserAvatar from '@/components/common/UserAvatar.vue'
import PostCard from '@/components/common/PostCard.vue'
import { Loading } from '@element-plus/icons-vue'

const userStore = useUserStore()
const postStore = usePostStore()

const userProfile = ref(null)
const topics = ref([])
const currentTopic = ref(null)
const page = ref(1)

const posts = computed(() => postStore.posts)
const loading = computed(() => postStore.loading)

onMounted(async () => {
  await Promise.all([
    fetchUserProfile(),
    fetchPosts(),
    fetchTopics(),
  ])
})

async function fetchUserProfile() {
  try {
    userProfile.value = await userStore.fetchUserProfile()
  } catch (error) {
    console.error('获取用户资料失败:', error)
  }
}

async function fetchPosts() {
  const params = {
    skip: 0,
    limit: 20,
  }

  if (currentTopic.value) {
    params.topic_id = currentTopic.value.id
  }

  await postStore.fetchPosts(params)
}

async function fetchTopics() {
  try {
    const result = await postStore.fetchTopics({ limit: 10 })
    topics.value = result
  } catch (error) {
    console.error('获取话题列表失败:', error)
  }
}

function filterByTopic(topic) {
  if (currentTopic.value?.id === topic.id) {
    currentTopic.value = null
  } else {
    currentTopic.value = topic
  }
  page.value = 1
  fetchPosts()
}
</script>

<style lang="scss" scoped>
.home-view {
  .home-content {
    display: flex;
    gap: 20px;
  }
}

.sidebar {
  width: 280px;
  flex-shrink: 0;

  .user-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    text-align: center;

    .user-stats {
      display: flex;
      justify-content: space-around;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;

      .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;

        .stat-value {
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }

        .stat-label {
          font-size: 12px;
          color: #999;
          margin-top: 4px;
        }
      }
    }
  }

  .topics-card {
    background: #fff;
    border-radius: 8px;
    padding: 16px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 12px;
    }

    .topic-list {
      .topic-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        cursor: pointer;
        transition: background 0.2s;

        &:hover {
          background: #f9f9f9;
        }

        .topic-name {
          font-size: 14px;
          color: #409eff;
        }

        .topic-count {
          font-size: 12px;
          color: #999;
        }
      }
    }
  }
}

.main-content {
  flex: 1;
  min-width: 0;

  .create-post {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }

    .create-input {
      flex: 1;
      height: 40px;
      line-height: 40px;
      padding: 0 16px;
      background: #f5f5f5;
      border-radius: 20px;
      color: #999;
      font-size: 14px;
    }
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 20px;
    color: #999;

    .el-icon {
      font-size: 20px;
    }
  }

  .empty {
    padding: 40px 0;
  }
}
</style>
