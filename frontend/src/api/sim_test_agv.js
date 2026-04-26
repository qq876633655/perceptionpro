import request from '@/utils/request'
import { downloadBlob } from '@/utils/request'

// ════════════════════════════════════════════════════════════
// CaseMap  /api/at_case_map/
// ════════════════════════════════════════════════════════════

export function getCaseMapList(params) {
  return request({ url: '/at_case_map/', method: 'get', params })
}
export function createCaseMap(data) {
  return request({ url: '/at_case_map/', method: 'post', data })
}
export function updateCaseMap(id, data) {
  return request({ url: `/at_case_map/${id}/`, method: 'patch', data })
}
export function deleteCaseMap(id) {
  return request({ url: `/at_case_map/${id}/`, method: 'delete' })
}
export function batchDeleteCaseMaps(ids) {
  return request({ url: '/at_case_map/batch_delete/', method: 'post', data: { ids } })
}
export function getCaseMapCreators() {
  return request({ url: '/at_case_map/creators/', method: 'get' })
}
/** 获取所有地图选项（用于 CaseProperty 下拉） */
export function getCaseMapOptions() {
  return request({ url: '/at_case_map/', method: 'get', params: { page: 1, page_size: 9999 } })
}

// ════════════════════════════════════════════════════════════
// CaseProperty  /api/at_case_property/
// ════════════════════════════════════════════════════════════

export function getCasePropertyList(params) {
  return request({ url: '/at_case_property/', method: 'get', params })
}
export function createCaseProperty(data) {
  return request({ url: '/at_case_property/', method: 'post', data })
}
export function updateCaseProperty(id, data) {
  return request({ url: `/at_case_property/${id}/`, method: 'patch', data })
}
export function deleteCaseProperty(id) {
  return request({ url: `/at_case_property/${id}/`, method: 'delete' })
}
export function batchDeleteCaseProperties(ids) {
  return request({ url: '/at_case_property/batch_delete/', method: 'post', data: { ids } })
}
export function batchCopyCaseProperties(ids, sim_test_version) {
  return request({ url: '/at_case_property/batch_copy/', method: 'post', data: { ids, sim_test_version } })
}
export function getCasePropertyCreators() {
  return request({ url: '/at_case_property/creators/', method: 'get' })
}
/** 上传文件夹到指定字段路径。data 应为 FormData（含 field_name, files[], paths[]） */
export function uploadCasePropertyFolder(id, data) {
  return request({ url: `/at_case_property/${id}/upload_folder_field/`, method: 'post', data })
}
/** 下载指定字段的文件夹（打包为 zip） */
export function downloadCasePropertyFolder(id, fieldName, zipName) {
  return downloadBlob(
    `/at_case_property/${id}/download_folder_field/`,
    { field_name: fieldName },
    zipName || `${fieldName}.zip`,
  )
}
/** 返回 CaseProperty.sim_test_version 去重列表（供 AgvTestTask 下拉） */
export function getCasePropertySimTestVersions() {
  return request({ url: '/at_case_property/sim_test_versions/', method: 'get' })
}
/** 返回 CaseProperty 各字段已有值去重列表（供筛选器/datalist）*/
export function getCasePropertyChoices() {
  return request({ url: '/at_case_property/choices/', method: 'get' })
}

// ════════════════════════════════════════════════════════════
// SchemeCommonParameter  /api/at_common_parameter/
// ════════════════════════════════════════════════════════════

export function getCommonParameterList(params) {
  return request({ url: '/at_common_parameter/', method: 'get', params })
}
export function createCommonParameter(data) {
  return request({ url: '/at_common_parameter/', method: 'post', data })
}
export function updateCommonParameter(id, data) {
  return request({ url: `/at_common_parameter/${id}/`, method: 'patch', data })
}
export function deleteCommonParameter(id) {
  return request({ url: `/at_common_parameter/${id}/`, method: 'delete' })
}
export function batchDeleteCommonParameters(ids) {
  return request({ url: '/at_common_parameter/batch_delete/', method: 'post', data: { ids } })
}
export function batchCopyCommonParameters(items) {
  return request({ url: '/at_common_parameter/batch_copy/', method: 'post', data: { items } })
}
export function getCommonParameterCreators() {
  return request({ url: '/at_common_parameter/creators/', method: 'get' })
}
/** 返回 SchemeCommonParameter 各字段已有值去重列表 */
export function getCommonParameterChoices() {
  return request({ url: '/at_common_parameter/choices/', method: 'get' })
}

// ════════════════════════════════════════════════════════════
// CaseTemplate  /api/at_case_template/
// ════════════════════════════════════════════════════════════

export function getCaseTemplateList(params) {
  return request({ url: '/at_case_template/', method: 'get', params })
}
export function createCaseTemplate(data) {
  return request({ url: '/at_case_template/', method: 'post', data })
}
export function updateCaseTemplate(id, data) {
  return request({ url: `/at_case_template/${id}/`, method: 'patch', data })
}
export function deleteCaseTemplate(id) {
  return request({ url: `/at_case_template/${id}/`, method: 'delete' })
}
export function batchDeleteCaseTemplates(ids) {
  return request({ url: '/at_case_template/batch_delete/', method: 'post', data: { ids } })
}
export function getCaseTemplateCreators() {
  return request({ url: '/at_case_template/creators/', method: 'get' })
}
/** 返回 CaseTemplate 各字段已有值去重列表 */
export function getCaseTemplateChoices() {
  return request({ url: '/at_case_template/choices/', method: 'get' })
}

// ════════════════════════════════════════════════════════════
// AgvTestTask  /api/at_test_task/
// ════════════════════════════════════════════════════════════

export function getAgvTestTaskList(params) {
  return request({ url: '/at_test_task/', method: 'get', params })
}
export function createAgvTestTask(data) {
  return request({ url: '/at_test_task/', method: 'post', data })
}
export function deleteAgvTestTask(id) {
  return request({ url: `/at_test_task/${id}/`, method: 'delete' })
}
export function batchDeleteAgvTestTasks(ids) {
  return request({ url: '/at_test_task/batch_delete/', method: 'post', data: { ids } })
}
export function cancelAgvTestTask(id) {
  return request({ url: `/at_test_task/${id}/cancel/`, method: 'post' })
}
export function getAgvTestTaskCreators() {
  return request({ url: '/at_test_task/creators/', method: 'get' })
}
