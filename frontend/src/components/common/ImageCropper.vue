<template>
  <Teleport to="body">
    <Transition name="cropper-fade">
      <div v-if="src" class="cropper-backdrop" @click.self="$emit('cancel')">
        <div class="cropper-modal">
          <div class="cropper-header">
            <h3>{{ title }}</h3>
            <button class="cropper-close" @click="$emit('cancel')" aria-label="Cerrar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <p class="cropper-hint">Arrastra para mover · Usa el slider para hacer zoom</p>

          <div
            ref="stageEl"
            class="cropper-stage"
            :style="stageStyle"
            @mousedown="onPointerDown"
            @touchstart.passive="onPointerDown"
            @wheel="onWheel"
          >
            <img
              v-if="src"
              ref="imgEl"
              :src="src"
              :style="imgStyle"
              @load="onImgLoad"
              draggable="false"
              alt=""
            />
            <!-- Grid overlay para guía visual -->
            <div class="cropper-grid">
              <span></span><span></span><span></span><span></span>
            </div>
          </div>

          <div class="cropper-zoom">
            <button class="zoom-btn" @click="setZoom(zoom - 0.1)" aria-label="Reducir zoom">−</button>
            <input
              type="range"
              v-model.number="zoom"
              min="1"
              max="3"
              step="0.01"
              class="zoom-slider"
            />
            <button class="zoom-btn" @click="setZoom(zoom + 0.1)" aria-label="Aumentar zoom">+</button>
          </div>

          <div class="cropper-actions">
            <button class="btn btn-ghost btn-sm" @click="$emit('cancel')">Cancelar</button>
            <button class="btn btn-primary" :disabled="processing" @click="apply">
              {{ processing ? 'Procesando...' : 'Aplicar recorte' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  file: { type: [File, Blob], default: null },
  aspectRatio: { type: Number, default: 1 }, // 1 = cuadrado, 3 = 3:1, etc
  maxOutput: { type: Number, default: 1200 }, // ancho máx output en px
  outputType: { type: String, default: 'image/jpeg' },
  outputQuality: { type: Number, default: 0.85 }, // calidad inicial — se ajusta hacia abajo si supera maxKB
  maxKB: { type: Number, default: 350 }, // tamaño objetivo en KB. Si supera, recomprime
  title: { type: String, default: 'Ajusta tu foto' },
})

const emit = defineEmits(['cropped', 'cancel'])

const stageEl = ref(null)
const imgEl = ref(null)
const src = ref(null)
const imgNaturalW = ref(0)
const imgNaturalH = ref(0)
const stageW = ref(400)
const stageH = ref(400)

const zoom = ref(1) // 1 = cover (mínimo), hasta 3
const offsetX = ref(0)
const offsetY = ref(0)
const processing = ref(false)

// Drag state
let dragging = false
let dragStartX = 0
let dragStartY = 0
let initialOffsetX = 0
let initialOffsetY = 0

watch(() => props.file, (file) => {
  if (!file) {
    if (src.value) URL.revokeObjectURL(src.value)
    src.value = null
    return
  }
  if (src.value) URL.revokeObjectURL(src.value)
  src.value = URL.createObjectURL(file)
  // reset zoom/offset
  zoom.value = 1
  offsetX.value = 0
  offsetY.value = 0
}, { immediate: true })

onUnmounted(() => {
  if (src.value) URL.revokeObjectURL(src.value)
  window.removeEventListener('mousemove', onPointerMove)
  window.removeEventListener('mouseup', onPointerUp)
  window.removeEventListener('touchmove', onPointerMove)
  window.removeEventListener('touchend', onPointerUp)
})

// Stage dimensions según aspect ratio
const stageStyle = computed(() => {
  const baseWidth = 400
  const w = baseWidth
  const h = baseWidth / props.aspectRatio
  stageW.value = w
  stageH.value = h
  return { width: `${w}px`, height: `${h}px` }
})

// Escala mínima para cubrir el stage (cover)
const minScale = computed(() => {
  if (!imgNaturalW.value || !imgNaturalH.value) return 1
  return Math.max(stageW.value / imgNaturalW.value, stageH.value / imgNaturalH.value)
})

// Escala efectiva
const scale = computed(() => minScale.value * zoom.value)

