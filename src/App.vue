<template>
  <div class="app-container">
    <header class="app-header">
      <h1>校园物流配送系统</h1>
    </header>
    <main class="app-main">
      <InferencePanel />
    </main>
    <footer class="app-footer">
      <p>&copy; 2026 校园物流配送系统</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import InferencePanel from './inference/InferencePanel.vue'
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: Arial, sans-serif;
}

.app-header {
  background-color: #409EFF;
  color: white;
  padding: 1rem 2rem;
  text-align: center;
}

.app-main {
  flex: 1;
  padding: 1rem;
  overflow: auto;
}

.app-footer {
  background-color: #f5f7fa;
  padding: 1rem;
  text-align: center;
  font-size: 0.9rem;
  color: #909399;
}
</style>