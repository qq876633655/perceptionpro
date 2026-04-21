import request from '@/utils/request'

// ════════════════════════════════════════════════════════════════════
// PerVersion  /api/per_version/
// 模型字段：version_num / versions_type / apply_project /
//           dev_test_result / database_file / test_result /
//           test_verdict / version_file / env(FK→PerEnv)
// ════════════════════════════════════════════════════════════════════

/**
 * 版本列表（分页 + 筛选）
 * @param {Object} params - { page, page_size, version_num, test_result, apply_project, ... }
 */
export function getVersionList(params) {
  return request({ url: '/per_version/', method: 'get', params })
}

/** 版本详情 */
export function getVersion(id) {
  return request({ url: `/per_version/${id}/`, method: 'get' })
}

/** 创建版本（不含 test_result / test_verdict） */
export function createVersion(data) {
  return request({ url: '/per_version/', method: 'post', data })
}

/**
 * 更新版本（禁止修改 version_num / version_file）
 * 可更新：versions_type / apply_project / dev_test_result /
 *         database_file / test_result / test_verdict / env
 */
export function updateVersion(id, data) {
  return request({ url: `/per_version/${id}/`, method: 'patch', data })
}

/** 删除单个版本 */
export function deleteVersion(id) {
  return request({ url: `/per_version/${id}/`, method: 'delete' })
}

/**
 * 批量删除版本
 * @param {number[]} ids
 */
export function batchDeleteVersions(ids) {
  return request({
    url: '/per_version/batch_delete/',
    method: 'post',
    data: { ids },
  })
}

/**
 * 上传版本文件 version_file（multipart/form-data）
 * @param {number} id - PerVersion ID
 * @param {FormData} formData  - 含字段 version_file
 * @param {Function} onProgress - (percent: number) => void
 */
export function uploadVersionFile(id, formData, onProgress) {
  return request({
    url: `/per_version/${id}/`,
    method: 'patch',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
}

/**
 * 上传数据库文件 database_file（multipart/form-data，仅支持 .db）
 * @param {number} id - PerVersion ID
 * @param {FormData} formData  - 含字段 database_file
 * @param {Function} onProgress
 */
export function uploadDatabaseFile(id, formData, onProgress) {
  return request({
    url: `/per_version/${id}/`,
    method: 'patch',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
}

// ════════════════════════════════════════════════════════════════════
// PerEnv  /api/per_env/
// 模型字段：env_name / apply_project / env_note / env_file
// ════════════════════════════════════════════════════════════════════

/** 环境列表 */
export function getEnvList(params) {
  return request({ url: '/per_env/', method: 'get', params })
}

/** 环境详情 */
export function getEnv(id) {
  return request({ url: `/per_env/${id}/`, method: 'get' })
}

/** 创建环境 */
export function createEnv(data) {
  return request({ url: '/per_env/', method: 'post', data })
}

/** 更新环境 */
export function updateEnv(id, data) {
  return request({ url: `/per_env/${id}/`, method: 'patch', data })
}

/** 删除环境 */
export function deleteEnv(id) {
  return request({ url: `/per_env/${id}/`, method: 'delete' })
}

/**
 * 上传环境文件 env_file（multipart/form-data）
 * @param {number} id - PerEnv ID
 * @param {FormData} formData  - 含字段 env_file
 * @param {Function} onProgress
 */
export function uploadEnvFile(id, formData, onProgress) {
  return request({
    url: `/per_env/${id}/`,
    method: 'patch',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
}
