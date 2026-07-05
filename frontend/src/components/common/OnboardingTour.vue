<template>
  <teleport to="body">
    <!-- Botón de ayuda flotante — siempre disponible para reabrir el manual -->
    <button
      v-if="!active"
      class="tour-help-fab"
      title="Ver manual de uso"
      @click="start(true)"
    >
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      <span class="tour-help-label">Ayuda</span>
    </button>

    <!-- Overlay del tour -->
    <div v-if="active" class="tour-overlay" @click.self="skip">
      <!-- Spotlight recortado sobre el elemento objetivo -->
      <div
        v-if="spotlight"
        class="tour-spotlight"
        :style="{
          top: spotlight.top + 'px',
          left: spotlight.left + 'px',
          width: spotlight.width + 'px',
          height: spotlight.height + 'px',
        }"
      ></div>

      <!-- Tooltip / tarjeta del paso -->
      <div class="tour-card" :style="cardStyle" role="dialog" aria-modal="true">
        <div class="tour-card-head">
          <span class="tour-step-count">Paso {{ index + 1 }} de {{ steps.length }}</span>
          <button class="tour-close" @click="skip" aria-label="Cerrar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div v-if="current.icon" class="tour-icon" v-html="current.icon"></div>
        <h3 class="tour-title">{{ current.title }}</h3>
        <p class="tour-body" v-html="current.body"></p>
        <div class="tour-progress">
          <span
            v-for="(s, i) in steps"
            :key="i"
            :class="['tour-dot', { done: i <= index }]"
          ></span>
        </div>
        <div class="tour-actions">
          <button class="tour-btn ghost" @click="skip">Saltar</button>
          <div class="tour-nav">
            <button v-if="index > 0" class="tour-btn outline" @click="prev">Atrás</button>
            <button class="tour-btn primary" @click="next">
              {{ index === steps.length - 1 ? '¡Listo!' : 'Siguiente' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  // Clave única del tour (para recordar si ya se vio). Ej: 'talent-dash-v1'
  tourKey: { type: String, required: true },
  // Array de pasos: { target?: 'selector', title, body, tab? }
  steps: { type: Array, required: true },
  // Auto-mostrar la primera vez
  auto: { type: Boolean, default: true },
})

// emit('navigate', tabKey) → el padre cambia de pestaña antes de resaltar
const emit = defineEmits(['navigate', 'finish'])

const active = ref(false)
const index = ref(0)
const spotlight = ref(null)
const cardStyle = ref({})

const current = computed(() => props.steps[index.value] || {})
const storageKey = computed(() => `pulsar_tour_${props.tourKey}`)

function alreadySeen() {
  try { return localStorage.getItem(storageKey.value) === '1' } catch { return false }
}
function markSeen() {
  try { localStorage.setItem(storageKey.value, '1') } catch { /* ignore */ }
}

async function positionForStep() {
  const step = current.value
  // Si el paso requiere una pestaña concreta, pedirle al padre que cambie
  if (step.tab) {
    emit('navigate', step.tab)
    await nextTick()
    await new Promise(r => setTimeout(r, 180)) // dejar animar el cambio de tab
  }

  const el = step.target ? document.querySelector(step.target) : null
  if (!el) {
    // Paso sin objetivo (bienvenida): centrar la tarjeta, sin spotlight
    spotlight.value = null
    cardStyle.value = {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
    }
    return
  }

  el.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' })
  await new Promise(r => setTimeout(r, 260))

  const r = el.getBoundingClientRect()
  const pad = 8
  spotlight.value = {
    top: r.top - pad,
    left: r.left - pad,
    width: r.width + pad * 2,
    height: r.height + pad * 2,
  }

  // Posicionar la tarjeta: debajo del objetivo si hay espacio, si no arriba
  const cardW = Math.min(360, window.innerWidth - 32)
  const spaceBelow = window.innerHeight - r.bottom
  let top, left
  if (spaceBelow > 260) {
    top = r.bottom + 16
  } else {
    top = Math.max(16, r.top - 260)
  }
  left = r.left + r.width / 2 - cardW / 2
  left = Math.max(16, Math.min(left, window.innerWidth - cardW - 16))
  cardStyle.value = { top: top + 'px', left: left + 'px', width: cardW + 'px', transform: 'none' }
}

