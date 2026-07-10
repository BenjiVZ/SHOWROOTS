<template>
  <div class="map-wrapper">
    <div class="map-hint">Toca una ciudad en el mapa</div>
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
// Mapa interactivo de Panamá con ciudades clickeables (mismo del onboarding).
// Uso: <CityPickerMap v-model="form.city" />
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const themeStore = useThemeStore()
const mapContainer = ref(null)
let mapInstance = null
let tileLayer = null
let cityMarkers = []
let resizeObserver = null

const panamaCities = [
  { name: 'Ciudad de Panamá', lat: 8.9824, lng: -79.5199 },
  { name: 'San Miguelito',    lat: 9.0504, lng: -79.4713 },
  { name: 'David',            lat: 8.4333, lng: -82.4333 },
  { name: 'Colón',            lat: 9.3547, lng: -79.9017 },
  { name: 'Santiago',         lat: 8.1000, lng: -80.9833 },
  { name: 'Chitré',           lat: 7.9667, lng: -80.4333 },
  { name: 'Penonomé',         lat: 8.5167, lng: -80.3500 },
  { name: 'Aguadulce',        lat: 8.2453, lng: -80.5431 },
  { name: 'La Chorrera',      lat: 8.8789, lng: -79.7822 },
  { name: 'Arraiján',         lat: 8.9500, lng: -79.6500 },
  { name: 'Bocas del Toro',   lat: 9.3404, lng: -82.2418 },
  { name: 'Las Tablas',       lat: 7.7647, lng: -80.2750 },
]

const TILE_DARK = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
function currentTileUrl() {
  return themeStore.theme === 'light' ? TILE_LIGHT : TILE_DARK
}

function makeMarkerIcon(active = false) {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div class="marker-dot${active ? ' active' : ''}"></div>`,
    iconSize: [active ? 18 : 12, active ? 18 : 12],
    iconAnchor: [active ? 9 : 6, active ? 9 : 6],
  })
}

function selectCity(cityName, fly = true) {
  emit('update:modelValue', cityName)
  const city = panamaCities.find(c => c.name === cityName)
  if (!city || !mapInstance) return
  if (fly) mapInstance.flyTo([city.lat, city.lng], 9, { duration: 0.8 })
  cityMarkers.forEach(({ marker, name }) => {
    marker.setIcon(makeMarkerIcon(name === cityName))
  })
}

function buildMap() {
  if (!mapContainer.value || mapInstance) return

  const initial = panamaCities.find(c => c.name === props.modelValue) || panamaCities[0]

  mapInstance = L.map(mapContainer.value, {
    center: [initial.lat, initial.lng],
    zoom: 8,
    zoomControl: false,
    attributionControl: false,
    scrollWheelZoom: false,
  })

  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance)

  // Markers de todas las ciudades, clickeables
  cityMarkers = panamaCities.map(c => {
    const isActive = c.name === props.modelValue
    const marker = L.marker([c.lat, c.lng], { icon: makeMarkerIcon(isActive) })
      .addTo(mapInstance)
      .bindTooltip(c.name, { direction: 'top', offset: [0, -8], className: 'city-tooltip' })
    marker.on('click', () => selectCity(c.name))
    return { marker, name: c.name }
  })

  resizeObserver = new ResizeObserver(() => mapInstance?.invalidateSize())
  resizeObserver.observe(mapContainer.value)
  requestAnimationFrame(() => mapInstance?.invalidateSize())
  setTimeout(() => mapInstance?.invalidateSize(), 400)
}

function destroyMap() {
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
  tileLayer = null
  cityMarkers = []
}

// Si el padre cambia la ciudad (ej: por el select), sincronizar el mapa
watch(() => props.modelValue, (val) => {
  if (!mapInstance || !val) return
  const city = panamaCities.find(c => c.name === val)
  if (!city) return
  mapInstance.flyTo([city.lat, city.lng], 9, { duration: 0.8 })
  cityMarkers.forEach(({ marker, name }) => {
    marker.setIcon(makeMarkerIcon(name === val))
  })
})

// Cambio de tema claro/oscuro
watch(() => themeStore.theme, () => {
  if (!mapInstance || !tileLayer) return
  mapInstance.removeLayer(tileLayer)
  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
})

onMounted(() => requestAnimationFrame(() => buildMap()))
onBeforeUnmount(() => destroyMap())
</script>

<style scoped>
.map-wrapper {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  position: relative;
  margin-top: var(--space-3, 12px);
}
.map-container {
  width: 100%;
  height: 240px;
  background: var(--color-bg-card);
}
.map-hint {
  position: absolute;
  top: 10px;
  left: 12px;
  z-index: 400;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  backdrop-filter: blur(8px);
  pointer-events: none;
}

/* Leaflet (inyecta HTML propio → :deep) */
:deep(.custom-marker) { background: none !important; border: none !important; }
:deep(.marker-dot) {
  width: 12px;
  height: 12px;
  background: var(--color-bg-primary);
  border: 2px solid var(--color-primary, #C1D82F);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--color-bg-card), 0 0 8px rgba(193,216,47,0.4);
  transition: all 0.2s ease;
  cursor: pointer;
}
:deep(.marker-dot:hover) {
  transform: scale(1.3);
  background: var(--color-primary, #C1D82F);
}
:deep(.marker-dot.active) {
  width: 18px;
  height: 18px;
  background: var(--color-primary, #C1D82F);
  box-shadow: 0 0 0 4px rgba(193,216,47,0.25), 0 0 16px rgba(193,216,47,0.6);
  animation: markerPulse 2s ease-in-out infinite;
}
@keyframes markerPulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(193,216,47,0.25), 0 0 16px rgba(193,216,47,0.6); }
  50% { box-shadow: 0 0 0 8px rgba(193,216,47,0.10), 0 0 20px rgba(193,216,47,0.7); }
}

:deep(.city-tooltip) {
  background: var(--color-bg-card) !important;
  color: var(--color-text-primary) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: 8px !important;
  padding: 4px 10px !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
}
:deep(.city-tooltip::before),
:deep(.leaflet-tooltip-top::before) { display: none !important; }

:deep(.leaflet-control-zoom) {
  border: none !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
  margin: 12px !important;
}
:deep(.leaflet-control-zoom a) {
  background: var(--color-bg-card) !important;
  color: var(--color-text-secondary) !important;
  border: 1px solid var(--color-border) !important;
  width: 30px !important;
  height: 30px !important;
  line-height: 28px !important;
  font-size: 16px !important;
}
:deep(.leaflet-control-zoom a:hover) {
  background: var(--color-bg-card-hover) !important;
  color: var(--color-primary, #C1D82F) !important;
  border-color: var(--color-primary, #C1D82F) !important;
}
:deep(.leaflet-control-zoom-in) { border-radius: 8px 8px 0 0 !important; }
:deep(.leaflet-control-zoom-out) { border-radius: 0 0 8px 8px !important; border-top: none !important; }

:deep(.leaflet-container) {
  background: var(--color-bg-card) !important;
  font-family: inherit !important;
  outline: none !important;
}
</style>
