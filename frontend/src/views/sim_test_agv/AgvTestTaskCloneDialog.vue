<template>
  <el-dialog v-model="visible" title="重发测试任务" width="620px"
    :close-on-click-modal="false" @closed="handleClosed">

    <!-- 原任务信息（只读展示） -->
    <el-descriptions :column="1" border size="small" style="margin-bottom:16px">
      <el-descriptions-item label="测试用例">
        <span class="file-name">{{ caseFileName }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="感知版本">
        <span class="file-name">{{ fileBasename(row?.per_version) || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="定位版本">
        <span class="file-name">{{ fileBasename(row?.loc_version) || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="控制版本">
        <span class="file-name">{{ fileBasename(row?.ctl_version) || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="整车版本">
        <span class="file-name">{{ fileBasename(row?.agv_version) || '-' }}</span>
      </el-descriptions-item>
    </el-descriptions>

    <el-divider content-position="left" style="margin:8px 0 16px">可修改字段</el-divider>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="使用资产版本" prop="sim_test_version" :error="serverErrors.sim_test_version">
            <el-select v-model="form.sim_test_version" placeholder="请选择" filterable style="width:100%">
              <el-option v-for="v in simTestVersions" :key="v" :label="v" :value="v" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="任务队列" prop="queue_name" :error="serverErrors.queue_name">
            <el-input v-model="form.queue_name" clearable @input="form.target_worker = ''" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="恢复默认版本" :error="serverErrors.recovery_default_version">
            <el-select v-model="form.recovery_default_version" style="width:100%">
              <el-option label="True" value="True" />
              <el-option label="False" value="False" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="待测基线版本" :error="serverErrors.base_version">
            <el-input v-model="form.base_version" placeholder="可选" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="指定 Worker" prop="target_worker" :error="serverErrors.target_worker">
            <el-select v-model="form.target_worker" placeholder="可选" clearable filterable style="width:100%">
              <el-option
                v-for="w in filteredWorkers"
                :key="w.hostname"
                :label="`${w.hostname} — ${workerStatusLabel(w.status)}`"
                :value="w.hostname"
                :disabled="w.status === 'offline'"
              />
            </el-select>
            <div v-if="form.queue_name && filteredWorkers.length === 0" style="font-size:12px;color:#e6a23c;margin-top:4px">
              当前队列无在线 Worker，任务将等待 Worker 上线后执行
            </div>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确认重发</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { cloneAgvTestTask, getWorkerStatus, getCasePropertySimTestVersions } from '@/api/sim_test_agv'
import { useFormErrors } from '@/composables/useFormErrors'

const props = defineProps({
  visible: Boolean,
  row: { type: Object, default: null },
})
const emit = defineEmits(['update:visible', 'success'])

const visible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v),
})

const formRef = ref(null)
const submitting = ref(false)
const workerList = ref([])
const simTestVersions = ref([])
const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()

const form = reactive({
  sim_test_version: '',
  queue_name: '',
  recovery_default_version: 'False',
  base_version: '',
  target_worker: '',
})

const rules = {
  sim_test_version: [{ required: true, message: '请选择使用资产版本', trigger: 'change' }],
  queue_name: [{ required: true, message: '请输入任务队列', trigger: 'blur' }],
  target_worker: [{
    validator: (rule, val, cb) => {
      if (!val) return cb()  // 不填则广播，不校验
      if (!workerList.value.length) return cb()  // 列表尚未加载，跳过校验
      const worker = workerList.value.find(w => w.hostname === val)
      if (!worker) return cb(new Error(`Worker「${val}」不在当前在线列表中`))
      if (worker.status === 'offline') return cb(new Error(`Worker「${val}」当前离线，无法派发`))
      cb()
    },
    trigger: 'change',
  }],
}

// 与新建弹窗一致——按 queue_name 过滤在线 worker
const filteredWorkers = computed(() => {
  if (!form.queue_name) return workerList.value.filter(w => w.status !== 'offline')
  return workerList.value.filter(w =>
    w.status !== 'offline' && w.queues.some(q => q === form.queue_name)
  )
})

const WORKER_STATUS = { online: '空闲', busy: '执行中', offline: '离线' }
function workerStatusLabel(s) { return WORKER_STATUS[s] ?? s }

function fileBasename(url) {
  if (!url) return ''
  try {
    return decodeURIComponent(url.split('/').pop())
  } catch {
    return url.split('/').pop()
  }
}

const caseFileName = computed(() => fileBasename(props.row?.agv_case_file))

watch(() => props.visible, async val => {
  if (!val) return
  clearServerErrors()
  // 用原任务数据初始化表单
  Object.assign(form, {
    sim_test_version: props.row?.sim_test_version ?? '',
    queue_name: props.row?.queue_name ?? '',
    recovery_default_version: props.row?.recovery_default_version ?? 'False',
    base_version: props.row?.base_version ?? '',
    target_worker: props.row?.target_worker ?? '',
  })
  try {
    const [verRes, workerRes] = await Promise.all([
      getCasePropertySimTestVersions(),
      getWorkerStatus(),
    ])
    simTestVersions.value = verRes.data ?? []
    workerList.value = Array.isArray(workerRes) ? workerRes : (workerRes.data ?? [])
  } catch {
    simTestVersions.value = []
    workerList.value = []
  }
})

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await cloneAgvTestTask(props.row.id, {
      sim_test_version: form.sim_test_version,
      queue_name: form.queue_name,
      recovery_default_version: form.recovery_default_version,
      base_version: form.base_version || '',
      target_worker: form.target_worker || '',
    })
    ElMessage.success('重发成功')
    visible.value = false
    emit('success')
  } catch (err) {
    applyServerErrors(err)
  } finally {
    submitting.value = false
  }
}

function handleClosed() {
  // 若动画结束前弹框已被重新打开，跳过重置，避免覆盖新数据
  if (visible.value) return
  formRef.value?.resetFields()
  clearServerErrors()
}
</script>

<style scoped>
.file-name {
  word-break: break-all;
  white-space: normal;
}
</style>
