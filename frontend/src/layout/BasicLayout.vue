<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="sidebar-logo" :class="{ 'logo-collapsed': isCollapsed }">
        <img
          src="/logo.png"
          :class="isCollapsed ? 'logo-img-sm' : 'logo-img'"
          alt="logo"
        />
        <Transition name="logo-fade">
          <span v-if="!isCollapsed" class="logo-text">PerceptionPro</span>
        </Transition>
      </div>

      <el-menu
        :default-active="activeMenu"
        background-color="#f0f2f5"
        text-color="#303133"
        active-text-color="#ffffff"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <el-sub-menu v-if="authStore.userInfo?.is_staff" index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/roles">角色管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/versions">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>版本管理</span>
          </template>
          <el-menu-item index="/versions/perception">感知版本</el-menu-item>
          <el-menu-item index="/versions/loc">定位版本</el-menu-item>
          <el-menu-item index="/versions/ctl">控制版本</el-menu-item>
          <el-menu-item index="/versions/sim">仿真版本</el-menu-item>
          <el-menu-item index="/versions/sen">传感器版本</el-menu-item>
          <el-menu-item index="/versions/at">自动化版本</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/data">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>数据管理</span>
          </template>
          <el-menu-item index="/data/sim_project_property">仿真项目数据</el-menu-item>
          <el-menu-item index="/data/sim_common_property">仿真通用数据</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/agv-sim">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>整车仿真测试</span>
          </template>
          <el-menu-item index="/agv-sim/case-map">地图管理</el-menu-item>
          <el-menu-item index="/agv-sim/case-property">资产管理</el-menu-item>
          <el-menu-item index="/agv-sim/common-parameter">通用参数</el-menu-item>
          <el-menu-item index="/agv-sim/case-template">用例模版</el-menu-item>
          <el-menu-item index="/agv-sim/test-task">测试任务</el-menu-item>
          <el-menu-item index="/agv-sim/worker-node">Worker 管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu v-if="authStore.userInfo?.is_staff" index="/get-test">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>感知取货测试</span>
          </template>
          <el-menu-item index="/get-test/target">物体数据</el-menu-item>
          <el-menu-item index="/get-test/agv-body">车体数据</el-menu-item>
          <el-menu-item index="/get-test/common-param">测试通参</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航 -->
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapsed = !isCollapsed">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <!-- 面包屑 -->
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="parentTitle" :to="{ path: parentPath }">{{
              parentTitle
            }}</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar
                size="small"
                :src="authStore.userInfo?.avatar || ''"
                :icon="authStore.userInfo?.avatar ? undefined : UserFilled"
                class="user-avatar"
                @click.stop="triggerAvatarUpload"
              />
              <span class="username">{{ authStore.userInfo?.username ?? '用户' }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <input
            ref="avatarInputRef"
            type="file"
            accept="image/*"
            style="display:none"
            @change="handleAvatarChange"
          />
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </el-container>

  <ChangePasswordDialog v-model:visible="changePwdVisible" />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { uploadAvatar } from '@/api/auth'
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)
const changePwdVisible = ref(false)
const avatarInputRef = ref(null)

// 默认密码未修改时自动弹出修改密码框
watch(
  () => authStore.userInfo?.is_default_password,
  (val) => {
    if (val) changePwdVisible.value = true
  },
  { immediate: true },
)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title)
const parentTitle = computed(() => route.meta?.parentTitle)
const parentPath = computed(() => route.meta?.parentPath)

async function handleCommand(command) {
  if (command === 'logout') {
    await ElMessageBox.confirm('确认退出登录？', '提示', {
      type: 'warning',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
    })
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'changePassword') {
    changePwdVisible.value = true
  }
}

function triggerAvatarUpload() {
  avatarInputRef.value?.click()
}

async function handleAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 3 * 1024 * 1024) {
    ElMessage.error('图片不能超过 3MB')
    e.target.value = ''
    return
  }
  const fd = new FormData()
  fd.append('avatar', file)
  try {
    const res = await uploadAvatar(fd)
    // 同步更新内存中的头像，不必重新拉取 userInfo
    if (authStore.userInfo) authStore.userInfo.avatar = res.data.avatar
    ElMessage.success('头像上传成功')
  } catch {
    // 错误已由拦截器统一提示
  } finally {
    e.target.value = ''
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

.layout-aside {
  background-color: #f0f2f5;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e0e3e8;
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #f0f2f5;
  overflow: hidden;
  flex-shrink: 0;
  padding: 0 12px;
  border-bottom: 1px solid #e0e3e8;
  transition: padding 0.3s;
}

.sidebar-logo.logo-collapsed {
  padding: 0;
  gap: 0;
}

.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: opacity 0.15s ease;
}
.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

.logo-img {
  height: 28px;
  width: 28px;
  object-fit: contain;
  flex-shrink: 0;
}

.logo-img-sm {
  height: 32px;
  width: 32px;
  object-fit: contain;
}

.logo-text {
  color: #303133;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  white-space: nowrap;
}

.logo-icon {
  color: #fff;
  font-size: 20px;
  font-weight: 700;
}

.el-menu {
  border-right: none;
  flex: 1;
}

/* 选中菜单项高亮背景 */
:deep(.el-menu-item.is-active) {
  background-color: #1890ff !important;
}

.layout-header {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #595959;
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: #595959;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-avatar {
  cursor: pointer;
  transition: opacity 0.2s;
}

.user-avatar:hover {
  opacity: 0.8;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #303133;
}

.username {
  font-size: 14px;
}

.layout-main {
  background-color: #f5f7fa;
  overflow-y: auto;
  padding: 20px;
}
</style>
