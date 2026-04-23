<template>
  <div class="admin-dash" :style="{ paddingTop: '100px' }">
    <div class="container">
      <header class="dash-header">
        <div>
          <h1 class="section-title">Panel <span class="text-gradient">Admin</span></h1>
          <p class="section-subtitle">Gestiona la plataforma Pulsar</p>
        </div>
      </header>

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
              <button class="btn btn-outline btn-sm" @click="toggleLevel(t)">
                {{ t.talent_level === 'premium' ? '→ Standard' : '→ Premium' }}
              </button>
              <button class="btn btn-ghost btn-sm" @click="toggleFeatured(t)">
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

    </div>
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

const tabs = [
  { key: 'talents', label: 'Talentos', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  { key: 'bookings', label: 'Reservas', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>' },
  { key: 'users', label: 'Usuarios', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>' },
  { key: 'payments', label: 'Pagos', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>' },
]

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

async function toggleLevel(t) {
  const newLevel = t.talent_level === 'premium' ? 'standard' : 'premium'
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

async function fetchTalents() { try { const { data } = await api.get('/admin/talents/'); talents.value = data.results || data } catch { /* */ } }
async function fetchBookings() { try { const { data } = await api.get('/admin/bookings/'); bookingsData.value = data.results || data } catch { /* */ } }
async function fetchUsers() { try { const { data } = await api.get('/admin/users/'); users.value = data.results || data } catch { /* */ } }
async function fetchPayments() { try { const { data } = await api.get('/admin/payments/'); payments.value = data.results || data } catch { /* */ } }

onMounted(() => Promise.all([fetchTalents(), fetchBookings(), fetchUsers(), fetchPayments()]))
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
.cell-actions { display: flex; gap: var(--space-2); flex-wrap: wrap; }
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
</style>
