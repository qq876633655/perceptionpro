import { ref } from 'vue'

/**
 * 处理后端 ValidationError 返回的字段级错误
 *
 * 后端错误格式：
 * {
 *   "code": 1001,
 *   "msg": "参数校验失败",
 *   "data": [{ "field": "version_num", "message": "该版本号已存在" }]
 * }
 *
 * 用法：
 *   const { serverErrors, applyServerErrors, clearServerErrors } = useFormErrors()
 *   // el-form-item 的 error 属性绑定：:error="serverErrors.version_num"
 */
export function useFormErrors() {
  // { fieldName: errorMessage }
  const serverErrors = ref({})

  /**
   * 将后端 errors 数组写入 serverErrors
   * @param {Array<{field: string, message: string}>} errors
   */
  function applyServerErrors(errors) {
    serverErrors.value = {}
    if (Array.isArray(errors)) {
      errors.forEach(({ field, message }) => {
        serverErrors.value[field] = message
      })
    }
  }

  function clearServerErrors() {
    serverErrors.value = {}
  }

  return { serverErrors, applyServerErrors, clearServerErrors }
}
