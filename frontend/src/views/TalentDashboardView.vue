<template>
  <div class="talent-dash" :style="{ paddingTop: '100px' }">
    <div class="container">
      <!-- Header -->
      <header class="dash-header">
        <div class="dash-header-left">
          <h1 class="section-title">Panel de <span class="text-gradient">Talento</span></h1>
          <p class="section-subtitle">Gestiona tu perfil, reservas y disponibilidad</p>
        </div>
        <div class="dash-header-actions">
          <router-link to="/search" class="btn btn-secondary btn-sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            Ver mi perfil público
          </router-link>
        </div>
      </header>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card" v-for="s in statsCards" :key="s.label">
          <div class="stat-icon" :style="{ background: s.bg }">
            <span v-html="s.icon"></span>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ s.value }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <nav class="dash-tabs">
        <button v-for="t in tabs" :key="t.key" :class="['tab-btn', { active: activeTab === t.key }]" @click="activeTab = t.key">
          <span v-html="t.icon"></span>
          {{ t.label }}
          <span v-if="t.badge" class="tab-badge">{{ t.badge }}</span>
        </button>
      </nav>

      <!-- Tab Content -->
      <div class="tab-content">

        <!-- ═══ Solicitudes Pendientes ═══ -->
        <section v-if="activeTab === 'requests'" class="tab-panel animate-fade-in">
          <div v-if="pendingRequests.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            <p>No tienes solicitudes pendientes</p>
          </div>
          <div v-else class="request-list">
            <div v-for="b in pendingRequests" :key="b.id" class="request-card glass">
              <div class="request-header">
                <div class="request-client">
                  <div class="client-avatar">{{ b.client_name?.[0] || '?' }}</div>
                  <div>
                    <strong>{{ b.client_name }}</strong>
                    <span class="request-type badge">{{ b.event_type_display }}</span>
                  </div>
                </div>
                <span class="request-date">{{ formatDate(b.event_date) }}</span>
              </div>
              <div class="request-details">
                <div class="detail-chip"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg> {{ b.event_location || b.event_city }}</div>
                <div class="detail-chip"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> {{ b.event_time_start }} - {{ b.event_time_end }}</div>
                <div class="detail-chip"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/></svg> {{ b.guest_count }} personas</div>
                <div v-if="b.precio_estimado" class="detail-chip price"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg> ${{ b.precio_estimado }}</div>
              </div>
              <p v-if="b.description" class="request-desc">{{ b.description }}</p>

              <!-- Adjust Price -->
              <div class="adjust-section" v-if="adjustingId === b.id">
                <div class="adjust-row">
                  <label class="label">Precio propuesto ($)</label>
                  <input v-model.number="adjustPrice" type="number" class="input-field" placeholder="Ej: 500" />
                </div>
                <div class="adjust-row">
                  <label class="label">Notas al cliente</label>
                  <textarea v-model="adjustNotes" class="input-field" rows="2" placeholder="Explica el ajuste..."></textarea>
                </div>
              </div>

              <div class="request-actions">
                <button class="btn btn-primary btn-sm" @click="handleRequest(b.id, 'aceptada')" :disabled="actionLoading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                  Aceptar
                </button>
                <button class="btn btn-outline btn-sm" @click="toggleAdjust(b)" :disabled="actionLoading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  {{ adjustingId === b.id ? 'Enviar ajuste' : 'Ajustar' }}
                </button>
                <button class="btn btn-ghost btn-sm reject-btn" @click="handleRequest(b.id, 'rechazada')" :disabled="actionLoading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Rechazar
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- ═══ Mis Reservas ═══ -->
        <section v-if="activeTab === 'bookings'" class="tab-panel animate-fade-in">
          <div v-if="allBookings.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <p>No tienes reservas aún</p>
          </div>
          <div v-else class="bookings-table">
            <div class="table-header">
              <span>Cliente</span><span>Evento</span><span>Fecha</span><span>Monto</span><span>Estado</span><span></span>
            </div>
            <div v-for="b in allBookings" :key="b.id" class="table-row" @click="$router.push(`/dashboard/bookings/${b.id}`)">
              <span class="cell-client">{{ b.client_name }}</span>
              <span>{{ b.event_type_display }}</span>
              <span>{{ formatDate(b.event_date) }}</span>
              <span class="cell-price">${{ b.quoted_price || b.precio_estimado || '—' }}</span>
              <span><span :class="['badge', statusBadge(b.status)]">{{ b.status_display }}</span></span>
              <span class="cell-arrow">→</span>
            </div>
          </div>
        </section>

        <!-- ═══ Ingresos ═══ -->
        <section v-if="activeTab === 'earnings'" class="tab-panel animate-fade-in">
          <div class="earnings-grid">
            <div class="earnings-card glass">
              <h3>Ingresos Totales</h3>
              <p class="earnings-amount text-gradient">${{ totalEarnings.toFixed(2) }}</p>
              <span class="earnings-sub">De {{ completedCount }} eventos completados</span>
            </div>
            <div class="earnings-card glass">
              <h3>Pendiente por cobrar</h3>
              <p class="earnings-amount" style="color: var(--color-warning)">${{ pendingEarnings.toFixed(2) }}</p>
              <span class="earnings-sub">Reservas activas</span>
            </div>
            <div class="earnings-card glass">
              <h3>Rating Promedio</h3>
              <p class="earnings-amount text-gradient">{{ profile?.rating_avg || '0.00' }} <span style="font-size:0.5em">★</span></p>
              <span class="earnings-sub">{{ profile?.total_reviews || 0 }} reseñas</span>
            </div>
          </div>
        </section>

        <!-- ═══ Calendario ═══ -->
        <section v-if="activeTab === 'calendar'" class="tab-panel animate-fade-in">
          <div class="calendar-container glass">
            <div class="calendar-header">
              <button class="btn btn-ghost btn-sm" @click="changeMonth(-1)">← Anterior</button>
              <h3>{{ monthNames[calMonth] }} {{ calYear }}</h3>
              <button class="btn btn-ghost btn-sm" @click="changeMonth(1)">Siguiente →</button>
            </div>
            <div class="calendar-weekdays">
              <span v-for="d in ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']" :key="d">{{ d }}</span>
            </div>
            <div class="calendar-grid">
              <div v-for="(day, i) in calendarDays" :key="i"
                :class="['cal-day', { 'other-month': !day.current, booked: day.status === 'booked', blocked: day.status === 'blocked', available: day.status === 'available', today: day.isToday }]"
                @click="day.current && toggleAvailability(day)">
                <span class="day-num">{{ day.day }}</span>
                <span v-if="day.status === 'booked'" class="day-tag">Reservado</span>
                <span v-else-if="day.status === 'blocked'" class="day-tag">Bloqueado</span>
              </div>
            </div>
            <div class="calendar-legend">
              <span class="legend-item"><span class="legend-dot" style="background: var(--color-primary)"></span> Disponible</span>
              <span class="legend-item"><span class="legend-dot" style="background: var(--color-accent)"></span> Reservado</span>
              <span class="legend-item"><span class="legend-dot" style="background: var(--color-text-muted)"></span> Bloqueado</span>
            </div>
          </div>
        </section>

        <!-- ═══ Editar Perfil ═══ -->
        <section v-if="activeTab === 'profile'" class="tab-panel animate-fade-in">
          <form @submit.prevent="saveProfile" class="profile-form">
            <!-- Cover Photo Upload -->
            <div class="cover-upload-section">
              <label class="label">Foto de Portada</label>
              <div class="cover-upload-area" @click="$refs.coverInput.click()" @dragover.prevent @drop.prevent="handleCoverDrop">
                <img v-if="coverPreview || profile?.cover_photo" :src="coverPreview || profile?.cover_photo" class="cover-preview" />
                <div v-else class="cover-placeholder">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  <p>Haz clic o arrastra una imagen aquí</p>
                  <span class="text-muted">JPG, PNG o WebP — máx 5MB</span>
                </div>
              </div>
              <input ref="coverInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleCoverSelect" />
              <button v-if="coverFile" type="button" class="btn btn-primary btn-sm" style="margin-top: var(--space-3)" @click="uploadCover" :disabled="uploadingCover">
                {{ uploadingCover ? 'Subiendo...' : '📷 Subir Foto de Portada' }}
              </button>
            </div>

            <div class="form-grid">
              <div class="form-group full">
                <label class="label">Nombre Artístico</label>
                <input v-model="profileForm.stage_name" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">Tipo de Talento</label>
                <select v-model="profileForm.talent_type" class="input-field">
                  <option value="dj">DJ</option>
                  <option value="musician">Músico</option>
                  <option value="band">Banda</option>
                </select>
              </div>
              <div class="form-group">
                <label class="label">Tarifa por Hora ($)</label>
                <input v-model.number="profileForm.hourly_rate" type="number" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">Ciudad</label>
                <input v-model="profileForm.city" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">País</label>
                <input v-model="profileForm.country" class="input-field" />
              </div>
              <div class="form-group full">
                <label class="label">Tagline</label>
                <input v-model="profileForm.tagline" class="input-field" placeholder="Frase corta que te describe" />
              </div>
              <div class="form-group full">
                <label class="label">Descripción / Biografía</label>
                <textarea v-model="profileForm.description" class="input-field" rows="4"></textarea>
              </div>
              <div class="form-group">
                <label class="label">Años de Experiencia</label>
                <input v-model.number="profileForm.experience_years" type="number" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">Instagram</label>
                <input v-model="profileForm.instagram" class="input-field" placeholder="@usuario" />
              </div>
              <div class="form-group">
                <label class="label">SoundCloud</label>
                <input v-model="profileForm.soundcloud" class="input-field" placeholder="https://..." />
              </div>
              <div class="form-group">
                <label class="label">Spotify</label>
                <input v-model="profileForm.spotify" class="input-field" placeholder="https://..." />
              </div>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="saving">
                {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
              <span v-if="saveSuccess" class="save-msg">✓ Perfil actualizado</span>
            </div>
          </form>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const activeTab = ref('requests')
const bookings = ref([])
const profile = ref(null)
const availability = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const adjustingId = ref(null)
const adjustPrice = ref(null)
const adjustNotes = ref('')
const saving = ref(false)
const saveSuccess = ref(false)
const coverFile = ref(null)
const coverPreview = ref(null)
const uploadingCover = ref(false)

function handleCoverSelect(e) {
  const file = e.target.files?.[0]
  if (file) setCoverFile(file)
}

function handleCoverDrop(e) {
  const file = e.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) setCoverFile(file)
}

