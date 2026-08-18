<template>
  <div class="notifs-page">
    <div class="container">
      <div class="head">
        <div>
          <h1>Notificaciones</h1>
          <p class="sub">Tu historial completo — nada se borra.</p>
        </div>
        <button v-if="unreadCount > 0" class="mark-all" @click="markAllRead">
          Marcar todas leídas
        </button>
      </div>

      <div class="tabs">
        <button :class="['tab', { active: tab === 'all' }]" @click="tab = 'all'">
          Todas
        </button>
        <button :class="['tab', { active: tab === 'unread' }]" @click="tab = 'unread'">
          Sin leer <span v-if="unreadCount > 0" class="pill">{{ unreadCount }}</span>
        </button>
      </div>

      <div v-if="loading && !notifications.length" class="state">
        <div class="spinner"></div>
        <p>Cargando…</p>
      </div>

      <div v-else-if="!filtered.length" class="state empty">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
          <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>
        </svg>
        <p>{{ tab === 'unread' ? 'No tenés notificaciones sin leer.' : 'Todavía no tenés notificaciones.' }}</p>
      </div>

      <div v-else class="list">
        <button
          v-for="n in filtered" :key="n.id"
          :class="['item', { unread: !n.is_read, clickable: !!n.link }]"
          @click="handleClick(n)">
          <span class="icon" :style="{ background: iconBg(n.notification_type) }" v-html="iconSvg(n.notification_type)"></span>
          <span class="body">
            <strong>{{ stripEmoji(n.title) }}</strong>
            <span class="msg">{{ stripEmoji(n.message) }}</span>
            <time>{{ timeAgo(n.created_at) }}</time>
          </span>
          <span v-if="!n.is_read" class="dot"></span>
        </button>
      </div>

      <div v-if="hasMore" class="more">
        <button class="more-btn" :disabled="loading" @click="loadMore">
          {{ loading ? 'Cargando…' : 'Cargar más antiguas' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const notifications = ref([])
const unreadCount = ref(0)
const loading = ref(false)
const page = ref(1)
const hasMore = ref(false)
const tab = ref('all')

const filtered = computed(() =>
  tab.value === 'unread'
    ? notifications.value.filter(n => !n.is_read)
    : notifications.value
)

async function load(reset = false) {
  loading.value = true
  if (reset) { notifications.value = []; page.value = 1 }
  try {
    const { data } = await api.get('/notifications/', { params: { page: page.value } })
    const items = data.results || data
    if (Array.isArray(items)) notifications.value.push(...items)
    hasMore.value = !!data.next
    page.value++
  } catch { /* */ } finally {
    loading.value = false
  }
}

function loadMore() { load(false) }

async function fetchUnread() {
  try {
    const { data } = await api.get('/notifications/unread-count/')
    unreadCount.value = data.unread_count
  } catch { /* */ }
}

async function markAllRead() {
  try {
    await api.post('/notifications/read/', {})
    notifications.value.forEach(n => { n.is_read = true })
    unreadCount.value = 0
  } catch { /* */ }
}

function handleClick(n) {
  if (!n.is_read) {
    n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    api.post('/notifications/read/', { ids: [n.id] }).catch(() => {})
  }
  if (n.link) router.push(n.link).catch(() => {})
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Ahora'
  if (mins < 60) return `${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `hace ${hrs} h`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `hace ${days} d`
  return new Date(dateStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

const EMOJI_RE = /[\p{Extended_Pictographic}\p{Emoji_Presentation}️]/gu
function stripEmoji(txt) {
  if (!txt) return ''
  return String(txt).replace(EMOJI_RE, '').replace(/\s+/g, ' ').trim()
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
    booking_cancelled: 'var(--color-error-light)',
  }
  return map[type] || 'rgba(255,255,255,0.06)'
}

function iconSvg(type) {
  const s = (stroke, inner) =>
    `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`
  const P = 'var(--color-primary)', G = 'var(--color-success)', R = 'var(--color-error)', W = 'var(--color-warning)', S = 'var(--color-secondary)', M = 'var(--color-text-muted)'
  const icons = {
    new_request: s(P, '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>'),
    request_accepted: s(G, '<polyline points="20 6 9 17 4 12"/>'),
    request_rejected: s(R, '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'),
    payment_received: s(G, '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>'),
    booking_confirmed: s(G, '<rect x="3" y="4" width="18" height="18" rx="2"/><polyline points="9 12 12 15 16 10"/>'),
    booking_completed: s(G, '<polyline points="20 6 9 17 4 12"/>'),
    booking_expired: s(M, '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    event_reminder: s(W, '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    reminder: s(W, '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    new_message: s(S, '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>'),
    new_review: s(W, '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'),
    system: s(G, '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>'),
    tier_upgrade: s(P, '<polyline points="17 11 12 6 7 11"/><polyline points="17 18 12 13 7 18"/>'),
    premium_invitation: s(P, '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'),
    flagged_warning: s(R, '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    open_gig_available: s(P, '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>'),
    open_gig_offer_received: s(P, '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>'),
    open_gig_offer_accepted: s(G, '<polyline points="20 6 9 17 4 12"/>'),
    open_gig_offer_rejected: s(M, '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'),
    open_gig_expired: s(M, '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'),
    booking_cancelled: s(R, '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'),
  }
  return icons[type] || s('currentColor', '<circle cx="12" cy="12" r="10"/>')
}

onMounted(() => {
  load(true)
  fetchUnread()
})
</script>

<style scoped>
.notifs-page { min-height: 100vh; background: var(--color-bg-primary); padding: var(--space-6) 0 var(--space-16); color: var(--color-text-primary); }
.container { max-width: 720px; margin: 0 auto; padding: 0 var(--space-5); }

.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: var(--space-5); }
.head h1 { margin: 0; font-size: 1.6rem; }
.sub { margin: 4px 0 0; color: var(--color-text-muted); font-size: 0.9rem; }
.mark-all { background: none; border: 1px solid var(--color-border); color: var(--color-primary); padding: 8px 14px; border-radius: var(--radius-full); cursor: pointer; font-size: 0.85rem; font-weight: 600; white-space: nowrap; }
.mark-all:hover { border-color: var(--color-primary); }

.tabs { display: flex; gap: 8px; margin-bottom: var(--space-4); border-bottom: 1px solid var(--color-border); }
.tab { background: none; border: none; border-bottom: 2px solid transparent; color: var(--color-text-secondary); padding: 10px 6px; cursor: pointer; font-family: inherit; font-size: 0.92rem; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.tab.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }
.pill { background: var(--color-accent); color: #fff; font-size: 0.7rem; font-weight: 700; border-radius: 10px; padding: 1px 7px; }

.list { display: flex; flex-direction: column; }
.item { display: flex; align-items: flex-start; gap: 14px; padding: 16px 12px; background: none; border: none; border-bottom: 1px solid var(--color-border); text-align: left; width: 100%; font-family: inherit; position: relative; }
.item.clickable { cursor: pointer; }
.item.clickable:hover { background: var(--color-bg-card-hover, rgba(255,255,255,0.03)); }
.item.unread { background: rgba(193,216,47,0.05); }
.icon { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.body { display: flex; flex-direction: column; gap: 3px; min-width: 0; flex: 1; }
.body strong { font-size: 0.95rem; color: var(--color-text-primary); }
.body .msg { font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.4; }
.body time { font-size: 0.72rem; color: var(--color-text-muted); margin-top: 2px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--color-primary); flex-shrink: 0; margin-top: 6px; }

.state { text-align: center; padding: var(--space-12) var(--space-4); color: var(--color-text-muted); }
.state.empty svg { opacity: 0.35; margin-bottom: 10px; }
.spinner { width: 36px; height: 36px; border: 3px solid rgba(255,255,255,0.1); border-top-color: var(--color-primary); border-radius: 50%; margin: 0 auto 12px; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.more { text-align: center; margin-top: var(--space-5); }
.more-btn { background: var(--color-bg-elevated, rgba(255,255,255,0.04)); border: 1px solid var(--color-border); color: var(--color-text-secondary); padding: 10px 20px; border-radius: var(--radius-full); cursor: pointer; font-family: inherit; font-weight: 600; }
.more-btn:hover:not(:disabled) { border-color: var(--color-primary); color: var(--color-text-primary); }
.more-btn:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 600px) {
  .head h1 { font-size: 1.35rem; }
}
</style>
