<template>
  <div class="partner-onboarding">
    <div class="container">
      <!-- Header -->
      <header class="onboard-header">
        <h1>Onboarding · Aliado de Producción</h1>
        <p class="onboard-sub">
          Antes de publicar packs de equipo necesitamos verificarte. Son 4 pasos rápidos.
        </p>
      </header>

      <!-- Status banner (si ya está en pending/verified/rejected) -->
      <div v-if="profile && profile.status === 'pending'" class="status-banner pending">
        <strong>⏳ Tu perfil está en revisión.</strong>
        Te avisaremos cuando un admin de Pulsar lo apruebe (target 48h).
      </div>
      <div v-else-if="profile && profile.status === 'verified'" class="status-banner verified">
        <strong>✅ Tu perfil está verificado.</strong>
        Ya podés publicar packs desde el dashboard de Aliado.
        <router-link to="/partner" class="banner-link">Ir al dashboard →</router-link>
      </div>
      <div v-else-if="profile && profile.status === 'rejected'" class="status-banner rejected">
        <strong>❌ Tu solicitud fue rechazada.</strong>
        <span v-if="profile.rejection_reason">Motivo: {{ profile.rejection_reason }}</span>
        <span>Podés ajustar y volver a enviar.</span>
      </div>

      <!-- Steps bar -->
      <div v-if="canEdit" class="steps-bar">
        <div v-for="(s, i) in stepLabels" :key="i" class="step" :class="{ active: step === i + 1, done: step > i + 1 }">
          {{ step > i + 1 ? '✓ ' : (i + 1) + '. ' }}{{ s }}
        </div>
      </div>

      <div v-if="loading" class="loading-state">Cargando…</div>

      <!-- ── STEP 1: Categorías ── -->
      <div v-else-if="canEdit && step === 1" class="card">
        <h2>¿Qué tipo de equipo ofrecés?</h2>
        <p class="card-sub">Elegí todas las categorías que tengas disponibles. Podrás detallarlas en cada Pack más adelante.</p>

        <div class="check-grid">
          <button
            v-for="c in CATEGORIES"
            :key="c.value"
            type="button"
            class="check-tile"
            :class="{ checked: form.categories.includes(c.value) }"
            @click="toggleCategory(c.value)"
          >
            <div class="check-icon" v-html="c.icon"></div>
            <div class="check-name">{{ c.label }}</div>
            <div class="check-meta">{{ c.meta }}</div>
          </button>
        </div>

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="step-actions">
          <button class="btn btn-ghost" @click="goBack">← Cancelar</button>
          <button class="btn btn-primary" :disabled="!form.categories.length || saving" @click="saveAndNext(2)">
            {{ saving ? 'Guardando…' : 'Siguiente →' }}
          </button>
        </div>
      </div>

      <!-- ── STEP 2: Fotos ── -->
      <div v-else-if="canEdit && step === 2" class="card">
        <h2>Fotos del equipo</h2>
        <p class="card-sub">
          Subí mínimo <strong>{{ MIN_PHOTOS }}</strong> fotos claras del equipo: setup armado, equipos individuales,
          y el depósito/garage donde lo guardás. Las usamos para verificar que existe.
        </p>

        <div class="photo-grid">
          <div v-for="p in profile?.photos || []" :key="p.id" class="photo-tile">
            <img :src="p.file" :alt="p.caption || 'Equipo'" />
            <button class="photo-remove" @click="deletePhoto(p.id)" :disabled="deletingId === p.id" aria-label="Eliminar">×</button>
          </div>
          <label class="photo-upload" :class="{ uploading: uploadingPhoto }">
            <input type="file" accept="image/*" hidden @change="onPhotoSelected" :disabled="uploadingPhoto" />
            <div v-if="uploadingPhoto" class="photo-upload-text">Subiendo…</div>
            <div v-else class="photo-upload-text">
              <div class="photo-upload-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 19a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h3l2-3h4l2 3h3a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
              </div>
              <strong>Agregar foto</strong>
              <span class="photo-upload-hint">JPG / PNG · máx 5MB</span>
            </div>
          </label>
        </div>

        <p class="photo-counter" :class="{ ok: (profile?.photo_count || 0) >= MIN_PHOTOS }">
          {{ profile?.photo_count || 0 }} / {{ MIN_PHOTOS }} fotos
          <span v-if="(profile?.photo_count || 0) >= MIN_PHOTOS">✓</span>
        </p>

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="step-actions">
          <button class="btn btn-ghost" @click="step = 1">← Anterior</button>
          <button
            class="btn btn-primary"
            :class="{ 'btn-disabled-clear': !canAdvancePhotos }"
            :disabled="!canAdvancePhotos"
            @click="step = 3"
            :title="canAdvancePhotos ? '' : `Te faltan ${MIN_PHOTOS - (profile?.photo_count || 0)} foto(s) para continuar`"
          >
            <span v-if="canAdvancePhotos">Siguiente →</span>
            <span v-else>Sube {{ MIN_PHOTOS - (profile?.photo_count || 0) }} foto{{ (MIN_PHOTOS - (profile?.photo_count || 0)) > 1 ? 's' : '' }} más</span>
          </button>
        </div>
      </div>

      <!-- ── STEP 3: Cobertura ── -->
      <div v-else-if="canEdit && step === 3" class="card">
        <h2>Cobertura y disponibilidad</h2>
        <p class="card-sub">Decinos hasta dónde llegás y cuántos eventos podés cubrir en simultáneo.</p>

        <div class="form-grid">
          <div class="form-group full">
            <label class="label">Ciudad principal</label>
            <select v-model="form.main_city" class="input-field" @change="onCityChange">
              <option value="" disabled>Selecciona tu ciudad</option>
              <option v-for="c in panamaCities" :key="c.name" :value="c.name">{{ c.name }}</option>
            </select>
          </div>

          <div class="form-group full">
            <div class="map-wrapper">
              <div class="map-hint">Toca una ciudad en el mapa</div>
              <div ref="mapContainer" class="map-container"></div>
            </div>
          </div>

          <div class="form-group full">
            <label class="label">Radio de cobertura: <strong>{{ form.coverage_radius_km }} km</strong></label>
            <input v-model.number="form.coverage_radius_km" type="range" min="10" max="300" step="10" class="range-slider" />
            <small class="form-hint">Hasta dónde te movés sin recargos.</small>
          </div>

          <div class="form-group">
            <label class="label">Fee por traslado fuera del área ($)</label>
            <input v-model.number="form.travel_fee_extra" type="number" min="0" class="input-field" placeholder="50" />
            <small class="form-hint">Si te llaman más lejos, este es el extra.</small>
          </div>
          <div class="form-group">
            <label class="label">Eventos simultáneos (por noche)</label>
            <select v-model.number="form.max_simultaneous_events" class="input-field">
              <option :value="1">1 evento por noche</option>
              <option :value="2">2 eventos por noche</option>
              <option :value="3">3 eventos por noche</option>
              <option :value="4">4+ eventos por noche</option>
            </select>
          </div>
          <div class="form-group full">
            <label class="label">Notas (opcional)</label>
            <textarea v-model="form.notes" rows="3" class="input-field" placeholder="Algo más que querés que sepamos: zonas específicas, restricciones, etc."></textarea>
          </div>
        </div>

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="step-actions">
          <button class="btn btn-ghost" @click="step = 2">← Anterior</button>
          <button class="btn btn-primary" :disabled="!form.main_city || saving" @click="saveAndNext(4)">
            {{ saving ? 'Guardando…' : 'Siguiente →' }}
          </button>
        </div>
      </div>

      <!-- ── STEP 4: Verificación ── -->
      <div v-else-if="canEdit && step === 4" class="card">
        <h2>Revisión y envío a verificación</h2>
        <p class="card-sub">Revisá los datos. Cuando envíes, un admin de Pulsar lo aprobará en máximo 48h.</p>

        <div class="review-block">
          <div class="review-row">
            <strong>Categorías</strong>
            <div class="review-chips">
              <span v-for="c in form.categories" :key="c" class="review-chip">{{ categoryLabel(c) }}</span>
            </div>
          </div>
          <div class="review-row">
            <strong>Ciudad</strong>
            <span>{{ form.main_city || '—' }}</span>
          </div>
          <div class="review-row">
            <strong>Cobertura</strong>
            <span>{{ form.coverage_radius_km }} km · ${{ form.travel_fee_extra || 0 }} fuera de área</span>
          </div>
          <div class="review-row">
            <strong>Capacidad</strong>
            <span>{{ form.max_simultaneous_events }} evento(s) por noche</span>
          </div>
          <div class="review-row">
            <strong>Fotos</strong>
            <span>{{ profile?.photo_count || 0 }} subidas</span>
          </div>
        </div>

        <div class="warning-note">
          ⚠️ Una vez enviado, no podés editar el perfil hasta que el admin responda.
        </div>

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="step-actions">
          <button class="btn btn-ghost" @click="step = 3">← Anterior</button>
          <button class="btn btn-primary" :disabled="submitting" @click="submitForVerification">
            {{ submitting ? 'Enviando…' : 'Enviar a verificación →' }}
          </button>
        </div>
      </div>

      <!-- Si está pending/verified, mostrar bloque informativo en lugar del wizard -->
      <div v-else-if="profile && !canEdit" class="card">
        <h2>Resumen de tu perfil</h2>
        <div class="review-block">
          <div class="review-row">
            <strong>Estado</strong>
            <span class="status-tag" :class="profile.status">{{ profile.status_display }}</span>
          </div>
          <div class="review-row">
            <strong>Categorías</strong>
            <div class="review-chips">
              <span v-for="c in profile.categories" :key="c" class="review-chip">{{ categoryLabel(c) }}</span>
            </div>
          </div>
          <div class="review-row">
            <strong>Ciudad · cobertura</strong>
            <span>{{ profile.main_city }} · {{ profile.coverage_radius_km }} km</span>
          </div>
          <div class="review-row">
            <strong>Fotos</strong>
            <span>{{ profile.photo_count }}</span>
          </div>
        </div>
        <div class="step-actions" style="justify-content: flex-end">
          <router-link v-if="profile.status === 'verified'" to="/partner" class="btn btn-primary">Ir al dashboard →</router-link>
          <button v-else class="btn btn-ghost" @click="goBack">← Volver</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '@/api'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const router = useRouter()

