<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑资产' : '新建资产'" width="700px"
    :close-on-click-modal="false" @closed="handleClosed">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="资产版本" prop="sim_test_version" :error="serverErrors.sim_test_version">
            <el-input v-if="isEdit" v-model="form.sim_test_version" disabled />
            <el-input v-else v-model="form.sim_test_version" list="cp-version-list" placeholder="请输入或选择" clearable />
            <datalist id="cp-version-list">
              <option v-for="v in fieldChoices.sim_test_version" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试车型" prop="sim_test_vehicle" :error="serverErrors.sim_test_vehicle">
            <el-input v-if="isEdit" v-model="form.sim_test_vehicle" disabled />
            <el-input v-else v-model="form.sim_test_vehicle" list="cp-vehicle-list" placeholder="请输入或选择" clearable />
            <datalist id="cp-vehicle-list">
              <option v-for="v in fieldChoices.sim_test_vehicle" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试方案" prop="sim_scheme_name" :error="serverErrors.sim_scheme_name">
            <el-input v-if="isEdit" v-model="form.sim_scheme_name" disabled />
            <el-input v-else v-model="form.sim_scheme_name" list="cp-scheme-list" placeholder="请输入或选择" clearable />
            <datalist id="cp-scheme-list">
              <option v-for="v in fieldChoices.sim_scheme_name" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="测试模块" prop="test_module" :error="serverErrors.test_module">
            <el-input v-model="form.test_module" list="cp-module-list" placeholder="请输入或选择" clearable />
            <datalist id="cp-module-list">
              <option v-for="v in fieldChoices.test_module" :key="v" :value="v" />
            </datalist>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="分区名称" :error="serverErrors.map">
            <el-select v-model="form.map" placeholder="可选" clearable filterable style="width:100%">
              <el-option v-for="m in caseMapOptions" :key="m.id" :label="m.district_name" :value="m.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="资产状态" prop="property_status" :error="serverErrors.property_status">
            <el-select v-model="form.property_status" style="width:100%">
              <el-option label="正常" value="正常" />
              <el-option label="维护" value="维护" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 文件字段 -->
      <el-form-item label="robotune备份" prop="backup_file_guard" :error="serverErrors.backup_file">
        <FileUploader ref="backupFileRef" :tip="isEdit && form.backup_file_url ? '已上传，可重新上传覆盖' : '请上传备份文件'"
          @change="f => { selectedBackupFile = f; form.backup_file_guard = f?.name ?? null; formRef?.validateField('backup_file_guard') }" />
      </el-form-item>

      <el-form-item label="wbt文件" prop="wbt_file_guard" :error="serverErrors.wbt_file">
        <FileUploader ref="wbtFileRef" :tip="isEdit && form.wbt_file_url ? '已上传，可重新上传覆盖' : '请上传wbt文件'"
          @change="f => { selectedWbtFile = f; form.wbt_file_guard = f?.name ?? null; formRef?.validateField('wbt_file_guard') }" />
      </el-form-item>

      <el-divider content-position="left">路径文件夹（上传后自动写入路径）</el-divider>

      <el-form-item label="lastagvpose *" prop="lastagvpose_guard">
        <div class="folder-row">
          <span class="folder-path">{{ form.lastagvpose_path || '（未上传）' }}</span>
          <input :ref="el => (folderInputRefs.lastagvpose_path = el)" type="file" webkitdirectory multiple
            style="display:none" @change="e => { handleFolderSelect(e, 'lastagvpose_path'); formRef?.validateField('lastagvpose_guard') }" />
          <el-button size="small" @click="folderInputRefs.lastagvpose_path?.click()">选择文件夹</el-button>
          <el-button v-if="isEdit && form.lastagvpose_path" size="small" type="primary"
            :loading="!!downloading.lastagvpose_path"
            @click="handleFolderDownload('lastagvpose_path', 'lastagvpose')">下载</el-button>
          <el-tag v-if="pendingFolders.lastagvpose_path" type="success" size="small" style="margin-left:4px">
            待上传: {{ pendingFolders.lastagvpose_path.root }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item v-for="field in otherFolderFields" :key="field.key" :label="field.label">
        <div class="folder-row">
          <span class="folder-path">{{ form[field.key] || '（未上传）' }}</span>
          <input :ref="el => (folderInputRefs[field.key] = el)" type="file" webkitdirectory multiple
            style="display:none" @change="e => handleFolderSelect(e, field.key)" />
          <el-button size="small" @click="folderInputRefs[field.key]?.click()">选择文件夹</el-button>
          <el-button v-if="isEdit && form[field.key]" size="small" type="primary"
            :loading="!!downloading[field.key]"
            @click="handleFolderDownload(field.key, field.label)">下载</el-button>
          <el-tag v-if="pendingFolders[field.key]" type="success" size="small" style="margin-left:4px">
            待上传: {{ pendingFolders[field.key].root }}
          </el-tag>
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
import { ref, reactive, computed, watch, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { createCaseProperty, updateCaseProperty, getCaseMapOptions, uploadCasePropertyFolder, downloadCasePropertyFolder, getCasePropertyChoices } from '@/api/sim_test_agv'
import { useFormErrors } from '@/composables/useFormErrors'
import FileUploader from '@/components/FileUploader.vue'

const props = defineProps({ visible: Boolean, editData: { type: Object, default: null } })
const emit = defineEmits(['update:visible', 'success'])
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.editData)

const formRef = ref(null)
const backupFileRef = ref(null)
const wbtFileRef = ref(null)
const submitting = ref(false)
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

let selectedBackupFile = null
let selectedWbtFile = null

const form = reactive({
  sim_test_version: '', sim_test_vehicle: '', sim_scheme_name: '', test_module: '',
  map: null, property_status: '正常',
  lastagvpose_path: '', mapping_ecal_path: '', extend_mapping_ecal_path: '', ply_path: '',
  backup_file_url: '', wbt_file_url: '',
  backup_file_guard: null, wbt_file_guard: null, lastagvpose_guard: null,
})

const rules = {
  sim_test_version: [{ required: true, message: '请输入资产版本', trigger: 'blur' }],
  sim_test_vehicle: [{ required: true, message: '请输入测试车型', trigger: 'blur' }],
  sim_scheme_name: [{ required: true, message: '请输入测试方案', trigger: 'blur' }],
  test_module: [{ required: true, message: '请输入测试模块', trigger: 'blur' }],
  property_status: [{ required: true, message: '请选择资产状态', trigger: 'change' }],
  lastagvpose_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !pendingFolders.lastagvpose_path && !form.lastagvpose_path)
        cb(new Error('请上传 lastagvpose 文件夹'))
      else cb()
    },
    trigger: 'change',
  }],
  backup_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedBackupFile) cb(new Error('请上传 robotune 备份文件'))
      else cb()
    },
    trigger: 'change',
  }],
  wbt_file_guard: [{
    required: true,
    validator: (rule, val, cb) => {
      if (!isEdit.value && !selectedWbtFile) cb(new Error('请上传 wbt 文件'))
      else cb()
    },
    trigger: 'change',
  }],
}

