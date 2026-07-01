<template>
  <div class="app-layout">
    <AppHeader :collapsed="sidebarCollapsed" @toggle-sidebar="toggleSidebar" />
    <div class="layout-container">
      <AppSidebar
        v-if="!isMobile"
        :collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
      />
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <AppFooter v-if="!isMobile" />
    <div v-if="isMobile" class="mobile-tabbar">
      <el-menu
        :default-active="activeMenu"
        class="mobile-menu"
        mode="horizontal"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/detect">
          <el-icon><Search /></el-icon>
          <span>检测</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI问答</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>历史</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>我的</span>
        </el-menu-item>
      </el-menu>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, ChatDotRound, Clock, User } from '@element-plus/icons-vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'

const route = useRoute()
const router = useRouter()

const sidebarCollapsed = ref(false)
const isMobile = ref(false)

const activeMenu = computed(() => route.path)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleMenuSelect(index) {
  router.push(index)
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
.app-layout {
  min-height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
}

.layout-container {
  display: flex;
  flex: 1;
  padding-top: 60px;
  position: relative;
  z-index: 10;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-x: hidden;
  min-height: calc(100vh - 60px - 60px);
}

.mobile-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border);
  padding-bottom: env(safe-area-inset-bottom);
}

.mobile-menu {
  border-bottom: none;
  justify-content: space-around;
}

.mobile-menu .el-menu-item {
  flex-direction: column;
  height: 60px;
  padding: 8px 16px;
  line-height: 1.2;
}

.mobile-menu .el-menu-item .el-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.mobile-menu .el-menu-item span {
  font-size: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
    padding-bottom: 80px;
    min-height: calc(100vh - 60px);
  }
}
</style>
