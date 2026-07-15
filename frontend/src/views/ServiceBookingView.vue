<template>
  <div class="svc-booking-page">
    <div class="container">
      <router-link to="/packs" class="back-link">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al catálogo
      </router-link>

      <div class="sb-layout">
        <!-- ── Form ── -->
        <div class="sb-form">
          <h1 class="section-title">Reservar servicios</h1>
          <p class="sb-intro">Arma tu producción con proveedores verificados. No necesitas un DJ — pero si quieres, puedes agregar uno.</p>

          <!-- 1. Producción -->
          <section class="sb-section">
            <h2 class="sb-h">
              <span class="sb-step">1</span> Elige tu producción
            </h2>

            <div class="prod-cats">
              <button v-for="c in prodCategories" :key="c.value" type="button"
                class="prod-cat-chip" :class="{ active: prodCategory === c.value }"
                @click="prodCategory = c.value">
                <span class="pc-icon" v-html="c.icon"></span> {{ c.label }}
              </button>
            </div>

            <div class="prod-size-bar">
              <span v-if="form.guest_count && suggestedEventSize && !showAllSizes" class="prod-size-hint">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
                Packs para ~{{ form.guest_count }} personas ({{ suggestedSizeLabel }})
              </span>
              <label class="prod-size-toggle">
                <input type="checkbox" v-model="showAllSizes" /> Ver todos los tamaños
              </label>
            </div>

            <div v-if="prodLoading" class="prod-loading"><span class="spinner"></span> Buscando proveedores…</div>

            <div v-else-if="prodPacks.length" class="packs-grid">
              <button type="button" v-for="p in prodPacks" :key="p.id"
                class="pack-card" :class="{ active: isInCart(p.id) }" @click="toggleCartPack(p)">
                <span v-if="p.includes_dj" class="pack-tag pack-tag-dj">Incluye DJ</span>
                <div class="pack-name">{{ p.name }}</div>
                <div class="prod-vendor">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18"/><path d="M5 21V7l8-4v18"/><path d="M19 21V11l-6-4"/></svg>
                  {{ p.vendor?.name }}<template v-if="p.vendor?.city"> · {{ p.vendor.city }}</template>
                </div>
                <div class="pack-price">${{ Number(p.price).toFixed(0) }}<span v-if="p.event_size_display" class="pack-sz">· {{ p.event_size_display }}</span></div>
                <div class="pack-check">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
              </button>
            </div>

            <div v-else class="prod-empty">
              <p>Aún no hay proveedores de <strong>{{ currentCatLabel }}</strong> publicados<template v-if="!showAllSizes && suggestedEventSize"> para ese tamaño</template>.</p>
              <button v-if="!showAllSizes" type="button" class="btn btn-ghost btn-sm" @click="showAllSizes = true">Ver todos los tamaños</button>
            </div>
          </section>

          <!-- 2. Datos del evento -->
          <section class="sb-section">
            <h2 class="sb-h"><span class="sb-step">2</span> Datos del evento</h2>

            <div class="form-group">
              <label class="form-label">Tipo de evento</label>
              <select v-model="form.event_type" class="form-input">
                <option value="" disabled>Selecciona…</option>
                <option v-for="(label, val) in eventTypeLabels" :key="val" :value="val">{{ label }}</option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Fecha</label>
                <input v-model="form.event_date" type="date" class="form-input" :min="minDate" @change="onDateChange">
              </div>
              <div class="form-group">
                <label class="form-label">Hora de inicio</label>
                <select v-model="form.event_time_start" class="form-input" @change="onTimeStartChange">
                  <option value="" disabled>Elige una hora</option>
                  <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Hora final</label>
                <select v-model="form.event_time_end" class="form-input" :disabled="!form.event_time_start">
                  <option value="" disabled>{{ form.event_time_start ? 'Elige la hora de fin' : 'Primero la hora de inicio' }}</option>
                  <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Invitados aprox.</label>
                <input v-model.number="form.guest_count" type="number" class="form-input" placeholder="150" min="1">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Ciudad</label>
              <select v-model="form.event_city" class="form-input">
                <option value="" disabled>Elige la ciudad</option>
                <option v-for="c in panamaCities" :key="c" :value="c">{{ c }}</option>
              </select>
              <CityPickerMap v-model="form.event_city" />
            </div>

            <div class="form-row">
              <div class="form-group" style="flex:2">
                <label class="form-label">Ubicación específica</label>
                <input v-model="form.event_location" type="text" class="form-input" placeholder="Ej: Hotel Riu, Salón Bella Vista">
              </div>
              <div class="form-group" style="flex:1">
                <label class="form-label">País</label>
                <input value="Panamá" type="text" class="form-input input-locked" readonly disabled>
              </div>
            </div>
          </section>

          <!-- 3. ¿Necesitas un DJ? -->
          <section class="sb-section">
            <h2 class="sb-h"><span class="sb-step">3</span> ¿Necesitas un DJ?</h2>
            <p class="sb-sub">Opcional. Puedes reservar solo los servicios, o sumar un DJ disponible para tu fecha.</p>

            <div class="dj-toggle">
              <button type="button" class="dj-opt" :class="{ active: !wantsDj }" @click="setWantsDj(false)">
                No, solo servicios
              </button>
              <button type="button" class="dj-opt" :class="{ active: wantsDj }" @click="setWantsDj(true)">
                Sí, agregar un DJ
              </button>
            </div>

            <div v-if="wantsDj" class="dj-picker">
              <p v-if="!form.event_date" class="dj-hint">Elige la fecha del evento (paso 2) para ver los DJs libres.</p>
              <div v-else-if="djLoading" class="prod-loading"><span class="spinner"></span> Buscando DJs disponibles…</div>
              <template v-else>
                <p v-if="djList.length" class="dj-hint">DJs libres el {{ formatDate(form.event_date) }}:</p>
                <div v-if="djList.length" class="dj-grid">
                  <button type="button" v-for="d in djList" :key="d.id"
                    class="dj-card" :class="{ active: selectedDjId === d.id }" @click="toggleDj(d)">
                    <img :src="d.cover_photo || defaultAvatar" :alt="d.stage_name" class="dj-thumb">
                    <div class="dj-info">
                      <span class="dj-name">{{ d.stage_name }}</span>
                      <span class="dj-meta">
                        <span class="dj-badge" :class="'lvl-' + d.talent_level">{{ levelLabel(d.talent_level) }}</span>
                        <span v-if="d.hourly_rate">${{ Number(d.hourly_rate).toFixed(0) }}/h</span>
                      </span>
                    </div>
                    <div class="dj-check">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                  </button>
                </div>
                <div v-else class="prod-empty">
                  <p>No hay DJs libres para esa fecha, o aún no hay DJs cargados. Puedes continuar solo con los servicios.</p>
                </div>
              </template>
            </div>
          </section>

          <div v-if="error" class="error-msg">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            {{ error }}
          </div>

          <button type="button" class="btn btn-primary btn-lg sb-submit" :disabled="submitting || !canSubmit" @click="handleSubmit">
            <span v-if="submitting" class="spinner"></span>
            <span v-else>Enviar solicitud</span>
          </button>
        </div>

        <!-- ── Sticky summary ── -->
        <aside class="sb-summary">
          <div class="summary-card glass">
            <h3>Tu reserva</h3>

            <div v-if="cartPacks.length" class="sum-block">
              <h4>Producción ({{ cartPacks.length }})</h4>
              <div v-for="p in cartPacks" :key="p.id" class="sum-line">
                <span class="sum-line-name">{{ p.name }} <small>· {{ p.vendor?.name }}</small></span>
                <span class="sum-line-price">${{ Number(p.price).toFixed(0) }}</span>
                <button type="button" class="sum-remove" @click="toggleCartPack(p)" aria-label="Quitar">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
            <p v-else class="sum-empty">Aún no agregaste servicios.</p>

            <div v-if="selectedDj" class="sum-block">
              <h4>DJ</h4>
              <div class="sum-line">
                <span class="sum-line-name">{{ selectedDj.stage_name }}</span>
                <span class="sum-line-price" v-if="djEstimate">${{ djEstimate.toFixed(0) }}</span>
              </div>
            </div>

            <div class="summary-divider"></div>
            <div class="sum-total">
              <span>Estimado</span>
              <span>${{ estimatedTotal.toFixed(0) }}</span>
            </div>
            <p class="sum-note">* Precio de referencia. El fee de gestión y el ITBMS se calculan al confirmar.</p>
          </div>
        </aside>
      </div>

      <!-- Success -->
      <div v-if="showSuccess" class="modal-overlay" @click.self="goDashboard">
        <div class="modal-card glass">
          <div class="success-icon">
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h2>¡Solicitud enviada!</h2>
          <p>Tu reserva de servicios fue creada. Los proveedores fueron notificados.</p>
          <div v-if="createdBooking?.booking_code" class="booking-code-block">
            <span class="code-label">Código de tu reserva</span>
            <code class="booking-code">{{ createdBooking.booking_code }}</code>
          </div>
          <div v-if="packWarnings.length" class="pack-warn-block">
            <strong>Algunos servicios no se pudieron agregar:</strong>
            <ul><li v-for="(w, i) in packWarnings" :key="i">{{ w }}</li></ul>
          </div>
          <div class="modal-actions">
            <button class="btn btn-primary" @click="goDashboard">Ver mis reservas</button>
            <router-link to="/packs" class="btn btn-ghost">Seguir explorando</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import CityPickerMap from '@/components/common/CityPickerMap.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const panamaCities = [
  'Ciudad de Panamá', 'San Miguelito', 'David', 'Colón', 'Santiago', 'Chitré',
  'Penonomé', 'Aguadulce', 'La Chorrera', 'Arraiján', 'Bocas del Toro', 'Las Tablas',
]
const eventTypeLabels = {
  wedding: 'Boda', corporate: 'Corporativo', birthday: 'Cumpleaños',
  private: 'Fiesta Privada', festival: 'Festival', club: 'Club/Discoteca',
  anniversary: 'Aniversario', graduation: 'Graduación', other: 'Otro',
}
const defaultAvatar = `data:image/svg+xml,${encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80"><rect fill="%23111" width="80" height="80"/><circle cx="40" cy="30" r="14" fill="%23C1D82F" opacity="0.3"/><ellipse cx="40" cy="62" rx="22" ry="14" fill="%23C1D82F" opacity="0.2"/></svg>')}`