function setCoverFile(file) {
  if (file.size > 5 * 1024 * 1024) {
    alert('La imagen no puede superar 5MB.')
    return
  }
  coverFile.value = file
  coverPreview.value = URL.createObjectURL(file)
}

async function uploadCover() {
  if (!coverFile.value) return
  uploadingCover.value = true
  try {
    const formData = new FormData()
    formData.append('cover_photo', coverFile.value)
    const { data } = await api.post('/talents/me/cover-photo/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (profile.value) profile.value.cover_photo = data.cover_photo
    coverFile.value = null
    saveSuccess.value = true
    setTimeout(() => saveSuccess.value = false, 3000)
  } catch (e) {
    alert('Error al subir la foto: ' + (e.response?.data?.error || 'Intenta de nuevo'))
  }
  uploadingCover.value = false
}

const calMonth = ref(new Date().getMonth())
const calYear = ref(new Date().getFullYear())
const monthNames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const profileForm = reactive({
  stage_name: '', talent_type: 'dj', hourly_rate: 0, city: '', country: 'Venezuela',
  tagline: '', description: '', experience_years: 0, instagram: '', soundcloud: '', spotify: ''
})

// Computed
const pendingRequests = computed(() => bookings.value.filter(b => ['solicitud_enviada','pendiente_respuesta'].includes(b.status)))
const allBookings = computed(() => bookings.value)
const completedBookings = computed(() => bookings.value.filter(b => b.status === 'completada'))
const completedCount = computed(() => completedBookings.value.length)
const totalEarnings = computed(() => completedBookings.value.reduce((sum, b) => sum + parseFloat(b.quoted_price || b.precio_estimado || 0), 0) * 0.85)
const pendingEarnings = computed(() => bookings.value.filter(b => ['confirmada','pendiente_pago'].includes(b.status)).reduce((sum, b) => sum + parseFloat(b.quoted_price || b.precio_estimado || 0), 0) * 0.85)

const tabs = computed(() => [
  { key: 'requests', label: 'Solicitudes', badge: pendingRequests.value.length || null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>' },
  { key: 'bookings', label: 'Reservas', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>' },
  { key: 'earnings', label: 'Ingresos', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>' },
  { key: 'calendar', label: 'Calendario', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>' },
  { key: 'profile', label: 'Mi Perfil', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
])

const statsCards = computed(() => [
  { label: 'Solicitudes Pendientes', value: pendingRequests.value.length, bg: 'var(--color-primary-ultra-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>' },
  { label: 'Reservas Activas', value: bookings.value.filter(b => ['confirmada','pendiente_pago','aceptada'].includes(b.status)).length, bg: 'var(--color-accent-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>' },
  { label: 'Eventos Completados', value: completedCount.value, bg: 'var(--color-success-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>' },
  { label: 'Rating', value: (profile.value?.rating_avg || 0) + ' ★', bg: 'var(--color-warning-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' },
])

// Calendar
const calendarDays = computed(() => {
  const firstDay = new Date(calYear.value, calMonth.value, 1)
  const lastDay = new Date(calYear.value, calMonth.value + 1, 0)
  let startWeekday = firstDay.getDay() || 7 // Monday = 1
  const days = []
  const prevMonth = new Date(calYear.value, calMonth.value, 0)
  for (let i = startWeekday - 1; i > 0; i--) {
    days.push({ day: prevMonth.getDate() - i + 1, current: false, status: null, isToday: false, dateStr: '' })
  }
  const today = new Date()
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${calYear.value}-${String(calMonth.value + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const avail = availability.value.find(a => a.date === dateStr)
    const isToday = today.getFullYear() === calYear.value && today.getMonth() === calMonth.value && today.getDate() === d
    days.push({ day: d, current: true, status: avail?.status || null, isToday, dateStr })
  }
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    days.push({ day: i, current: false, status: null, isToday: false, dateStr: '' })
  }
  return days
})

function changeMonth(delta) {
  calMonth.value += delta
  if (calMonth.value > 11) { calMonth.value = 0; calYear.value++ }
  if (calMonth.value < 0) { calMonth.value = 11; calYear.value-- }
  fetchAvailability()
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-VE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function statusBadge(status) {
  const map = { solicitud_enviada: '', pendiente_respuesta: 'badge-warning', aceptada: 'badge-success', pendiente_pago: 'badge-warning', confirmada: 'badge-success', completada: 'badge-cyan', rechazada: 'badge-error', cancelada: 'badge-error' }
  return map[status] || ''
}

// Actions
async function handleRequest(bookingId, newStatus) {
  actionLoading.value = true
  try {
    const payload = { status: newStatus }
    if (adjustingId.value === bookingId && adjustPrice.value) {
      payload.quoted_price = adjustPrice.value
      payload.talent_notes = adjustNotes.value
    }
    await api.patch(`/bookings/${bookingId}/status/`, payload)
    await fetchBookings()
    adjustingId.value = null
    adjustPrice.value = null
    adjustNotes.value = ''
  } catch (e) {
    alert(e.response?.data?.error || 'Error al procesar la solicitud')
  }
  actionLoading.value = false
}

function toggleAdjust(booking) {
  if (adjustingId.value === booking.id) {
    handleRequest(booking.id, 'aceptada')
  } else {
    adjustingId.value = booking.id
    adjustPrice.value = parseFloat(booking.precio_estimado) || null
    adjustNotes.value = ''
  }
}

async function toggleAvailability(day) {
  if (!day.dateStr || !profile.value) return
  try {
    if (day.status === 'blocked') {
      await api.delete('/availability/manage/', { data: { date: day.dateStr } })
    } else if (!day.status || day.status === 'available') {
      await api.post('/availability/manage/', { date: day.dateStr, status: 'blocked' })
    }
    await fetchAvailability()
  } catch { /* silent */ }
}

async function saveProfile() {
  saving.value = true
  saveSuccess.value = false
  try {
    await api.patch('/talents/me/', profileForm)
    saveSuccess.value = true
    setTimeout(() => saveSuccess.value = false, 3000)
  } catch (e) {
    alert('Error al guardar: ' + (e.response?.data?.detail || 'Intenta de nuevo'))
  }
  saving.value = false
}

async function fetchBookings() {
  try {
    const { data } = await api.get('/bookings/')
    bookings.value = data
  } catch { /* silent */ }
}

async function fetchProfile() {
  try {
    const { data } = await api.get('/talents/me/')
    profile.value = data
    Object.keys(profileForm).forEach(k => { if (data[k] !== undefined) profileForm[k] = data[k] })
  } catch { /* silent */ }
}

async function fetchAvailability() {
  if (!profile.value) return
  try {
    const { data } = await api.get(`/talents/${profile.value.id}/availability/`)
    availability.value = data
  } catch { /* silent */ }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchBookings(), fetchProfile()])
  await fetchAvailability()
  loading.value = false
})
</script>

<style scoped>
.talent-dash { min-height: 100vh; padding-bottom: var(--space-16); }
.dash-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: var(--space-8); flex-wrap: wrap; gap: var(--space-4); }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-8); }
.stat-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-xl); transition: all var(--transition-base); }
.stat-card:hover { border-color: var(--color-border-hover); transform: translateY(-2px); }
.stat-icon { width: 48px; height: 48px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-family: var(--font-heading); font-size: var(--font-size-2xl); display: block; }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-muted); }

