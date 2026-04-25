<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑版本' : '新建版本'" width="540px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="版本号" prop="versions" :error="serverErrors.versions">
        <el-input v-model="form.versions" :disabled="isEdit"
          :placeholder="isEdit ? '版本号创建后不可修改' : '请输入版本号'" clearable />
      </el-form-item>
      <el-form-item label="发布说明" prop="release_note" :error="serverErrors.release_note">
        <el-input v-model="form.release_note" type="textarea" :rows="4" placeholder="可选" />
      </el-form-item>
      <el-form-item v-if="isEdit" label="版本文件">
        <span class="file-hint">{{ props.editData?.versions_file ? '已上传（创建后不可修改）' : '未上传' }}</span>
      </el-form-item>
      <el-form-item v-else label="版本文件" prop="versions_file_guard" :error="serverErrors.versions_file">
        <FileUploader ref="fileRef" tip="请上传版本文件" @change="handleFileChange" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createAtVersions, updateAtVersions } from '@/api/sim_test_agv'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const fileRef = ref(null)
const submitting = ref(false)
const selectedFile = ref(null)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({ versions: '', release_note: '', versions_file_guard: null })

const rules = {
  versions: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  versions_file_guard: [{
    required: true,
    validator: (rule, value, cb) => {
      if (!isEdit.value && !selectedFile.value) cb(new Error('请上传版本文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

function handleFileChange(file) {
  selectedFile.value = file
  form.versions_file_guard = file ? file.name : null
  formRef.value?.validateField('versions_file_guard')
}

watch(() => props.visible, val => {
  if (val) {
    clearServerErrors()
    selectedFile.value = null
    fileRef.value?.reset?.()
    if (props.editData) {
      form.versions = props.editData.versions
      form.release_note = props.editData.release_note || ''
    } else {
      form.versions = ''
      form.release_note = ''
    }
    form.versions_file_guard = null
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const fd = new FormData()
    if (!isEdit.value) {
      fd.append('versions', form.versions)
      if (selectedFile.value) fd.append('versions_file', selectedFile.value)
    }
    fd.append('release_note', form.release_note || '')

    if (isEdit.value) {
      await updateAtVersions(props.editData.id, fd)
      ElMessage.success('修改成功')
    } else {
      await createAtVersions(fd)
      ElMessage.success('创建成功')
    }
    visible.value = false
    emit('success')
  } catch (err) {
    applyServerErrors(err)
  } finally {
    submitting.value = false
  }
}

function handleClosed() { clearServerErrors() }
</script>

<style scoped>
.file-hint { color: #909399; font-size: 13px; }
</style>
