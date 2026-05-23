<template>
  <div class="partner-dashboard">
    <div class="container">
      <!-- Header -->
      <div class="dashboard-header animate-fade-in-up">
        <div class="header-left">
          <div class="partner-badge">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
          </div>
          <div>
            <h1>Dashboard de Aliado</h1>
            <p class="subtitle">Gestión de reservas y comisiones</p>
          </div>
        </div>
        <router-link to="/search" class="btn btn-cta">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Nueva Reserva
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando dashboard...</p>
      </div>

      <!-- Stats Cards -->
      <div v-else class="animate-fade-in-up" style="animation-delay: 0.1s;">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon bookings-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_bookings }}</span>
              <span class="stat-label">Reservas Totales</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon active-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.active_bookings }}</span>
              <span class="stat-label">Activas</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon completed-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.completed_bookings }}</span>
              <span class="stat-label">Completadas</span>
            </div>
          </div>

          <div class="stat-card highlight">
            <div class="stat-icon commission-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">${{ formatMoney(stats.total_commission_earned) }}</span>
              <span class="stat-label">Comisiones Ganadas</span>
            </div>
          </div>
        </div>

        <!-- Pending Commission Banner -->
        <div v-if="parseFloat(stats.pending_commission) > 0" class="pending-banner">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          Tienes <strong>${{ formatMoney(stats.pending_commission) }}</strong> en comisiones pendientes de pago
        </div>

        <!-- Recent Bookings -->
        <div class="section-header">
          <h2>Reservas Recientes</h2>
          <router-link to="/dashboard" class="link-muted">Ver todas</router-link>
        </div>

        <div v-if="recentBookings.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.4">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <p>Aun no tienes reservas.</p>
          <router-link to="/search" class="btn btn-outline">Buscar Talentos</router-link>
        </div>

        <div v-else class="bookings-list">
          <div v-for="booking in recentBookings" :key="booking.id" class="booking-card glass" @click="goToBooking(booking.id)">
            <div class="booking-left">
              <div class="booking-avatar">
                <img v-if="booking.talent_avatar" :src="booking.talent_avatar" alt="">
                <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
                </svg>
              </div>
              <div class="booking-info">
                <h3>{{ booking.talent_name }}</h3>
                <p>{{ booking.event_type_display }} &middot; {{ formatDate(booking.event_date) }}</p>
                <p class="booking-location">{{ booking.event_city || booking.event_location }}</p>
              </div>
            </div>
            <div class="booking-right">
              <span class="status-badge" :class="'status-' + booking.status">
                {{ booking.status_display }}
              </span>
              <span class="booking-price" v-if="booking.quoted_price || booking.precio_estimado">
                ${{ formatMoney(booking.quoted_price || booking.precio_estimado) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(true)
const stats = ref({
  total_bookings: 0,
  active_bookings: 0,
  completed_bookings: 0,
  total_commission_earned: '0.00',
  pending_commission: '0.00',
})
const recentBookings = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/api/partner/dashboard/')
    stats.value = data.stats
    recentBookings.value = data.recent_bookings
  } catch (err) {
    console.error('Error loading partner dashboard:', err)
  } finally {
    loading.value = false
  }
})

function formatMoney(val) {
  return parseFloat(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('es-VE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function goToBooking(id) {
  router.push(`/dashboard/bookings/${id}`)
}
</script>

<style scoped>
.partner-dashboard {
  min-height: 100vh;
  padding: var(--space-8) var(--space-6);
  background: var(--color-bg-primary);
}

.container { max-width: 1100px; margin: 0 auto; }

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.partner-badge {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg-primary);
}

.dashboard-header h1 {
  font-size: var(--font-size-2xl);
  font-family: var(--font-heading);
  margin: 0;
}

.subtitle {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin: 0;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
}

.stat-card.highlight {
  background: linear-gradient(135deg, rgba(var(--color-primary-rgb, 163,190,140), 0.1), rgba(var(--color-primary-rgb, 163,190,140), 0.05));
  border-color: var(--color-primary);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bookings-icon { background: rgba(136, 192, 208, 0.15); color: #88c0d0; }
.active-icon { background: rgba(235, 203, 139, 0.15); color: #ebcb8b; }
.completed-icon { background: rgba(163, 190, 140, 0.15); color: #a3be8c; }
.commission-icon { background: rgba(163, 190, 140, 0.2); color: #a3be8c; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text-primary); }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: 2px; }

/* Pending banner */
.pending-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: rgba(235, 203, 139, 0.1);
  border: 1px solid rgba(235, 203, 139, 0.3);
  border-radius: var(--radius-lg);
  color: #ebcb8b;
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
}

/* Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.section-header h2 {
  font-size: var(--font-size-lg);
  font-family: var(--font-heading);
}

.link-muted {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.link-muted:hover { color: var(--color-primary-light); }

/* Bookings list */
.bookings-list { display: flex; flex-direction: column; gap: var(--space-3); }

.booking-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.booking-card:hover {
  transform: translateX(4px);
  border-color: var(--color-border-hover);
}

.booking-left { display: flex; align-items: center; gap: var(--space-4); }

.booking-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-input);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.booking-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.booking-info h3 {
  font-size: var(--font-size-base);
  margin: 0 0 2px;
}

.booking-info p {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.booking-location {
  font-size: var(--font-size-xs) !important;
  color: var(--color-text-muted) !important;
}

.booking-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-2);
}

.booking-price {
  font-weight: 600;
  color: var(--color-primary-light);
  font-size: var(--font-size-base);
}

/* Status badges */
.status-badge {
  font-size: var(--font-size-xs);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.status-solicitud_enviada { background: rgba(136,192,208,0.15); color: #88c0d0; }
.status-pendiente_respuesta { background: rgba(235,203,139,0.15); color: #ebcb8b; }
.status-aceptada { background: rgba(163,190,140,0.15); color: #a3be8c; }
.status-pendiente_pago { background: rgba(208,135,112,0.15); color: #d08770; }
.status-confirmada { background: rgba(163,190,140,0.2); color: #a3be8c; }
.status-completada { background: rgba(163,190,140,0.3); color: #a3be8c; }
.status-rechazada { background: rgba(191,97,106,0.15); color: #bf616a; }
.status-cancelada { background: rgba(191,97,106,0.1); color: #bf616a; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: var(--space-12) var(--space-6);
  color: var(--color-text-muted);
}

.empty-state p { margin: var(--space-4) 0; }

/* Loading */
.loading-state {
  text-align: center;
  padding: var(--space-16) 0;
  color: var(--color-text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary-light);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto var(--space-4);
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .booking-card { flex-direction: column; align-items: flex-start; gap: var(--space-3); }
  .booking-right { align-items: flex-start; flex-direction: row; gap: var(--space-3); }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
  .dashboard-header { flex-direction: column; align-items: flex-start; }
}
</style>
