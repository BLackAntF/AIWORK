<template>
  <footer class="app-footer">
    <div class="footer-content">
      <p class="copyright">
        © 2024 YOLO Detection System. All rights reserved.
      </p>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.app-footer {
  height: 60px;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.footer-content {
  text-align: center;
}

.copyright {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-tertiary);
}
</style>
