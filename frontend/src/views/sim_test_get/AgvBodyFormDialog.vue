<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑车体数据' : '新建车体数据'" width="720px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="测试车型" prop="agv_type" :error="serverErrors.agv_type">
            <el-input v-model="form.agv_type" placeholder="请输入测试车型" clearable />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">车体尺寸</el-divider>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="左边车宽" prop="left_width" :error="serverErrors.left_width">
            <el-input-number v-model="form.left_width" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="右边车宽" prop="right_width" :error="serverErrors.right_width">
            <el-input-number v-model="form.right_width" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="前方车长" prop="front_length" :error="serverErrors.front_length">
            <el-input-number v-model="form.front_length" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="后方车长" prop="back_length" :error="serverErrors.back_length">
            <el-input-number v-model="form.back_length" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="原车前悬距" prop="load_position_x" :error="serverErrors.load_position_x">
            <el-input-number v-model="form.load_position_x" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">货叉参数</el-divider>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="货叉长度" prop="fork_length" :error="serverErrors.fork_length">
            <el-input-number v-model="form.fork_length" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="货叉内宽" prop="fork_inner_width" :error="serverErrors.fork_inner_width">
            <el-input-number v-model="form.fork_inner_width" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="货叉宽度" prop="fork_width" :error="serverErrors.fork_width">
            <el-input-number v-model="form.fork_width" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="货叉厚度" prop="fork_thickness" :error="serverErrors.fork_thickness">
            <el-input-number v-model="form.fork_thickness" :precision="4" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">传感器与节点</el-divider>
      <el-form-item label="传感器外参" prop="sensor_extrinsic" :error="serverErrors.sensor_extrinsic">
        <el-input v-model="form.sensor_extrinsic" type="textarea" :rows="4" placeholder="请输入传感器外参" />
      </el-form-item>
      <el-form-item label="车体节点" prop="agv_node" :error="serverErrors.agv_node">
        <el-input v-model="form.agv_node" type="textarea" :rows="4" placeholder="请输入车体节点" />
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
import { createAgvBody, updateAgvBody } from '@/api/sim_test_get'
import { useFormErrors } from '@/composables/useFormErrors'

const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const submitting = ref(false)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const defaultForm = () => ({
  agv_type: '',
  left_width: 0, right_width: 0, front_length: 0, back_length: 0,
  fork_length: 0, fork_inner_width: 0, fork_width: 0, fork_thickness: 0,
  load_position_x: 0,
  sensor_extrinsic: '', agv_node: '',
})

const form = reactive(defaultForm())

const rules = {
  agv_type: [{ required: true, message: '请输入测试车型', trigger: 'blur' }],
  left_width: [{ required: true, message: '请输入左边车宽', trigger: 'blur' }],
  right_width: [{ required: true, message: '请输入右边车宽', trigger: 'blur' }],
  front_length: [{ required: true, message: '请输入前方车长', trigger: 'blur' }],
  back_length: [{ required: true, message: '请输入后方车长', trigger: 'blur' }],
  fork_length: [{ required: true, message: '请输入货叉长度', trigger: 'blur' }],
  fork_inner_width: [{ required: true, message: '请输入货叉内宽', trigger: 'blur' }],
  fork_width: [{ required: true, message: '请输入货叉宽度', trigger: 'blur' }],
  fork_thickness: [{ required: true, message: '请输入货叉厚度', trigger: 'blur' }],
  load_position_x: [{ required: true, message: '请输入原车前悬距', trigger: 'blur' }],
  sensor_extrinsic: [{ required: true, message: '请输入传感器外参', trigger: 'blur' }],
  agv_node: [{ required: true, message: '请输入车体节点', trigger: 'blur' }],
}

watch(() => props.visible, val => {
  if (val) {
    clearServerErrors()
    Object.assign(form, defaultForm())
    if (props.editData) {
      const d = props.editData
      Object.keys(form).forEach(k => {
        if (k in d) form[k] = d[k]
      })
    }
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateAgvBody(props.editData.id, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createAgvBody({ ...form })
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
