<template>
  <div class="notif-wrapper" ref="wrapperRef">
    <button class="notif-bell" @click="toggleOpen" :title="`${unreadCount} notificaciones sin leer`">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 01-3.46 0"/>
      </svg>
      <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="notif-dropdown glass">
        <div class="notif-header">
          <h4>Notificaciones</h4>
          <button v-if="unreadCount > 0" class="mark-all-btn" @click="markAllRead">Marcar todas leídas</button>
        </div>
        <div class="notif-list" v-if="notifications.length > 0">
          <div v-for="n in notifications" :key="n.id"
            :class="['notif-item', { unread: !n.is_read }]"
            @click="handleClick(n)">
            <div class="notif-icon-wrap" :style="{ background: iconBg(n.notification_type) }">
              <span v-html="iconSvg(n.notification_type)"></span>
            </div>
            <div class="notif-content">
              <strong>{{ stripEmoji(n.title) }}</strong>
              <p>{{ stripEmoji(n.message) }}</p>
              <time>{{ timeAgo(n.created_at) }}</time>
            </div>
            <div v-if="!n.is_read" class="notif-dot"></div>
          </div>
        </div>
        <div v-else class="notif-empty">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
          <p>Sin notificaciones</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const isOpen = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const wrapperRef = ref(null)

function toggleOpen() {
  isOpen.value = !isOpen.value
  if (isOpen.value) fetchNotifications()
}

async function fetchNotifications() {
  try {
    const { data } = await api.get('/notifications/')
    const items = data.results || data
    notifications.value = Array.isArray(items) ? items.slice(0, 15) : []
  } catch { /* */ }
}

async function fetchUnreadCount() {
  try {
    const { data } = await api.get('/notifications/unread-count/')
    unreadCount.value = data.unread_count
  } catch { /* */ }
}

async function markAllRead() {
  try {
    await api.post('/notifications/read/', {})
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
  } catch { /* */ }
}

async function handleClick(n) {
  if (!n.is_read) {
    try {
      await api.post('/notifications/read/', { ids: [n.id] })
      n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch { /* */ }
  }
  isOpen.value = false
  if (n.link) router.push(n.link)
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Ahora'
  if (mins < 60) return `${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h`
  const days = Math.floor(hrs / 24)
  return `${days}d`
}

function iconBg(type) {
  const map = {
    new_request: 'var(--color-primary-ultra-light)',
    request_accepted: 'var(--color-success-light)',
    request_rejected: 'var(--color-error-light)',
    payment_received: 'var(--color-success-light)',
    booking_confirmed: 'var(--color-success-light)',
    booking_completed: 'var(--color-success-light)',
    booking_expired: 'rgba(150,150,150,0.15)',
    event_reminder: 'var(--color-warning-light)',
    reminder: 'var(--color-warning-light)',
    new_message: 'var(--color-secondary-light)',
    new_review: 'var(--color-warning-light)',
    system: 'var(--color-success-light)',
    tier_upgrade: 'var(--color-primary-ultra-light)',
    premium_invitation: 'var(--color-primary-ultra-light)',
    flagged_warning: 'var(--color-error-light)',
    open_gig_available: 'var(--color-primary-ultra-light)',
    open_gig_offer_received: 'var(--color-primary-ultra-light)',
    open_gig_offer_accepted: 'var(--color-success-light)',
    open_gig_offer_rejected: 'rgba(150,150,150,0.15)',
    open_gig_expired: 'rgba(150,150,150,0.15)',
  }
  return map[type] || 'rgba(255,255,255,0.05)'
}

function iconSvg(type) {
  const icons = {
    // Solicitudes tradicionales
    new_request: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    request_accepted: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
    request_rejected: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-error)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    // Pagos
    payment_received: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    // Bookings
    booking_confirmed: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><polyline points="9 12 12 15 16 10"/></svg>',
    booking_completed: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
    booking_expired: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    // Recordatorios
    event_reminder: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    reminder: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    // Chat
    new_message: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-secondary)" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>',
    // Reseñas
    new_review: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    // Sistema / verificación (shield-check)
    system: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
    // Tier / plan
    tier_upgrade: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><polyline points="17 11 12 6 7 11"/><polyline points="17 18 12 13 7 18"/></svg>',
    premium_invitation: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    // Warning (alert-triangle)
    flagged_warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-error)" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    // Solicitudes abiertas — rayo
    open_gig_available: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>',
    open_gig_offer_received: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>',
    open_gig_offer_accepted: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
    open_gig_offer_rejected: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    open_gig_expired: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  }
  return icons[type] || '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>'
}

