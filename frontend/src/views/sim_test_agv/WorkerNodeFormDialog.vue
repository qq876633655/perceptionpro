<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑 Worker 节点' : '新建 Worker 节点'" width="520px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="Worker 名称" prop="hostname" :error="serverErrors.hostname">
        <el-input v-model="form.hostname" placeholder="如 celery@dev_test01.webotsC1@server1" clearable />
      </el-form-item>
      <el-form-item label="Docker 类型" :error="serverErrors.docker_type">
        <el-input v-model="form.docker_type" placeholder="如 webotsC1、webotsC2（供任务脚本使用）" clearable />
      </el-form-item>
      <el-form-item label="IP 地址" :error="serverErrors.ip_address">
        <el-input v-model="form.ip_address" placeholder="可选，如 10.20.24.10" clearable />
      </el-form-item>
      <el-form-item label="备注" :error="serverErrors.note">
        <el-input v-model="form.note" type="textarea" :rows="3" placeholder="可选" />
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
import { createWorkerNode, updateWorkerNode } from '@/api/sim_test_agv'

const props = defineProps({ visible: Boolean, row: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v),
})

const isEdit = computed(() => !!props.row)

const formRef = ref(null)
const submitting = ref(false)
const serverErrors = reactive({})

const form = reactive({ hostname: '', docker_type: '', ip_address: '', note: '' })

const rules = {
  hostname: [{ required: true, message: '请输入 Worker 名称', trigger: 'blur' }],
}

watch(() => props.visible, v => {
  if (v) {
    Object.assign(serverErrors, { hostname: '', docker_type: '', ip_address: '', note: '' })
    if (props.row) {
      form.hostname    = props.row.hostname    || ''
      form.docker_type = props.row.docker_type || ''
      form.ip_address  = props.row.ip_address  || ''
      form.note        = props.row.note        || ''
    } else {
      form.hostname    = ''
      form.docker_type = ''
      form.ip_address  = ''
      form.note        = ''
    }
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateWorkerNode(props.row.id, form)
    } else {
      await createWorkerNode(form)
    }
    ElMessage.success(isEdit.value ? '保存成功' : '创建成功')
    emit('success')
    visible.value = false
  } catch (err) {
    const data = err?.response?.data || {}
    Object.assign(serverErrors, data)
    if (data.detail) ElMessage.error(data.detail)
  } finally {
    submitting.value = false
  }
}

function handleClosed() {
  formRef.value?.resetFields()
}
</script>