const displayedW = computed(() => imgNaturalW.value * scale.value)
const displayedH = computed(() => imgNaturalH.value * scale.value)

const imgStyle = computed(() => ({
  width: `${displayedW.value}px`,
  height: `${displayedH.value}px`,
  transform: `translate(${offsetX.value}px, ${offsetY.value}px)`,
  cursor: dragging ? 'grabbing' : 'grab',
}))

function onImgLoad() {
  if (!imgEl.value) return
  imgNaturalW.value = imgEl.value.naturalWidth
  imgNaturalH.value = imgEl.value.naturalHeight
  // Centrar
  clampAndCenter()
}

function clampAndCenter() {
  const dw = displayedW.value
  const dh = displayedH.value
  // Centrar inicial
  offsetX.value = (stageW.value - dw) / 2
  offsetY.value = (stageH.value - dh) / 2
}

function clampOffset() {
  // El image scaled debe SIEMPRE cubrir el stage
  const dw = displayedW.value
  const dh = displayedH.value
  const minX = stageW.value - dw
  const minY = stageH.value - dh
  if (offsetX.value > 0) offsetX.value = 0
  if (offsetY.value > 0) offsetY.value = 0
  if (offsetX.value < minX) offsetX.value = minX
  if (offsetY.value < minY) offsetY.value = minY
}

// Re-clamp on zoom change.
// Vue.watch(zoom, (newVal, oldVal)) recibe el valor viejo antes del cambio,
// pero los computed (scale, displayedW) ya tienen el valor nuevo cuando llega aquí.
// Calculamos el ratio usando los valores de zoom directamente.
watch(zoom, (newZoom, oldZoom) => {
  if (!imgNaturalW.value || !oldZoom) return
  const ratio = newZoom / oldZoom
  if (ratio === 1) return
  // Mantener el punto central del stage durante el zoom
  const centerX = stageW.value / 2
  const centerY = stageH.value / 2
  offsetX.value = centerX - (centerX - offsetX.value) * ratio
  offsetY.value = centerY - (centerY - offsetY.value) * ratio
  clampOffset()
})

function setZoom(v) {
  zoom.value = Math.max(1, Math.min(3, v))
}

function onPointerDown(e) {
  if (e.type === 'mousedown' && e.button !== 0) return
  dragging = true
  const pt = pointFrom(e)
  dragStartX = pt.x
  dragStartY = pt.y
  initialOffsetX = offsetX.value
  initialOffsetY = offsetY.value
  window.addEventListener('mousemove', onPointerMove)
  window.addEventListener('mouseup', onPointerUp)
  window.addEventListener('touchmove', onPointerMove, { passive: false })
  window.addEventListener('touchend', onPointerUp)
}

function onPointerMove(e) {
  if (!dragging) return
  if (e.type === 'touchmove') e.preventDefault()
  const pt = pointFrom(e)
  offsetX.value = initialOffsetX + (pt.x - dragStartX)
  offsetY.value = initialOffsetY + (pt.y - dragStartY)
  clampOffset()
}

function onPointerUp() {
  dragging = false
  window.removeEventListener('mousemove', onPointerMove)
  window.removeEventListener('mouseup', onPointerUp)
  window.removeEventListener('touchmove', onPointerMove)
  window.removeEventListener('touchend', onPointerUp)
}

function pointFrom(e) {
  if (e.touches && e.touches[0]) return { x: e.touches[0].clientX, y: e.touches[0].clientY }
  if (e.changedTouches && e.changedTouches[0]) return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY }
  return { x: e.clientX, y: e.clientY }
}

function onWheel(e) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.05 : 0.05
  setZoom(zoom.value + delta)
}

function canvasToBlob(canvas, type, quality) {
  return new Promise(resolve => canvas.toBlob(resolve, type, quality))
}

