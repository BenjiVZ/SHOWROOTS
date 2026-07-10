<template>
  <div class="coverage-map-wrapper">
    <div class="coverage-map-hint">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
      {{ hintText || `${city || '—'} · ${radius} km de cobertura` }}
    </div>
    <div ref="mapContainer" class="coverage-map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  city: { type: String, default: '' },
  radius: { type: Number, default: 50 },
  // Texto del hint flotante; si no se pasa, muestra "ciudad · radio km de cobertura"
  hintText: { type: String, default: '' },
  // Ocultar el círculo de cobertura (ej: en la reserva solo interesa la ciudad)
  showCircle: { type: Boolean, default: true },
})

const themeStore = useThemeStore()
const mapContainer = ref(null)
let mapInstance = null
let coverageCircle = null
let cityMarker = null
let tileLayer = null
let resizeObserver = null

const PANAMA_CITIES = {
  'Ciudad de Panamá': [8.9824, -79.5199],
  'San Miguelito':    [9.0504, -79.4713],
  'David':            [8.4333, -82.4333],
  'Colón':            [9.3547, -79.9017],
  'Santiago':         [8.1000, -80.9833],
  'Chitré':           [7.9667, -80.4333],
  'Penonomé':         [8.5167, -80.3500],
  'Aguadulce':        [8.2453, -80.5431],
  'La Chorrera':      [8.8789, -79.7822],
  'Arraiján':         [8.9500, -79.6500],
  'Bocas del Toro':   [9.3404, -82.2418],
  'Las Tablas':       [7.7647, -80.2750],
}

const TILE_DARK = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
function currentTileUrl() {
  return themeStore.theme === 'light' ? TILE_LIGHT : TILE_DARK
}

function getCoords() {
  return PANAMA_CITIES[props.city] || PANAMA_CITIES['Ciudad de Panamá']
}

function buildMap() {
  if (!mapContainer.value || mapInstance) return
  const [lat, lng] = getCoords()

  mapInstance = L.map(mapContainer.value, {
    center: [lat, lng],
    zoom: 8,
    zoomControl: false,
    attributionControl: false,
    scrollWheelZoom: false,
    dragging: false,
    touchZoom: false,
    doubleClickZoom: false,
    boxZoom: false,
    keyboard: false,
  })

  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)

  // Marker en la ciudad
  cityMarker = L.marker([lat, lng], {
    icon: L.divIcon({
      className: 'coverage-marker',
      html: '<div class="coverage-marker-dot"></div>',
      iconSize: [16, 16],
      iconAnchor: [8, 8],
    }),
  }).addTo(mapInstance)

  // Círculo de cobertura (opcional)
  if (props.showCircle) {
    coverageCircle = L.circle([lat, lng], {
      radius: (props.radius || 50) * 1000,
      color: '#C1D82F',
      fillColor: '#C1D82F',
      fillOpacity: 0.12,
      weight: 2,
      dashArray: '6 4',
    }).addTo(mapInstance)
  }

  // Encuadrar para que el círculo se vea entero
  fitBoundsToCoverage()

  resizeObserver = new ResizeObserver(() => mapInstance?.invalidateSize())
  resizeObserver.observe(mapContainer.value)
  requestAnimationFrame(() => mapInstance?.invalidateSize())
  setTimeout(() => mapInstance?.invalidateSize(), 300)
}

function fitBoundsToCoverage() {
  if (!mapInstance) return
  if (coverageCircle) {
    const bounds = coverageCircle.getBounds()
    mapInstance.fitBounds(bounds, { padding: [20, 20], maxZoom: 10 })
  } else {
    // Sin círculo: centrar en la ciudad con zoom cercano
    mapInstance.setView(getCoords(), 11)
  }
}

function destroyMap() {
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
  coverageCircle = null
  cityMarker = null
  tileLayer = null
}

// Re-centrar si cambia la ciudad o el radio
watch(() => props.city, () => {
  if (!mapInstance) return
  const [lat, lng] = getCoords()
  mapInstance.setView([lat, lng])
  cityMarker?.setLatLng([lat, lng])
  coverageCircle?.setLatLng([lat, lng])
  fitBoundsToCoverage()
})
watch(() => props.radius, (val) => {
  if (coverageCircle) {
    coverageCircle.setRadius((val || 50) * 1000)
    fitBoundsToCoverage()
  }
})

// Cambio de tema
watch(() => themeStore.theme, () => {
  if (!mapInstance || !tileLayer) return
  mapInstance.removeLayer(tileLayer)
  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
})

onMounted(() => {
  requestAnimationFrame(() => buildMap())
})
onBeforeUnmount(() => destroyMap())
</script>

<style scoped>
.coverage-map-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  margin-top: var(--space-3);
}
.coverage-map {
  width: 100%;
  height: 220px;
  background: var(--color-bg-card);
}
.coverage-map-hint {
  position: absolute;
  top: 10px;
  left: 12px;
  z-index: 400;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 999px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  pointer-events: none;
}
.coverage-map-hint svg { color: var(--color-primary); }

:deep(.coverage-marker) { background: none !important; border: none !important; }
:deep(.coverage-marker-dot) {
  width: 16px;
  height: 16px;
  background: var(--color-primary, #C1D82F);
  border: 3px solid var(--color-bg-card);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--color-primary, #C1D82F), 0 0 14px rgba(193,216,47,0.55);
}
:deep(.leaflet-container) {
  background: var(--color-bg-card) !important;
  font-family: inherit !important;
  outline: none !important;
}
</style>
