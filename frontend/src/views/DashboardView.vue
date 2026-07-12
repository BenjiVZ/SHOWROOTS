<template>
  <div class="dashboard-page">
    <div class="container">
      <div class="dashboard-header animate-fade-in-up">
        <div>
          <h1 class="section-title">Dashboard</h1>
          <p class="section-subtitle">Bienvenido, <strong>{{ auth.user?.first_name || auth.user?.username }}</strong></p>
        </div>
        <div class="header-right">
          <div class="role-level-group">
            <span class="badge" :class="roleBadgeClass">{{ auth.roleLabel }}</span>
            <span v-if="auth.isTalent && talentProfile" class="level-badge" :class="talentProfile.talent_level === 'premium' ? 'level-premium' : 'level-standard'">
              <svg v-if="talentProfile.talent_level === 'premium'" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              {{ talentProfile.talent_level === 'premium' ? 'Premium' : 'Estándar' }}
            </span>
          </div>
          <button v-if="unreadCount > 0" class="notif-btn" @click="showNotifications = !showNotifications">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
            <span class="notif-badge">{{ unreadCount }}</span>
          </button>
        </div>
      </div>

      <!-- Notifications Dropdown -->
      <div v-if="showNotifications" class="notif-dropdown glass animate-fade-in-up">
        <div class="notif-header">
          <h4>Notificaciones</h4>
          <button @click="markAllRead" class="btn-text">Marcar todas leídas</button>
        </div>
        <div v-for="n in notifications" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }" @click="handleNotifClick(n)">
          <div class="notif-dot" v-if="!n.is_read"></div>
          <div>
            <strong>{{ n.title }}</strong>
            <p>{{ n.message }}</p>
            <span class="notif-time">{{ timeAgo(n.created_at) }}</span>
          </div>
        </div>
        <div v-if="!notifications.length" class="notif-empty">Sin notificaciones</div>
      </div>

      <!-- Quick Stats — KPIs del cliente -->
      <div class="stats-grid animate-fade-in-up" style="animation-delay:0.1s" data-tour="stats">
        <div class="stat-card glass">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </div>
          <div>
            <span class="stat-value">{{ upcomingCount }}</span>
            <span class="stat-label">Próximos eventos</span>
          </div>
        </div>
        <div class="stat-card glass">
          <div class="stat-icon" style="background:rgba(16,185,129,0.1);color:#10b981;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <div>
            <span class="stat-value">${{ inEscrowTotal.toFixed(2) }}</span>
            <span class="stat-label">En custodia</span>
          </div>
        </div>
        <div class="stat-card glass">
          <div class="stat-icon stat-icon-success">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div>
            <span class="stat-value">{{ completedCount }}</span>
            <span class="stat-label">Eventos completados</span>
          </div>
        </div>
        <div v-if="!auth.isTalent && creditBalance > 0" class="stat-card glass stat-credit">
          <div class="stat-icon" style="background:rgba(193,216,47,0.12);color:var(--color-primary);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <div>
            <span class="stat-value">${{ Number(creditBalance).toFixed(0) }}</span>
            <span class="stat-label">Crédito Pulsar</span>
          </div>
        </div>
        <div v-if="auth.isTalent || auth.isPartner" class="stat-card glass">
          <div class="stat-icon" style="background:rgba(193,216,47,0.1);color:var(--color-primary);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
          </div>
          <div>
            <span class="stat-value">${{ totalEarnings }}</span>
            <span class="stat-label">Ingresos</span>
          </div>
        </div>
      </div>

      <!-- Próximos eventos con countdown (hero cards) -->
      <div v-if="upcomingWithCountdown.length" class="upcoming-section animate-fade-in-up" style="animation-delay:0.12s">
        <h3 class="upcoming-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          Próximos eventos
        </h3>
        <div class="upcoming-grid">
          <router-link v-for="b in upcomingWithCountdown" :key="b.id" :to="`/dashboard/bookings/${b.id}`" class="upcoming-card">
            <div class="uc-countdown">
              <div class="uc-cd-unit"><strong>{{ b.cd.days }}</strong><span>días</span></div>
              <div class="uc-cd-unit"><strong>{{ b.cd.hours }}</strong><span>hrs</span></div>
              <div class="uc-cd-unit"><strong>{{ b.cd.minutes }}</strong><span>min</span></div>
            </div>
            <div class="uc-info">
              <strong>{{ auth.isTalent ? b.client_name : b.talent_name }}</strong>
              <p>{{ b.event_type_display || b.event_type }} · {{ formatDate(b.event_date) }}</p>
              <span v-if="b.event_city" class="uc-location">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ b.event_city }}
              </span>
            </div>
            <span class="uc-escrow">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              ${{ Number(b.amount_paid || 0).toFixed(2) }} en custodia
            </span>
          </router-link>
        </div>
      </div>

      <!-- Solicitudes abiertas (solo clientes / partners) -->
      <div v-if="!auth.isTalent" class="open-gigs-banner animate-fade-in-up" style="animation-delay:0.14s">
        <div class="ogb-left">
          <div class="ogb-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          </div>
          <div>
            <strong>Solicitudes abiertas</strong>
            <p>Publica lo que necesitas y los DJs te envían ofertas — Premium primero, después Pro y Standard.</p>
          </div>
        </div>
        <div class="ogb-actions">
          <router-link to="/dashboard/open-gigs" class="btn btn-ghost btn-sm">Mis solicitudes</router-link>
          <router-link to="/open-gig/new" class="btn btn-primary btn-sm">Publicar</router-link>
        </div>
      </div>

      <!-- Filter Tabs -->
      <div class="tabs animate-fade-in-up" style="animation-delay:0.15s" data-tour="tabs">
        <button v-for="tab in tabs" :key="tab.value" class="tab-btn" :class="{ active: activeTab === tab.value }" @click="activeTab = tab.value">
          {{ tab.label }}
          <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
        </button>
      </div>

      <!-- Bookings List -->
      <div class="bookings-section animate-fade-in-up" style="animation-delay:0.2s" data-tour="bookings">
        <div v-if="loading" class="loading-state">
          <div v-for="i in 3" :key="i" class="skeleton" style="height:80px;margin-bottom:var(--space-3);border-radius:var(--radius-lg);"></div>
        </div>

        <div v-else-if="filteredBookings.length" class="bookings-list">
          <router-link v-for="booking in filteredBookings" :key="booking.id" :to="`/dashboard/bookings/${booking.id}`" class="booking-item glass">
            <div class="booking-info">
              <h4>{{ auth.isTalent ? booking.client_name : booking.talent_name }}</h4>
              <p>
                {{ booking.event_type_display || booking.event_type }} — {{ formatDate(booking.event_date) }}
                <span v-if="booking.event_city"> · {{ booking.event_city }}</span>
              </p>
            </div>
            <div class="booking-meta">
              <span v-if="booking.quoted_price || booking.precio_estimado" class="booking-price">
                ${{ booking.quoted_price || booking.precio_estimado }}
              </span>
              <span class="status-badge" :class="statusClass(booking.status)">
                {{ statusLabel(booking.status) }}
              </span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chevron"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </router-link>
        </div>

        <div v-else class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color:var(--color-text-muted);margin-bottom:var(--space-4);">
            <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <h3>{{ emptyMessage }}</h3>
          <p>{{ emptyDescription }}</p>
          <router-link v-if="auth.isClient || auth.isPartner" to="/search" class="btn btn-primary" style="margin-top:var(--space-4);">
            Buscar Talentos
          </router-link>
        </div>
      </div>
    </div>

    <!-- Manual de uso / tour guiado (primera vez + botón de ayuda siempre) -->
    <OnboardingTour tour-key="client-dash-v1" :steps="tourSteps" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import OnboardingTour from '@/components/common/OnboardingTour.vue'

