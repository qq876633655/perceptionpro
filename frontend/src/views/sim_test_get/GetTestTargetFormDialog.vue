<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑载具数据' : '新建载具数据'" width="820px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="140px">
      <!-- 基本信息 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="载具名称" prop="target_name" :error="serverErrors.target_name">
            <el-input v-model="form.target_name" placeholder="请输入载具名称" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="类型" prop="target_type" :error="serverErrors.target_type">
            <el-select v-model="form.target_type" style="width:100%">
              <el-option label="托盘" value="pallet" />
              <el-option label="料笼" value="cage" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="模型材质" prop="texture" :error="serverErrors.texture">
            <el-select v-model="form.texture" style="width:100%">
              <el-option label="塑料" value="plastic" />
              <el-option label="金属" value="metal" />
              <el-option label="木材" value="wood" />
              <el-option label="镜面空洞" value="mirror_hollow" />
              <el-option label="塑料破损" value="plastic_damaged" />
              <el-option label="镜面" value="mirror" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="模型颜色" prop="color" :error="serverErrors.color">
            <el-select v-model="form.color" style="width:100%">
              <el-option label="白色" value="white" />
              <el-option label="黄色" value="yellow" />
              <el-option label="蓝色" value="blue" />
              <el-option label="黑色" value="black" />
              <el-option label="红色" value="red" />
              <el-option label="红棕色" value="red_brown" />
              <el-option label="银色" value="silver" />
              <el-option label="原木色" value="wood_color" />
              <el-option label="黑色空洞" value="black_hollow" />
              <el-option label="银灰色" value="silver_gray" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="入叉面长" prop="length" :error="serverErrors.length">
            <el-input-number v-model="form.length" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="入叉面宽" prop="width" :error="serverErrors.width">
            <el-input-number v-model="form.width" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="入叉面高" prop="height" :error="serverErrors.height">
            <el-input-number v-model="form.height" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 卡板参数 -->
      <el-divider content-position="left">卡板参数</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="墩宽列表" prop="pallet" :error="serverErrors.pallet">
            <el-input v-model="form.pallet" placeholder="如: 0,0,0" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="孔宽列表" prop="hole" :error="serverErrors.hole">
            <el-input v-model="form.hole" placeholder="如: 0,0" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="墩高" :error="serverErrors.pallet_height">
            <el-input-number v-model="form.pallet_height" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="面板高度" :error="serverErrors.top_height">
            <el-input-number v-model="form.top_height" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="底板高度" :error="serverErrors.bottom_height">
            <el-input-number v-model="form.bottom_height" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="面板y方向突出量" :error="serverErrors.card_width_expand">
            <el-input-number v-model="form.card_width_expand" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="面板x方向突出量" :error="serverErrors.card_length_expand">
            <el-input-number v-model="form.card_length_expand" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="入叉高度偏移量" :error="serverErrors.fork_in_bias_height">
            <el-input-number v-model="form.fork_in_bias_height" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="roi区域偏移距离" :error="serverErrors.adaption_z_reserve">
            <el-input-number v-model="form.adaption_z_reserve" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="卡板长度" :error="serverErrors.card_length">
            <el-input-number v-model="form.card_length" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="卡板高度" :error="serverErrors.card_height">
            <el-input-number v-model="form.card_height" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 中心点坐标 -->
      <el-divider content-position="left">物体坐标入叉面中心点</el-divider>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="中心点 x" :error="serverErrors.t_target_in_fork_center_x">
            <el-input-number v-model="form.t_target_in_fork_center_x" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="中心点 y" :error="serverErrors.t_target_in_fork_center_y">
            <el-input-number v-model="form.t_target_in_fork_center_y" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="中心点 z" :error="serverErrors.t_target_in_fork_center_z">
            <el-input-number v-model="form.t_target_in_fork_center_z" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 模型信息 -->
      <el-divider content-position="left">模型信息</el-divider>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="模型名称" prop="model_name" :error="serverErrors.model_name">
            <el-input v-model="form.model_name" placeholder="请输入模型名称" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="引用路径" prop="extern_proto_path" :error="serverErrors.extern_proto_path">
            <el-input v-model="form.extern_proto_path" placeholder="请输入引用路径" clearable />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="节点参数" prop="node_params" :error="serverErrors.node_params">
        <el-input v-model="nodeParamsText" type="textarea" :rows="5"
          placeholder="请输入 JSON 格式的节点参数" @blur="parseNodeParams" />
        <div v-if="nodeParamsError" style="color: #f56c6c; font-size: 12px; margin-top: 4px;">
          {{ nodeParamsError }}
        </div>
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
import { createGetTestTarget, updateGetTestTarget } from '@/api/sim_test_get'
import { useFormErrors } from '@/composables/useFormErrors'

const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const submitting = ref(false)
const nodeParamsText = ref('')
const nodeParamsError = ref('')
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const defaultForm = () => ({
  target_name: '', target_type: 'pallet',
  pallet: '0,0,0', hole: '0,0',
  pallet_height: 0, top_height: 0, bottom_height: 0,
  card_width_expand: 0, card_length_expand: 0,
  fork_in_bias_height: 0, adaption_z_reserve: 0,
  card_length: 0, card_height: 0,
  texture: '', color: '',
  length: 0, width: 0, height: 0,
  t_target_in_fork_center_x: 0, t_target_in_fork_center_y: 0, t_target_in_fork_center_z: 0,
  model_name: '', extern_proto_path: '',
  node_params: {},
})

const form = reactive(defaultForm())

const rules = {
  target_name: [{ required: true, message: '请输入载具名称', trigger: 'blur' }],
  target_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  texture: [{ required: true, message: '请选择材质', trigger: 'change' }],
  color: [{ required: true, message: '请选择颜色', trigger: 'change' }],
  length: [{ required: true, message: '请输入入叉面长', trigger: 'blur' }],
  width: [{ required: true, message: '请输入入叉面宽', trigger: 'blur' }],
  height: [{ required: true, message: '请输入入叉面高', trigger: 'blur' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  extern_proto_path: [{ required: true, message: '请输入引用路径', trigger: 'blur' }],
  node_params: [{ required: true, message: '请输入节点参数', trigger: 'blur' }],
}

function parseNodeParams() {
  nodeParamsError.value = ''
  try {
    form.node_params = JSON.parse(nodeParamsText.value || '{}')
  } catch {
    nodeParamsError.value = 'JSON 格式有误，请检查'
  }
}

watch(() => props.visible, val => {
  if (val) {
    clearServerErrors()
    nodeParamsError.value = ''
    Object.assign(form, defaultForm())
    if (props.editData) {
      const d = props.editData
      Object.keys(form).forEach(k => {
        if (k in d) form[k] = d[k]
      })
      nodeParamsText.value = JSON.stringify(d.node_params ?? {}, null, 2)
    } else {
      nodeParamsText.value = '{}'
    }
  }
})

async function handleSubmit() {
  parseNodeParams()
  if (nodeParamsError.value) return
  await formRef.value.validate()
  submitting.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await updateGetTestTarget(props.editData.id, payload)
      ElMessage.success('修改成功')
    } else {
      await createGetTestTarget(payload)
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