// Strip emojis (y símbolos pictográficos) del principio del texto,
// para que las notificaciones viejas que los tenían en el título/mensaje
// se muestren limpias (ahora los emojis viven en el ícono del lado izquierdo).
const EMOJI_RE = /[\p{Extended_Pictographic}\p{Emoji_Presentation}️]/gu
function stripEmoji(txt) {
  if (!txt) return ''
  return String(txt).replace(EMOJI_RE, '').replace(/\s+/g, ' ').trim()
}

function handleOutsideClick(e) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) isOpen.value = false
}

let pollInterval
onMounted(() => {
  fetchUnreadCount()
  pollInterval = setInterval(fetchUnreadCount, 30000)
  document.addEventListener('click', handleOutsideClick)
})
onUnmounted(() => {
  clearInterval(pollInterval)
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.notif-wrapper { position: relative; }
.notif-bell { position: relative; background: none; border: none; color: var(--color-text-secondary); padding: var(--space-2); border-radius: var(--radius-sm); transition: all var(--transition-fast); cursor: pointer; }
.notif-bell:hover { color: var(--color-primary); background: rgba(193,216,47,0.06); }
.notif-badge { position: absolute; top: -2px; right: -2px; background: var(--color-accent); color: white; font-size: 9px; font-weight: 700; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid var(--color-bg-primary); }

.notif-dropdown { position: absolute; top: calc(100% + 8px); right: -60px; width: 380px; max-height: 480px; border-radius: var(--radius-xl); overflow: hidden; z-index: var(--z-dropdown); }
.notif-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--color-border); }
.notif-header h4 { font-family: var(--font-heading); font-size: var(--font-size-base); }
.mark-all-btn { background: none; border: none; color: var(--color-primary); font-size: var(--font-size-xs); cursor: pointer; font-weight: 500; }
.mark-all-btn:hover { text-decoration: underline; }

.notif-list { overflow-y: auto; max-height: 380px; }
.notif-item { display: flex; align-items: flex-start; gap: var(--space-3); padding: var(--space-4) var(--space-5); cursor: pointer; transition: background var(--transition-fast); border-bottom: 1px solid rgba(255,255,255,0.03); position: relative; }
.notif-item:hover { background: var(--color-bg-card-hover); }
.notif-item.unread { background: rgba(193,216,47,0.04); }
.notif-icon-wrap { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.notif-content { flex: 1; min-width: 0; }
.notif-content strong { font-size: var(--font-size-sm); display: block; margin-bottom: 2px; }
.notif-content p { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 0; line-height: 1.4; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.notif-content time { font-size: 10px; color: var(--color-text-muted); }
.notif-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-primary); flex-shrink: 0; margin-top: 6px; }

.notif-empty { padding: var(--space-10); text-align: center; color: var(--color-text-muted); }
.notif-empty svg { margin: 0 auto var(--space-3); opacity: 0.3; }
.notif-empty p { font-size: var(--font-size-sm); }

.dropdown-enter-active { transition: all 0.2s ease; }
.dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from { opacity: 0; transform: translateY(-8px) scale(0.95); }
.dropdown-leave-to { opacity: 0; transform: translateY(-4px) scale(0.98); }

@media (max-width: 768px) {
  .notif-wrapper { width: 100%; max-width: 280px; display: flex; justify-content: center; }
  .notif-bell { width: 100%; display: flex; align-items: center; justify-content: center; gap: var(--space-2); padding: var(--space-3) var(--space-5); border: 1px solid var(--color-border); border-radius: var(--radius-lg); font-size: var(--font-size-lg); }
  .notif-bell::after { content: 'Notificaciones'; font-family: var(--font-body); font-size: var(--font-size-base); }
  .notif-badge { position: static; margin-left: var(--space-1); }
  .notif-dropdown { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); right: auto; width: calc(100vw - 32px); max-width: 400px; max-height: 70vh; border-radius: var(--radius-xl); box-shadow: 0 20px 60px rgba(0,0,0,0.5); z-index: 9999; }
  .dropdown-enter-from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
  .dropdown-leave-to { opacity: 0; transform: translate(-50%, -50%) scale(0.95); }
}

/* ---- Light Mode Overrides ---- */
[data-theme="light"] .notif-badge {
  border-color: #F5F5F0;
}
[data-theme="light"] .notif-dropdown {
  background: rgba(255, 255, 255, 0.96);
  border-color: rgba(0, 0, 0, 0.08);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}
[data-theme="light"] .notif-item {
  border-bottom-color: rgba(0, 0, 0, 0.04);
}
[data-theme="light"] .notif-item.unread {
  background: rgba(107, 138, 15, 0.04);
}
[data-theme="light"] .notif-item:hover {
  background: rgba(107, 138, 15, 0.06);
}
[data-theme="light"] .notif-bell:hover {
  background: rgba(107, 138, 15, 0.06);
}
</style>