const auth = useAuthStore()
const router = useRouter()

// ── Manual de uso: pasos del tour del dashboard de cliente ──
const tourSteps = [
  {
    title: '¡Bienvenido a Pulsar!',
    body: 'Este es tu panel. Desde aquí sigues tus reservas de DJs, músicos y bandas para tus eventos. Te muestro lo básico en 20 segundos.',
  },
  {
    target: '[data-tour="stats"]',
    title: 'Tu resumen',
    body: 'Aquí ves tus <strong>próximos eventos</strong>, el dinero <strong>en custodia</strong> (protegido hasta que se realice el evento) y tus eventos completados.',
  },
  {
    target: '[data-tour="tabs"]',
    title: 'Filtrá tus reservas',
    body: 'Usa estas pestañas para filtrar por estado: <strong>todas, activas, completadas o canceladas</strong>.',
  },
  {
    target: '[data-tour="bookings"]',
    title: 'Tus reservas',
    body: 'Cada reserva se abre con un click para ver el detalle, chatear con el talento y <strong>pagar de forma segura</strong>. El dinero queda protegido hasta el día del evento.',
  },
  {
    title: '¿Necesitas repasar?',
    body: 'Puedes reabrir este manual cuando quieras con el botón <strong>“Ayuda”</strong> abajo a la derecha. ¡A disfrutar tu evento!',
  },
]
const bookings = ref([])
const notifications = ref([])
const unreadCount = ref(0)
const loading = ref(true)
const showNotifications = ref(false)
const activeTab = ref('all')
const talentProfile = ref(null)

