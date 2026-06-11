<template>
  <div class="image-upload">
    <el-upload
      :action="uploadUrl"
      :headers="headers"
      :file-list="fileList"
      :limit="limit"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-remove="handleRemove"
      :on-exceed="handleExceed"
      list-type="picture-card"
      accept="image/*"
    >
      <el-icon><Plus /></el-icon>
    </el-upload>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  limit: {
    type: Number,
    default: 9,
  },
  maxSize: {
    type: Number,
    default: 10, // MB
  },
})

const emit = defineEmits(['update:modelValue'])

const userStore = useUserStore()

const uploadUrl = '/api/v1/upload/image'

const headers = computed(() => ({
  Authorization: `Bearer ${userStore.token}`,
}))

const fileList = computed(() =>
  props.modelValue.map((url, index) => ({
    name: `image-${index}`,
    url,
  }))
)

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }

  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize
  if (!isLtMaxSize) {
    ElMessage.error(`图片大小不能超过 ${props.maxSize}MB`)
    return false
  }

  return true
}

function handleSuccess(response, file) {
  const newUrls = [...props.modelValue, response.url]
  emit('update:modelValue', newUrls)
}

function handleRemove(file) {
  const newUrls = props.modelValue.filter((url) => url !== file.url)
  emit('update:modelValue', newUrls)
}

function handleExceed() {
  ElMessage.warning(`最多只能上传 ${props.limit} 张图片`)
}
</script>

<style lang="scss" scoped>
.image-upload {
  :deep(.el-upload--picture-card) {
    width: 100px;
    height: 100px;
  }

  :deep(.el-upload-list--picture-card .el-upload-list__item) {
    width: 100px;
    height: 100px;
  }
}
</style>
