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
            <el-input v-model="form.sim_test_version" list="scp-version-list" placeholder="请输入或选择" clearable />
            <datalist id="scp-version-list">
              <option v-for="v in fieldChoices.sim_test_version" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试车型" prop="sim_test_vehicle" :error="serverErrors.sim_test_vehicle">
            <el-input v-model="form.sim_test_vehicle" list="scp-vehicle-list" placeholder="请输入或选择" clearable />
            <datalist id="scp-vehicle-list">
              <option v-for="v in fieldChoices.sim_test_vehicle" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试模块" prop="test_module" :error="serverErrors.test_module">
            <el-input v-model="form.test_module" list="scp-module-list" placeholder="请输入或选择" clearable />
            <datalist id="scp-module-list">
              <option v-for="v in fieldChoices.test_module" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="通参状态" prop="common_parameter_status">
            <el-select v-model="form.common_parameter_status" style="width:100%">
              <el-option label="正常" value="正常" />
              <el-option label="维护" value="维护" />
            </el-select>
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
import { createCommonParameter, updateCommonParameter, getCommonParameterChoices } from '@/api/sim_test_agv'
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
  common_parameter_name: '', sim_test_version: '', sim_test_vehicle: '',
  test_module: '', parameter_desc: '', common_parameter_status: '正常',
  common_parameter_file_guard: null,
})

const rules = {
  common_parameter_name: [{ required: true, message: '请输入通参名称', trigger: 'blur' }],
  sim_test_version: [{ required: true, message: '请输入资产版本', trigger: 'blur' }],
  sim_test_vehicle: [{ required: true, message: '请输入测试车型', trigger: 'blur' }],
  test_module: [{ required: true, message: '请输入测试模块', trigger: 'blur' }],
  common_parameter_status: [{ required: true, message: '请选择通参状态', trigger: 'change' }],
  common_parameter_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedFile) cb(new Error('请上传通参文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

const fieldChoices = reactive({ sim_test_version: [], sim_test_vehicle: [], test_module: [] })

watch(() => props.visible, async val => {
  if (!val) return
  clearServerErrors()
  selectedFile = null
  fileRef.value?.reset?.()
  try {
    const res = await getCommonParameterChoices()
    const ch = res.data ?? res
    Object.assign(fieldChoices, ch)
  } catch {}
  if (props.editData) {
    const d = props.editData
    Object.assign(form, {
      common_parameter_name: d.common_parameter_name,
      sim_test_version: d.sim_test_version,
      sim_test_vehicle: d.sim_test_vehicle,
      test_module: d.test_module || '',
      parameter_desc: d.parameter_desc || '',
      common_parameter_status: d.common_parameter_status || '正常',
      common_parameter_file_guard: 'existing',
    })
  } else {
    Object.assign(form, {
      common_parameter_name: '', sim_test_version: '', sim_test_vehicle: '',
      test_module: '', parameter_desc: '', common_parameter_status: '正常',
      common_parameter_file_guard: null,
    })
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
    fd.append('test_module', form.test_module || '')
    fd.append('parameter_desc', form.parameter_desc || '')
    fd.append('common_parameter_status', form.common_parameter_status)
    if (selectedFile) fd.append('common_parameter_file', selectedFile)

    if (isEdit.value) {
      await updateCommonParameter(props.editData.id, fd)
      ElMessage.success('修改成功')
    } else {
      await createCommonParameter(fd)
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