async function apply() {
  if (!imgEl.value || processing.value) return
  processing.value = true
  try {
    // Calcular fuente en píxeles de imagen original
    const s = scale.value
    const sourceX = -offsetX.value / s
    const sourceY = -offsetY.value / s
    const sourceW = stageW.value / s
    const sourceH = stageH.value / s

    // Output: ancho ≤ maxOutput, ratio preservado.
    // Usamos 1.5x del stage como base (no 2x) para reducir peso final.
    const outputW = Math.min(props.maxOutput, Math.round(stageW.value * 1.5))
    const outputH = Math.round(outputW / props.aspectRatio)

    const canvas = document.createElement('canvas')
    canvas.width = outputW
    canvas.height = outputH
    const ctx = canvas.getContext('2d')
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'
    // Fondo blanco para JPEGs (evita transparencia rara)
    if (props.outputType === 'image/jpeg') {
      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, outputW, outputH)
    }
    ctx.drawImage(
      imgEl.value,
      sourceX, sourceY, sourceW, sourceH,
      0, 0, outputW, outputH
    )

    // Compresión iterativa: si el blob supera maxKB, bajar calidad hasta llegar
    const maxBytes = props.maxKB * 1024
    let quality = props.outputQuality
    let blob = await canvasToBlob(canvas, props.outputType, quality)

    while (blob && blob.size > maxBytes && quality > 0.5) {
      quality -= 0.08
      blob = await canvasToBlob(canvas, props.outputType, quality)
    }

    if (!blob) {
      throw new Error('Canvas toBlob falló')
    }

    // Construir File para mantener nombre + tipo
    const originalName = props.file?.name || 'image.jpg'
    const ext = props.outputType === 'image/png' ? '.png' : '.jpg'
    const baseName = originalName.replace(/\.[^.]+$/, '').slice(0, 40)
    // Añadir timestamp único para evitar colisiones de nombre en el backend
    const unique = Date.now().toString(36)
    const cropped = new File([blob], `${baseName}-${unique}${ext}`, { type: props.outputType })

    emit('cropped', cropped)
  } catch (err) {
    console.error('Crop error:', err)
    alert('No se pudo procesar la imagen. Intenta con otra.')
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.cropper-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.cropper-modal {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-5);
  width: 100%;
  max-width: 460px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
}

.cropper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}
.cropper-header h3 { font-size: 1.1rem; margin: 0; }
.cropper-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.cropper-close:hover { background: var(--color-bg-primary); color: var(--color-text-primary); }

.cropper-hint {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.cropper-stage {
  position: relative;
  margin: 0 auto var(--space-4);
  background: #000;
  border-radius: var(--radius-lg);
  overflow: hidden;
  user-select: none;
  touch-action: none;
  max-width: 100%;
}

.cropper-stage img {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  transform-origin: 0 0;
  will-change: transform, width, height;
  /* Override global reset (img { max-width: 100%; height: auto; }) que comprime la imagen */
  max-width: none !important;
  max-height: none !important;
  min-width: 0 !important;
  min-height: 0 !important;
}

/* Grid overlay (regla de tercios) */
.cropper-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(to right, transparent calc(33.33% - 1px), rgba(255,255,255,0.25) 33.33%, rgba(255,255,255,0.25) calc(33.33% + 1px), transparent calc(33.33% + 1px), transparent calc(66.66% - 1px), rgba(255,255,255,0.25) 66.66%, rgba(255,255,255,0.25) calc(66.66% + 1px), transparent calc(66.66% + 1px)),
    linear-gradient(to bottom, transparent calc(33.33% - 1px), rgba(255,255,255,0.25) 33.33%, rgba(255,255,255,0.25) calc(33.33% + 1px), transparent calc(33.33% + 1px), transparent calc(66.66% - 1px), rgba(255,255,255,0.25) 66.66%, rgba(255,255,255,0.25) calc(66.66% + 1px), transparent calc(66.66% + 1px));
  box-shadow: inset 0 0 0 2px var(--color-primary);
}

.cropper-zoom {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding: 0 var(--space-2);
}
.zoom-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.zoom-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.zoom-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 2px;
  background: var(--color-border);
  outline: none;
}
.zoom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(193,216,47,0.3);
}
.zoom-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border: none;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
}

.cropper-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}

.cropper-fade-enter-active, .cropper-fade-leave-active {
  transition: opacity 0.2s ease;
}
.cropper-fade-enter-from, .cropper-fade-leave-to { opacity: 0; }

@media (max-width: 520px) {
  .cropper-stage { width: 100% !important; height: auto !important; aspect-ratio: v-bind('props.aspectRatio'); }
}
</style>
