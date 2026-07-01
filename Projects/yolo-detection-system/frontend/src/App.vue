<template>
  <div class="app-container">
    <ParticlesBackground />
    <div class="app-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ParticlesBackground from '@/components/ParticlesBackground.vue'
import { useThemeStore } from '@/store/modules/theme'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  position: relative;
  background: var(--color-bg-primary);
  transition: background 0.3s ease;
}

.app-content {
  position: relative;
  z-index: 10;
  min-height: 100vh;
}
</style>
