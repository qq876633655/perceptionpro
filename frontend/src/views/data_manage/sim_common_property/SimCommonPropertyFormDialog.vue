<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑仿真通用数据' : '新建仿真通用数据'"
    width="560px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="版本号" prop="versions" :error="serverErrors.versions">
        <el-input v-model="form.versions" placeholder="请输入版本号" clearable />
      </el-form-item>

      <el-form-item label="标签" prop="property_tag" :error="serverErrors.property_tag">
        <el-input v-model="form.property_tag" placeholder="请输入标签（可选）" clearable />
      </el-form-item>

      <el-form-item label="资产说明" prop="property_desc" :error="serverErrors.property_desc">
        <el-input v-model="form.property_desc" type="textarea" :rows="3" placeholder="请输入资产说明（可选）" />
      </el-form-item>

      <!-- 新建：文件必选 -->
      <el-form-item v-if="!isEdit" label="通用资产" prop="common_property" :error="serverErrors.common_property">
        <FileUploader ref="uploaderRef" tip="请上传通用资产文件" @change="handleFileChange" />
      </el-form-item>

      <!-- 编辑：显示当前文件 + 可选替换 -->
      <template v-if="isEdit">
        <el-form-item label="当前文件">
          <a
            v-if="props.editData?.common_property"
            :href="props.editData.common_property"
            target="_blank"
            class="download-link"
          >
            {{ extractFilename(props.editData.common_property) }}
          </a>
          <span v-else class="no-file">暂无文件</span>
        </el-form-item>
        <el-form-item label="替换文件" :error="serverErrors.common_property">
          <FileUploader ref="uploaderRef" tip="上传后将覆盖原文件（可不替换）" @change="handleFileChange" />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '创建数据' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createSimCommonProperty, updateSimCommonProperty } from '@/api/data_manage'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({
  visible: Boolean,
  editData: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v),
})

const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const uploaderRef = ref(null)
const submitting = ref(false)
const selectedFile = ref(null)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({
  versions: '',
  property_tag: '',
  property_desc: '',
  common_property: null,
})

const rules = {
  versions: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  common_property: [
    {
      required: true,
      validator: (rule, value, callback) => {
        if (!isEdit.value && !selectedFile.value) {
          callback(new Error('请上传通用资产文件'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

function handleFileChange(file) {
  selectedFile.value = file
  form.common_property = file ? file.name : null
  formRef.value?.validateField('common_property')
}

function extractFilename(url) {
  if (!url) return ''
  return decodeURIComponent(url.split('/').pop())
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      clearServerErrors()
      selectedFile.value = null
      if (props.editData) {
        Object.assign(form, {
          versions: props.editData.versions ?? '',
          property_tag: props.editData.property_tag ?? '',
          property_desc: props.editData.property_desc ?? '',
          common_property: null,
        })
      } else {
        Object.assign(form, { versions: '', property_tag: '', property_desc: '', common_property: null })
      }
    }
  },
)

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
        payload.append('versions', form.versions)
        payload.append('property_tag', form.property_tag ?? '')
        payload.append('property_desc', form.property_desc ?? '')
        payload.append('common_property', selectedFile.value)
      } else {
        payload = {
          versions: form.versions,
          property_tag: form.property_tag,
          property_desc: form.property_desc,
        }
      }
      await updateSimCommonProperty(props.editData.id, payload)
      ElMessage.success('更新成功')
    } else {
      const formData = new FormData()
      formData.append('versions', form.versions)
      if (form.property_tag) formData.append('property_tag', form.property_tag)
      if (form.property_desc) formData.append('property_desc', form.property_desc)
      formData.append('common_property', selectedFile.value)
      await createSimCommonProperty(formData)
      ElMessage.success('创建成功')
    }
    emit('success')
    visible.value = false
  } catch (err) {
    if (err?.data && typeof err.data === 'object') {
      applyServerErrors(
        Object.entries(err.data).map(([field, msgs]) => ({
          field,
          message: Array.isArray(msgs) ? msgs[0] : msgs,
        })),
      )
    } else {
      ElMessage.error('操作失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

function handleClosed() {
  formRef.value?.resetFields()
  clearServerErrors()
  selectedFile.value = null
}
</script>

<style scoped>
.download-link {
  color: #409eff;
  text-decoration: none;
}
.download-link:hover {
  text-decoration: underline;
}
.no-file {
  color: #909399;
  font-size: 13px;
}
</style>
