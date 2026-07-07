<template>
  <div class="my-gigs-page">
    <div class="container">
      <router-link to="/dashboard" class="back-link">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al dashboard
      </router-link>

      <div class="header-row">
        <div>
          <h1 class="page-title">Mis solicitudes abiertas</h1>
          <p class="page-sub">Publicá una solicitud y recibí ofertas de DJs sin elegir a uno específico.</p>
        </div>
        <router-link to="/open-gig/new" class="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Nueva solicitud
        </router-link>
      </div>

      <div v-if="loading" class="loading">Cargando…</div>

      <div v-else-if="!gigs.length" class="empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <h3>Todavía no publicaste solicitudes</h3>
        <p>Publicá una y los DJs te enviarán ofertas.</p>
        <router-link to="/open-gig/new" class="btn btn-primary">Publicar solicitud</router-link>
      </div>

      <div v-else class="gigs-list">
        <router-link v-for="g in gigs" :key="g.id"
          :to="{ name: 'open-gig-detail', params: { id: g.id } }"
          class="gig-card">
          <div class="gig-head">
            <span class="status-pill" :class="'status-' + g.status">{{ statusLabel(g.status) }}</span>
            <span class="tier-pill" v-if="g.status === 'open' && g.requested_items?.includes('dj')">
              Visible: {{ tierLabel(g.visible_to_tier) }}
            </span>
          </div>
          <div v-if="g.requested_items_display?.length" class="gig-needs">
            <span v-for="it in g.requested_items_display" :key="it.key"
              class="need-chip" :class="'need-' + it.key">{{ it.label }}</span>
          </div>
          <h3 class="gig-title">
            {{ g.event_name || g.event_type_display }}
          </h3>
          <div class="gig-meta">
            <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> {{ formatDate(g.event_date) }}</span>
            <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg> {{ g.event_city || 'Panamá' }}</span>
            <span><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> {{ g.event_time_start }} · {{ g.event_duration_hours }}h</span>
          </div>
          <div class="gig-footer">
            <span class="offers-badge" :class="{ 'has-offers': g.offers_count }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              {{ g.offers_count }} oferta{{ g.offers_count === 1 ? '' : 's' }}
            </span>
            <span class="see-more">Ver detalles ›</span>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const gigs = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/open-gigs/')
    gigs.value = Array.isArray(data) ? data : (data.results || [])
  } finally {
    loading.value = false
  }
}

const STATUS_MAP = {
  open: 'Abierta',
  assigned: 'Asignada',
  expired: 'Expirada',
  cancelled: 'Cancelada',
}
const TIER_MAP = { premium: 'Solo Premium', pro: 'Premium + Pro', all: 'Todos los DJs' }

function statusLabel(s) { return STATUS_MAP[s] || s }
function tierLabel(t) { return TIER_MAP[t] || t }
function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-PA', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(load)
</script>

<style scoped>
.my-gigs-page { min-height: 100vh; background: #0a0a0a; padding: 24px 0 60px; color: #f5f5f5; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }

.back-link {
  display: inline-flex; align-items: center; gap: 6px;
  color: #C1D82F; text-decoration: none; font-weight: 500;
  margin-bottom: 20px;
}

.header-row { display: flex; justify-content: space-between; align-items: end; margin-bottom: 24px; gap: 16px; flex-wrap: wrap; }
.page-title { margin: 0; font-size: 1.8rem; color: #fff; }
.page-sub { margin: 4px 0 0; color: #a0a0a0; font-size: 0.95rem; }

.btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; border-radius: 999px; font-weight: 600;
  text-decoration: none; cursor: pointer; border: 1px solid transparent;
  font-size: 0.92rem;
}
.btn-primary { background: #C1D82F; color: #0d0d0d; }
.btn-primary:hover { background: #d5ef47; }

.loading, .empty {
  text-align: center; padding: 60px 20px; color: #a0a0a0;
}
.empty svg { color: #4a4a4a; margin-bottom: 12px; }
.empty h3 { color: #fff; margin: 8px 0 4px; }
.empty p { margin-bottom: 16px; }

.gigs-list { display: grid; gap: 14px; }
.gig-card {
  display: block; text-decoration: none; color: inherit;
  background: #141414; border: 1px solid #242424;
  border-radius: 14px; padding: 18px 20px;
  transition: transform 0.15s, border-color 0.15s;
}
.gig-card:hover { transform: translateY(-1px); border-color: #3a3a3a; }

.gig-head { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.status-pill {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.3px;
  padding: 3px 10px; border-radius: 999px; text-transform: uppercase;
}
.status-open { background: rgba(193, 216, 47, 0.15); color: #C1D82F; }
.status-assigned { background: rgba(60, 180, 130, 0.18); color: #6ee7a7; }
.status-expired { background: rgba(150, 150, 150, 0.15); color: #a0a0a0; }
.status-cancelled { background: rgba(220, 60, 60, 0.15); color: #ff8a8a; }
.tier-pill {
  font-size: 0.72rem; color: #a0a0a0; padding: 3px 10px;
  border: 1px solid #2a2a2a; border-radius: 999px;
}

.gig-needs { display: flex; flex-wrap: wrap; gap: 5px; margin: 4px 0 10px; }
.need-chip {
  display: inline-flex; padding: 3px 10px;
  border-radius: 999px; font-size: 0.72rem; font-weight: 600;
  background: rgba(193, 216, 47, 0.14); color: #C1D82F;
  border: 1px solid rgba(193, 216, 47, 0.3);
}
.need-chip.need-sound   { background: rgba(90, 160, 255, 0.13); color: #a5c6ff; border-color: rgba(165, 198, 255, 0.28); }
.need-chip.need-lights  { background: rgba(255, 180, 60, 0.15); color: #f5c85c; border-color: rgba(245, 200, 92, 0.28); }
.need-chip.need-booth   { background: rgba(200, 100, 220, 0.15); color: #d4a5ff; border-color: rgba(212, 165, 255, 0.28); }
.need-chip.need-screens { background: rgba(90, 220, 190, 0.13); color: #7fddc0; border-color: rgba(127, 221, 192, 0.28); }
.need-chip.need-other   { background: rgba(180, 180, 180, 0.13); color: #cfcfcf; border-color: rgba(200, 200, 200, 0.2); }

.gig-title { margin: 0 0 10px; font-size: 1.1rem; color: #fff; }
.gig-meta {
  display: flex; flex-wrap: wrap; gap: 14px;
  color: #a0a0a0; font-size: 0.86rem; margin-bottom: 12px;
}
.gig-meta span { display: inline-flex; align-items: center; gap: 5px; }
.gig-meta svg { color: #C1D82F; }

.gig-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 1px solid #242424;
}
.offers-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 12px; border-radius: 999px;
  background: #0d0d0d; border: 1px solid #2a2a2a;
  font-size: 0.82rem; color: #a0a0a0;
}
.offers-badge.has-offers { border-color: #C1D82F; color: #C1D82F; }
.see-more { color: #a0a0a0; font-size: 0.85rem; }
</style>