const MIN_PHOTOS = 4

const SVG_O = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
const CATEGORIES = [
  { value: 'sound',    label: 'Sonido',          meta: 'Monitores, subs, mixers',
    icon: `${SVG_O}<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>` },
  { value: 'lights',   label: 'Iluminación',     meta: 'Par cans, moving heads',
    icon: `${SVG_O}<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>` },
  { value: 'screens',  label: 'Pantallas',       meta: 'LED, proyección',
    icon: `${SVG_O}<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>` },
  { value: 'mics',     label: 'Microfonía',      meta: 'SM58, inalámbricos',
    icon: `${SVG_O}<path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>` },
  { value: 'dj_booth', label: 'DJ Booth',        meta: 'Estándar, con branding',
    icon: `${SVG_O}<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>` },
  { value: 'fx',       label: 'FX / Especiales', meta: 'Humo, láser, piro',
    icon: `${SVG_O}<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><path d="M12 3v3"/><path d="M12 18v3"/><path d="M3 12h3"/><path d="M18 12h3"/></svg>` },
]

const stepLabels = ['Categorías', 'Fotos', 'Cobertura', 'Verificación']

const loading = ref(true)
const profile = ref(null)
const step = ref(1)
const saving = ref(false)
const submitting = ref(false)
const error = ref('')
const uploadingPhoto = ref(false)
const deletingId = ref(null)

