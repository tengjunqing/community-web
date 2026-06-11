<template>
  <div class="group-create">
    <div class="create-card">
      <h2 class="card-title">创建群组</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="群组名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入群组名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="群组简介" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="介绍一下你的群组..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="选择分类">
            <el-option label="兴趣" value="兴趣" />
            <el-option label="学习" value="学习" />
            <el-option label="生活" value="生活" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>

        <el-form-item label="群组类型">
          <el-radio-group v-model="form.is_public">
            <el-radio :label="1">公开</el-radio>
            <el-radio :label="0">私密</el-radio>
          </el-radio-group>
          <div class="form-tip">
            {{ form.is_public ? '任何人可以搜索并加入' : '需要邀请或审核才能加入' }}
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleSubmit"
          >
            创建群组
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupStore } from '@/stores/group'
import { ElMessage } from 'element-plus'

const router = useRouter()
const groupStore = useGroupStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  name: '',
  description: '',
  category: '',
  is_public: 1,
})

const rules = {
  name: [
    { required: true, message: '请输入群组名称', trigger: 'blur' },
    { max: 100, message: '名称长度不能超过100个字符', trigger: 'blur' },
  ],
  description: [
    { max: 1000, message: '简介长度不能超过1000个字符', trigger: 'blur' },
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const group = await groupStore.createGroup({
      name: form.name,
      description: form.description,
      category: form.category,
      is_public: form.is_public,
    })
    ElMessage.success('创建成功')
    router.push(`/group/${group.id}`)
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.group-create {
  max-width: 600px;
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

  .form-tip {
    font-size: 12px;
    color: #999;
    margin-top: 4px;
  }
}
</style>
