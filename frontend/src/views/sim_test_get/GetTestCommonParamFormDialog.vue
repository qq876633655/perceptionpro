<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑通参' : '新建通参'" width="600px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="通参名称" prop="common_parameter_name" :error="serverErrors.common_parameter_name">
            <el-input v-model="form.common_parameter_name" placeholder="请输入通参名称" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="资产版本" prop="sim_test_version" :error="serverErrors.sim_test_version">
            <el-input v-model="form.sim_test_version" placeholder="请输入资产版本" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试车型" prop="sim_test_vehicle" :error="serverErrors.sim_test_vehicle">
            <el-input v-model="form.sim_test_vehicle" placeholder="请输入测试车型" clearable />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="通参描述" :error="serverErrors.parameter_desc">
        <el-input v-model="form.parameter_desc" type="textarea" :rows="3" placeholder="可选" />
      </el-form-item>
      <el-form-item label="通参文件" prop="common_parameter_file_guard" :error="serverErrors.common_parameter_file">
        <FileUploader ref="fileRef"
          :tip="isEdit ? '可重新上传覆盖' : '请上传通参文件（必填）'"
          @change="f => { selectedFile = f; form.common_parameter_file_guard = f?.name ?? null; formRef?.validateField('common_parameter_file_guard') }" />
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
import { createGetTestCommonParam, updateGetTestCommonParam } from '@/api/sim_test_get'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const fileRef = ref(null)
const submitting = ref(false)
let selectedFile = null
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({
  common_parameter_name: '',
  sim_test_version: '',
  sim_test_vehicle: '',
  parameter_desc: '',
  common_parameter_file_guard: null,
})

const rules = {
  common_parameter_name: [{ required: true, message: '请输入通参名称', trigger: 'blur' }],
  sim_test_version: [{ required: true, message: '请输入资产版本', trigger: 'blur' }],
  sim_test_vehicle: [{ required: true, message: '请输入测试车型', trigger: 'blur' }],
  common_parameter_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedFile) cb(new Error('请上传通参文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

watch(() => props.visible, val => {
  if (val) {
    clearServerErrors()
    selectedFile = null
    fileRef.value?.reset?.()
    Object.assign(form, {
      common_parameter_name: '',
      sim_test_version: '',
      sim_test_vehicle: '',
      parameter_desc: '',
      common_parameter_file_guard: null,
    })
    if (props.editData) {
      form.common_parameter_name = props.editData.common_parameter_name || ''
      form.sim_test_version = props.editData.sim_test_version || ''
      form.sim_test_vehicle = props.editData.sim_test_vehicle || ''
      form.parameter_desc = props.editData.parameter_desc || ''
    }
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('common_parameter_name', form.common_parameter_name)
    fd.append('sim_test_version', form.sim_test_version)
    fd.append('sim_test_vehicle', form.sim_test_vehicle)
    fd.append('parameter_desc', form.parameter_desc || '')
    if (selectedFile) fd.append('common_parameter_file', selectedFile)

    if (isEdit.value) {
      await updateGetTestCommonParam(props.editData.id, fd)
      ElMessage.success('修改成功')
    } else {
      await createGetTestCommonParam(fd)
      ElMessage.success('创建成功')
    }
    visible.value = false
    emit('success')
  } catch (err) {
    if (err?.response?.data) applyServerErrors(err.response.data)
    else ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

function handleClosed() {
  formRef.value?.resetFields()
  clearServerErrors()
}
</script>
