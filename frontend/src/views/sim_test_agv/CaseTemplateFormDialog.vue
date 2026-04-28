<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑模版' : '新建模版'" width="560px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="资产版本" prop="sim_test_version" :error="serverErrors.sim_test_version">
        <el-input v-model="form.sim_test_version" list="ct-version-list" placeholder="请输入或选择" clearable />
        <datalist id="ct-version-list">
          <option v-for="v in fieldChoices.sim_test_version" :key="v" :value="v" />
        </datalist>
      </el-form-item>
      <el-form-item label="测试模块 *" prop="test_module" :error="serverErrors.test_module">
        <el-input v-model="form.test_module" list="ct-module-list" placeholder="请输入或选择" clearable />
        <datalist id="ct-module-list">
          <option v-for="v in fieldChoices.test_module" :key="v" :value="v" />
        </datalist>
      </el-form-item>
      <el-form-item label="用例说明" prop="case_desc" :error="serverErrors.case_desc">
        <el-input v-model="form.case_desc" type="textarea" :rows="3" placeholder="请输入用例说明" />
      </el-form-item>
      <el-form-item label="用例文件" prop="case_file_guard" :error="serverErrors.case_file">
        <FileUploader ref="fileRef"
          :tip="isEdit ? '可重新上传覆盖' : '请上传用例文件（必填）'"
          @change="f => { selectedFile = f; form.case_file_guard = f?.name ?? null; formRef?.validateField('case_file_guard') }" />
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
import { createCaseTemplate, updateCaseTemplate, getCaseTemplateChoices } from '@/api/sim_test_agv'
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

const form = reactive({ sim_test_version: '', test_module: '', case_desc: '', case_file_guard: null })

const rules = {
  sim_test_version: [{ required: true, message: '请输入资产版本', trigger: 'blur' }],
  test_module: [{ required: true, message: '请输入测试模块', trigger: 'blur' }],
  case_desc: [{ required: true, message: '请输入用例说明', trigger: 'blur' }],
  case_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedFile) cb(new Error('请上传用例文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

const fieldChoices = reactive({ sim_test_version: [], test_module: [] })

watch(() => props.visible, async val => {
  if (!val) return
  clearServerErrors()
  selectedFile = null
  fileRef.value?.reset?.()
  try {
    const res = await getCaseTemplateChoices()
    const ch = res.data ?? res
    Object.assign(fieldChoices, ch)
  } catch {}
  if (props.editData) {
    const d = props.editData
    Object.assign(form, {
      sim_test_version: d.sim_test_version,
      test_module: d.test_module || '',
      case_desc: d.case_desc,
      case_file_guard: 'existing',
    })
  } else {
    Object.assign(form, { sim_test_version: '', test_module: '', case_desc: '', case_file_guard: null })
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('sim_test_version', form.sim_test_version)
    fd.append('test_module', form.test_module || '')
    fd.append('case_desc', form.case_desc)
    if (selectedFile) fd.append('case_file', selectedFile)

    if (isEdit.value) {
      await updateCaseTemplate(props.editData.id, fd, (p) => fileRef.value?.setProgress(p))
      ElMessage.success('修改成功')
    } else {
      await createCaseTemplate(fd, (p) => fileRef.value?.setProgress(p))
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
