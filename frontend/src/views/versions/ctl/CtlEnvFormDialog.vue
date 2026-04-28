<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑环境' : '新建环境'" width="560px" :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="环境名称" prop="env_name" :error="serverErrors.env_name">
        <el-input v-model="form.env_name" :disabled="isEdit" :placeholder="isEdit ? '环境名称创建后不可修改' : '请输入环境名称'" clearable />
      </el-form-item>
      <el-form-item label="适用专项" prop="apply_project" :error="serverErrors.apply_project">
        <el-input v-model="form.apply_project" placeholder="如：主线版本" clearable />
      </el-form-item>
      <el-form-item label="环境描述" prop="env_note" :error="serverErrors.env_note">
        <el-input v-model="form.env_note" type="textarea" :rows="3" placeholder="请输入环境描述（可选）" />
      </el-form-item>
      <el-form-item v-if="!isEdit" label="环境文件" prop="env_file" :error="serverErrors.env_file">
        <FileUploader ref="uploaderRef" tip="请上传环境文件" @change="handleFileChange" />
      </el-form-item>
      <template v-if="isEdit">
        <el-form-item label="当前文件">
          <a v-if="props.editData?.env_file" :href="props.editData.env_file" target="_blank" class="download-link">{{ extractFilename(props.editData.env_file) }}</a>
          <span v-else class="no-file">暂无文件</span>
        </el-form-item>
        <el-form-item label="替换文件" :error="serverErrors.env_file">
          <FileUploader ref="uploaderRef" tip="上传后将覆盖原文件（可不替换）" @change="handleFileChange" />
        </el-form-item>
      </template>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ isEdit ? '保存修改' : '创建环境' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ctlApi } from '@/api/version'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: (v) => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const uploaderRef = ref(null)
const submitting = ref(false)
const selectedFile = ref(null)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({ env_name: '', apply_project: '主线版本', env_note: '', env_file: null })
const rules = {
  env_name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
  apply_project: [{ required: true, message: '请输入适用专项', trigger: 'blur' }],
  env_file: [{
    required: true,
    validator: (rule, value, callback) => {
      if (!isEdit.value && !selectedFile.value) callback(new Error('请上传环境文件'))
      else callback()
    },
    trigger: 'change',
  }],
}

function handleFileChange(file) {
  selectedFile.value = file
  form.env_file = file ? file.name : null
  formRef.value?.validateField('env_file')
}

watch(() => props.visible, (val) => {
  if (val) {
    clearServerErrors()
    selectedFile.value = null
    if (props.editData) {
      Object.assign(form, { env_name: props.editData.env_name ?? '', apply_project: props.editData.apply_project ?? '主线版本', env_note: props.editData.env_note ?? '', env_file: null })
    } else {
      Object.assign(form, { env_name: '', apply_project: '主线版本', env_note: '', env_file: null })
    }
  }
})

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  clearServerErrors()
  try {
    if (isEdit.value) {
      let payload
      if (selectedFile.value) {
        payload = new FormData()
        payload.append('apply_project', form.apply_project)
        payload.append('env_note', form.env_note ?? '')
        payload.append('env_file', selectedFile.value)
      } else {
        payload = { apply_project: form.apply_project, env_note: form.env_note }
      }
      await ctlApi.updateEnv(props.editData.id, payload)
      ElMessage.success('更新成功')
    } else {
      const fd = new FormData()
      fd.append('env_name', form.env_name)
      fd.append('apply_project', form.apply_project)
      if (form.env_note) fd.append('env_note', form.env_note)
      fd.append('env_file', selectedFile.value)
      await ctlApi.createEnv(fd)
      ElMessage.success('创建成功')
    }
    emit('success')
    visible.value = false
  } catch (err) {
    if (err?.data && typeof err.data === 'object') {
      applyServerErrors(Object.entries(err.data).map(([field, msgs]) => ({ field, message: Array.isArray(msgs) ? msgs[0] : msgs })))
    }
  } finally { submitting.value = false }
}

function handleClosed() {
  formRef.value?.resetFields()
  uploaderRef.value?.reset()
  selectedFile.value = null
  clearServerErrors()
}
function extractFilename(url) { if (!url) return ''; return decodeURIComponent(url.split('/').pop()) }
</script>

<style scoped>
.download-link { color: #409eff; text-decoration: none; word-break: break-all; }
.download-link:hover { text-decoration: underline; }
.no-file { color: #909399; font-size: 13px; }
</style>
