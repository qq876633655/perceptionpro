import { ref, reactive } from 'vue'

/**
 * 通用分页 composable
 *
 * 用法：
 *   const { pagination, tableData, loading, fetchData, handlePageChange, handleSizeChange }
 *     = usePagination(getVersionList)
 *
 * @param {Function} apiFn - 接受 params 对象，返回 Promise<{data, pagination}>
 * @param {Object} defaultParams - 默认查询参数（筛选条件等）
 */
export function usePagination(apiFn, defaultParams = {}) {
  const loading = ref(false)
  const tableData = ref([])

  const pagination = reactive({
    page: 1,
    page_size: 10,
    total: 0,
    total_pages: 1,
  })

  const filters = reactive({ ...defaultParams })

  async function fetchData(extraParams = {}) {
    loading.value = true
    try {
      const res = await apiFn({
        page: pagination.page,
        page_size: pagination.page_size,
        ...filters,
        ...extraParams,
      })
      tableData.value = res.data ?? []
      if (res.pagination) {
        pagination.total = res.pagination.count
        pagination.total_pages = res.pagination.total_pages
        pagination.page = res.pagination.page
        pagination.page_size = res.pagination.page_size
      }
    } finally {
      loading.value = false
    }
  }

  function handlePageChange(page) {
    pagination.page = page
    fetchData()
  }

  function handleSizeChange(size) {
    pagination.page_size = size
    pagination.page = 1
    fetchData()
  }

  function resetAndFetch(newFilters = {}) {
    Object.assign(filters, newFilters)
    pagination.page = 1
    fetchData()
  }

  return {
    loading,
    tableData,
    pagination,
    filters,
    fetchData,
    handlePageChange,
    handleSizeChange,
    resetAndFetch,
  }
}
