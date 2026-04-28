<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑版本' : '新建版本'" width="620px" :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="版本号" prop="version_num" :error="serverErrors.version_num">
        <el-input v-model="form.version_num" :disabled="isEdit" :placeholder="isEdit ? '版本号创建后不可修改' : '请输入版本号，如 v1.0.0'" clearable />
      </el-form-item>
      <el-form-item label="版本类型" prop="versions_type" :error="serverErrors.versions_type">
        <el-checkbox-group v-model="form.versions_type">
          <el-checkbox value="feature">feature</el-checkbox>
          <el-checkbox value="dev">dev</el-checkbox>
          <el-checkbox value="test">test</el-checkbox>
          <el-checkbox value="hotfix">hotfix</el-checkbox>
          <el-checkbox value="release">release</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="适用专项" prop="apply_project" :error="serverErrors.apply_project">
        <el-input v-model="form.apply_project" placeholder="如：主线版本" clearable />
      </el-form-item>
      <el-form-item label="关联环境" prop="env" :error="serverErrors.env">
        <el-select v-model="form.env" placeholder="请选择关联环境" style="width: 100%" clearable filterable>
          <el-option v-for="env in envOptions" :key="env.id" :label="env.env_name" :value="env.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="研发提测" prop="dev_test_result" :error="serverErrors.dev_test_result">
        <el-input v-model="form.dev_test_result" type="textarea" :rows="3" placeholder="请输入研发提测内容" />
      </el-form-item>
      <template v-if="isEdit">
        <el-form-item label="测试结果" prop="test_result" :error="serverErrors.test_result">
          <el-select v-model="form.test_result" placeholder="请选择测试结果" style="width: 100%">
            <el-option label="未开始" value="未开始" />
            <el-option label="测试中" value="测试中" />
            <el-option label="通过" value="通过" />
            <el-option label="失败" value="失败" />
            <el-option label="中断" value="中断" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试总结" prop="test_verdict" :error="serverErrors.test_verdict">
          <el-input v-model="form.test_verdict" type="textarea" :rows="3" placeholder="请输入测试总结" />
        </el-form-item>
      </template>
      <el-form-item v-if="isEdit" label="版本文件">
        <el-input :model-value="props.editData?.version_file ? '已上传（版本文件创建后不可修改）' : '未上传（版本文件创建后不可修改）'" disabled />
      </el-form-item>
      <el-form-item v-else label="版本文件" prop="version_file" :error="serverErrors.version_file">
        <FileUploader ref="versionFileRef" tip="请上传版本文件" @change="handleVersionFileChange" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">{{ isEdit ? '保存修改' : '创建版本' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { atApi } from '@/api/version'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({
  visible: Boolean,
  editData: { type: Object, default: null },
})
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: (v) => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const versionFileRef = ref(null)
const submitting = ref(false)
const selectedVersionFile = ref(null)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({
  version_num: '', versions_type: [], apply_project: '主线版本',
  env: null, dev_test_result: '', test_result: '未开始', test_verdict: '', version_file: null,
})

const rules = {
  version_num: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9._\-]+$/, message: '版本号仅支持字母、数字、点(.)、横线(-)、下划线(_)', trigger: 'blur' },
  ],
  versions_type: [{ required: true, message: '请至少选择一种版本类型', trigger: 'change' }],
  apply_project: [{ required: true, message: '请输入适用专项', trigger: 'blur' }],
  env: [{ required: true, message: '请选择关联环境', trigger: 'change' }],
  version_file: [{
    required: true,
    validator: (rule, value, callback) => {
      if (!isEdit.value && !selectedVersionFile.value) callback(new Error('请上传版本文件'))
      else callback()
    },
    trigger: 'change',
  }],
}

function handleVersionFileChange(file) {
  selectedVersionFile.value = file
  form.version_file = file ? file.name : null
  formRef.value?.validateField('version_file')
}

const envOptions = ref([])
async function loadEnvOptions() {
  try {
    const res = await atApi.getEnvList({ page_size: 999 })
    envOptions.value = res.data ?? []
  } catch {}
}

watch(() => props.visible, (val) => {
  if (val) {
    clearServerErrors()
    selectedVersionFile.value = null
    if (props.editData) {
      Object.assign(form, {
        version_num: props.editData.version_num,
        versions_type: props.editData.versions_type ?? [],
        apply_project: props.editData.apply_project ?? '主线版本',
        env: props.editData.env,
        dev_test_result: props.editData.dev_test_result ?? '',
        test_result: props.editData.test_result ?? '未开始',
        test_verdict: props.editData.test_verdict ?? '',
        version_file: props.editData.version_file ?? null,
      })
    } else {
      Object.assign(form, { version_num: '', versions_type: [], apply_project: '主线版本', env: null, dev_test_result: '', test_result: '未开始', test_verdict: '', version_file: null })
    }
    loadEnvOptions()
  }
})

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  clearServerErrors()
  try {
    if (!isEdit.value) {
      const fd = new FormData()
      fd.append('version_num', form.version_num)
      fd.append('versions_type', JSON.stringify(form.versions_type))
      fd.append('apply_project', form.apply_project)
      if (form.env != null) fd.append('env', form.env)
      if (form.dev_test_result) fd.append('dev_test_result', form.dev_test_result)
      fd.append('version_file', selectedVersionFile.value)
      await atApi.createVersion(fd)
      ElMessage.success('版本创建成功')
    } else {
      await atApi.updateVersion(props.editData.id, {
        versions_type: form.versions_type,
        apply_project: form.apply_project,
        env: form.env,
        dev_test_result: form.dev_test_result,
        test_result: form.test_result,
        test_verdict: form.test_verdict ?? '',
      })
      ElMessage.success('版本修改成功')
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
  versionFileRef.value?.reset()
  selectedVersionFile.value = null
  clearServerErrors()
}
</script>
