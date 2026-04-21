<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑版本' : '新建版本'"
    width="600px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <!-- 版本号：仅创建时可填，编辑时禁用 -->
      <el-form-item label="版本号" prop="version_num" :error="serverErrors.version_num">
        <el-input
          v-model="form.version_num"
          :disabled="isEdit"
          :placeholder="isEdit ? '版本号创建后不可修改' : '请输入版本号，如 v1.0.0'"
          clearable
        />
      </el-form-item>

      <el-form-item label="版本类型" prop="versions_type" :error="serverErrors.versions_type">
        <el-select
          v-model="form.versions_type"
          placeholder="请选择版本类型"
          style="width: 100%"
          multiple
          allow-create
          filterable
        >
          <el-option label="功能版本" value="功能版本" />
          <el-option label="修复版本" value="修复版本" />
          <el-option label="性能版本" value="性能版本" />
          <el-option label="安全版本" value="安全版本" />
        </el-select>
      </el-form-item>

      <el-form-item label="适用专项" prop="apply_project" :error="serverErrors.apply_project">
        <el-input
          v-model="form.apply_project"
          placeholder="如：主线版本"
          clearable
        />
      </el-form-item>

      <el-form-item label="关联环境" prop="env" :error="serverErrors.env">
        <el-select
          v-model="form.env"
          placeholder="请选择关联环境"
          style="width: 100%"
          clearable
          filterable
        >
          <el-option
            v-for="env in envOptions"
            :key="env.id"
            :label="env.env_name"
            :value="env.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="研发提测" prop="dev_test_result" :error="serverErrors.dev_test_result">
        <el-input
          v-model="form.dev_test_result"
          type="textarea"
          :rows="3"
          placeholder="请输入研发提测内容"
        />
      </el-form-item>

      <!-- 以下字段仅编辑时显示 -->
      <template v-if="isEdit">
        <el-form-item label="测试结果" prop="test_result" :error="serverErrors.test_result">
          <el-select v-model="form.test_result" placeholder="请选择测试结果" style="width: 100%">
            <el-option label="未开始" value="未开始" />
            <el-option label="测试中" value="测试中" />
            <el-option label="通过" value="通过" />
            <el-option label="不通过" value="不通过" />
          </el-select>
        </el-form-item>

        <el-form-item label="测试总结" prop="test_verdict" :error="serverErrors.test_verdict">
          <el-input
            v-model="form.test_verdict"
            type="textarea"
            :rows="3"
            placeholder="请输入测试总结"
          />
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '创建版本' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createVersion, updateVersion, getEnvList } from '@/api/version'
import { useFormErrors } from '@/composables/useFormErrors'

const props = defineProps({
  visible: Boolean,
  /** 编辑时传入行数据，null 表示新建 */
  editData: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v),
})

const isEdit = computed(() => !!props.editData)

// ── 表单 ────────────────────────────────────────────────────────────
const formRef = ref(null)
const submitting = ref(false)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({
  version_num: '',
  versions_type: [],
  apply_project: '主线版本',
  env: null,
  dev_test_result: '',
  test_result: '未开始',
  test_verdict: '',
})

const rules = {
  version_num: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  versions_type: [{ required: true, message: '请选择版本类型', trigger: 'change' }],
}

// 打开弹窗时回填数据
watch(
  () => props.visible,
  (val) => {
    if (val) {
      clearServerErrors()
      if (props.editData) {
        Object.assign(form, {
          version_num: props.editData.version_num,
          versions_type: props.editData.versions_type ?? [],
          apply_project: props.editData.apply_project ?? '主线版本',
          env: props.editData.env,
          dev_test_result: props.editData.dev_test_result ?? '',
          test_result: props.editData.test_result ?? '未开始',
          test_verdict: props.editData.test_verdict ?? '',
        })
      }
      loadEnvOptions()
    }
  },
)

// ── 环境选项 ────────────────────────────────────────────────────────
const envOptions = ref([])
async function loadEnvOptions() {
  try {
    const res = await getEnvList({ page_size: 999 })
    envOptions.value = res.data ?? []
  } catch {
    // 忽略，不影响主流程
  }
}

// ── 提交 ────────────────────────────────────────────────────────────
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  clearServerErrors()
  try {
    const payload = {
      versions_type: form.versions_type,
      apply_project: form.apply_project,
      env: form.env,
      dev_test_result: form.dev_test_result,
    }
    if (isEdit.value) {
      payload.test_result = form.test_result
      payload.test_verdict = form.test_verdict
    } else {
      payload.version_num = form.version_num
    }

    if (isEdit.value) {
      await updateVersion(props.editData.id, payload)
      ElMessage.success('版本修改成功')
    } else {
      await createVersion(payload)
      ElMessage.success('版本创建成功')
    }
    emit('success')
    visible.value = false
  } catch (err) {
    // 后端字段校验错误回填
    if (Array.isArray(err?.data)) {
      applyServerErrors(err.data)
    }
  } finally {
    submitting.value = false
  }
}

// ── 关闭时重置 ────────────────────────────────────────────────────────
function handleClosed() {
  formRef.value?.resetFields()
  Object.assign(form, {
    version_num: '',
    versions_type: [],
    apply_project: '主线版本',
    env: null,
    dev_test_result: '',
    test_result: '未开始',
    test_verdict: '',
  })
  clearServerErrors()
}
</script>