/* Tabs */
.dash-tabs { display: flex; gap: var(--space-1); background: var(--color-bg-card); border-radius: var(--radius-xl); padding: var(--space-1); margin-bottom: var(--space-6); overflow-x: auto; border: 1px solid var(--color-border); }
.tab-btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-5); border-radius: var(--radius-lg); font-size: var(--font-size-sm); font-weight: 500; color: var(--color-text-muted); background: transparent; border: none; cursor: pointer; transition: all var(--transition-fast); white-space: nowrap; }
.tab-btn:hover { color: var(--color-text-primary); background: rgba(255,255,255,0.03); }
.tab-btn.active { background: var(--gradient-primary); color: #000; font-weight: 600; }
.tab-badge { background: var(--color-accent); color: white; font-size: 10px; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

/* Empty State */
.empty-state { text-align: center; padding: var(--space-16) var(--space-4); color: var(--color-text-muted); }
.empty-state svg { margin: 0 auto var(--space-4); opacity: 0.4; }

/* Request Cards */
.request-list { display: flex; flex-direction: column; gap: var(--space-4); }
.request-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.request-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); flex-wrap: wrap; gap: var(--space-3); }
.request-client { display: flex; align-items: center; gap: var(--space-3); }
.client-avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--gradient-cta); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; }
.request-date { font-size: var(--font-size-sm); color: var(--color-primary); font-weight: 600; }
.request-details { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-3); }
.detail-chip { display: inline-flex; align-items: center; gap: var(--space-1); padding: var(--space-1) var(--space-3); background: rgba(255,255,255,0.04); border-radius: var(--radius-full); font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.detail-chip.price { color: var(--color-primary); background: var(--color-primary-ultra-light); font-weight: 600; }
.request-desc { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-4); font-style: italic; border-left: 2px solid var(--color-border); padding-left: var(--space-3); }
.request-actions { display: flex; gap: var(--space-3); flex-wrap: wrap; }
.reject-btn { color: var(--color-accent) !important; }
.reject-btn:hover { background: var(--color-accent-light) !important; }

