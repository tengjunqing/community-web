<template>
  <div class="profile-view" v-loading="loading">
    <div v-if="user" class="profile-content">
      <!-- 用户信息卡片 -->
      <div class="profile-card">
        <div class="profile-header">
          <el-avatar :size="80" :src="user.avatar">
            {{ user.nickname?.charAt(0) || 'U' }}
          </el-avatar>
          <div class="profile-info">
            <h2 class="profile-name">{{ user.nickname || user.username }}</h2>
            <p class="profile-bio">{{ user.bio || '这个人很懒，什么都没写' }}</p>
          </div>
          <div class="profile-actions">
            <template v-if="isCurrentUser">
              <el-button @click="$router.push('/profile/edit')">编辑资料</el-button>
            </template>
            <template v-else>
              <el-button
                v-if="user.is_following"
                @click="handleUnfollow"
              >
                已关注
              </el-button>
              <el-button
                v-else
                type="primary"
                @click="handleFollow"
              >
                关注
              </el-button>
              <el-button @click="handleSendMessage">发私信</el-button>
            </template>
          </div>
        </div>

        <div class="profile-stats">
          <div class="stat-item">
            <span class="stat-value">{{ user.post_count || 0 }}</span>
            <span class="stat-label">动态</span>
          </div>
          <div class="stat-item" @click="showFollowers = true">
            <span class="stat-value">{{ user.follower_count || 0 }}</span>
            <span class="stat-label">粉丝</span>
          </div>
          <div class="stat-item" @click="showFollowing = true">
            <span class="stat-value">{{ user.following_count || 0 }}</span>
            <span class="stat-label">关注</span>
          </div>
        </div>

        <div v-if="user.interests?.length" class="profile-interests">
          <span
            v-for="interest in user.interests"
            :key="interest.id"
            class="interest-tag"
          >
            {{ interest.name }}
          </span>
        </div>
      </div>

      <!-- 动态列表 -->
      <div class="post-section">
        <h3 class="section-title">动态</h3>
        <PostCard v-for="post in posts" :key="post.id" :post="post" />

        <div v-if="loadingPosts" class="loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <el-empty v-if="!loadingPosts && posts.length === 0" description="暂无动态" />
      </div>
    </div>

    <!-- 粉丝列表弹窗 -->
    <el-dialog v-model="showFollowers" title="粉丝" width="400px">
      <div class="user-list">
        <div v-for="follower in followers" :key="follower.id" class="user-item">
          <UserAvatar :user="follower" :size="40" show-name />
        </div>
        <el-empty v-if="followers.length === 0" description="暂无粉丝" />
      </div>
    </el-dialog>

    <!-- 关注列表弹窗 -->
    <el-dialog v-model="showFollowing" title="关注" width="400px">
      <div class="user-list">
        <div v-for="item in following" :key="item.id" class="user-item">
          <UserAvatar :user="item" :size="40" show-name />
        </div>
        <el-empty v-if="following.length === 0" description="暂无关注" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { usePostStore } from '@/stores/post'
import { userApi } from '@/api'
import UserAvatar from '@/components/common/UserAvatar.vue'
import PostCard from '@/components/common/PostCard.vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const postStore = usePostStore()

const user = ref(null)
const posts = ref([])
const followers = ref([])
const following = ref([])
const loading = ref(false)
const loadingPosts = ref(false)
const showFollowers = ref(false)
const showFollowing = ref(false)

const userId = computed(() => route.params.id)
const isCurrentUser = computed(() => userStore.userId === Number(userId.value))

watch(userId, () => {
  fetchProfile()
  fetchPosts()
})

onMounted(async () => {
  await fetchProfile()
  await fetchPosts()
})

async function fetchProfile() {
  loading.value = true
  try {
    user.value = await userStore.fetchUserProfile(userId.value)
  } catch (error) {
    console.error('获取用户资料失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchPosts() {
  loadingPosts.value = true
  try {
    const result = await postStore.fetchPosts({
      user_id: userId.value,
      skip: 0,
      limit: 20,
    })
    posts.value = result.items
  } catch (error) {
    console.error('获取动态列表失败:', error)
  } finally {
    loadingPosts.value = false
  }
}

async function fetchFollowers() {
  try {
    const result = await userApi.getFollowers(userId.value, { limit: 50 })
    followers.value = result.items
  } catch (error) {
    console.error('获取粉丝列表失败:', error)
  }
}

async function fetchFollowing() {
  try {
    const result = await userApi.getFollowing(userId.value, { limit: 50 })
    following.value = result.items
  } catch (error) {
    console.error('获取关注列表失败:', error)
  }
}

async function handleFollow() {
  try {
    await userStore.followUser(userId.value)
    user.value.is_following = true
    user.value.follower_count++
    ElMessage.success('关注成功')
  } catch (error) {
    console.error('关注失败:', error)
  }
}

async function handleUnfollow() {
  try {
    await userStore.unfollowUser(userId.value)
    user.value.is_following = false
    user.value.follower_count--
    ElMessage.success('取消关注成功')
  } catch (error) {
    console.error('取消关注失败:', error)
  }
}

async function handleSendMessage() {
  try {
    const conversation = await messageApi.createConversation(userId.value)
    router.push('/messages')
  } catch (error) {
    console.error('创建会话失败:', error)
  }
}

watch(showFollowers, (val) => {
  if (val) fetchFollowers()
})

watch(showFollowing, (val) => {
  if (val) fetchFollowing()
})
</script>

<style lang="scss" scoped>
.profile-view {
  max-width: 680px;
  margin: 0 auto;
}

.profile-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;

  .profile-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 20px;

    .profile-info {
      flex: 1;

      .profile-name {
        font-size: 20px;
        font-weight: 600;
        color: #333;
        margin-bottom: 4px;
      }

      .profile-bio {
        font-size: 14px;
        color: #666;
        line-height: 1.5;
      }
    }
  }

  .profile-stats {
    display: flex;
    gap: 40px;
    padding: 16px 0;
    border-top: 1px solid #f0f0f0;
    border-bottom: 1px solid #f0f0f0;

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;

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

      &:hover .stat-label {
        color: #409eff;
      }
    }
  }

  .profile-interests {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 16px;

    .interest-tag {
      padding: 4px 12px;
      background: #f0f9ff;
      color: #409eff;
      border-radius: 16px;
      font-size: 12px;
    }
  }
}

.post-section {
  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin-bottom: 16px;
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 20px;
    color: #999;
  }
}

.user-list {
  .user-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }
  }
}
</style>
