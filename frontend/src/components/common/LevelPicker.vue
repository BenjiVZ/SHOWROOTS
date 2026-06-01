<template>
  <div class="level-picker" ref="rootRef">
    <button
      ref="triggerRef"
      type="button"
      class="lp-trigger"
      :class="[`lp-${modelValue}`]"
      :disabled="disabled"
      @click.stop="toggle"
    >
      <span class="lp-stars" v-html="starsHtml(modelValue)"></span>
      <span class="lp-label">{{ LEVEL_META[modelValue]?.label || '—' }}</span>
      <svg class="lp-chevron" :class="{ rotated: open }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
    </button>

    <Teleport to="body">
      <Transition name="lp-fade">
        <div
          v-if="open"
          class="lp-menu"
          ref="menuRef"
          :style="{ top: menuPos.top + 'px', left: menuPos.left + 'px' }"
        >
          <button
            v-for="opt in OPTIONS"
            :key="opt.value"
            type="button"
            class="lp-option"
            :class="[`lp-${opt.value}`, { active: opt.value === modelValue }]"
            @click="select(opt.value)"
          >
            <span class="lp-stars" v-html="starsHtml(opt.value)"></span>
            <div class="lp-text">
              <strong>{{ opt.label }}</strong>
              <small>{{ opt.subtitle }}</small>
            </div>
            <svg v-if="opt.value === modelValue" class="lp-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: 'standard' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'change'])

const OPTIONS = [
  { value: 'standard', label: 'Standard', subtitle: 'Entrada · 20% comisión' },
  { value: 'pro',      label: 'Pro',      subtitle: '10+ eventos · 15% comisión' },
  { value: 'premium',  label: 'Premium',  subtitle: 'Por invitación · 12% comisión' },
]

const LEVEL_META = {
  standard: { label: 'Standard', stars: 0 },
  pro:      { label: 'Pro',      stars: 1 },
  premium:  { label: 'Premium',  stars: 2 },
}

const STAR_SVG = '<svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'

function starsHtml(level) {
  const n = LEVEL_META[level]?.stars || 0
  if (n === 0) {
    // Para Standard, mostramos un círculo neutro
    return '<span class="lp-circle"></span>'
  }
  return STAR_SVG.repeat(n)
}

const open = ref(false)
const rootRef = ref(null)
const triggerRef = ref(null)
const menuRef = ref(null)
const menuPos = ref({ top: 0, left: 0 })

const MENU_WIDTH = 240   // debe coincidir con .lp-menu min-width
const MENU_HEIGHT = 180  // alto aproximado para decidir si abrir arriba

function computeMenuPosition() {
  if (!triggerRef.value) return
  const r = triggerRef.value.getBoundingClientRect()
  const vh = window.innerHeight
  const vw = window.innerWidth
  // Por defecto alineado a la derecha del trigger, justo debajo
  let left = r.right - MENU_WIDTH
  let top = r.bottom + 6
  // Si no cabe a la izquierda, alinear a la izquierda del trigger
  if (left < 8) left = Math.min(r.left, vw - MENU_WIDTH - 8)
  // Si no hay espacio abajo, abrir arriba
  if (top + MENU_HEIGHT > vh - 8) {
    top = r.top - MENU_HEIGHT - 6
  }
  menuPos.value = { top, left }
}

function toggle() {
  if (open.value) {
    open.value = false
  } else {
    computeMenuPosition()
    open.value = true
  }
}

function select(value) {
  open.value = false
  if (value === props.modelValue) return
  emit('update:modelValue', value)
  emit('change', value)
}

function onDocClick(e) {
  if (!open.value) return
  const inTrigger = rootRef.value && rootRef.value.contains(e.target)
  const inMenu = menuRef.value && menuRef.value.contains(e.target)
  if (!inTrigger && !inMenu) open.value = false
}
function onKey(e) {
  if (e.key === 'Escape') open.value = false
}
function onScrollOrResize() {
  if (open.value) computeMenuPosition()
}

onMounted(() => {
  document.addEventListener('mousedown', onDocClick)
  document.addEventListener('keydown', onKey)
  window.addEventListener('scroll', onScrollOrResize, true)
  window.addEventListener('resize', onScrollOrResize)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocClick)
  document.removeEventListener('keydown', onKey)
  window.removeEventListener('scroll', onScrollOrResize, true)
  window.removeEventListener('resize', onScrollOrResize)
})
</script>

<style scoped>
.level-picker {
  position: relative;
  display: inline-block;
}

/* ── Trigger (botón cerrado) ── */
.lp-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px 5px 8px;
  border-radius: 999px;
  background: var(--color-bg-elevated, rgba(255,255,255,0.04));
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.lp-trigger:hover:not(:disabled) {
  border-color: var(--color-text-secondary);
  background: var(--color-bg-card);
}
.lp-trigger:disabled { opacity: 0.5; cursor: not-allowed; }
.lp-trigger.lp-pro {
  background: rgba(193,216,47,0.10);
  border-color: rgba(193,216,47,0.4);
  color: #C1D82F;
}
.lp-trigger.lp-premium {
  background: rgba(245,158,11,0.10);
  border-color: rgba(245,158,11,0.4);
  color: #f59e0b;
}
.lp-chevron {
  opacity: 0.6;
  transition: transform 0.18s ease;
  margin-left: 2px;
}
.lp-chevron.rotated { transform: rotate(180deg); }

/* Estrellas y círculo */
.lp-stars {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  line-height: 0;
}
.lp-circle {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.5;
}

</style>

<!-- Estilos del menú: NO scoped porque Teleport lo saca del árbol del componente -->
<style>
.lp-menu {
  position: fixed;
  min-width: 240px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 6px;
  box-shadow: 0 14px 36px rgba(0,0,0,0.32), 0 4px 12px rgba(0,0,0,0.14);
  z-index: 9999;
}
.lp-menu .lp-option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  color: var(--color-text-primary);
  transition: background 0.12s ease;
}
.lp-menu .lp-option:hover { background: var(--color-bg-elevated, rgba(255,255,255,0.04)); }
.lp-menu .lp-option.active { background: var(--color-bg-elevated, rgba(255,255,255,0.06)); }
.lp-menu .lp-option .lp-stars {
  flex-shrink: 0;
  width: 32px;
  display: inline-flex;
  justify-content: center;
  color: var(--color-text-muted);
}
.lp-menu .lp-stars {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  line-height: 0;
}
.lp-menu .lp-circle {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.5;
}
.lp-menu .lp-option.lp-pro .lp-stars { color: #C1D82F; }
.lp-menu .lp-option.lp-premium .lp-stars { color: #f59e0b; }
.lp-menu .lp-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.lp-menu .lp-text strong {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
}
.lp-menu .lp-text small {
  display: block;
  font-size: 0.72rem;
  color: var(--color-text-muted);
  line-height: 1.2;
  margin-top: 2px;
}
.lp-menu .lp-check {
  flex-shrink: 0;
  color: var(--color-primary);
}

/* Animación */
.lp-fade-enter-active,
.lp-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.lp-fade-enter-from,
.lp-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
