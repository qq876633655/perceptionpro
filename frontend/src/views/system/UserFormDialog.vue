<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑用户' : '新建用户'"
    width="560px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="用户名" prop="username" :error="serverErrors.username">
        <el-input
          v-model="form.username"
          :disabled="isEdit"
          :placeholder="isEdit ? '用户名创建后不可修改' : '请输入用户名'"
          clearable
        />
      </el-form-item>

      <el-form-item label="手机号" prop="phone_number" :error="serverErrors.phone_number">
        <el-input v-model="form.phone_number" placeholder="请输入手机号" clearable />
      </el-form-item>

      <el-form-item label="密码" prop="password" :error="serverErrors.password">
        <el-input
          v-model="form.password"
          type="password"
          :placeholder="isEdit ? '密码已加密存储，如需修改请输入新密码' : '不填默认 Test123456'"
          clearable
          show-password
        />
        <div v-if="isEdit" style="font-size:12px; color:#909399; margin-top:4px;">
          密码经过单向加密，无法查看原始内容
        </div>
      </el-form-item>

      <el-form-item label="管理员" prop="is_staff">
        <el-switch
          v-if="isSuperUser"
          v-model="form.is_staff"
          active-text="是"
          inactive-text="否"
        />
        <el-tag v-else :type="form.is_staff ? 'warning' : 'info'" size="small">
          {{ form.is_staff ? '管理员' : '普通用户' }}
        </el-tag>
      </el-form-item>

      <el-form-item label="超级管理员" prop="is_superuser">
        <el-switch
          v-if="isSuperUser"
          v-model="form.is_superuser"
          active-text="是"
          inactive-text="否"
        />
        <el-tag v-else :type="form.is_superuser ? 'danger' : 'info'" size="small">
          {{ form.is_superuser ? '是' : '否' }}
        </el-tag>
      </el-form-item>

      <el-form-item label="账号状态" prop="is_active">
        <el-switch
          v-model="form.is_active"
          active-text="正常"
          inactive-text="禁用"
          :active-value="true"
          :inactive-value="false"
        />
      </el-form-item>

      <el-form-item label="角色" :error="serverErrors.group_ids">
        <el-select
          v-model="form.group_ids"
          multiple
          placeholder="请选择角色（可多选）"
          style="width: 100%"
          clearable
          filterable
        >
          <el-option
            v-for="g in groupOptions"
            :key="g.id"
            :label="g.name"
            :value="g.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '创建用户' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createUser, updateUser } from '@/api/admin'
import { useFormErrors } from '@/composables/useFormErrors'

const props = defineProps({
  visible: Boolean,
  editData: { type: Object, default: null },
  groupOptions: { type: Array, default: () => [] },
  isSuperUser: { type: Boolean, default: false },
})
const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v),
})
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const submitting = ref(false)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({
  username: '',
  phone_number: '',
  password: '',
  is_staff: false,
  is_superuser: false,
  is_active: true,
  group_ids: [],
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  phone_number: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^\+?[0-9]{5,15}$/, message: '手机号格式不正确（支持国际号码）', trigger: 'blur' },
  ],
  password: [
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      clearServerErrors()
      if (props.editData) {
        Object.assign(form, {
          username: props.editData.username ?? '',
          phone_number: props.editData.phone_number ?? '',
          password: '',
          is_staff: !!props.editData.is_staff,
          is_superuser: !!props.editData.is_superuser,
          is_active: props.editData.is_active !== false,
          group_ids: props.editData.group_ids ?? [],
        })
      } else {
        Object.assign(form, {
          username: '', phone_number: '', password: '',
          is_staff: false, is_superuser: false, is_active: true, group_ids: [],
        })
      }
    }
  },
)

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  clearServerErrors()
  const payload = {
    phone_number: form.phone_number,
    is_active: form.is_active,
    group_ids: form.group_ids,
  }
  // 超级管理员才能修改这两个字段
  if (props.isSuperUser) {
    payload.is_staff = form.is_staff
    payload.is_superuser = form.is_superuser
  }
  if (form.password) payload.password = form.password
  if (!isEdit.value) payload.username = form.username

  try {
    if (isEdit.value) {
      await updateUser(props.editData.id, payload)
      ElMessage.success('用户修改成功')
    } else {
      await createUser(payload)
      ElMessage.success('用户创建成功')
    }
    emit('success')
    visible.value = false
  } catch (err) {
    if (err?.data && typeof err.data === 'object') {
      applyServerErrors(
        Object.entries(err.data).map(([field, msgs]) => ({
          field,
          message: Array.isArray(msgs) ? msgs[0] : msgs,
        })),
      )
    }
  } finally {
    submitting.value = false
  }
}

function handleClosed() {
  formRef.value?.resetFields()
  clearServerErrors()
}
</script>
