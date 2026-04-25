<template>
  <el-dialog
    v-model="visible"
    title="修改密码"
    width="420px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-alert
      v-if="isDefault"
      type="warning"
      :closable="false"
      style="margin-bottom: 16px"
      title="当前使用的是默认密码，请尽快修改以保障账号安全。"
    />
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="当前密码" prop="old_password">
        <el-input
          v-model="form.old_password"
          type="password"
          :placeholder="isDefault ? '默认密码 Test123456' : '请输入当前密码'"
          show-password
          clearable
        />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input
          v-model="form.new_password"
          type="password"
          placeholder="不少于6位"
          show-password
          clearable
        />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm_password">
        <el-input
          v-model="form.confirm_password"
          type="password"
          placeholder="再次输入新密码"
          show-password
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确认修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v),
})

const authStore = useAuthStore()
const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const isDefault = computed(() => !!authStore.userInfo?.is_default_password)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 开启弹框时，如果是默认密码则自动填入
watch(visible, (val) => {
  if (val && isDefault.value) {
    form.old_password = 'Test123456'
  }
})

const rules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await changePassword({
      old_password: form.old_password,
      new_password: form.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    visible.value = false
    authStore.logout()
    router.push('/login')
  } catch {
    // 错误已由拦截器统一提示
  } finally {
    submitting.value = false
  }
}

function handleClosed() {
  formRef.value?.resetFields()
}
</script>
