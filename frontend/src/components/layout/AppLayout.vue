<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <el-icon :size="24"><Promotion /></el-icon>
          <span class="logo-text">兴趣圈</span>
        </router-link>

        <!-- 导航菜单 -->
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/groups" class="nav-item" :class="{ active: $route.path.startsWith('/group') }">
            <el-icon><UserFilled /></el-icon>
            <span>群组</span>
          </router-link>
          <router-link to="/messages" class="nav-item" :class="{ active: $route.path === '/messages' }">
            <el-badge :value="messageStore.unreadCount" :hidden="messageStore.unreadCount === 0">
              <el-icon><ChatDotRound /></el-icon>
            </el-badge>
            <span>私信</span>
          </router-link>
        </nav>

        <!-- 用户操作区 -->
        <div class="user-actions">
          <!-- 发布按钮 -->
          <el-button type="primary" @click="$router.push('/post/create')">
            <el-icon><EditPen /></el-icon>
            <span>发动态</span>
          </el-button>

          <!-- 用户头像下拉菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-avatar">
              <el-avatar :size="36" :src="userStore.userInfo?.avatar">
                {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人主页
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useMessageStore } from '@/stores/message'
import {
  Promotion,
  HomeFilled,
  UserFilled,
  ChatDotRound,
  EditPen,
  User,
  Setting,
  SwitchButton,
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const messageStore = useMessageStore()

onMounted(async () => {
  // 获取用户信息
  if (userStore.isAuthenticated && !userStore.userInfo) {
    await userStore.fetchUserInfo()
  }

  // 获取会话列表（用于未读消息数）
  if (userStore.isAuthenticated) {
    await messageStore.fetchConversations()
  }
})

function handleCommand(command) {
  switch (command) {
    case 'profile':
      router.push(`/profile/${userStore.userId}`)
      break
    case 'settings':
      router.push('/profile/edit')
      break
    case 'logout':
      userStore.logout()
      router.push('/login')
      break
  }
}
</script>

<style lang="scss" scoped>
.app-layout {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 100;

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: #409eff;
    font-size: 20px;
    font-weight: 600;

    .logo-text {
      background: linear-gradient(135deg, #409eff, #67c23a);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }

  .nav-menu {
    display: flex;
    align-items: center;
    gap: 40px;

    .nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      text-decoration: none;
      color: #666;
      font-size: 12px;
      transition: color 0.2s;

      .el-icon {
        font-size: 20px;
      }

      &:hover,
      &.active {
        color: #409eff;
      }
    }
  }

  .user-actions {
    display: flex;
    align-items: center;
    gap: 16px;

    .user-avatar {
      cursor: pointer;
      display: flex;
      align-items: center;
    }
  }
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 20px;
}
</style>