const form = reactive({
  categories: [],
  main_city: '',
  coverage_radius_km: 50,
  travel_fee_extra: null,
  max_simultaneous_events: 1,
  notes: '',
})

const canEdit = computed(() => {
  if (!profile.value) return true
  return ['draft', 'rejected'].includes(profile.value.status)
})

const canAdvancePhotos = computed(() => {
  // Cuenta tanto el photo_count del backend como las photos cargadas (por si el backend tarda)
  const count = profile.value?.photo_count ?? profile.value?.photos?.length ?? 0
  return count >= MIN_PHOTOS
})

function categoryLabel(value) {
  return CATEGORIES.find(c => c.value === value)?.label || value
}

function toggleCategory(value) {
  const idx = form.categories.indexOf(value)
  if (idx >= 0) form.categories.splice(idx, 1)
  else form.categories.push(value)
}

function goBack() {
  router.push('/account')
}

async function fetchProfile() {
  loading.value = true
  try {
    const { data } = await api.get('/partner/production/')
    profile.value = data
    // Hidratar form desde el backend
    form.categories = Array.isArray(data.categories) ? [...data.categories] : []
    form.main_city = data.main_city || ''
    form.coverage_radius_km = data.coverage_radius_km ?? 50
    form.travel_fee_extra = data.travel_fee_extra ?? null
    form.max_simultaneous_events = data.max_simultaneous_events || 1
    form.notes = data.notes || ''
    // Posicionar en el step correcto si estaba en progreso
    if (canEdit.value && data.onboarding_step >= 1 && data.onboarding_step <= 4) {
      step.value = data.onboarding_step
    }
  } catch (e) {
    if (e?.response?.status === 403) {
      error.value = 'Activá primero el rol Aliado en Mi Cuenta.'
      setTimeout(() => router.push('/account'), 1500)
    } else {
      error.value = 'No se pudo cargar tu perfil.'
    }
  }
  loading.value = false
}