async function start(force = false) {
  if (!force && alreadySeen()) return
  index.value = 0
  active.value = true
  document.body.style.overflow = 'hidden'
  await positionForStep()
}

async function next() {
  if (index.value >= props.steps.length - 1) {
    finish()
    return
  }
  index.value++
  await positionForStep()
}

async function prev() {
  if (index.value === 0) return
  index.value--
  await positionForStep()
}

function cleanup() {
  active.value = false
  spotlight.value = null
  document.body.style.overflow = ''
}

function finish() {
  markSeen()
  cleanup()
  emit('finish')
}

function skip() {
  markSeen()
  cleanup()
}

function onResize() {
  if (active.value) positionForStep()
}

onMounted(async () => {
  window.addEventListener('resize', onResize)
  if (props.auto && !alreadySeen()) {
    await new Promise(r => setTimeout(r, 600)) // esperar a que el dashboard cargue
    start()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  document.body.style.overflow = ''
})

// Permitir al padre reabrir el tour: ref.start(true)
defineExpose({ start })
</script>

<style scoped>
/* ── Botón de ayuda flotante ── */
.tour-help-fab {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 900;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 999px;
  border: none;
  background: var(--color-primary, #c6ff00);
  color: #0a0a0a;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.tour-help-fab:hover { transform: translateY(-2px); box-shadow: 0 8px 26px rgba(0, 0, 0, 0.4); }
.tour-help-label { line-height: 1; }
@media (max-width: 640px) {
  .tour-help-fab { right: 14px; bottom: 14px; padding: 12px; }
  .tour-help-label { display: none; }
}

/* ── Overlay + spotlight ── */
.tour-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.62);
}
.tour-spotlight {
  position: fixed;
  border-radius: 12px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.62);
  border: 2px solid var(--color-primary, #c6ff00);
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

/* ── Tarjeta del paso ── */
.tour-card {
  position: fixed;
  z-index: 1001;
  width: 360px;
  max-width: calc(100vw - 32px);
  background: var(--color-bg-card, #16181d);
  border: 1px solid var(--color-border, #2a2d35);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  transition: top 0.28s ease, left 0.28s ease;
}
.tour-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.tour-step-count {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary, #c6ff00);
  font-weight: 700;
}
.tour-close {
  background: none;
  border: none;
  color: var(--color-text-muted, #9aa0aa);
  font-size: 1rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 6px;
}
.tour-close:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.tour-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: rgba(198, 255, 0, 0.12);
  color: var(--color-primary, #c6ff00);
  margin-bottom: 12px;
}
.tour-icon :deep(svg) { width: 24px; height: 24px; }
.tour-title {
  margin: 0 0 8px;
  font-size: 1.15rem;
  color: var(--color-text-primary, #fff);
}
.tour-body {
  margin: 0 0 14px;
  font-size: 0.92rem;
  line-height: 1.5;
  color: var(--color-text-muted, #c3c8d0);
}
.tour-body :deep(strong) { color: var(--color-text-primary, #fff); }
.tour-progress {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}
.tour-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border, #2a2d35);
  transition: background 0.2s;
}
.tour-dot.done { background: var(--color-primary, #c6ff00); }
.tour-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.tour-nav { display: flex; gap: 8px; }
.tour-btn {
  padding: 9px 16px;
  border-radius: 9px;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
}
.tour-btn.primary { background: var(--color-primary, #c6ff00); color: #0a0a0a; }
.tour-btn.primary:hover { filter: brightness(1.08); }
.tour-btn.outline {
  background: transparent;
  border-color: var(--color-border, #2a2d35);
  color: var(--color-text-primary, #fff);
}
.tour-btn.outline:hover { border-color: var(--color-primary, #c6ff00); }
.tour-btn.ghost {
  background: transparent;
  color: var(--color-text-muted, #9aa0aa);
}
.tour-btn.ghost:hover { color: #fff; }
</style>