const statusMap = {
  solicitud_enviada: { label: 'Solicitud Enviada', class: 'status-info' },
  pendiente_respuesta: { label: 'Pendiente', class: 'status-warning' },
  aceptada: { label: 'Aceptada', class: 'status-success' },
  rechazada: { label: 'Rechazada', class: 'status-error' },
  pendiente_pago: { label: 'Pendiente de Pago', class: 'status-warning' },
  confirmada: { label: 'Confirmada', class: 'status-success' },
  completada: { label: 'Completada', class: 'status-completed' },
  cancelada: { label: 'Cancelada', class: 'status-error' },
}

const pendingCount = computed(() =>
  bookings.value.filter(b => ['solicitud_enviada', 'pendiente_respuesta', 'pendiente_pago'].includes(b.status)).length
)
const confirmedCount = computed(() =>
  bookings.value.filter(b => b.status === 'confirmada').length
)
const totalEarnings = computed(() => {
  return bookings.value
    .filter(b => ['confirmada', 'completada'].includes(b.status))
    .reduce((sum, b) => sum + parseFloat(b.quoted_price || b.precio_estimado || 0), 0)
    .toFixed(2)
})

// KPIs nuevos para el cliente
const now = new Date()
const upcomingCount = computed(() =>
  bookings.value.filter(b => b.status === 'confirmada' && new Date(b.event_date) >= now).length
)

// Cards con countdown — hasta 3 próximos confirmados
const nowMs = ref(Date.now())
setInterval(() => { nowMs.value = Date.now() }, 30000)

const upcomingWithCountdown = computed(() => {
  return bookings.value
    .filter(b => b.status === 'confirmada' && b.event_date && b.event_time_start)
    .map(b => {
      const target = new Date(`${b.event_date}T${b.event_time_start}`).getTime()
      const diff = target - nowMs.value
      if (diff <= 0) return null
      return {
        ...b,
        cd: {
          days: Math.floor(diff / 86400000),
          hours: Math.floor((diff % 86400000) / 3600000),
          minutes: Math.floor((diff % 3600000) / 60000),
        }
      }
    })
    .filter(Boolean)
    .sort((a, b) => new Date(a.event_date) - new Date(b.event_date))
    .slice(0, 3)
})
const completedCount = computed(() =>
  bookings.value.filter(b => b.status === 'completada').length
)
const inEscrowTotal = computed(() => {
  // Bookings con pago hecho pero evento aún no completado
  return bookings.value
    .filter(b => b.status === 'confirmada')
    .reduce((sum, b) => sum + parseFloat(b.amount_paid || 0), 0)
})
const creditBalance = ref(0)

const tabs = computed(() => [
  { value: 'all', label: 'Todas', count: bookings.value.length },
  { value: 'active', label: 'Activas', count: bookings.value.filter(b => !['completada', 'cancelada', 'rechazada'].includes(b.status)).length },
  { value: 'completed', label: 'Completadas', count: bookings.value.filter(b => b.status === 'completada').length },
])

