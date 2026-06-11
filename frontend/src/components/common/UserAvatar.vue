<template>
  <div class="user-avatar" @click="goToProfile">
    <el-avatar :size="size" :src="user?.avatar">
      {{ user?.nickname?.charAt(0) || 'U' }}
    </el-avatar>
    <div v-if="showName" class="user-name">
      {{ user?.nickname || user?.username }}
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
  size: {
    type: [Number, String],
    default: 40,
  },
  showName: {
    type: Boolean,
    default: false,
  },
})

const router = useRouter()

function goToProfile() {
  if (props.user?.id) {
    router.push(`/profile/${props.user.id}`)
  }
}
</script>

<style lang="scss" scoped>
.user-avatar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;

  .user-name {
    font-size: 14px;
    color: #333;
    font-weight: 500;

    &:hover {
      color: #409eff;
    }
  }
}
</style>
