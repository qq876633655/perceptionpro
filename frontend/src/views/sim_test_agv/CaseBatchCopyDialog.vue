<template>
  <el-dialog
    v-model="visible"
    title="批量复制资产"
    width="560px"
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    @closed="handleClosed"
  >
    <el-alert type="warning" :closable="false" style="margin-bottom: 16px">
      复制除资产版本以外的内容，复制过程中不要关闭窗口
    </el-alert>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="资产版本" prop="sim_test_version">
        <el-input v-model="form.sim_test_version" placeholder="请输入新的资产版本号" clearable :disabled="loading" />
      </el-form-item>
    </el-form>

    <div style="margin: 12px 0 6px; color: #606266; font-size: 13px">待复制记录：</div>
    <el-table :data="rows" size="small" border max-height="240">
      <el-table-column prop="sim_test_version" label="资产版本" min-width="120" />
      <el-table-column prop="sim_test_vehicle" label="测试车型" min-width="100" />
      <el-table-column prop="sim_scheme_name" label="测试方案" min-width="120" />
    </el-table>

    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { batchCopyCaseProperties } from '@/api/sim_test_agv'

const props = defineProps({
  visible: Boolean,
  rows: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:visible', 'success'])

const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const loading = ref(false)
const formRef = ref(null)
const form = reactive({ sim_test_version: '' })

const selectedVersions = computed(() => new Set(props.rows.map(r => r.sim_test_version)))

const rules = {
  sim_test_version: [
    { required: true, message: '请输入资产版本', trigger: 'blur' },
    {
      validator: (rule, val, cb) => {
        if (val && selectedVersions.value.has(val)) {
          cb(new Error('新版本号不能与已选记录的资产版本相同'))
        } else {
          cb()
        }
      },
      trigger: 'blur',
    },
  ],
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const ids = props.rows.map(r => r.id)
    await batchCopyCaseProperties(ids, form.sim_test_version)
    ElMessage.success('复制成功')
    visible.value = false
    emit('success')
  } catch (err) {
    const detail = err?.response?.data?.detail || '复制失败，请重试'
    ElMessage.error(detail)
  } finally {
    loading.value = false
  }
}

function handleClosed() {
  form.sim_test_version = ''
  formRef.value?.resetFields()
}
</script>