/* Adjust Section */
.adjust-section { padding: var(--space-4); background: rgba(193,216,47,0.05); border: 1px solid var(--color-border); border-radius: var(--radius-lg); margin-bottom: var(--space-4); }
.adjust-row { margin-bottom: var(--space-3); }

/* Bookings Table */
.bookings-table { border: 1px solid var(--color-border); border-radius: var(--radius-xl); overflow: hidden; }
.table-header { display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 1fr 1.5fr 40px; padding: var(--space-3) var(--space-5); font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--color-border); }
.table-row { display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 1fr 1.5fr 40px; padding: var(--space-4) var(--space-5); align-items: center; font-size: var(--font-size-sm); border-bottom: 1px solid rgba(255,255,255,0.03); cursor: pointer; transition: background var(--transition-fast); }
.table-row:hover { background: var(--color-bg-card-hover); }
.cell-client { font-weight: 600; }
.cell-price { color: var(--color-primary); font-weight: 600; }
.cell-arrow { color: var(--color-text-muted); font-size: var(--font-size-lg); }

/* Earnings */
.earnings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--space-4); }
.earnings-card { padding: var(--space-8); border-radius: var(--radius-xl); text-align: center; }
.earnings-card h3 { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-3); font-family: var(--font-family); }
.earnings-amount { font-family: var(--font-heading); font-size: var(--font-size-4xl); margin-bottom: var(--space-2); }
.earnings-sub { font-size: var(--font-size-xs); color: var(--color-text-muted); }

