<template>
  <div class="group-list">
    <div class="list-header">
      <h2>群组</h2>
      <el-button type="primary" @click="$router.push('/group/create')">
        <el-icon><Plus /></el-icon>
        创建群组
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索群组..."
        prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
      <el-select v-model="category" placeholder="分类" clearable @change="fetchGroups">
        <el-option label="兴趣" value="兴趣" />
        <el-option label="学习" value="学习" />
        <el-option label="生活" value="生活" />
        <el-option label="其他" value="其他" />
      </el-select>
    </div>

    <!-- 群组列表 -->
    <div class="group-grid">
      <div
        v-for="group in groups"
        :key="group.id"
        class="group-card"
        @click="$router.push(`/group/${group.id}`)"
      >
        <div class="group-cover">
          <el-image :src="group.cover" fit="cover">
            <template #error>
              <div class="cover-placeholder">
                <el-icon :size="40"><UserFilled /></el-icon>
              </div>
            </template>
          </el-image>
        </div>
        <div class="group-info">
          <h3 class="group-name">{{ group.name }}</h3>
          <p class="group-desc text-ellipsis-2">{{ group.description || '暂无简介' }}</p>
          <div class="group-meta">
            <span class="member-count">
              <el-icon><User /></el-icon>
              {{ group.member_count }}人
            </span>
            <el-tag v-if="group.is_member" type="success" size="small">已加入</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <el-empty v-if="!loading && groups.length === 0" description="暂无群组" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGroupStore } from '@/stores/group'
import { Plus, UserFilled, User, Loading } from '@element-plus/icons-vue'
import { debounce } from '@/utils/helpers'

const groupStore = useGroupStore()

const keyword = ref('')
const category = ref('')
const page = ref(1)

const groups = computed(() => groupStore.groups)
const loading = computed(() => groupStore.loading)

const handleSearch = debounce(() => {
  page.value = 1
  fetchGroups()
}, 300)

onMounted(async () => {
  await fetchGroups()
})

async function fetchGroups() {
  const params = {
    skip: 0,
    limit: 20,
  }

  if (keyword.value) {
    params.keyword = keyword.value
  }

  if (category.value) {
    params.category = category.value
  }

  await groupStore.fetchGroups(params)
}
</script>

<style lang="scss" scoped>
.group-list {
  .list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;

    h2 {
      font-size: 24px;
      font-weight: 600;
      color: #333;
    }
  }

  .search-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;

    .el-input {
      flex: 1;
    }

    .el-select {
      width: 120px;
    }
  }

  .group-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }

  .group-card {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    }

    .group-cover {
      height: 150px;
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
      padding: 16px;

      .group-name {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
      }

      .group-desc {
        font-size: 13px;
        color: #666;
        line-height: 1.5;
        margin-bottom: 12px;
        height: 40px;
      }

      .group-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;

        .member-count {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
          color: #999;
        }
      }
    }
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
</style>
