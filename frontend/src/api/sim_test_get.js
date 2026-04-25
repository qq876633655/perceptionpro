import request from '@/utils/request'

// ════════════════════════════════════════════════════════════
// GetTestTarget  /api/gt_test_target/
// ════════════════════════════════════════════════════════════

export function getGetTestTargetList(params) {
  return request({ url: '/gt_test_target/', method: 'get', params })
}
export function createGetTestTarget(data) {
  return request({ url: '/gt_test_target/', method: 'post', data })
}
export function updateGetTestTarget(id, data) {
  return request({ url: `/gt_test_target/${id}/`, method: 'patch', data })
}
export function deleteGetTestTarget(id) {
  return request({ url: `/gt_test_target/${id}/`, method: 'delete' })
}
export function batchDeleteGetTestTargets(ids) {
  return request({ url: '/gt_test_target/batch_delete/', method: 'post', data: { ids } })
}
export function getGetTestTargetCreators() {
  return request({ url: '/gt_test_target/creators/', method: 'get' })
}

// ════════════════════════════════════════════════════════════
// AgvBody  /api/gt_agv_body/
// ════════════════════════════════════════════════════════════

export function getAgvBodyList(params) {
  return request({ url: '/gt_agv_body/', method: 'get', params })
}
export function createAgvBody(data) {
  return request({ url: '/gt_agv_body/', method: 'post', data })
}
export function updateAgvBody(id, data) {
  return request({ url: `/gt_agv_body/${id}/`, method: 'patch', data })
}
export function deleteAgvBody(id) {
  return request({ url: `/gt_agv_body/${id}/`, method: 'delete' })
}
export function batchDeleteAgvBodies(ids) {
  return request({ url: '/gt_agv_body/batch_delete/', method: 'post', data: { ids } })
}
export function getAgvBodyCreators() {
  return request({ url: '/gt_agv_body/creators/', method: 'get' })
}

// ════════════════════════════════════════════════════════════
// GetTestCommonParameter  /api/gt_common_param/
// ════════════════════════════════════════════════════════════

export function getGetTestCommonParamList(params) {
  return request({ url: '/gt_common_param/', method: 'get', params })
}
export function createGetTestCommonParam(data) {
  return request({ url: '/gt_common_param/', method: 'post', data })
}
export function updateGetTestCommonParam(id, data) {
  return request({ url: `/gt_common_param/${id}/`, method: 'patch', data })
}
export function deleteGetTestCommonParam(id) {
  return request({ url: `/gt_common_param/${id}/`, method: 'delete' })
}
export function batchDeleteGetTestCommonParams(ids) {
  return request({ url: '/gt_common_param/batch_delete/', method: 'post', data: { ids } })
}
export function getGetTestCommonParamCreators() {
  return request({ url: '/gt_common_param/creators/', method: 'get' })
}
export function getGetTestCommonParamChoices() {
  return request({ url: '/gt_common_param/choices/', method: 'get' })
}