async function saveAndNext(nextStep) {
  saving.value = true
  error.value = ''
  try {
    const { data } = await api.patch('/partner/production/', {
      categories: form.categories,
      main_city: form.main_city,
      coverage_radius_km: form.coverage_radius_km,
      travel_fee_extra: form.travel_fee_extra,
      max_simultaneous_events: form.max_simultaneous_events,
      notes: form.notes,
      onboarding_step: nextStep,
    })
    profile.value = data
    step.value = nextStep
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo guardar.'
  }
  saving.value = false
}

async function onPhotoSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'La imagen no puede superar 5MB.'
    return
  }
  uploadingPhoto.value = true
  error.value = ''
  const fd = new FormData()
  fd.append('file', file)
  try {
    await api.post('/partner/production/photos/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await fetchProfile() // refresh photo list + counter
  } catch (err) {
    error.value = err?.response?.data?.detail || 'No se pudo subir la foto.'
  }
  uploadingPhoto.value = false
}

async function deletePhoto(id) {
  deletingId.value = id
  try {
    await api.delete(`/partner/production/photos/${id}/`)
    await fetchProfile()
  } catch { /* silent */ }
  deletingId.value = null
}

async function submitForVerification() {
  submitting.value = true
  error.value = ''
  try {
    const { data } = await api.post('/partner/production/submit/')
    profile.value = data
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No se pudo enviar.'
  }
  submitting.value = false
}

// ── Mapa de Panamá ──
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

const mapContainer = ref(null)
let mapInstance = null
let coverageCircle = null
let tileLayer = null
let cityMarkers = []
let resizeObserver = null

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

function selectCityOnMap(cityName) {
  form.main_city = cityName
  const city = panamaCities.find(c => c.name === cityName)
  if (!city || !mapInstance) return
  mapInstance.flyTo([city.lat, city.lng], 9, { duration: 0.8 })
  coverageCircle?.setLatLng([city.lat, city.lng])
  cityMarkers.forEach(({ marker, name }) => {
    marker.setIcon(makeMarkerIcon(name === cityName))
  })
}

