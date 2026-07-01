<template>
  <header class="app-header glass-navbar">
    <div class="header-left">
      <button v-if="!isMobile" class="collapse-btn" @click="$emit('toggle-sidebar')">
        <el-icon :size="20">
          <Fold v-if="!collapsed" />
          <Expand v-else />
        </el-icon>
      </button>
      <div class="logo">
        <span class="logo-text font-logo">YOLO DETECT</span>
      </div>
    </div>
    <div class="header-right">
      <ThemeToggle />
      <el-dropdown trigger="click" class="user-dropdown" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="36" class="user-avatar">
            {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
          </el-avatar>
          <span v-if="!isMobile" class="username">{{ userStore.userInfo?.username || '用户' }}</span>
          <el-icon class="arrow-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Fold, Expand, ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { useUserStore } from '@/store/modules/user'

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-sidebar'])

const router = useRouter()
const userStore = useUserStore()
const isMobile = ref(false)

function handleCommand(command) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  }
}

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-accent);
}

.logo {
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-accent);
  text-shadow: 0 0 10px var(--color-accent-glow);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px;
  border-radius: 8px;
  transition: background 0.3s ease;
}

.user-info:hover {
  background: var(--color-bg-tertiary);
}

.user-avatar {
  background: var(--color-accent);
  color: #fff;
  font-weight: 600;
}

.username {
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.arrow-icon {
  color: var(--color-text-tertiary);
  font-size: 12px;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }

  .logo-text {
    font-size: 16px;
  }
}
</style>
