<template>
  <div class="profile-edit">
    <div class="edit-card">
      <h2 class="card-title">编辑资料</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :headers="headers"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
          >
            <el-avatar :size="80" :src="form.avatar">
              {{ form.nickname?.charAt(0) || 'U' }}
            </el-avatar>
            <div class="upload-tip">点击更换头像</div>
          </el-upload>
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input
            v-model="form.nickname"
            placeholder="请输入昵称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="个人简介" prop="bio">
          <el-input
            v-model="form.bio"
            type="textarea"
            :rows="4"
            placeholder="介绍一下自己..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="兴趣标签">
          <el-select
            v-model="form.interest_ids"
            multiple
            filterable
            placeholder="选择你感兴趣的话题"
          >
            <el-option
              v-for="tag in interestTags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleSubmit"
          >
            保存修改
          </el-button>
          <el-button size="large" @click="$router.back()">
            取消
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const interestTags = ref([])

const form = reactive({
  avatar: '',
  nickname: '',
  bio: '',
  interest_ids: [],
})

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { max: 50, message: '昵称长度不能超过50个字符', trigger: 'blur' },
  ],
  bio: [
    { max: 500, message: '个人简介长度不能超过500个字符', trigger: 'blur' },
  ],
}

const uploadUrl = '/api/v1/upload/image'
const headers = computed(() => ({
  Authorization: `Bearer ${userStore.token}`,
}))

onMounted(async () => {
  await fetchProfile()
  await fetchInterestTags()
})

async function fetchProfile() {
  try {
    const profile = await userStore.fetchUserProfile()
    form.avatar = profile.avatar || ''
    form.nickname = profile.nickname || ''
    form.bio = profile.bio || ''
    form.interest_ids = profile.interests?.map(i => i.id) || []
  } catch (error) {
    console.error('获取用户资料失败:', error)
  }
}

async function fetchInterestTags() {
  try {
    // 这里需要一个获取兴趣标签的接口
    // interestTags.value = await api.getInterestTags()
    interestTags.value = []
  } catch (error) {
    console.error('获取兴趣标签失败:', error)
  }
}

function handleAvatarSuccess(response) {
  form.avatar = response.url
  ElMessage.success('头像上传成功')
}

function beforeAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }

  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB')
    return false
  }

  return true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.updateProfile({
      nickname: form.nickname,
      bio: form.bio,
      avatar: form.avatar,
      interest_ids: form.interest_ids,
    })
    ElMessage.success('保存成功')
    router.push(`/profile/${userStore.userId}`)
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.profile-edit {
  max-width: 600px;
  margin: 0 auto;
}

.edit-card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;

  .card-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin-bottom: 24px;
  }
}

.avatar-uploader {
  text-align: center;

  .el-avatar {
    cursor: pointer;
    transition: opacity 0.2s;

    &:hover {
      opacity: 0.8;
    }
  }

  .upload-tip {
    margin-top: 8px;
    font-size: 12px;
    color: #999;
  }
}
</style>
