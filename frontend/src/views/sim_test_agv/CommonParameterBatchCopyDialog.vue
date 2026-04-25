<template>
  <el-dialog
    v-model="visible"
    title="批量复制通参"
    width="680px"
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    @opened="handleOpened"
    @closed="handleClosed"
  >
    <el-alert type="warning" :closable="false" style="margin-bottom: 16px">
      复制除通参名称以外的内容，所有通参名称必须修改，复制过程中不要关闭窗口
    </el-alert>

    <el-table :data="editItems" border size="small" style="margin-bottom: 8px">
      <el-table-column label="新通参名称 *" min-width="200">
        <template #default="{ row, $index }">
          <el-input
            v-model="row.newName"
            placeholder="请输入新通参名称"
            :disabled="loading"
            size="small"
            :status="nameErrors[$index] ? 'error' : ''"
            @blur="validateRow($index)"
            @input="clearError($index)"
          />
          <div v-if="nameErrors[$index]" style="color:#f56c6c;font-size:12px;margin-top:2px">
            {{ nameErrors[$index] }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="sim_test_version" label="资产版本" min-width="130" />
      <el-table-column prop="sim_test_vehicle" label="测试车型" min-width="110" />
    </el-table>

    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { batchCopyCommonParameters, getCommonParameterChoices } from '@/api/sim_test_agv'

const props = defineProps({
  visible: Boolean,
  rows: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:visible', 'success'])

const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const loading = ref(false)

// 每行编辑状态：含 newName + 原始字段
const editItems = ref([])
// 每行错误信息
const nameErrors = ref([])
// 已有通参名称集合（从 choices 接口加载）
const existingNames = ref(new Set())

watch(() => props.visible, val => {
  if (val) return
  // 关闭时重置
  editItems.value = []
  nameErrors.value = []
})

async function handleOpened() {
  // 初始化编辑行
  editItems.value = props.rows.map(r => ({
    id: r.id,
    newName: r.common_parameter_name,
    sim_test_version: r.sim_test_version,
    sim_test_vehicle: r.sim_test_vehicle,
    common_parameter_name: r.common_parameter_name,
  }))
  nameErrors.value = props.rows.map(() => '')

  // 加载已有名称
  try {
    const res = await getCommonParameterChoices()
    const ch = res.data ?? res
    existingNames.value = new Set(ch.common_parameter_name ?? [])
  } catch {
    existingNames.value = new Set()
  }
}

function handleClosed() {
  editItems.value = []
  nameErrors.value = []
}

function validateRow(idx) {
  const name = (editItems.value[idx]?.newName || '').trim()
  if (!name) {
    nameErrors.value[idx] = '通参名称不能为空'
    return false
  }
  // 和当前输入的其他行重复
  const others = editItems.value.filter((_, i) => i !== idx).map(r => r.newName.trim())
  if (others.includes(name)) {
    nameErrors.value[idx] = '与其他行的通参名称重复'
    return false
  }
  // 和数据库已有名称重复
  if (existingNames.value.has(name)) {
    nameErrors.value[idx] = '该通参名称已存在'
    return false
  }
  nameErrors.value[idx] = ''
  return true
}

function clearError(idx) {
  nameErrors.value[idx] = ''
}

async function handleSubmit() {
  // 全量校验
  let valid = true
  editItems.value.forEach((_, idx) => {
    if (!validateRow(idx)) valid = false
  })
  if (!valid) {
    ElMessage.warning('请修正表格中的错误后再提交')
    return
  }

  loading.value = true
  try {
    const items = editItems.value.map(r => ({
      id: r.id,
      common_parameter_name: r.newName.trim(),
    }))
    await batchCopyCommonParameters(items)
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
</script>