const filteredBookings = computed(() => {
  if (activeTab.value === 'active') return bookings.value.filter(b => !['completada', 'cancelada', 'rechazada'].includes(b.status))
  if (activeTab.value === 'completed') return bookings.value.filter(b => b.status === 'completada')
  return bookings.value
})

const emptyMessage = computed(() => {
  if (auth.isTalent) return 'Sin solicitudes aún'
  return 'Sin reservas aún'
})
const emptyDescription = computed(() => {
  if (auth.isTalent) return 'Las solicitudes de clientes aparecerán aquí.'
  return 'Explora talentos y solicita tu primera reserva.'
})

const roleBadgeClass = computed(() => {
  const map = { talent: 'badge-accent', client: 'badge-cyan', partner: 'badge-warning', admin: 'badge-error' }
  return map[auth.user?.role] || ''
})

function statusClass(s) { return statusMap[s]?.class || '' }
function statusLabel(s) { return statusMap[s]?.label || s }

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-VE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `hace ${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs}h`
  return `hace ${Math.floor(hrs / 24)}d`
}

async function markAllRead() {
  await api.post('/notifications/read/')
  notifications.value.forEach(n => n.is_read = true)
  unreadCount.value = 0
}

function handleNotifClick(n) {
  if (n.link) router.push(n.link)
  showNotifications.value = false
}

onMounted(async () => {
  try {
    const requests = [
      api.get('/bookings/'),
      api.get('/notifications/'),
      api.get('/notifications/unread-count/'),
    ]
    if (auth.isTalent) requests.push(api.get('/talents/me/'))
    const results = await Promise.all(requests)
    bookings.value = results[0].data.results || results[0].data
    notifications.value = (results[1].data.results || results[1].data).slice(0, 10)
    unreadCount.value = results[2].data.unread_count
    if (auth.isTalent && results[3]) talentProfile.value = results[3].data
    // Fetch credit balance (solo si no es talento)
    if (!auth.isTalent) {
      try {
        const { data } = await api.get('/credits/')
        creditBalance.value = parseFloat(data.balance || 0)
      } catch { /* silent */ }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard-page {
  padding-top: var(--space-4);
  min-height: 100vh;
  padding-bottom: var(--space-16);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-10);
}

.header-right { display: flex; align-items: center; gap: var(--space-3); }
.role-level-group { display: flex; align-items: center; gap: var(--space-2); }

.level-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 12px; border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: 700;
  letter-spacing: 0.03em;
}
.level-premium {
  background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 50%, #D97706 100%);
  color: #1a0e00;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.35);
}
.level-standard {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}

.notif-btn {
  position: relative;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-2);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.notif-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.notif-badge {
  position: absolute;
  top: -4px; right: -4px;
  background: var(--color-accent);
  color: white;
  font-size: 10px;
  font-weight: 700;
  width: 18px; height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notif-dropdown {
  position: relative;
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  margin-bottom: var(--space-6);
  max-height: 400px;
  overflow-y: auto;
}
.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}
.notif-header h4 { font-size: var(--font-size-sm); }
.btn-text { background: none; border: none; color: var(--color-primary); font-size: var(--font-size-xs); cursor: pointer; }

.notif-item {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.notif-item:hover { background: var(--color-bg-elevated); }
.notif-item.unread { background: rgba(193,216,47,0.05); }
.notif-dot { width: 8px; height: 8px; background: var(--color-primary); border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.notif-item strong { font-size: var(--font-size-sm); display: block; margin-bottom: 2px; }
.notif-item p { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-bottom: 2px; }
.notif-time { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.notif-empty { text-align: center; padding: var(--space-6); color: var(--color-text-muted); font-size: var(--font-size-sm); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.stat-card {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
}
.stat-card:hover { transform: translateY(-2px); border-color: var(--color-border-hover); }
.stat-icon {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-primary-ultra-light);
  color: var(--color-primary-light);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}
.stat-icon-warning { background: var(--color-warning-light); color: var(--color-warning); }
.stat-icon-success { background: var(--color-success-light); color: var(--color-success); }
.stat-value { display: block; font-family: var(--font-heading); font-size: var(--font-size-2xl); line-height: 1; }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-muted); }

/* Tabs */
.tabs {
  display: flex; gap: var(--space-2);
  margin-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--space-1);
}
.tab-btn {
  background: none; border: none;
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast);
  display: flex; align-items: center; gap: var(--space-2);
}
.tab-btn:hover { color: var(--color-text-primary); }
.tab-btn.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }
.tab-count {
  background: var(--color-bg-elevated);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
}

