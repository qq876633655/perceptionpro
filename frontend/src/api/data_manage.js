import request from '@/utils/request'

// ════════════════════════════════════════════════════════════════════
// SimProjectProperty  /api/sim_project_property/
// 字段：uid / apply_project / project_property / property_desc /
//       property_tag / creator
// ════════════════════════════════════════════════════════════════════

export function getSimProjectPropertyList(params) {
  return request({ url: '/sim_project_property/', method: 'get', params })
}

export function getSimProjectPropertyCreators() {
  return request({ url: '/sim_project_property/creators/', method: 'get' })
}

export function createSimProjectProperty(data, onProgress) {
  return request({
    url: '/sim_project_property/', method: 'post', data,
    ...(onProgress && { onUploadProgress: (e) => e.total && onProgress(Math.round(e.loaded * 100 / e.total)) }),
  })
}

export function updateSimProjectProperty(id, data, onProgress) {
  return request({
    url: `/sim_project_property/${id}/`, method: 'patch', data,
    ...(onProgress && { onUploadProgress: (e) => e.total && onProgress(Math.round(e.loaded * 100 / e.total)) }),
  })
}

export function deleteSimProjectProperty(id) {
  return request({ url: `/sim_project_property/${id}/`, method: 'delete' })
}

export function batchDeleteSimProjectProperties(ids) {
  return request({ url: '/sim_project_property/batch_delete/', method: 'post', data: { ids } })
}

// ════════════════════════════════════════════════════════════════════
// SimCommonProperty  /api/sim_common_property/
// 字段：uid / versions / common_property / property_desc / property_tag
// ════════════════════════════════════════════════════════════════════

export function getSimCommonPropertyList(params) {
  return request({ url: '/sim_common_property/', method: 'get', params })
}

export function getSimCommonPropertyCreators() {
  return request({ url: '/sim_common_property/creators/', method: 'get' })
}

export function createSimCommonProperty(data, onProgress) {
  return request({
    url: '/sim_common_property/', method: 'post', data,
    ...(onProgress && { onUploadProgress: (e) => e.total && onProgress(Math.round(e.loaded * 100 / e.total)) }),
  })
}

export function updateSimCommonProperty(id, data, onProgress) {
  return request({
    url: `/sim_common_property/${id}/`, method: 'patch', data,
    ...(onProgress && { onUploadProgress: (e) => e.total && onProgress(Math.round(e.loaded * 100 / e.total)) }),
  })
}

export function deleteSimCommonProperty(id) {
  return request({ url: `/sim_common_property/${id}/`, method: 'delete' })
}

export function batchDeleteSimCommonProperties(ids) {
  return request({ url: '/sim_common_property/batch_delete/', method: 'post', data: { ids } })
}
