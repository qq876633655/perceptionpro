<template>
  <el-dialog
    v-model="visible"
    :title="`上传版本文件 - ${row?.version_num ?? ''}`"
    width="500px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-alert
      type="info"
      :closable="false"
      style="margin-bottom: 16px"
    >
      <template #default>
        支持上传版本文件（如 .zip / .tar.gz）。上传后将覆盖原有文件。
      </template>
    </el-alert>

    <FileUploader
      ref="uploaderRef"
      accept=".zip,.tar.gz,.gz"
      tip="支持 .zip / .tar.gz 格式，大小不超过 500MB"
      @change="selectedFile = $event"
    />

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        :loading="uploading"
        :disabled="!selectedFile"
        @click="handleUpload"
      >
        {{ uploading ? `上传中 ${progress}%` : '开始上传' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadVersionFile } from '@/api/version'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({
  visible: Boolean,
  row: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v),
})

const uploaderRef = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const progress = ref(0)

async function handleUpload() {
  if (!selectedFile.value || !props.row?.id) return

  const formData = new FormData()
  formData.append('version_file', selectedFile.value)

  uploading.value = true
  progress.value = 0

  try {
    await uploadVersionFile(props.row.id, formData, (p) => {
      progress.value = p
      uploaderRef.value?.setProgress(p)
    })
    ElMessage.success('文件上传成功')
    emit('success')
    visible.value = false
  } catch {
    // 错误已在拦截器处理
  } finally {
    uploading.value = false
  }
}

function handleClosed() {
  uploaderRef.value?.reset()
  selectedFile.value = null
  progress.value = 0
}
</script>
