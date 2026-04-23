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

export function createSimProjectProperty(data) {
  return request({ url: '/sim_project_property/', method: 'post', data })
}

export function updateSimProjectProperty(id, data) {
  return request({ url: `/sim_project_property/${id}/`, method: 'patch', data })
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

export function createSimCommonProperty(data) {
  return request({ url: '/sim_common_property/', method: 'post', data })
}

export function updateSimCommonProperty(id, data) {
  return request({ url: `/sim_common_property/${id}/`, method: 'patch', data })
}

export function deleteSimCommonProperty(id) {
  return request({ url: `/sim_common_property/${id}/`, method: 'delete' })
}

export function batchDeleteSimCommonProperties(ids) {
  return request({ url: '/sim_common_property/batch_delete/', method: 'post', data: { ids } })
}
