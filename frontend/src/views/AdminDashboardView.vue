<template>
  <div class="admin-dash" :style="{ paddingTop: '100px' }">
    <div class="container">
      <header class="dash-header">
        <div>
          <h1 class="section-title">Panel <span class="text-gradient">Admin</span></h1>
          <p class="section-subtitle">Gestiona la plataforma Pulsar</p>
        </div>
      </header>

      <!-- Banner: talentos pendientes de aprobación -->
      <div v-if="pendingTalentsCount > 0" class="pending-banner" @click="goToPending">
        <div class="pending-banner-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 8v4l3 3"/><circle cx="12" cy="12" r="10"/></svg>
        </div>
        <div class="pending-banner-body">
          <strong>{{ pendingTalentsCount }} {{ pendingTalentsCount === 1 ? 'talento espera' : 'talentos esperan' }} aprobación</strong>
          <p>Revisa sus perfiles y aprúebalos para que aparezcan en búsqueda.</p>
        </div>
        <button class="btn btn-primary btn-sm">Revisar ahora →</button>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card" v-for="s in statCards" :key="s.label">
          <div class="stat-icon" :style="{ background: s.bg }"><span v-html="s.icon"></span></div>
          <div><span class="stat-value">{{ s.value }}</span><span class="stat-label">{{ s.label }}</span></div>
        </div>
      </div>

      <!-- Tabs -->
      <nav class="dash-tabs">
        <button v-for="t in tabs" :key="t.key" :class="['tab-btn', { active: activeTab === t.key }]" @click="activeTab = t.key">
          <span v-html="t.icon"></span> {{ t.label }}
          <span v-if="t.badge" class="tab-badge">{{ t.badge }}</span>
        </button>
      </nav>

      <!-- ═══ Talentos ═══ -->
      <section v-if="activeTab === 'talents'" class="tab-panel animate-fade-in">
        <div class="filters-bar">
          <select v-model="talentFilter" class="input-field" style="max-width:200px">
            <option value="all">Todos</option>
            <option value="pending">Pendientes</option>
            <option value="approved">Aprobados</option>
            <option value="premium">Premium</option>
          </select>
        </div>
        <div class="admin-table">
          <div class="admin-table-header">
            <span>Talento</span><span>Tipo</span><span>Ciudad</span><span>Nivel</span><span>Estado</span><span>Acciones</span>
          </div>
          <div v-for="t in filteredTalents" :key="t.id" class="admin-table-row">
            <span class="cell-name">
              <div class="cell-avatar">{{ t.stage_name?.[0] || '?' }}</div>
              <div><strong>{{ t.stage_name }}</strong><br><small style="color:var(--color-text-muted)">{{ t.user_name }}</small></div>
            </span>
            <span>{{ t.talent_type_display || t.talent_type }}</span>
            <span>{{ t.city }}</span>
            <span>
              <span :class="['badge', t.talent_level === 'premium' ? 'badge-warning' : '']">{{ t.talent_level }}</span>
            </span>
            <span>
              <span :class="['badge', t.is_approved ? 'badge-success' : 'badge-error']">{{ t.is_approved ? 'Aprobado' : 'Pendiente' }}</span>
            </span>
            <span class="cell-actions">
              <button v-if="!t.is_approved" class="btn btn-primary btn-sm" @click="approveTalent(t.id, true)">Aprobar</button>
              <button v-else class="btn btn-ghost btn-sm" @click="approveTalent(t.id, false)">Revocar</button>
              <select
                class="level-select"
                :value="t.talent_level"
                @change="changeLevel(t, $event.target.value)"
                title="Cambiar plan del talento"
              >
                <option value="standard">Standard</option>
                <option value="pro">Pro</option>
                <option value="premium">Premium</option>
              </select>
              <button class="btn btn-ghost btn-sm" @click="toggleFeatured(t)" :title="t.is_featured ? 'Quitar destacado' : 'Destacar'">
                {{ t.is_featured ? '★' : '☆' }}
              </button>
            </span>
          </div>
          <div v-if="filteredTalents.length === 0" class="empty-row">Sin resultados</div>
        </div>
      </section>

      <!-- ═══ Reservas ═══ -->
      <section v-if="activeTab === 'bookings'" class="tab-panel animate-fade-in">
        <div class="filters-bar">
          <select v-model="bookingFilter" class="input-field" style="max-width:200px">
            <option value="all">Todas</option>
            <option value="active">Activas</option>
            <option value="completed">Completadas</option>
            <option value="cancelled">Canceladas</option>
          </select>
          <button class="btn btn-ghost btn-sm" @click="downloadBookingsCSV" style="margin-left: auto">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Exportar CSV
          </button>
        </div>
        <div class="admin-table">
          <div class="admin-table-header">
            <span>ID</span><span>Cliente</span><span>Talento</span><span>Fecha</span><span>Monto</span><span>Estado</span>
          </div>
          <div v-for="b in filteredBookings" :key="b.id" class="admin-table-row clickable" @click="$router.push(`/dashboard/bookings/${b.id}`)">
            <span>#{{ b.id }}</span>
            <span>{{ b.client_name }}</span>
            <span>{{ b.talent_name }}</span>
            <span>{{ formatDate(b.event_date) }}</span>
            <span class="cell-price">${{ b.quoted_price || b.precio_estimado || '—' }}</span>
            <span><span :class="['badge', statusBadge(b.status)]">{{ b.status_display }}</span></span>
          </div>
          <div v-if="filteredBookings.length === 0" class="empty-row">Sin resultados</div>
        </div>
      </section>

      <!-- ═══ Usuarios ═══ -->
      <section v-if="activeTab === 'users'" class="tab-panel animate-fade-in">
        <div class="admin-table">
          <div class="admin-table-header">
            <span>Usuario</span><span>Email</span><span>Rol</span><span>Registro</span><span>Estado</span>
          </div>
          <div v-for="u in users" :key="u.id" class="admin-table-row">
            <span><strong>{{ u.first_name }} {{ u.last_name }}</strong></span>
            <span style="color:var(--color-text-muted)">{{ u.email }}</span>
            <span><span :class="['badge', roleBadge(u.role)]">{{ u.role }}</span></span>
            <span>{{ formatDate(u.date_joined) }}</span>
            <span><span :class="['badge', u.is_active ? 'badge-success' : 'badge-error']">{{ u.is_active ? 'Activo' : 'Inactivo' }}</span></span>
          </div>
          <div v-if="users.length === 0" class="empty-row">Sin usuarios</div>
        </div>
      </section>

      <!-- ═══ Pagos ═══ -->
      <section v-if="activeTab === 'payments'" class="tab-panel animate-fade-in">
        <div class="earnings-grid" style="margin-bottom:var(--space-8)">
          <div class="earnings-card glass">
            <h3>Ingresos Totales</h3>
            <p class="earnings-amount text-gradient">${{ paymentStats.total.toFixed(2) }}</p>
          </div>
          <div class="earnings-card glass">
            <h3>Comisión Pulsar</h3>
            <p class="earnings-amount" style="color:var(--color-primary)">${{ paymentStats.commission.toFixed(2) }}</p>
          </div>
          <div class="earnings-card glass">
            <h3>Pagos Pendientes</h3>
            <p class="earnings-amount" style="color:var(--color-warning)">${{ paymentStats.pending.toFixed(2) }}</p>
          </div>
        </div>
        <div class="admin-table">
          <div class="admin-table-header">
            <span>ID</span><span>Booking</span><span>Monto</span><span>Tipo</span><span>Comisión SR</span><span>Estado</span><span>Fecha</span>
          </div>
          <div v-for="p in payments" :key="p.id" class="admin-table-row">
            <span>#{{ p.id }}</span>
            <span>#{{ p.booking }}</span>
            <span class="cell-price">${{ p.amount }}</span>
            <span>{{ p.payment_type_display || p.payment_type }}</span>
            <span style="color:var(--color-primary)">${{ p.commission_showroots }}</span>
            <span><span :class="['badge', p.payment_status === 'completed' ? 'badge-success' : 'badge-warning']">{{ p.payment_status }}</span></span>
            <span>{{ formatDate(p.created_at) }}</span>
          </div>
        </div>
      </section>

      <!-- ═══ Disputas ═══ -->
      <section v-if="activeTab === 'disputes'" class="tab-panel animate-fade-in">
        <div v-if="!disputes.length" class="empty-state" style="padding: var(--space-8)">
          <p style="opacity: 0.6">No hay disputas abiertas.</p>
        </div>
        <div v-else class="disputes-list">
          <div v-for="d in disputes" :key="d.id" class="dispute-card">
            <div class="dispute-head">
              <code class="dispute-code">{{ d.booking_code }}</code>
              <span :class="['badge', d.status === 'open' || d.status === 'investigating' ? 'badge-warning' : 'badge-success']">{{ d.status_display }}</span>
              <span class="cell-muted">{{ formatDate(d.created_at) }}</span>
            </div>
            <div class="dispute-body">
              <strong>{{ d.reason_display }}</strong>
              <p class="dispute-desc">{{ d.description }}</p>
              <p class="cell-muted" style="font-size: 0.78rem">
                Reportado por: <strong>{{ d.reported_by_name }}</strong>
              </p>
              <div v-if="d.refund_amount" class="dispute-refund">
                💸 Reembolsado: <strong>${{ Number(d.refund_amount).toFixed(2) }}</strong>
              </div>
            </div>
            <div v-if="d.status === 'open' || d.status === 'investigating'" class="dispute-actions">
              <button class="btn btn-primary btn-sm" @click="openRefundForBooking(d.booking_id, d.booking_code)">
                Emitir reembolso
              </button>
              <router-link :to="`/dashboard/bookings/${d.booking_id}`" class="btn btn-ghost btn-sm">
                Ver booking
              </router-link>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ Mensajes filtrados (anti-desintermediación) ═══ -->
      <section v-if="activeTab === 'flagged'" class="tab-panel animate-fade-in">
        <div v-if="flaggedStats" class="flagged-stats">
          <div class="flagged-stat-card">
            <strong>{{ flaggedStats.total_flagged }}</strong>
            <span>Mensajes filtrados</span>
          </div>
          <div class="flagged-stat-card">
            <strong>{{ flaggedStats.top_senders.length }}</strong>
            <span>Usuarios involucrados</span>
          </div>
          <div class="flagged-stat-card">
            <strong>{{ Object.keys(flaggedStats.categories).length }}</strong>
            <span>Categorías</span>
          </div>
        </div>

        <div v-if="flaggedStats && Object.keys(flaggedStats.categories).length" class="flagged-categories">
          <h4>Categorías más comunes</h4>
          <div class="flagged-cat-list">
            <span v-for="(count, cat) in flaggedStats.categories" :key="cat" class="flagged-cat-chip">
              {{ catLabel(cat) }}: <strong>{{ count }}</strong>
            </span>
          </div>
        </div>

        <div v-if="flaggedStats && flaggedStats.top_senders.length" class="flagged-top">
          <h4>Top usuarios con más violaciones</h4>
          <div class="admin-table flagged-top-table">
            <div class="admin-table-header">
              <span>Usuario</span><span>Email</span><span>Violaciones</span>
            </div>
            <div v-for="u in flaggedStats.top_senders" :key="u['sender__id']" class="admin-table-row">
              <span>{{ u['sender__first_name'] }} {{ u['sender__last_name'] }}</span>
              <span class="cell-muted">{{ u['sender__email'] }}</span>
              <span style="color: #E85D4A; font-weight: 700">{{ u.count }}</span>
            </div>
          </div>
        </div>

        <h4 style="margin-top: var(--space-6); margin-bottom: var(--space-3)">Mensajes detectados</h4>
        <div v-if="!flaggedMessages.length" class="empty-state" style="padding: var(--space-6)">
          <p style="opacity: 0.6">Ningún mensaje ha sido filtrado todavía.</p>
        </div>
        <div v-else class="flagged-messages-list">
          <div v-for="m in flaggedMessages" :key="m.id" class="flagged-msg-card">
            <div class="flagged-msg-head">
              <span><strong>{{ m.sender_name }}</strong></span>
              <span class="cell-muted">Booking {{ m.booking_code || `#${m.booking}` }}</span>
              <span class="cell-muted">{{ formatDate(m.created_at) }}</span>
            </div>
            <div class="flagged-msg-body">
              <div class="flagged-msg-row">
                <span class="flagged-msg-label">Publicado (filtrado):</span>
                <p>{{ m.content }}</p>
              </div>
              <div class="flagged-msg-row">
                <span class="flagged-msg-label">Original (vio el admin):</span>
                <p class="flagged-msg-raw">{{ m.raw_content || '—' }}</p>
              </div>
              <div class="flagged-msg-cats">
                <span v-for="cat in (m.flagged_categories || [])" :key="cat" class="flagged-cat-chip">
                  {{ catLabel(cat) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- Refund Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="refundModal.open" class="refund-modal-backdrop" @click.self="refundModal.open = false">
          <div class="refund-modal">
            <h3>Emitir reembolso</h3>
            <p class="refund-sub">Booking <code>{{ refundModal.booking_code }}</code></p>

            <div class="form-group">
              <label class="label">Monto (USD)</label>
              <input v-model="refundModal.amount" type="number" min="0" step="0.01" class="input-field" placeholder="0.00" />
            </div>

            <div class="form-group">
              <label class="label">Nota interna</label>
              <textarea v-model="refundModal.note" rows="2" class="input-field" placeholder="Razón del reembolso"></textarea>
            </div>

            <p class="refund-note">
              Se creará un <strong>ClientCredit</strong> a favor del cliente. Si hay disputa abierta, se cerrará automáticamente.
            </p>

            <p v-if="refundModal.error" class="cell-muted" style="color: #E85D4A">{{ refundModal.error }}</p>

            <div class="refund-actions">
              <button class="btn btn-ghost btn-sm" @click="refundModal.open = false">Cancelar</button>
              <button class="btn btn-primary btn-sm" :disabled="refundModal.loading || !refundModal.amount" @click="submitRefund">
                {{ refundModal.loading ? 'Procesando...' : 'Emitir reembolso' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const activeTab = ref('talents')
const talents = ref([])
const bookingsData = ref([])
const users = ref([])
const payments = ref([])
const talentFilter = ref('all')
const bookingFilter = ref('all')

// Mensajes flagged
const flaggedMessages = ref([])
const flaggedStats = ref(null)

// Disputas
const disputes = ref([])
const openDisputesCount = computed(() => disputes.value.filter(d => d.status === 'open' || d.status === 'investigating').length)
const pendingTalentsCount = computed(() => talents.value.filter(t => !t.is_approved).length)

function goToPending() {
  activeTab.value = 'talents'
  talentFilter.value = 'pending'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Refund modal
const refundModal = ref({
  open: false,
  booking_id: null,
  booking_code: '',
  amount: '',
  reason: 'refund',
  note: '',
  loading: false,
  error: '',
})

function openRefundForBooking(bookingId, bookingCode) {
  refundModal.value = {
    open: true,
    booking_id: bookingId,
    booking_code: bookingCode || '',
    amount: '',
    reason: 'refund',
    note: '',
    loading: false,
    error: '',
  }
}

async function submitRefund() {
  refundModal.value.loading = true
  refundModal.value.error = ''
  try {
    await api.post(`/admin/bookings/${refundModal.value.booking_id}/refund/`, {
      amount: refundModal.value.amount,
      reason: refundModal.value.reason,
      note: refundModal.value.note,
    })
    refundModal.value.open = false
    await fetchDisputes()
  } catch (err) {
    refundModal.value.error = err.response?.data?.error || 'No se pudo emitir el reembolso.'
  } finally {
    refundModal.value.loading = false
  }
}

async function fetchDisputes() {
  try {
    const { data } = await api.get('/admin/disputes/')
    disputes.value = data
  } catch { /* silent */ }
}

function downloadBookingsCSV() {
  // Usa token JWT del localStorage para auth
  const token = localStorage.getItem('access_token')
  fetch('/api/admin/bookings/export/', {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.blob()).then(blob => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bookings-${new Date().toISOString().slice(0,10)}.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }).catch(() => alert('No se pudo descargar el CSV.'))
}

const CAT_LABELS = {
  phone: 'Teléfono', email: 'Email', username_at: 'Usuario (@)',
  whatsapp: 'WhatsApp', call_me: 'Solicitud contacto', social: 'Red social', url: 'URL',
}
function catLabel(cat) { return CAT_LABELS[cat] || cat }

async function fetchFlagged() {
  try {
    const [msgRes, statsRes] = await Promise.all([
      api.get('/admin/flagged-messages/'),
      api.get('/admin/flagged-messages/stats/'),
    ])
    flaggedMessages.value = msgRes.data.results || msgRes.data
    flaggedStats.value = statsRes.data
  } catch { /* admin only, silent */ }
}

const tabs = computed(() => [
  { key: 'talents', label: 'Talentos', badge: pendingTalentsCount.value || null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  { key: 'bookings', label: 'Reservas', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>' },
  { key: 'users', label: 'Usuarios', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>' },
  { key: 'payments', label: 'Pagos', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>' },
  { key: 'flagged', label: 'Mensajes filtrados', badge: flaggedStats.value?.total_flagged || null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>' },
  { key: 'disputes', label: 'Disputas', badge: openDisputesCount.value || null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/></svg>' },
])

const filteredTalents = computed(() => {
  if (talentFilter.value === 'pending') return talents.value.filter(t => !t.is_approved)
  if (talentFilter.value === 'approved') return talents.value.filter(t => t.is_approved)
  if (talentFilter.value === 'premium') return talents.value.filter(t => t.talent_level === 'premium')
  return talents.value
})

const filteredBookings = computed(() => {
  if (bookingFilter.value === 'active') return bookingsData.value.filter(b => ['solicitud_enviada','pendiente_respuesta','aceptada','pendiente_pago','confirmada'].includes(b.status))
  if (bookingFilter.value === 'completed') return bookingsData.value.filter(b => b.status === 'completada')
  if (bookingFilter.value === 'cancelled') return bookingsData.value.filter(b => ['cancelada','rechazada'].includes(b.status))
  return bookingsData.value
})

const paymentStats = computed(() => {
  const completed = payments.value.filter(p => p.payment_status === 'completed')
  const pending = payments.value.filter(p => p.payment_status === 'pending')
  return {
    total: completed.reduce((s, p) => s + parseFloat(p.amount || 0), 0),
    commission: completed.reduce((s, p) => s + parseFloat(p.commission_showroots || 0), 0),
    pending: pending.reduce((s, p) => s + parseFloat(p.amount || 0), 0),
  }
})

const statCards = computed(() => [
  { label: 'Talentos', value: talents.value.length, bg: 'var(--color-primary-ultra-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  { label: 'Reservas', value: bookingsData.value.length, bg: 'var(--color-accent-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/></svg>' },
  { label: 'Usuarios', value: users.value.length, bg: 'var(--color-secondary-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-secondary)" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/></svg>' },
  { label: 'Ingresos', value: '$' + paymentStats.value.total.toFixed(0), bg: 'var(--color-success-light)', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>' },
])

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-VE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function statusBadge(status) {
  const map = { solicitud_enviada: '', pendiente_respuesta: 'badge-warning', aceptada: 'badge-success', pendiente_pago: 'badge-warning', confirmada: 'badge-success', completada: 'badge-cyan', rechazada: 'badge-error', cancelada: 'badge-error' }
  return map[status] || ''
}

function roleBadge(role) {
  const map = { admin: 'badge-accent', talent: 'badge-warning', client: '', partner: 'badge-cyan' }
  return map[role] || ''
}

async function approveTalent(id, approve) {
  try {
    await api.patch(`/admin/talents/${id}/`, { is_approved: approve })
    await fetchTalents()
  } catch (e) { alert('Error: ' + (e.response?.data?.detail || 'Intenta de nuevo')) }
}

async function changeLevel(t, newLevel) {
  if (!['standard', 'pro', 'premium'].includes(newLevel)) return
  if (newLevel === t.talent_level) return
  try {
    await api.patch(`/admin/talents/${t.id}/`, { talent_level: newLevel })
    await fetchTalents()
  } catch (e) { alert('Error: ' + (e.response?.data?.detail || 'Intenta de nuevo')) }
}

async function toggleFeatured(t) {
  try {
    await api.patch(`/admin/talents/${t.id}/`, { is_featured: !t.is_featured })
    await fetchTalents()
  } catch (e) { alert('Error: ' + (e.response?.data?.detail || 'Intenta de nuevo')) }
}

async function fetchTalents() {
  try {
    const { data } = await api.get('/admin/talents/')
    talents.value = data.results || data
    // Si hay pendientes y el filtro aún es 'all' (primera carga), arranca en 'pending'
    if (talentFilter.value === 'all' && talents.value.some(t => !t.is_approved)) {
      talentFilter.value = 'pending'
    }
  } catch { /* */ }
}
async function fetchBookings() { try { const { data } = await api.get('/admin/bookings/'); bookingsData.value = data.results || data } catch { /* */ } }
async function fetchUsers() { try { const { data } = await api.get('/admin/users/'); users.value = data.results || data } catch { /* */ } }
async function fetchPayments() { try { const { data } = await api.get('/admin/payments/'); payments.value = data.results || data } catch { /* */ } }

onMounted(() => Promise.all([fetchTalents(), fetchBookings(), fetchUsers(), fetchPayments(), fetchFlagged(), fetchDisputes()]))
</script>

<style scoped>
.admin-dash { min-height: 100vh; padding-bottom: var(--space-16); }
.dash-header { margin-bottom: var(--space-8); }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-8); }
.stat-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-xl); }
.stat-icon { width: 48px; height: 48px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-family: var(--font-heading); font-size: var(--font-size-2xl); display: block; }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-muted); }

.dash-tabs { display: flex; gap: var(--space-1); background: var(--color-bg-card); border-radius: var(--radius-xl); padding: var(--space-1); margin-bottom: var(--space-6); overflow-x: auto; border: 1px solid var(--color-border); }
.tab-btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-5); border-radius: var(--radius-lg); font-size: var(--font-size-sm); font-weight: 500; color: var(--color-text-muted); background: transparent; border: none; cursor: pointer; transition: all var(--transition-fast); white-space: nowrap; }
.tab-btn:hover { color: var(--color-text-primary); }
.tab-btn.active { background: var(--gradient-primary); color: #000; font-weight: 600; }
.tab-badge { background: var(--color-accent); color: white; font-size: 10px; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

.filters-bar { margin-bottom: var(--space-4); }

.admin-table { border: 1px solid var(--color-border); border-radius: var(--radius-xl); overflow: hidden; }
.admin-table-header { display: grid; grid-template-columns: 2.5fr 1fr 1fr 1fr 1fr 2fr; padding: var(--space-3) var(--space-5); font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--color-border); }
.admin-table-row { display: grid; grid-template-columns: 2.5fr 1fr 1fr 1fr 1fr 2fr; padding: var(--space-4) var(--space-5); align-items: center; font-size: var(--font-size-sm); border-bottom: 1px solid rgba(255,255,255,0.03); transition: background var(--transition-fast); }
.admin-table-row:hover { background: var(--color-bg-card-hover); }
.admin-table-row.clickable { cursor: pointer; }
.cell-name { display: flex; align-items: center; gap: var(--space-3); }
.cell-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--gradient-cta); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; flex-shrink: 0; }
.cell-price { color: var(--color-primary); font-weight: 600; }
.cell-actions { display: flex; gap: var(--space-2); flex-wrap: wrap; align-items: center; }
.level-select {
  padding: 4px 8px;
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  transition: border-color var(--transition-fast);
}
.level-select:hover { border-color: var(--color-primary); }
.level-select:focus { outline: none; border-color: var(--color-primary); }
.empty-row { padding: var(--space-8); text-align: center; color: var(--color-text-muted); }

.earnings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: var(--space-4); }
.earnings-card { padding: var(--space-6); border-radius: var(--radius-xl); text-align: center; }
.earnings-card h3 { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-3); font-family: var(--font-family); }
.earnings-amount { font-family: var(--font-heading); font-size: var(--font-size-3xl); }

@media (max-width: 768px) {
  .admin-table-header { display: none; }
  .admin-table-row { grid-template-columns: 1fr 1fr; gap: var(--space-2); }
  .cell-actions { grid-column: 1 / -1; }
}

/* Flagged messages tab */
.flagged-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}
.flagged-stat-card {
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
}
.flagged-stat-card strong {
  display: block;
  font-family: var(--font-heading);
  font-size: 1.8rem;
  color: #E85D4A;
  margin-bottom: 4px;
}
.flagged-stat-card span {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}

.flagged-categories, .flagged-top { margin-bottom: var(--space-6); }
.flagged-categories h4, .flagged-top h4, .flagged-messages-list + h4 {
  font-size: 0.9rem;
  margin-bottom: var(--space-3);
  color: var(--color-text-secondary);
}
.flagged-cat-list { display: flex; flex-wrap: wrap; gap: 8px; }
.flagged-cat-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(232, 93, 74, 0.08);
  border: 1px solid rgba(232, 93, 74, 0.3);
  color: #E85D4A;
  font-size: 0.78rem;
}
.flagged-cat-chip strong { margin-left: 4px; color: var(--color-text-primary); }

.flagged-top-table { margin-bottom: var(--space-4); }

.flagged-messages-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.flagged-msg-card {
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid rgba(232, 93, 74, 0.3);
  border-left: 4px solid #E85D4A;
  border-radius: var(--radius-lg);
}
.flagged-msg-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border);
  font-size: 0.82rem;
}
.cell-muted { color: var(--color-text-muted); }
.flagged-msg-row { margin-bottom: var(--space-2); }
.flagged-msg-label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}
.flagged-msg-row p {
  margin: 0;
  font-size: 0.88rem;
  color: var(--color-text-primary);
}
.flagged-msg-raw {
  font-style: italic;
  color: #E85D4A !important;
}
.flagged-msg-cats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: var(--space-2);
}

