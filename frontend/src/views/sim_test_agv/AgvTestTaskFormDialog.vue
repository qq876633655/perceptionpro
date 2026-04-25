<template>
  <el-dialog v-model="visible" title="新建测试任务" width="680px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="使用资产版本" prop="sim_test_version" :error="serverErrors.sim_test_version">
            <el-select v-model="form.sim_test_version" placeholder="请选择" filterable style="width:100%">
              <el-option v-for="v in simTestVersions" :key="v" :label="v" :value="v" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="任务队列" prop="queue_name" :error="serverErrors.queue_name">
            <el-input v-model="form.queue_name" placeholder="请输入任务队列" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="恢复默认版本" :error="serverErrors.recovery_default_version">
            <el-select v-model="form.recovery_default_version" style="width:100%">
              <el-option label="True" value="True" />
              <el-option label="False" value="False" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="待测基线版本" :error="serverErrors.base_version">
            <el-input v-model="form.base_version" placeholder="可选" clearable />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 文件字段 -->
      <el-form-item label="测试用例" prop="agv_case_file_guard" :error="serverErrors.agv_case_file">
        <FileUploader ref="caseFileRef" tip="请上传测试用例文件（必填）"
          @change="f => { selectedFiles.agv_case_file = f; form.agv_case_file_guard = f?.name ?? null; formRef?.validateField('agv_case_file_guard') }" />
      </el-form-item>
      <el-form-item label="感知测试版本" :error="serverErrors.per_version">
        <FileUploader ref="perFileRef" tip="可选" @change="f => (selectedFiles.per_version = f)" />
      </el-form-item>
      <el-form-item label="定位测试版本" :error="serverErrors.loc_version">
        <FileUploader ref="locFileRef" tip="可选" @change="f => (selectedFiles.loc_version = f)" />
      </el-form-item>
      <el-form-item label="控制测试版本" :error="serverErrors.ctl_version">
        <FileUploader ref="ctlFileRef" tip="可选" @change="f => (selectedFiles.ctl_version = f)" />
      </el-form-item>
      <el-form-item label="整车测试版本" :error="serverErrors.agv_version">
        <FileUploader ref="agvFileRef" tip="可选" @change="f => (selectedFiles.agv_version = f)" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">创建任务</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createAgvTestTask, getCasePropertySimTestVersions } from '@/api/sim_test_agv'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })

const formRef = ref(null)
const caseFileRef = ref(null)
const perFileRef = ref(null)
const locFileRef = ref(null)
const ctlFileRef = ref(null)
const agvFileRef = ref(null)
const submitting = ref(false)
const simTestVersions = ref([])
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const selectedFiles = reactive({
  agv_case_file: null,
  per_version: null,
  loc_version: null,
  ctl_version: null,
  agv_version: null,
})

const form = reactive({
  sim_test_version: '',
  queue_name: '',
  recovery_default_version: 'False',
  base_version: '',
  agv_case_file_guard: null,
})

const rules = {
  sim_test_version: [{ required: true, message: '请选择使用资产版本', trigger: 'change' }],
  queue_name: [{ required: true, message: '请输入任务队列', trigger: 'blur' }],
  agv_case_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!selectedFiles.agv_case_file) cb(new Error('请上传测试用例文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

watch(() => props.visible, async val => {
  if (!val) return
  clearServerErrors()
  Object.keys(selectedFiles).forEach(k => (selectedFiles[k] = null))
  caseFileRef.value?.reset?.()
  perFileRef.value?.reset?.()
  locFileRef.value?.reset?.()
  ctlFileRef.value?.reset?.()
  agvFileRef.value?.reset?.()
  Object.assign(form, { sim_test_version: '', queue_name: '', recovery_default_version: 'False', base_version: '', agv_case_file_guard: null })

  try {
    const res = await getCasePropertySimTestVersions()
    simTestVersions.value = res.data ?? []
  } catch { simTestVersions.value = [] }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('sim_test_version', form.sim_test_version)
    fd.append('queue_name', form.queue_name)
    fd.append('recovery_default_version', form.recovery_default_version)
    if (form.base_version) fd.append('base_version', form.base_version)
    if (selectedFiles.agv_case_file) fd.append('agv_case_file', selectedFiles.agv_case_file)
    if (selectedFiles.per_version) fd.append('per_version', selectedFiles.per_version)
    if (selectedFiles.loc_version) fd.append('loc_version', selectedFiles.loc_version)
    if (selectedFiles.ctl_version) fd.append('ctl_version', selectedFiles.ctl_version)
    if (selectedFiles.agv_version) fd.append('agv_version', selectedFiles.agv_version)

    await createAgvTestTask(fd)
    ElMessage.success('创建成功')
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
