<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑地图' : '新建地图'" width="480px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="分区名称" prop="district_name" :error="serverErrors.district_name">
        <el-input v-model="form.district_name" placeholder="请输入分区名称" clearable />
      </el-form-item>
      <el-form-item v-if="isEdit" label="地图文件">
        <span class="file-hint">{{ props.editData?.map_file ? '已上传（可重新上传覆盖）' : '未上传' }}</span>
      </el-form-item>
      <el-form-item label="地图文件" prop="map_file_guard" :error="serverErrors.map_file">
        <FileUploader ref="fileRef" :tip="isEdit ? '可重新上传覆盖' : '请上传地图文件（必填）'"
          @change="f => { selectedFile = f; form.map_file_guard = f?.name ?? null; formRef?.validateField('map_file_guard') }" />
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
import { createCaseMap, updateCaseMap } from '@/api/sim_test_agv'
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

const form = reactive({ district_name: '', map_file_guard: null })
const rules = {
  district_name: [{ required: true, message: '请输入分区名称', trigger: 'blur' }],
  map_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedFile.value) cb(new Error('请上传地图文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

watch(() => props.visible, val => {
  if (val) {
    clearServerErrors()
    selectedFile.value = null
    fileRef.value?.reset?.()
    form.district_name = props.editData?.district_name || ''
    form.map_file_guard = isEdit.value ? 'existing' : null
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('district_name', form.district_name)
    if (selectedFile.value) fd.append('map_file', selectedFile.value)

    if (isEdit.value) {
      await updateCaseMap(props.editData.id, fd, (p) => fileRef.value?.setProgress(p))
      ElMessage.success('修改成功')
    } else {
      await createCaseMap(fd, (p) => fileRef.value?.setProgress(p))
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