const _pc = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
const prodCategories = [
  { value: 'sound',    label: 'Sonido',     icon: `${_pc}<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>` },
  { value: 'lights',   label: 'Luces',      icon: `${_pc}<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>` },
  { value: 'screens',  label: 'Pantallas',  icon: `${_pc}<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>` },
  { value: 'mics',     label: 'Micrófonos', icon: `${_pc}<path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>` },
  { value: 'dj_booth', label: 'DJ Booth',   icon: `${_pc}<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>` },
  { value: 'fx',       label: 'Efectos',    icon: `${_pc}<path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/></svg>` },
]
const SIZE_LABELS = { small: 'Hasta 80', medium: '80–300', large: '300+' }

const form = ref({
  event_type: '', event_date: '', event_time_start: '', event_time_end: '',
  event_city: 'Ciudad de Panamá', event_location: '', guest_count: null, event_indoor: true,
})
const error = ref('')
const submitting = ref(false)
const showSuccess = ref(false)
const createdBooking = ref(null)
const packWarnings = ref([])

const minDate = computed(() => {
  const d = new Date(); d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
})

const timeOptions = (() => {
  const opts = []
  for (let m = 0; m < 24 * 60; m += 30) {
    const h = Math.floor(m / 60), mm = m % 60
    const value = `${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
    const h12 = h % 12 === 0 ? 12 : h % 12
    const label = `${h12}:${String(mm).padStart(2, '0')} ${h < 12 ? 'AM' : 'PM'}`
    opts.push({ value, label })
  }
  return opts
})()

function onTimeStartChange() {
  // Sugerir 4h por defecto si no hay fin
  if (form.value.event_time_start && !form.value.event_time_end) {
    const [sh, sm] = form.value.event_time_start.split(':').map(Number)
    let end = sh * 60 + sm + 240
    if (end >= 1440) end -= 1440
    form.value.event_time_end = `${String(Math.floor(end / 60)).padStart(2, '0')}:${String(end % 60).padStart(2, '0')}`
  }
}

const durationHours = computed(() => {
  if (!form.value.event_time_start || !form.value.event_time_end) return 0
  const [sh, sm] = form.value.event_time_start.split(':').map(Number)
  const [eh, em] = form.value.event_time_end.split(':').map(Number)
  let diff = (eh * 60 + em) - (sh * 60 + sm)
  if (diff <= 0) diff += 1440
  return Math.round((diff / 60) * 100) / 100
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d + 'T12:00:00').toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'long' })
}

// ── Catálogo de producción ──
const prodCategory = ref('sound')
const prodPacks = ref([])
const prodLoading = ref(false)
const showAllSizes = ref(false)
const suggestedEventSize = computed(() => {
  const g = form.value.guest_count || 0
  if (!g) return ''
  if (g < 80) return 'small'
  if (g <= 300) return 'medium'
  return 'large'
})
const suggestedSizeLabel = computed(() => SIZE_LABELS[suggestedEventSize.value] || '')
const currentCatLabel = computed(() => prodCategories.find(c => c.value === prodCategory.value)?.label || '')

async function fetchProdPacks() {
  prodLoading.value = true
  try {
    const params = { category: prodCategory.value }
    if (!showAllSizes.value && suggestedEventSize.value) params.event_size = suggestedEventSize.value
    const { data } = await api.get('/production-packs/', { params })
    prodPacks.value = Array.isArray(data) ? data : (data.results || [])
  } catch { prodPacks.value = [] } finally { prodLoading.value = false }
}
watch([prodCategory, showAllSizes, suggestedEventSize], fetchProdPacks)

const cartPacks = ref([])
function isInCart(id) { return cartPacks.value.some(p => p.id === id) }
function toggleCartPack(p) {
  const i = cartPacks.value.findIndex(x => x.id === p.id)
  if (i >= 0) cartPacks.value.splice(i, 1)
  else cartPacks.value.push(p)
}
const cartSubtotal = computed(() => cartPacks.value.reduce((s, p) => s + Number(p.price || 0), 0))

// ── DJ opcional ──
const wantsDj = ref(false)
const djList = ref([])
const djLoading = ref(false)
const selectedDjId = ref(null)
const selectedDj = computed(() => djList.value.find(d => d.id === selectedDjId.value) || null)
const djEstimate = computed(() => {
  if (!selectedDj.value?.hourly_rate || durationHours.value <= 0) return 0
  return Number(selectedDj.value.hourly_rate) * durationHours.value
})
const levelLabel = (l) => ({ premium: '★★ Premium', pro: '★ Pro', standard: 'Standard' }[l] || 'Standard')

function setWantsDj(v) {
  wantsDj.value = v
  if (!v) selectedDjId.value = null
  else if (form.value.event_date) fetchDjs()
}
function onDateChange() {
  if (wantsDj.value && form.value.event_date) fetchDjs()
}
async function fetchDjs() {
  if (!form.value.event_date) return
  djLoading.value = true
  try {
    const { data } = await api.get('/talents/', {
      params: { talent_type: 'dj', available_date: form.value.event_date, ordering: '-rating_avg' },
    })
    djList.value = data.results || data || []
  } catch { djList.value = [] } finally { djLoading.value = false }
}
function toggleDj(d) {
  selectedDjId.value = selectedDjId.value === d.id ? null : d.id
}

// ── Totales ──
const estimatedTotal = computed(() => cartSubtotal.value + djEstimate.value)

const canSubmit = computed(() =>
  cartPacks.value.length > 0 &&
  form.value.event_type && form.value.event_date &&
  form.value.event_time_start && form.value.event_time_end && form.value.event_location
)

function validate() {
  if (!cartPacks.value.length) return 'Agrega al menos un servicio de producción.'
  if (!form.value.event_type) return 'Selecciona el tipo de evento.'
  if (!form.value.event_date) return 'Selecciona la fecha.'
  if (!form.value.event_time_start || !form.value.event_time_end) return 'Selecciona la hora de inicio y fin.'
  if (!form.value.event_location) return 'Ingresa la ubicación.'
  return ''
}

async function handleSubmit() {
  const v = validate()
  if (v) { error.value = v; return }
  if (!auth.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  error.value = ''
  submitting.value = true
  try {
    const payload = {
      event_type: form.value.event_type,
      event_date: form.value.event_date,
      event_time_start: form.value.event_time_start,
      event_time_end: form.value.event_time_end,
      event_duration_hours: durationHours.value,
      event_location: form.value.event_location,
      event_city: form.value.event_city,
      event_indoor: form.value.event_indoor,
      guest_count: form.value.guest_count || 0,
      additional_services: [],
    }
    // Si el cliente eligió un DJ, es una reserva normal con DJ + packs.
    // Si no, es una reserva de solo-servicios (talent omitido → NULL).
    if (wantsDj.value && selectedDjId.value) payload.talent = selectedDjId.value

    const { data } = await api.post('/bookings/create/', payload)
    createdBooking.value = data

    packWarnings.value = []
    for (const p of cartPacks.value) {
      try {
        await api.post(`/bookings/${data.id}/packs/`, { pack_id: p.id })
      } catch (e) {
        packWarnings.value.push(e.response?.data?.detail || `No se pudo agregar "${p.name}".`)
      }
    }
    showSuccess.value = true
  } catch (e) {
    const d = e.response?.data
    error.value = d ? Object.values(d).flat().join(' ') : 'Error al enviar la solicitud.'
  } finally {
    submitting.value = false
  }
}

function goDashboard() {
  router.push(auth.user?.role === 'partner' ? '/partner' : '/dashboard')
}

onMounted(() => {
  fetchProdPacks()
  // Pre-cargar un pack si viene ?pack=ID desde el catálogo
  const pre = route.query.pack
  if (pre) {
    api.get(`/production-packs/${pre}/`).then(({ data }) => {
      if (data && data.id) cartPacks.value.push(data)
    }).catch(() => {})
  }
})
</script>

<style scoped>
.svc-booking-page { padding-top: var(--space-4); padding-bottom: var(--space-16); min-height: 100vh; }
.back-link {
  display: inline-flex; align-items: center; gap: var(--space-2);
  color: var(--color-text-muted); font-size: var(--font-size-sm); margin-bottom: var(--space-6);
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--color-primary); }
.sb-layout { display: grid; grid-template-columns: 1fr 340px; gap: var(--space-10); align-items: start; }
.sb-intro { color: var(--color-text-muted); margin: var(--space-2) 0 var(--space-6); }

.sb-section {
  border: 1px solid var(--color-border); border-radius: var(--radius-xl);
  padding: var(--space-6); margin-bottom: var(--space-5); background: var(--color-bg-card);
}
.sb-h { display: flex; align-items: center; gap: var(--space-3); font-size: var(--font-size-lg); margin-bottom: var(--space-4); }
.sb-step {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: var(--color-primary); color: var(--color-bg-primary);
  display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem;
}
.sb-sub { color: var(--color-text-muted); font-size: var(--font-size-sm); margin: -8px 0 var(--space-4); }

/* Form basics */
.form-group { display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-4); }
.form-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-secondary); }
.form-input {
  background: var(--color-bg-elevated); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base); color: var(--color-text-primary); font-family: var(--font-body);
  transition: border-color var(--transition-fast);
}
.form-input:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-ultra-light); }
select.form-input { cursor: pointer; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-4); }
.input-locked { opacity: 0.7; cursor: not-allowed; border-style: dashed; }

/* Categorías + packs */
.prod-cats { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-4); }
.prod-cat-chip {
  display: inline-flex; align-items: center; gap: 6px; padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full); border: 1px solid var(--color-border);
  background: var(--color-bg-elevated); color: var(--color-text-secondary);
  font-size: var(--font-size-sm); font-family: var(--font-body); cursor: pointer; transition: all var(--transition-fast);
}
.prod-cat-chip:hover { border-color: var(--color-primary); color: var(--color-primary); }
.prod-cat-chip.active { border-color: var(--color-primary); background: var(--color-primary); color: var(--color-bg-primary); font-weight: 600; }
.pc-icon { display: inline-flex; align-items: center; }

.prod-size-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-4); }
.prod-size-hint { display: inline-flex; align-items: center; gap: 5px; font-size: var(--font-size-xs); color: var(--color-text-muted); }
.prod-size-toggle { display: inline-flex; align-items: center; gap: 6px; font-size: var(--font-size-xs); color: var(--color-text-secondary); cursor: pointer; user-select: none; }
.prod-size-toggle input { accent-color: var(--color-primary); cursor: pointer; }
.prod-loading { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-6); color: var(--color-text-muted); font-size: var(--font-size-sm); }

.packs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: var(--space-3); }
.pack-card {
  position: relative; text-align: left; cursor: pointer; padding: var(--space-4);
  border-radius: var(--radius-lg); border: 1.5px solid var(--color-border);
  background: var(--color-bg-elevated); transition: all var(--transition-fast); font-family: var(--font-body);
}
.pack-card:hover { border-color: var(--color-primary); }
.pack-card.active { border-color: var(--color-primary); background: var(--color-primary-ultra-light); box-shadow: 0 0 0 3px var(--color-primary-ultra-light); }
.pack-tag { position: absolute; top: -9px; right: 10px; padding: 2px 8px; border-radius: 999px; font-size: 0.62rem; font-weight: 800; }
.pack-tag-dj { background: var(--color-accent); color: #fff; }
.pack-name { font-weight: 700; color: var(--color-text-primary); margin-bottom: 2px; }
.prod-vendor { display: flex; align-items: center; gap: 5px; font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 2px 0 var(--space-2); }
.prod-vendor svg { color: var(--color-primary); flex-shrink: 0; }
.pack-price { font-size: var(--font-size-lg); font-weight: 700; color: var(--color-text-primary); }
.pack-sz { font-size: var(--font-size-sm); color: var(--color-text-muted); font-weight: 500; margin-left: 4px; }
.pack-check {
  position: absolute; top: 10px; right: 10px; width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; border: 1.5px solid var(--color-border);
  color: transparent; background: var(--color-bg-card); transition: all var(--transition-fast);
}
.pack-card.active .pack-check { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-bg-primary); }

.prod-empty { text-align: center; padding: var(--space-6); border: 1px dashed var(--color-border); border-radius: var(--radius-lg); display: flex; flex-direction: column; gap: var(--space-2); align-items: center; }
.prod-empty p { font-size: var(--font-size-sm); color: var(--color-text-secondary); margin: 0; }

/* DJ picker */
.dj-toggle { display: flex; gap: var(--space-2); margin-bottom: var(--space-4); }
.dj-opt {
  flex: 1; padding: var(--space-3); border-radius: var(--radius-lg); border: 1px solid var(--color-border);
  background: var(--color-bg-elevated); color: var(--color-text-secondary); font-family: var(--font-body);
  font-size: var(--font-size-sm); cursor: pointer; transition: all var(--transition-fast);
}
.dj-opt.active { border-color: var(--color-primary); color: var(--color-primary); background: var(--color-primary-ultra-light); font-weight: 600; }
.dj-hint { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-3); }
.dj-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-3); }
.dj-card {
  position: relative; display: flex; align-items: center; gap: var(--space-3); text-align: left; cursor: pointer;
  padding: var(--space-3); border-radius: var(--radius-lg); border: 1.5px solid var(--color-border);
  background: var(--color-bg-elevated); transition: all var(--transition-fast); font-family: var(--font-body);
}
.dj-card:hover { border-color: var(--color-primary); }
.dj-card.active { border-color: var(--color-primary); background: var(--color-primary-ultra-light); }
.dj-thumb { width: 46px; height: 46px; border-radius: var(--radius-md); object-fit: cover; flex-shrink: 0; }
.dj-info { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.dj-name { font-weight: 700; color: var(--color-text-primary); font-size: var(--font-size-sm); }
.dj-meta { display: flex; align-items: center; gap: 6px; font-size: var(--font-size-xs); color: var(--color-text-muted); }
.dj-badge { padding: 1px 6px; border-radius: 999px; font-size: 0.6rem; font-weight: 700; border: 1px solid var(--color-border); }
.dj-badge.lvl-premium { border-color: var(--color-accent); color: var(--color-accent); }
.dj-badge.lvl-pro { border-color: var(--color-primary); color: var(--color-primary); }
.dj-check {
  position: absolute; top: 8px; right: 8px; width: 20px; height: 20px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; border: 1.5px solid var(--color-border);
  color: transparent; background: var(--color-bg-card);
}
.dj-card.active .dj-check { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-bg-primary); }

/* Submit */
.sb-submit { width: 100%; justify-content: center; margin-top: var(--space-2); }
.error-msg {
  display: flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-4);
  background: rgba(232,93,74,0.1); border: 1px solid rgba(232,93,74,0.3); border-radius: var(--radius-lg);
  color: var(--color-accent); font-size: var(--font-size-sm); margin-bottom: var(--space-4);
}
.spinner { width: 20px; height: 20px; border: 2px solid transparent; border-top-color: currentColor; border-radius: 50%; animation: spin 0.6s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Summary */
.sb-summary { position: sticky; top: 100px; }
.summary-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.summary-card h3 { font-size: var(--font-size-lg); margin-bottom: var(--space-4); }
.sum-block { margin-bottom: var(--space-4); }
.sum-block h4 { font-size: var(--font-size-xs); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: var(--space-2); }
.sum-line { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); }
.sum-line-name { flex: 1; font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.sum-line-name small { color: var(--color-text-muted); }
.sum-line-price { font-weight: 700; color: var(--color-text-primary); font-size: var(--font-size-sm); }
.sum-remove { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; border: none; background: transparent; color: var(--color-text-muted); cursor: pointer; }
.sum-remove:hover { background: rgba(232,93,74,0.12); color: var(--color-accent); }
.sum-empty { font-size: var(--font-size-sm); color: var(--color-text-muted); }
.summary-divider { height: 1px; background: var(--color-border); margin: var(--space-4) 0; }
.sum-total { display: flex; justify-content: space-between; font-size: var(--font-size-lg); font-weight: 700; color: var(--color-primary); }
.sum-note { font-size: var(--font-size-xs); color: var(--color-text-muted); font-style: italic; margin-top: var(--space-2); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: var(--space-6); }
.modal-card { max-width: 460px; width: 100%; padding: var(--space-8); border-radius: var(--radius-2xl); text-align: center; }
.success-icon { display: flex; justify-content: center; margin-bottom: var(--space-4); }
.modal-card h2 { margin-bottom: var(--space-3); }
.modal-card p { color: var(--color-text-secondary); margin-bottom: var(--space-4); }
.booking-code-block { padding: var(--space-4); background: var(--color-bg-card); border: 1px dashed var(--color-border); border-radius: var(--radius-lg); margin: var(--space-4) 0; }
.code-label { display: block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; color: var(--color-text-muted); margin-bottom: 6px; }
.booking-code { font-family: 'Courier New', monospace; font-size: 1.3rem; font-weight: 700; color: var(--color-primary); letter-spacing: 1px; }
.pack-warn-block { text-align: left; padding: var(--space-3) var(--space-4); background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3); border-radius: var(--radius-lg); margin-bottom: var(--space-4); font-size: 0.8rem; color: var(--color-text-secondary); }
.pack-warn-block strong { color: #f59e0b; display: block; margin-bottom: 4px; }
.pack-warn-block ul { margin: 0; padding-left: var(--space-4); }
.modal-actions { display: flex; flex-direction: column; gap: var(--space-3); }

@media (max-width: 900px) {
  .sb-layout { grid-template-columns: 1fr; }
  .sb-summary { position: static; order: -1; }
}
</style>