/* Calendar */
.calendar-container { padding: var(--space-6); border-radius: var(--radius-xl); }
.calendar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.calendar-header h3 { font-family: var(--font-heading); font-size: var(--font-size-xl); }
.calendar-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: var(--font-size-xs); color: var(--color-text-muted); font-weight: 600; margin-bottom: var(--space-2); }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; }
.cal-day { aspect-ratio: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: var(--radius-md); font-size: var(--font-size-sm); cursor: pointer; transition: all var(--transition-fast); border: 1px solid transparent; position: relative; }
.cal-day:hover { background: rgba(255,255,255,0.05); }
.cal-day.other-month { opacity: 0.2; pointer-events: none; }
.cal-day.today { border-color: var(--color-primary); }
.cal-day.booked { background: var(--color-accent-light); border-color: var(--color-accent); }
.cal-day.blocked { background: rgba(255,255,255,0.05); border-color: var(--color-text-muted); }
.cal-day.available { background: var(--color-primary-ultra-light); }
.day-num { font-weight: 500; }
.day-tag { font-size: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.calendar-legend { display: flex; gap: var(--space-6); justify-content: center; margin-top: var(--space-4); }
.legend-item { display: flex; align-items: center; gap: var(--space-2); font-size: var(--font-size-xs); color: var(--color-text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }

/* Profile Form */
.profile-form { max-width: 800px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-bottom: var(--space-6); }
.form-group.full { grid-column: 1 / -1; }
.form-actions { display: flex; align-items: center; gap: var(--space-4); }
.save-msg { color: var(--color-success); font-size: var(--font-size-sm); font-weight: 500; }

/* Cover Photo Upload */
.cover-upload-section { margin-bottom: var(--space-6); }
.cover-upload-area {
  width: 100%; aspect-ratio: 3/1; border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl); cursor: pointer; overflow: hidden;
  transition: all var(--transition-base); position: relative;
  display: flex; align-items: center; justify-content: center;
}
.cover-upload-area:hover { border-color: var(--color-primary); background: rgba(193,216,47,0.03); }
.cover-preview { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { text-align: center; color: var(--color-text-muted); padding: var(--space-4); }
.cover-placeholder p { margin: var(--space-2) 0; font-size: var(--font-size-sm); }
.cover-placeholder .text-muted { font-size: var(--font-size-xs); opacity: 0.6; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .table-header { display: none; }
  .table-row { grid-template-columns: 1fr 1fr; gap: var(--space-2); }
  .form-grid { grid-template-columns: 1fr; }
  .dash-tabs { gap: 0; }
  .tab-btn { padding: var(--space-2) var(--space-3); font-size: var(--font-size-xs); }
}
</style>
