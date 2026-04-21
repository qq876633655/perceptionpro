<template>
  <div class="file-uploader">
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :limit="1"
      :accept="accept"
      :on-change="handleChange"
      :on-exceed="handleExceed"
      :on-remove="handleRemove"
      :file-list="fileList"
      drag
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          {{ tip }}
        </div>
      </template>
    </el-upload>

    <!-- 上传进度 -->
    <el-progress
      v-if="progress > 0 && progress < 100"
      :percentage="progress"
      style="margin-top: 8px"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  /** 允许上传的文件类型，如 ".zip,.tar.gz" */
  accept: {
    type: String,
    default: '',
  },
  /** 提示文字 */
  tip: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['change'])

const uploadRef = ref(null)
const fileList = ref([])
const progress = ref(0)

function handleChange(file) {
  fileList.value = [file]
  emit('change', file.raw)
}

function handleExceed(files) {
  // 超出限制时自动替换
  uploadRef.value?.clearFiles()
  const file = files[0]
  uploadRef.value?.handleStart(file)
  emit('change', file)
}

function handleRemove() {
  fileList.value = []
  emit('change', null)
}

/** 供父组件重置 */
function reset() {
  uploadRef.value?.clearFiles()
  fileList.value = []
  progress.value = 0
}

/** 供父组件设置进度 */
function setProgress(val) {
  progress.value = val
}

defineExpose({ reset, setProgress })
</script>

<style scoped>
.file-uploader :deep(.el-upload-dragger) {
  width: 100%;
}
</style>