function onCityChange() {
  selectCityOnMap(form.main_city)
}

function buildMap() {
  if (!mapContainer.value || mapInstance) return
  const initial = panamaCities.find(c => c.name === form.main_city) || panamaCities[0]
  if (!form.main_city) form.main_city = initial.name

  mapInstance = L.map(mapContainer.value, {
    center: [initial.lat, initial.lng],
    zoom: 8,
    zoomControl: false,
    attributionControl: false,
    scrollWheelZoom: false,
  })

  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance)

  cityMarkers = panamaCities.map(c => {
    const isActive = c.name === form.main_city
    const marker = L.marker([c.lat, c.lng], { icon: makeMarkerIcon(isActive) })
      .addTo(mapInstance)
      .bindTooltip(c.name, { direction: 'top', offset: [0, -8], className: 'city-tooltip' })
    marker.on('click', () => selectCityOnMap(c.name))
    return { marker, name: c.name }
  })

  coverageCircle = L.circle([initial.lat, initial.lng], {
    radius: (form.coverage_radius_km || 50) * 1000,
    color: '#C1D82F',
    fillColor: '#C1D82F',
    fillOpacity: 0.10,
    weight: 1.5,
    dashArray: '6 4',
  }).addTo(mapInstance)

  resizeObserver = new ResizeObserver(() => mapInstance?.invalidateSize())
  resizeObserver.observe(mapContainer.value)
  requestAnimationFrame(() => mapInstance?.invalidateSize())
  setTimeout(() => mapInstance?.invalidateSize(), 400)
}

function destroyMap() {
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
  coverageCircle = null
  tileLayer = null
  cityMarkers = []
}

// Live update del círculo cuando se mueve el slider
watch(() => form.coverage_radius_km, (val) => {
  if (coverageCircle) coverageCircle.setRadius((val || 50) * 1000)
})

// Swap del tile cuando cambia el tema
watch(() => themeStore.theme, () => {
  if (!mapInstance || !tileLayer) return
  mapInstance.removeLayer(tileLayer)
  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
})

// Construir / destruir el mapa al entrar / salir del paso 3
watch(() => step.value, (s) => {
  if (s !== 3 && mapInstance) destroyMap()
  if (s === 3) nextTick(() => buildMap())
})

// El ref del container puede aparecer después por el v-if
watch(mapContainer, (el) => {
  if (el && step.value === 3 && !mapInstance) {
    requestAnimationFrame(() => buildMap())
  }
})

onMounted(fetchProfile)
onBeforeUnmount(() => destroyMap())
</script>

<style scoped>
.partner-onboarding { padding-top: 100px; padding-bottom: var(--space-12); min-height: 100vh; }
.container { max-width: 900px; margin: 0 auto; padding: 0 var(--space-4); }

.onboard-header { margin-bottom: var(--space-6); }
.onboard-header h1 { font-family: 'Poppins', sans-serif; font-size: 1.75rem; margin-bottom: var(--space-2); }
.onboard-sub { color: var(--color-text-muted); }

