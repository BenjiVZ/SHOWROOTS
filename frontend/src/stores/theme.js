import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // Initialize from localStorage or system preference
  const saved = localStorage.getItem('pulsar-theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const theme = ref(saved || (prefersDark ? 'dark' : 'dark'))

  // Apply theme to the document
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t)
  }

  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  const isDark = () => theme.value === 'dark'

  // Watch and persist
  watch(theme, (val) => {
    localStorage.setItem('pulsar-theme', val)
    applyTheme(val)
  }, { immediate: true })

  return { theme, toggle, isDark }
})
