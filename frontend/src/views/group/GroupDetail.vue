<template>
  <div class="group-detail" v-loading="loading">
    <div v-if="group" class="detail-content">
      <!-- 群组信息卡片 -->
      <div class="group-card">
        <div class="group-cover">
          <el-image :src="group.cover" fit="cover">
            <template #error>
              <div class="cover-placeholder">
                <el-icon :size="60"><UserFilled /></el-icon>
              </div>
            </template>
          </el-image>
        </div>

        <div class="group-info">
          <div class="info-header">
            <h1 class="group-name">{{ group.name }}</h1>
            <div class="group-actions">
              <template v-if="group.is_member">
                <el-button @click="handleLeave">退出群组</el-button>
                <el-button type="primary" @click="showPostDialog = true">发动态</el-button>
              </template>
              <template v-else>
                <el-button type="primary" @click="handleJoin">加入群组</el-button>
              </template>
            </div>
          </div>

          <p class="group-desc">{{ group.description || '暂无简介' }}</p>

          <div class="group-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ group.member_count }}人
            </span>
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              创建于 {{ formatDateTime(group.created_at) }}
            </span>
            <el-tag v-if="group.is_public" type="success" size="small">公开</el-tag>
            <el-tag v-else type="info" size="small">私密</el-tag>
          </div>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="group-content">
        <el-tabs v-model="activeTab">
          <!-- 动态 -->
          <el-tab-pane label="动态" name="posts">
            <div class="post-list">
              <PostCard v-for="item in groupPosts" :key="item.id" :post="item.post" />
              <el-empty v-if="groupPosts.length === 0" description="暂无动态" />
            </div>
          </el-tab-pane>

          <!-- 成员 -->
          <el-tab-pane label="成员" name="members">
            <div class="member-list">
              <div v-for="member in members" :key="member.id" class="member-item">
                <UserAvatar :user="member.user" :size="48" show-name />
                <div class="member-info">
                  <span class="member-role">
                    {{ member.role === 3 ? '群主' : member.role === 2 ? '管理员' : '成员' }}
                  </span>
                  <span class="join-time">加入于 {{ formatDateTime(member.joined_at) }}</span>
                </div>
              </div>
              <el-empty v-if="members.length === 0" description="暂无成员" />
            </div>
          </el-tab-pane>

          <!-- 公告 -->
          <el-tab-pane label="公告" name="announcements">
            <div class="announcement-list">
              <div v-for="announcement in announcements" :key="announcement.id" class="announcement-item">
                <h3 class="announcement-title">{{ announcement.title }}</h3>
                <p class="announcement-content">{{ announcement.content }}</p>
                <div class="announcement-meta">
                  <UserAvatar :user="announcement.creator" :size="24" />
                  <span class="meta-text">{{ announcement.creator?.nickname }}</span>
                  <span class="meta-text">{{ formatDateTime(announcement.created_at) }}</span>
                </div>
              </div>
              <el-empty v-if="announcements.length === 0" description="暂无公告" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 发布动态弹窗 -->
    <el-dialog v-model="showPostDialog" title="发布群组动态" width="500px">
      <el-form>
        <el-form-item>
          <el-input
            v-model="postContent"
            type="textarea"
            :rows="4"
            placeholder="分享你的想法..."
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPostDialog = false">取消</el-button>
        <el-button type="primary" :loading="posting" @click="handlePost">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useGroupStore } from '@/stores/group'
import { formatDateTime } from '@/utils/helpers'
import UserAvatar from '@/components/common/UserAvatar.vue'
import PostCard from '@/components/common/PostCard.vue'
import { UserFilled, User, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const groupStore = useGroupStore()

const activeTab = ref('posts')
const showPostDialog = ref(false)
const postContent = ref('')
const posting = ref(false)

const groupId = computed(() => route.params.id)
const group = computed(() => groupStore.currentGroup)
const members = computed(() => groupStore.members)
const groupPosts = computed(() => groupStore.groupPosts)
const announcements = computed(() => groupStore.announcements)
const loading = computed(() => groupStore.loading)

watch(activeTab, (tab) => {
  switch (tab) {
    case 'members':
      fetchMembers()
      break
    case 'announcements':
      fetchAnnouncements()
      break
  }
})

onMounted(async () => {
  await fetchGroup()
  await fetchGroupPosts()
})

async function fetchGroup() {
  try {
    await groupStore.fetchGroup(groupId.value)
  } catch (error) {
    console.error('获取群组详情失败:', error)
  }
}

async function fetchGroupPosts() {
  try {
    await groupStore.fetchGroupPosts(groupId.value, { skip: 0, limit: 20 })
  } catch (error) {
    console.error('获取群组动态失败:', error)
  }
}

async function fetchMembers() {
  try {
    await groupStore.fetchMembers(groupId.value, { limit: 50 })
  } catch (error) {
    console.error('获取成员列表失败:', error)
  }
}

async function fetchAnnouncements() {
  try {
    await groupStore.fetchAnnouncements(groupId.value, { limit: 20 })
  } catch (error) {
    console.error('获取公告列表失败:', error)
  }
}

async function handleJoin() {
  try {
    await groupStore.joinGroup(groupId.value)
    ElMessage.success('加入成功')
  } catch (error) {
    console.error('加入失败:', error)
  }
}

async function handleLeave() {
  try {
    await groupStore.leaveGroup(groupId.value)
    ElMessage.success('已退出群组')
  } catch (error) {
    console.error('退出失败:', error)
  }
}

async function handlePost() {
  if (!postContent.value.trim()) return

  posting.value = true
  try {
    await groupStore.createGroupPost(groupId.value, {
      content: postContent.value,
    })
    showPostDialog.value = false
    postContent.value = ''
    ElMessage.success('发布成功')
  } catch (error) {
    console.error('发布失败:', error)
  } finally {
    posting.value = false
  }
}
</script>

<style lang="scss" scoped>
.group-detail {
  max-width: 800px;
  margin: 0 auto;
}

.group-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;

  .group-cover {
    height: 200px;
    overflow: hidden;

    .el-image {
      width: 100%;
      height: 100%;
    }

    .cover-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
    }
  }

  .group-info {
    padding: 20px;

    .info-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;

      .group-name {
        font-size: 24px;
        font-weight: 600;
        color: #333;
      }
    }

    .group-desc {
      font-size: 14px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 16px;
    }

    .group-meta {
      display: flex;
      align-items: center;
      gap: 16px;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        color: #999;
      }
    }
  }
}

.group-content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.member-list {
  .member-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .member-info {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .member-role {
        font-size: 12px;
        color: #409eff;
        background: #e8f4ff;
        padding: 2px 8px;
        border-radius: 4px;
      }

      .join-time {
        font-size: 12px;
        color: #999;
      }
    }
  }
}

.announcement-list {
  .announcement-item {
    padding: 16px 0;
    border-bottom: 1px solid #f0f0f0;

    &:last-child {
      border-bottom: none;
    }

    .announcement-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin-bottom: 8px;
    }

    .announcement-content {
      font-size: 14px;
      color: #666;
      line-height: 1.6;
      margin-bottom: 12px;
    }

    .announcement-meta {
      display: flex;
      align-items: center;
      gap: 8px;

      .meta-text {
        font-size: 12px;
        color: #999;
      }
    }
  }
}
</style>