/* Bookings */
.bookings-list { display: flex; flex-direction: column; gap: var(--space-3); }

/* Upcoming with countdown */
.upcoming-section { margin-bottom: var(--space-6); }
.upcoming-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}
.upcoming-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-3);
}
.upcoming-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  background: linear-gradient(135deg, rgba(193,216,47,0.06), rgba(16,185,129,0.02));
  border: 1px solid rgba(193,216,47,0.25);
  border-radius: var(--radius-xl);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-fast);
}
.upcoming-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary);
}
.uc-countdown {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  justify-content: space-around;
}
.uc-cd-unit { text-align: center; }
.uc-cd-unit strong {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  color: var(--color-primary);
  line-height: 1;
}
.uc-cd-unit span {
  display: block;
  margin-top: 2px;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}
.uc-info strong {
  display: block;
  font-size: 1rem;
  margin-bottom: 4px;
}
.uc-info p {
  margin: 0 0 4px;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}
.uc-location { font-size: 0.78rem; color: var(--color-text-muted); }
.uc-escrow {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(16,185,129,0.1);
  color: #10b981;
  font-size: 0.72rem;
  font-weight: 600;
}
.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5) var(--space-6);
  border-radius: var(--radius-xl);
  transition: all var(--transition-fast);
  text-decoration: none;
  color: inherit;
}
.booking-item:hover { border-color: var(--color-primary); transform: translateX(4px); }
.booking-info h4 { font-size: var(--font-size-base); margin-bottom: var(--space-1); }
.booking-info p { color: var(--color-text-muted); font-size: var(--font-size-sm); }
.booking-meta { display: flex; align-items: center; gap: var(--space-4); }
.booking-price { font-weight: 700; color: var(--color-primary); font-size: var(--font-size-lg); }
.chevron { color: var(--color-text-muted); }

/* Status badges */
.status-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  white-space: nowrap;
}
.status-info { background: rgba(100,149,237,0.15); color: #6495ed; }
.status-warning { background: var(--color-warning-light); color: var(--color-warning); }
.status-success { background: var(--color-success-light); color: var(--color-success); }
.status-error { background: rgba(232,93,74,0.15); color: var(--color-accent); }
.status-completed { background: rgba(193,216,47,0.15); color: var(--color-primary); }

.empty-state { text-align: center; padding: var(--space-16); }
.empty-state h3 { font-size: var(--font-size-xl); margin-bottom: var(--space-2); }
.empty-state p { color: var(--color-text-muted); font-size: var(--font-size-sm); }

.loading-state { padding: var(--space-4); }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .booking-item { flex-direction: column; align-items: flex-start; gap: var(--space-3); }
  .booking-meta { width: 100%; justify-content: space-between; }
  .tabs { overflow-x: auto; }
}

/* Banner solicitudes abiertas */
.open-gigs-banner {
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  padding: 16px 20px; margin-bottom: var(--space-4);
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, rgba(193, 216, 47, 0.13), rgba(193, 216, 47, 0.03));
  border: 1px solid rgba(193, 216, 47, 0.32);
}
.ogb-left { display: flex; align-items: center; gap: 14px; min-width: 0; }
.ogb-icon {
  flex-shrink: 0; width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(193, 216, 47, 0.18); border-radius: 50%; color: var(--color-primary);
}
.ogb-left strong { color: var(--color-text-primary); font-size: 0.98rem; }
.ogb-left p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.85rem; line-height: 1.4; }
.ogb-actions { display: flex; gap: 8px; flex-shrink: 0; }
@media (max-width: 600px) {
  .open-gigs-banner { flex-direction: column; align-items: stretch; }
  .ogb-actions { justify-content: flex-end; }
}
</style>