// ── 地图选项 & 字段 choices ──────────────────────────────────────────
const caseMapOptions = ref([])
const fieldChoices = reactive({ sim_test_version: [], sim_test_vehicle: [], sim_scheme_name: [], test_module: [] })

watch(() => props.visible, async val => {
  if (!val) return
  clearServerErrors()
  selectedBackupFile = null
  selectedWbtFile = null
  backupFileRef.value?.reset?.()
  wbtFileRef.value?.reset?.()
  Object.keys(pendingFolders).forEach(k => delete pendingFolders[k])

    try {
      const mapRes = await getCaseMapOptions()
      caseMapOptions.value = mapRes.data ?? []
    } catch { caseMapOptions.value = [] }
    try {
      const chRes = await getCasePropertyChoices()
      const ch = chRes.data ?? chRes
      Object.assign(fieldChoices, ch)
    } catch {}

  if (props.editData) {
    const d = props.editData
    Object.assign(form, {
      sim_test_version: d.sim_test_version,
      sim_test_vehicle: d.sim_test_vehicle,
      sim_scheme_name: d.sim_scheme_name,
      test_module: d.test_module,
      map: d.map ?? null,
      property_status: d.property_status || '正常',
      lastagvpose_path: d.lastagvpose_path || '',
      mapping_ecal_path: d.mapping_ecal_path || '',
      extend_mapping_ecal_path: d.extend_mapping_ecal_path || '',
      ply_path: d.ply_path || '',
      backup_file_url: d.backup_file || '',
      wbt_file_url: d.wbt_file || '',
      backup_file_guard: d.backup_file ? 'existing' : null,
      wbt_file_guard: d.wbt_file ? 'existing' : null,
      lastagvpose_guard: d.lastagvpose_path ? 'existing' : null,
    })
  } else {
    Object.assign(form, {
      sim_test_version: '', sim_test_vehicle: '', sim_scheme_name: '', test_module: '',
      map: null, property_status: '正常',
      lastagvpose_path: '', mapping_ecal_path: '', extend_mapping_ecal_path: '', ply_path: '',
      backup_file_url: '', wbt_file_url: '', backup_file_guard: null, wbt_file_guard: null, lastagvpose_guard: null,
    })
  }
})