/* Disputes */
.disputes-list { display: flex; flex-direction: column; gap: var(--space-3); }
.dispute-card {
  padding: var(--space-5);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-left: 4px solid #f59e0b;
  border-radius: var(--radius-lg);
}
.dispute-head {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border);
}
.dispute-code {
  font-family: 'Courier New', monospace;
  font-size: 0.78rem;
  color: var(--color-primary);
  font-weight: 700;
}
.dispute-body strong {
  display: block;
  font-size: 0.95rem;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.dispute-desc {
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: var(--space-2);
}
.dispute-refund {
  margin-top: var(--space-2);
  padding: 6px 12px;
  background: rgba(16,185,129,0.08);
  border-left: 3px solid #10b981;
  color: #10b981;
  font-size: 0.82rem;
}
.dispute-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

/* Refund modal */
.refund-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-4);
}
.refund-modal {
  width: 100%;
  max-width: 480px;
  padding: var(--space-6);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
}
.refund-modal h3 {
  font-size: 1.2rem;
  margin-bottom: var(--space-2);
}
.refund-sub {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}
.refund-sub code {
  font-family: 'Courier New', monospace;
  color: var(--color-primary);
}
.refund-note {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  padding: 8px 12px;
  background: rgba(193,216,47,0.05);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}
.refund-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}

.filters-bar { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-4); }

/* Pending talents banner */
.pending-banner {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  margin-bottom: var(--space-6);
  background: linear-gradient(90deg, rgba(193,216,47,0.10), rgba(193,216,47,0.04));
  border: 1px solid rgba(193,216,47,0.35);
  border-left: 4px solid var(--color-primary);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: transform var(--transition-fast), background var(--transition-fast);
}
.pending-banner:hover { transform: translateY(-1px); background: linear-gradient(90deg, rgba(193,216,47,0.16), rgba(193,216,47,0.06)); }
.pending-banner-icon {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: rgba(193,216,47,0.18);
  color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.pending-banner-body { flex: 1; min-width: 0; }
.pending-banner-body strong { display: block; font-size: 1rem; color: var(--color-text-primary); margin-bottom: 2px; }
.pending-banner-body p { margin: 0; font-size: 0.85rem; color: var(--color-text-muted); }
@media (max-width: 600px) {
  .pending-banner { flex-wrap: wrap; }
  .pending-banner-body { flex-basis: 100%; }
}
</style>
