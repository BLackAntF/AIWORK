<template>
  <button class="theme-toggle btn-glow" @click="toggleTheme">
    <el-icon :size="20" class="theme-icon">
      <Sunny v-if="themeStore.isDark" />
      <Moon v-else />
    </el-icon>
  </button>
</template>

<script setup>
import { Sunny, Moon } from '@element-plus/icons-vue'
import { useThemeStore } from '@/store/modules/theme'

const themeStore = useThemeStore()

function toggleTheme() {
  themeStore.toggleTheme()
}
</script>

<style scoped>
.theme-toggle {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.theme-icon {
  transition: transform 0.3s ease;
}

.theme-toggle:hover .theme-icon {
  transform: rotate(180deg);
}
</style>