// ── 文件夹上传 ──────────────────────────────────────────────────────
const otherFolderFields = [
  { key: 'mapping_ecal_path', label: '自动建图ecal' },
  { key: 'extend_mapping_ecal_path', label: '扩展建图ecal' },
  { key: 'ply_path', label: '感知模版' },
]
const folderInputRefs = reactive({})
const pendingFolders = reactive({})  // { fieldKey: { files: [], paths: [], root: '' } }
const downloading = reactive({})

function handleFolderSelect(event, fieldKey) {
  const files = Array.from(event.target.files)
  if (!files.length) return
  const paths = files.map(f => f.webkitRelativePath || f.name)
  const root = paths[0].split('/')[0]
  pendingFolders[fieldKey] = { files, paths, root }
  if (fieldKey === 'lastagvpose_path') form.lastagvpose_guard = root
  // 清空 input 以允许重新选择同一文件夹
  event.target.value = ''
}

async function handleFolderDownload(fieldKey, label) {
  downloading[fieldKey] = true
  try {
    await downloadCasePropertyFolder(props.editData.id, fieldKey, `${label}.zip`)
  } catch {
    ElMessage.error('下载失败')
  } finally {
    downloading[fieldKey] = false
  }
}

// ── 提交 ────────────────────────────────────────────────────────────
async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  let savedId = props.editData?.id
  try {
    const fd = new FormData()
    fd.append('sim_test_version', form.sim_test_version)
    fd.append('sim_test_vehicle', form.sim_test_vehicle)
    fd.append('sim_scheme_name', form.sim_scheme_name)
    fd.append('test_module', form.test_module)
    fd.append('property_status', form.property_status)
    if (form.map != null) fd.append('map', form.map)
    if (selectedBackupFile) fd.append('backup_file', selectedBackupFile)
    if (selectedWbtFile) fd.append('wbt_file', selectedWbtFile)

    if (isEdit.value) {
      await updateCaseProperty(savedId, fd)
    } else {
      const res = await createCaseProperty(fd)
      savedId = res.data?.id ?? res.id
    }

    // 上传待上传的文件夹（全部 4 个字段）
    const allFolderKeys = ['lastagvpose_path', 'mapping_ecal_path', 'extend_mapping_ecal_path', 'ply_path']
    for (const key of allFolderKeys) {
      const pending = pendingFolders[key]
      if (!pending) continue
      const ffd = new FormData()
      ffd.append('field_name', key)
      pending.files.forEach((f, i) => {
        ffd.append('files', f)
        ffd.append('paths', pending.paths[i])
      })
      await uploadCasePropertyFolder(savedId, ffd)
    }

    ElMessage.success(isEdit.value ? '修改成功' : '创建成功')
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
.folder-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.folder-path { font-size: 12px; color: #606266; min-width: 120px; word-break: break-all; }
</style>
