<template>
  <div id="webdj-app">
    <NavBar />
    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import NavBar from '@/components/common/NavBar.vue'
import AppFooter from '@/components/common/AppFooter.vue'
</script>

<style scoped>
#webdj-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
  padding-top: calc(80px + var(--space-4));
}
</style>
