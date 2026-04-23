<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑角色' : '新建角色'"
    width="680px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="角色名称" prop="name" :error="serverErrors.name">
        <el-input v-model="form.name" placeholder="请输入角色名称" clearable />
      </el-form-item>

      <el-form-item label="权限">
        <!-- 搜索框 -->
        <el-input
          v-model="permSearch"
          placeholder="搜索权限名称或代码"
          clearable
          style="margin-bottom: 10px"
          @input="filterPerms"
        />
        <!-- 按 app_label 分组展示 -->
        <div class="perm-list">
          <div v-if="!allPermsLoading && !filteredGroups.length" class="perm-empty">暂无权限数据</div>
          <el-skeleton v-if="allPermsLoading" :rows="4" animated />
          <div v-for="group in filteredGroups" :key="group.app_label" class="perm-group">
            <div class="perm-group-title">
              <el-checkbox
                :model-value="isGroupAllChecked(group)"
                :indeterminate="isGroupIndeterminate(group)"
                @change="toggleGroup(group, $event)"
              >
                {{ group.app_label }}
              </el-checkbox>
            </div>
            <div class="perm-items">
              <el-checkbox
                v-for="perm in group.perms"
                :key="perm.id"
                v-model="form.permission_ids"
                :label="perm.id"
                class="perm-item"
              >
                <span class="perm-name">{{ perm.name }}</span>
                <span class="perm-code">{{ perm.codename }}</span>
              </el-checkbox>
            </div>
          </div>
        </div>
        <div class="perm-count">已选 {{ form.permission_ids.length }} 个权限</div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '创建角色' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createGroup, updateGroup, getAllPermissions } from '@/api/admin'
import { useFormErrors } from '@/composables/useFormErrors'

const props = defineProps({
  visible: Boolean,
  editData: { type: Object, default: null },
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
  name: '',
  permission_ids: [],
})
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
}

// ── 权限列表 ────────────────────────────────────────────────────────
const allPerms = ref([])
const allPermsLoading = ref(false)
const permSearch = ref('')
const filteredGroups = ref([])

async function loadAllPermissions() {
  allPermsLoading.value = true
  try {
    const res = await getAllPermissions()
    allPerms.value = res.data ?? []
    applyFilter()
  } finally {
    allPermsLoading.value = false
  }
}

function applyFilter() {
  const q = permSearch.value.trim().toLowerCase()
  // 按 app_label 分组
  const map = {}
  for (const p of allPerms.value) {
    if (q && !p.name.toLowerCase().includes(q) && !p.codename.toLowerCase().includes(q)) continue
    if (!map[p.app_label]) map[p.app_label] = { app_label: p.app_label, perms: [] }
    map[p.app_label].perms.push(p)
  }
  filteredGroups.value = Object.values(map).sort((a, b) => a.app_label.localeCompare(b.app_label))
}

function filterPerms() {
  applyFilter()
}

// 分组全选状态
function isGroupAllChecked(group) {
  return group.perms.every((p) => form.permission_ids.includes(p.id))
}
function isGroupIndeterminate(group) {
  const checked = group.perms.filter((p) => form.permission_ids.includes(p.id)).length
  return checked > 0 && checked < group.perms.length
}
function toggleGroup(group, checked) {
  const ids = group.perms.map((p) => p.id)
  if (checked) {
    const set = new Set([...form.permission_ids, ...ids])
    form.permission_ids = [...set]
  } else {
    form.permission_ids = form.permission_ids.filter((id) => !ids.includes(id))
  }
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      clearServerErrors()
      permSearch.value = ''
      if (props.editData) {
        form.name = props.editData.name ?? ''
        form.permission_ids = props.editData.permission_ids ?? []
      } else {
        form.name = ''
        form.permission_ids = []
      }
      if (!allPerms.value.length) loadAllPermissions()
      else applyFilter()
    }
  },
)

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  clearServerErrors()
  try {
    const payload = { name: form.name, permission_ids: form.permission_ids }
    if (isEdit.value) {
      await updateGroup(props.editData.id, payload)
      ElMessage.success('角色修改成功')
    } else {
      await createGroup(payload)
      ElMessage.success('角色创建成功')
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

<style scoped>
.perm-list {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px 12px;
  max-height: 360px;
  overflow-y: auto;
  width: 100%;
}

.perm-empty {
  color: #909399;
  text-align: center;
  padding: 20px 0;
  font-size: 13px;
}

.perm-group {
  margin-bottom: 10px;
}

.perm-group-title {
  font-weight: 600;
  color: #303133;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 6px;
}

.perm-items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 0;
}

.perm-item {
  width: 50%;
  margin-right: 0 !important;
}

.perm-name {
  font-size: 12px;
  color: #303133;
}

.perm-code {
  font-size: 11px;
  color: #909399;
  margin-left: 4px;
}

.perm-count {
  margin-top: 6px;
  font-size: 12px;
  color: #606266;
}
</style>