.status-banner {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-5);
  font-size: 0.95rem;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
}
.status-banner.pending { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #f59e0b; }
.status-banner.verified { background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; }
.status-banner.rejected { background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444; }
.banner-link { color: inherit; font-weight: 700; text-decoration: underline; margin-left: auto; }

.steps-bar {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  padding: var(--space-3);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  flex-wrap: wrap;
}
.step {
  flex: 1 1 120px;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  text-align: center;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
}
.step.done { color: #10b981; background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.3); }
.step.active { color: var(--color-primary); background: rgba(193, 216, 47, 0.08); border-color: var(--color-primary); font-weight: 600; }

.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}
.card h2 { font-size: 1.25rem; margin-bottom: var(--space-2); }
.card-sub { color: var(--color-text-muted); font-size: 0.9rem; margin-bottom: var(--space-5); line-height: 1.5; }

.check-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.check-tile {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  cursor: pointer;
  text-align: center;
  transition: all var(--transition-fast);
}
.check-tile:hover { border-color: var(--color-border-hover); }
.check-tile.checked {
  border-color: var(--color-primary);
  background: rgba(193, 216, 47, 0.06);
}
.check-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  margin-bottom: var(--space-2);
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}
.check-tile:hover .check-icon { color: var(--color-text-primary); }
.check-tile.checked .check-icon { color: var(--color-primary); }
.check-name { color: var(--color-text-primary); font-weight: 600; font-size: 0.9rem; }
.check-meta { color: var(--color-text-muted); font-size: 0.75rem; margin-top: 4px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}
.form-group.full { grid-column: 1 / -1; }
.form-group { display: flex; flex-direction: column; }
.label { color: var(--color-text-muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.input-field {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  font-family: inherit;
}
.input-field:focus { border-color: var(--color-primary); outline: none; }
.form-hint { color: var(--color-text-muted); font-size: 0.75rem; margin-top: 4px; }

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.photo-tile {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
}
.photo-tile img { width: 100%; height: 100%; object-fit: cover; display: block; }
.photo-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0,0,0,0.7);
  color: #fff;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  line-height: 1;
}
.photo-upload {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  transition: all var(--transition-fast);
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.8rem;
}
.photo-upload:hover { border-color: var(--color-primary); color: var(--color-primary); }
.photo-upload.uploading { opacity: 0.6; pointer-events: none; }
.photo-upload-text { padding: var(--space-2); }
.photo-upload-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}
.photo-upload:hover .photo-upload-icon { color: var(--color-primary); }
.photo-upload-hint { display: block; font-size: 0.7rem; opacity: 0.7; margin-top: 4px; }

.photo-counter { color: var(--color-text-muted); font-size: 0.85rem; margin-top: var(--space-2); }
.photo-counter.ok { color: #10b981; font-weight: 600; }

.review-block {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}
.review-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-2) 0;
  border-bottom: 1px dashed var(--color-border);
  font-size: 0.9rem;
}
.review-row:last-child { border-bottom: none; }
.review-row strong { color: var(--color-text-muted); font-weight: 500; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; flex-shrink: 0; }
.review-chips { display: flex; flex-wrap: wrap; gap: 4px; justify-content: flex-end; }
.review-chip {
  background: rgba(193, 216, 47, 0.1);
  color: var(--color-primary);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
}

.status-tag {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}
.status-tag.draft { background: rgba(140,140,140,0.15); color: var(--color-text-muted); }
.status-tag.pending { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.status-tag.verified { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.status-tag.rejected { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.warning-note {
  background: rgba(245, 158, 11, 0.06);
  border-left: 3px solid #f59e0b;
  padding: var(--space-3);
  margin-bottom: var(--space-4);
  font-size: 0.85rem;
  color: #f59e0b;
  border-radius: 0 8px 8px 0;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  margin-top: var(--space-5);
}

/* Estado claramente deshabilitado para que el usuario lo entienda */
.btn-disabled-clear,
.btn-disabled-clear:hover {
  background: var(--color-bg-elevated, #e5e5e5) !important;
  color: var(--color-text-muted, #999) !important;
  border-color: var(--color-border, #ddd) !important;
  cursor: not-allowed !important;
  opacity: 0.7;
  box-shadow: none !important;
  transform: none !important;
}

.form-error {
  color: #ef4444;
  font-size: 0.85rem;
  margin: var(--space-3) 0 0;
}

.loading-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-8);
}

@media (max-width: 720px) {
  .form-grid { grid-template-columns: 1fr; }
  .map-container { height: 200px; }
}

/* ── Mapa de Panamá (step 3) ── */
.map-wrapper {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  position: relative;
}
.map-container {
  width: 100%;
  height: 280px;
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

/* Slider de radio */
.range-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  outline: none;
  margin-top: 8px;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(193,216,47,0.3);
}
.range-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(193,216,47,0.3);
}

/* Leaflet (no scoped — los nodos los inyecta Leaflet en body / dentro) */
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
