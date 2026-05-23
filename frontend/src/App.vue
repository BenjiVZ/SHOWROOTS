<template>
  <div id="webdj-app">
    <NavBar />
    <main :class="{ 'no-padding': isFullscreenPage }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter v-if="!isFullscreenPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/common/NavBar.vue'
import AppFooter from '@/components/common/AppFooter.vue'

const route = useRoute()
const fullscreenPages = ['talent-onboarding']
const isFullscreenPage = computed(() => fullscreenPages.includes(route.name))
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

main.no-padding {
  padding-top: 0;
}
</style>
