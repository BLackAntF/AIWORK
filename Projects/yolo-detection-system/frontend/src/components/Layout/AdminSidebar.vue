<template>
  <aside class="admin-sidebar" :class="{ collapsed }">
    <div class="sidebar-content">
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        class="sidebar-menu"
        @select="handleSelect"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>管理概览</template>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/knowledge">
          <el-icon><Document /></el-icon>
          <template #title>知识库管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/detections">
          <el-icon><Search /></el-icon>
          <template #title>检测记录</template>
        </el-menu-item>
        <el-menu-item index="/admin/stats">
          <el-icon><DataLine /></el-icon>
          <template #title>数据统计</template>
        </el-menu-item>
        <el-menu-item index="/admin/config">
          <el-icon><Setting /></el-icon>
          <template #title>系统配置</template>
        </el-menu-item>
      </el-menu>
    </div>
    <div class="sidebar-toggle" @click="$emit('toggle-sidebar')">
      <el-icon :size="16">
        <Fold v-if="!collapsed" />
        <Expand v-else />
      </el-icon>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Odometer, User, Document, Search, DataLine, Setting, Fold, Expand } from '@element-plus/icons-vue'

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

function handleSelect(index) {
  router.push(index)
}
</script>

<style scoped>
.admin-sidebar {
  width: 220px;
  min-height: calc(100vh - 60px - 60px);
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  position: relative;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.sidebar-content {
  padding: 16px 0;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 4px 12px;
  border-radius: 8px;
  color: var(--color-text-secondary);
}

.sidebar-menu .el-menu-item:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-accent);
}

.sidebar-menu .el-menu-item.is-active {
  background: var(--color-accent-glow);
  color: var(--color-accent);
}

.sidebar-menu .el-menu-item .el-icon {
  font-size: 18px;
}

.sidebar-toggle {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text-tertiary);
  background: var(--color-bg-tertiary);
  transition: all 0.3s ease;
}

.sidebar-toggle:hover {
  color: var(--color-accent);
  background: var(--color-accent-glow);
}

.admin-sidebar.collapsed .sidebar-toggle {
  left: 50%;
}
</style>
