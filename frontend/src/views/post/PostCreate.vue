<template>
  <div class="post-create">
    <div class="create-card">
      <h2 class="card-title">发布动态</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="分享你的兴趣和想法..."
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="图片">
          <ImageUpload v-model="form.images" :limit="9" />
        </el-form-item>

        <el-form-item label="话题">
          <el-select
            v-model="form.topic_id"
            placeholder="选择话题（可选）"
            clearable
            filterable
          >
            <el-option
              v-for="topic in topics"
              :key="topic.id"
              :label="topic.name"
              :value="topic.id"
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
            发布
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePostStore } from '@/stores/post'
import ImageUpload from '@/components/common/ImageUpload.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const postStore = usePostStore()

const formRef = ref(null)
const loading = ref(false)
const topics = ref([])

const form = reactive({
  content: '',
  images: [],
  topic_id: null,
})

const rules = {
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    { min: 1, max: 5000, message: '内容长度为1-5000个字符', trigger: 'blur' },
  ],
}

onMounted(async () => {
  await fetchTopics()
})

async function fetchTopics() {
  try {
    topics.value = await postStore.fetchTopics({ limit: 50 })
  } catch (error) {
    console.error('获取话题列表失败:', error)
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await postStore.createPost({
      content: form.content,
      images: form.images.length > 0 ? form.images : null,
      topic_id: form.topic_id,
    })
    ElMessage.success('发布成功')
    router.push('/')
  } catch (error) {
    console.error('发布失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.post-create {
  max-width: 680px;
  margin: 0 auto;
}

.create-card {
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
</style>
