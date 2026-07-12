<template>
  <div class="detail-page">
    <div class="container">
      <router-link :to="isTalent ? '/talent-dashboard' : '/dashboard/open-gigs'" class="back-link">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver
      </router-link>

      <div v-if="loading" class="loading">Cargando…</div>

      <template v-else-if="gig">
        <!-- Cabecera -->
        <div class="head-card">
          <div class="head-top">
            <span class="status-pill" :class="'status-' + gig.status">{{ statusLabel(gig.status) }}</span>
            <span v-if="gig.status === 'open' && gig.requested_items && gig.requested_items.includes('dj')" class="tier-pill">
              Visible: {{ tierLabel(gig.visible_to_tier) }}
            </span>
          </div>
          <div v-if="gig.requested_items_display?.length" class="requested-row">
            <span class="requested-label">Necesita:</span>
            <span v-for="it in gig.requested_items_display" :key="it.key"
              class="requested-chip" :class="'need-' + it.key">
              {{ it.label }}
            </span>
          </div>
          <h1 class="event-title">{{ gig.event_name || gig.event_type_display }}</h1>
          <div class="meta-grid">
            <div><label>Fecha</label><span>{{ formatDate(gig.event_date) }}</span></div>
            <div><label>Horario</label><span>{{ gig.event_time_start }} – {{ gig.event_time_end }}</span></div>
            <div><label>Duración</label><span>{{ gig.event_duration_hours }}h</span></div>
            <div><label>Ciudad</label><span>{{ gig.event_city || 'Panamá' }}</span></div>
            <div><label>Ubicación</label><span>{{ gig.event_location }}</span></div>
            <div><label>Invitados</label><span>{{ gig.guest_count || '—' }}</span></div>
            <div><label>Espacio</label><span>{{ gig.event_indoor ? 'Interior' : 'Exterior' }}</span></div>
            <div v-if="gig.genre_preference"><label>Género</label><span>{{ gig.genre_preference }}</span></div>
            <div v-if="gig.budget"><label>Presupuesto</label><span>USD {{ gig.budget }}</span></div>
          </div>
          <div v-if="gig.description" class="description">
            <label>Descripción</label>
            <p>{{ gig.description }}</p>
          </div>
          <div v-if="isOwner && gig.status === 'open'" class="owner-actions">
            <button class="btn btn-ghost" @click="cancelGig">Cancelar solicitud</button>
          </div>
        </div>

        <!-- ═══ Panel para DJ ═══ -->
        <div v-if="isTalent && gig.status === 'open' && gig.requested_items?.includes('dj') && !myTalentOffer" class="offer-form-card">
          <h2>Envía tu oferta como DJ</h2>
          <p class="sub">El cliente verá tu perfil, rating y precio. Sé competitivo.</p>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Tu precio (USD) *</label>
              <input v-model.number="djOfferForm.quoted_price" type="number" min="1" step="1" class="form-input" required>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Mensaje para el cliente</label>
            <textarea v-model="djOfferForm.message" class="form-input" rows="3"
              placeholder="Contale por qué eres su mejor opción, qué incluye tu servicio…"></textarea>
          </div>
          <div v-if="offerError" class="error-msg">{{ offerError }}</div>
          <div class="cta-row">
            <button class="btn btn-primary" @click="sendDjOffer" :disabled="sending || !djOfferForm.quoted_price">
              {{ sending ? 'Enviando…' : 'Enviar oferta' }}
            </button>
          </div>
        </div>

        <div v-else-if="isTalent && myTalentOffer" class="my-offer-card">
          <h2>Tu oferta como DJ</h2>
          <div class="my-offer-row">
            <span class="price">USD {{ myTalentOffer.quoted_price }}</span>
            <span class="status-pill" :class="'status-offer-' + myTalentOffer.status">{{ offerStatusLabel(myTalentOffer.status) }}</span>
          </div>
          <p v-if="myTalentOffer.message" class="offer-msg">"{{ myTalentOffer.message }}"</p>
          <p class="sub">Enviada el {{ formatDateTime(myTalentOffer.created_at) }}.</p>
        </div>

        <div v-else-if="isTalent && !gig.requested_items?.includes('dj')" class="my-offer-card">
          <p class="sub">Esta solicitud no está pidiendo DJ.</p>
        </div>

        <!-- ═══ Panel para Partner ═══ -->
        <div v-if="isPartner && gig.status === 'open'" class="offer-form-card">
          <h2>Enviar oferta de pack</h2>
          <p class="sub">Puedes mandar una oferta por cada categoría que ofrezcas. Elige uno de tus packs (opcional).</p>

          <template v-for="cat in partnerCoverableCats" :key="cat">
            <div v-if="!myPartnerOfferFor(cat)" class="partner-offer-block">
              <div class="partner-offer-title">Oferta para <strong>{{ needLabel(cat) }}</strong></div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Precio (USD) *</label>
                  <input v-model.number="partnerForms[cat].quoted_price" type="number" min="1" step="1" class="form-input">
                </div>
                <div class="form-group" style="flex:2">
                  <label class="form-label">Tu pack (opcional)</label>
                  <select v-model.number="partnerForms[cat].pack_id" class="form-input">
                    <option :value="null">— sin pack específico —</option>
                    <option v-for="p in packsForCategory(cat)" :key="p.id" :value="p.id">
                      {{ p.name }} · USD {{ p.price }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Mensaje</label>
                <textarea v-model="partnerForms[cat].message" class="form-input" rows="2"
                  placeholder="Qué incluye la oferta, condiciones, etc."></textarea>
              </div>
              <div class="cta-row">
                <button class="btn btn-primary btn-sm"
                  @click="sendPartnerOffer(cat)"
                  :disabled="sending || !partnerForms[cat].quoted_price">
                  Enviar oferta de {{ needLabel(cat) }}
                </button>
              </div>
            </div>
            <div v-else class="partner-my-offer">
              <div class="partner-offer-title">
                <strong>{{ needLabel(cat) }}</strong>
                <span class="status-pill" :class="'status-offer-' + myPartnerOfferFor(cat).status" style="margin-left:8px">
                  {{ offerStatusLabel(myPartnerOfferFor(cat).status) }}
                </span>
              </div>
              <div class="partner-price">USD {{ myPartnerOfferFor(cat).quoted_price }}</div>
              <p v-if="myPartnerOfferFor(cat).pack_name" class="sub">Pack: {{ myPartnerOfferFor(cat).pack_name }}</p>
              <p v-if="myPartnerOfferFor(cat).message" class="offer-msg">"{{ myPartnerOfferFor(cat).message }}"</p>
            </div>
          </template>
          <p v-if="!partnerCoverableCats.length" class="sub">Esta solicitud no incluye categorías que cubras.</p>
          <div v-if="offerError" class="error-msg">{{ offerError }}</div>
        </div>

        <!-- Panel para cliente: ver ofertas agrupadas por categoría -->
        <div v-if="isOwner" class="offers-panel">
          <h2>Ofertas recibidas ({{ visibleOffers.length }})</h2>

          <div v-if="!visibleOffers.length" class="no-offers">
            <p>Aún no hay ofertas. Te avisaremos por email cuando lleguen.</p>
          </div>

          <div v-else class="offers-by-category">
            <div v-for="cat in gig.requested_items || []" :key="cat" class="offer-category">
              <h3 class="offer-cat-title">
                <span class="requested-chip" :class="'need-' + cat">{{ needLabel(cat) }}</span>
                <span v-if="acceptedInCategory(cat)" class="cat-status cat-status-accepted">✓ Aceptada</span>
              </h3>
              <div v-if="!offersForCategory(cat).length" class="cat-empty">Sin ofertas todavía.</div>
              <div v-else class="offers-list">
                <div v-for="o in offersForCategory(cat)" :key="o.id" class="offer-card"
                  :class="{ 'offer-accepted': o.status === 'accepted', 'offer-rejected': o.status === 'rejected' }">
                  <div class="offer-left">
                    <img v-if="o.provider_avatar" :src="o.provider_avatar" :alt="o.provider_name" class="avatar">
                    <div v-else class="avatar avatar-placeholder">{{ (o.provider_name || '?').charAt(0) }}</div>
                  </div>
                  <div class="offer-body">
                    <div class="offer-head">
                      <router-link v-if="o.offer_kind === 'dj' && o.talent"
                        :to="`/talent/${o.talent}`" class="talent-name">{{ o.provider_name }}</router-link>
                      <span v-else class="talent-name">{{ o.provider_name }}</span>
                      <span v-if="o.offer_kind === 'dj'" class="tier-badge" :class="'tier-' + o.talent_level">{{ tierBadge(o.talent_level) }}</span>
                      <span v-else class="tier-badge">Aliado</span>
                    </div>
                    <div class="offer-meta">
                      <span v-if="o.offer_kind === 'dj' && Number(o.talent_rating) > 0">★ {{ Number(o.talent_rating).toFixed(1) }} ({{ o.talent_reviews }})</span>
                      <span v-if="o.provider_city"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg> {{ o.provider_city }}</span>
                      <span v-if="o.pack_name"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg> {{ o.pack_name }}</span>
                    </div>
                    <p v-if="o.message" class="offer-message">"{{ o.message }}"</p>
                  </div>
                  <div class="offer-right">
                    <div class="offer-price">USD {{ o.quoted_price }}</div>
                    <div v-if="o.status === 'pending' && !acceptedInCategory(cat) && ['open','assigned'].includes(gig.status)" class="offer-actions">
                      <button class="btn btn-primary btn-sm" @click="acceptOffer(o)">Aceptar</button>
                      <button class="btn btn-ghost btn-sm" @click="rejectOffer(o)">Rechazar</button>
                    </div>
                    <div v-else class="offer-status">
                      <span class="status-pill" :class="'status-offer-' + o.status">{{ offerStatusLabel(o.status) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="empty">Solicitud no encontrada.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const NEED_LABELS = {
  dj: 'DJ', sound: 'Sonido', lights: 'Luces',
  booth: 'DJ Booth', screens: 'Pantallas', other: 'Otro',
}
// item de request → categorías de pack del partner que lo cubren
const NEED_TO_PACK_CATS = {
  sound: ['sound'], lights: ['lights'], booth: ['dj_booth'],
  screens: ['screens'], other: ['mics', 'fx', 'sound', 'lights', 'screens', 'dj_booth'],
}

const gig = ref(null)
const loading = ref(true)
const sending = ref(false)
const offerError = ref('')

const djOfferForm = reactive({ quoted_price: null, message: '' })

// Formularios de partner por categoría — se auto-inicializan cuando cambia gig
const partnerForms = reactive({})
const myPacks = ref([])
const partnerProfile = ref(null)

const currentUser = computed(() => auth.user || {})
const isOwner = computed(() => gig.value && gig.value.client === currentUser.value.id)
const isTalent = computed(() => currentUser.value?.role === 'talent')
const isPartner = computed(() => currentUser.value?.role === 'partner' || currentUser.value?.is_partner_active)

const myTalentOffer = computed(() => {
  if (!isTalent.value || !gig.value?.offers) return null
  return gig.value.offers.find(o => o.offer_kind === 'dj' && o.provider_user_id === currentUser.value.id) || null
})

function myPartnerOfferFor(cat) {
  if (!isPartner.value || !gig.value?.offers) return null
  return gig.value.offers.find(o => o.offer_kind === 'pack' && o.covers_item === cat && o.provider_user_id === currentUser.value.id) || null
}

const partnerCoverableCats = computed(() => {
  if (!gig.value || !isPartner.value) return []
  const requested = gig.value.requested_items || []
  const myCats = new Set(partnerProfile.value?.categories || [])
  if (!myCats.size) {
    // Sin categorías definidas aún: mostramos todas las de pack solicitadas
    return requested.filter(i => i !== 'dj')
  }
  return requested.filter(item => {
    if (item === 'dj') return false
    const needed = NEED_TO_PACK_CATS[item] || []
    return needed.some(c => myCats.has(c))
  })
})

function packsForCategory(cat) {
  const wantedPackCats = new Set(NEED_TO_PACK_CATS[cat] || [])
  return myPacks.value.filter(p => wantedPackCats.has(p.category))
}

const visibleOffers = computed(() => gig.value?.offers || [])

function offersForCategory(cat) {
  return visibleOffers.value.filter(o => o.covers_item === cat)
}

function acceptedInCategory(cat) {
  return visibleOffers.value.some(o => o.covers_item === cat && o.status === 'accepted')
}

function needLabel(cat) { return NEED_LABELS[cat] || cat }

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/open-gigs/${route.params.id}/`)
    gig.value = data
  } catch (e) {
    gig.value = null
  } finally {
    loading.value = false
  }
}

async function loadPartnerContext() {
  if (!isPartner.value) return
  try {
    const [profRes, packsRes] = await Promise.all([
      api.get('/partner/production/').catch(() => ({ data: null })),
      api.get('/partner/production/packs/').catch(() => ({ data: [] })),
    ])
    partnerProfile.value = profRes.data || null
    const packsData = packsRes.data
    myPacks.value = Array.isArray(packsData) ? packsData : (packsData?.results || [])
  } catch { /* silencioso */ }
}

// Inicializar formulario partner por categoría cuando gig o packs cambian
watch([() => partnerCoverableCats.value.join(','), () => myPacks.value.length], () => {
  partnerCoverableCats.value.forEach(cat => {
    if (!partnerForms[cat]) {
      partnerForms[cat] = { quoted_price: null, pack_id: null, message: '' }
    }
  })
})

async function sendDjOffer() {
  offerError.value = ''
  if (!djOfferForm.quoted_price || djOfferForm.quoted_price <= 0) {
    offerError.value = 'Ingresa un precio válido.'
    return
  }
  sending.value = true
  try {
    await api.post(`/open-gigs/${gig.value.id}/offers/`, {
      quoted_price: djOfferForm.quoted_price,
      message: djOfferForm.message,
    })
    await load()
  } catch (e) {
    offerError.value = e?.response?.data?.error || e?.response?.data?.detail || 'No se pudo enviar la oferta.'
  } finally {
    sending.value = false
  }
}

async function sendPartnerOffer(cat) {
  offerError.value = ''
  const f = partnerForms[cat]
  if (!f?.quoted_price || f.quoted_price <= 0) {
    offerError.value = 'Ingresa un precio válido.'
    return
  }
  sending.value = true
  try {
    await api.post(`/open-gigs/${gig.value.id}/offers/`, {
      quoted_price: f.quoted_price,
      message: f.message,
      pack_id: f.pack_id || null,
      covers_item: cat,
    })
    await load()
  } catch (e) {
    offerError.value = e?.response?.data?.error || e?.response?.data?.detail || 'No se pudo enviar la oferta.'
  } finally {
    sending.value = false
  }
}

async function acceptOffer(o) {
  const msg = o.offer_kind === 'dj'
    ? `¿Aceptar la oferta de ${o.provider_name} por USD ${o.quoted_price}? Se creará la reserva.`
    : `¿Aceptar el pack de ${o.provider_name} por USD ${o.quoted_price}?`
  if (!confirm(msg)) return
  try {
    const { data } = await api.post(`/open-gigs/${gig.value.id}/offers/${o.id}/accept/`)
    // Solo redirigimos al detalle del booking si la request quedó completamente asignada
    if (data.gig_status === 'assigned' && data.booking_id) {
      router.push({ name: 'booking-detail', params: { id: data.booking_id } })
    } else {
      await load()
    }
  } catch (e) {
    alert(e?.response?.data?.error || 'No se pudo aceptar la oferta.')
  }
}

async function rejectOffer(o) {
  if (!confirm(`¿Rechazar la oferta de ${o.provider_name}?`)) return
  try {
    await api.post(`/open-gigs/${gig.value.id}/offers/${o.id}/reject/`)
    await load()
  } catch (e) {
    alert(e?.response?.data?.error || 'No se pudo rechazar la oferta.')
  }
}

async function cancelGig() {
  if (!confirm('¿Cancelar esta solicitud? Se rechazarán las ofertas pendientes.')) return
  try {
    await api.post(`/open-gigs/${gig.value.id}/cancel/`)
    await load()
  } catch (e) {
    alert('No se pudo cancelar.')
  }
}

const STATUS_MAP = { open: 'Abierta', assigned: 'Asignada', expired: 'Expirada', cancelled: 'Cancelada' }
const TIER_MAP = { premium: 'Solo Premium', pro: 'Premium + Pro', all: 'Todos los DJs' }
const OFFER_STATUS = { pending: 'Pendiente', accepted: 'Aceptada', rejected: 'Rechazada', withdrawn: 'Retirada' }

function statusLabel(s) { return STATUS_MAP[s] || s }
function tierLabel(t) { return TIER_MAP[t] || t }
function offerStatusLabel(s) { return OFFER_STATUS[s] || s }
function tierBadge(level) {
  if (level === 'premium') return '⭐ Premium'
  if (level === 'pro') return 'Pro'
  return 'Standard'
}
function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-PA', { day: '2-digit', month: 'short', year: 'numeric' })
}
function formatDateTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('es-PA', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  await load()
  await loadPartnerContext()
})
</script>

<style scoped>
.detail-page { min-height: 100vh; background: #0a0a0a; padding: 24px 0 60px; color: #f5f5f5; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }

.back-link {
  display: inline-flex; align-items: center; gap: 6px;
  color: #C1D82F; text-decoration: none; font-weight: 500;
  margin-bottom: 20px;
}

.loading, .empty { text-align: center; padding: 60px 20px; color: #a0a0a0; }

.head-card, .offer-form-card, .my-offer-card, .offers-panel {
  background: #141414; border: 1px solid #242424;
  border-radius: 14px; padding: 22px 24px;
  margin-bottom: 18px;
}

.head-top { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
.status-pill {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.3px;
  padding: 3px 10px; border-radius: 999px; text-transform: uppercase;
}
.status-open { background: rgba(193, 216, 47, 0.15); color: #C1D82F; }
.status-assigned { background: rgba(60, 180, 130, 0.18); color: #6ee7a7; }
.status-expired { background: rgba(150, 150, 150, 0.15); color: #a0a0a0; }
.status-cancelled { background: rgba(220, 60, 60, 0.15); color: #ff8a8a; }
.status-offer-pending { background: rgba(240, 180, 60, 0.16); color: #f5c85c; }
.status-offer-accepted { background: rgba(60, 180, 130, 0.18); color: #6ee7a7; }
.status-offer-rejected { background: rgba(220, 60, 60, 0.15); color: #ff8a8a; }
.status-offer-withdrawn { background: rgba(150, 150, 150, 0.15); color: #a0a0a0; }
.tier-pill { font-size: 0.72rem; color: #a0a0a0; padding: 3px 10px; border: 1px solid #2a2a2a; border-radius: 999px; }

.event-title { margin: 0 0 16px; font-size: 1.6rem; color: #fff; }
.meta-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px 20px;
  margin-bottom: 14px;
}
.meta-grid > div { display: flex; flex-direction: column; gap: 2px; }
.meta-grid label { font-size: 0.75rem; color: #7a7a7a; text-transform: uppercase; letter-spacing: 0.4px; }
.meta-grid span { color: #f0f0f0; font-size: 0.95rem; }

.description { border-top: 1px solid #242424; padding-top: 14px; }
.description label { font-size: 0.75rem; color: #7a7a7a; text-transform: uppercase; letter-spacing: 0.4px; }
.description p { color: #cfcfcf; margin: 6px 0 0; line-height: 1.55; white-space: pre-wrap; }

.owner-actions { margin-top: 16px; border-top: 1px solid #242424; padding-top: 14px; }

.offer-form-card h2, .my-offer-card h2, .offers-panel h2 { margin: 0 0 6px; font-size: 1.15rem; color: #fff; }
.sub { margin: 0 0 14px; color: #a0a0a0; font-size: 0.88rem; }

.form-group { margin-bottom: 14px; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
.form-label { display: block; font-size: 0.82rem; color: #cfcfcf; margin-bottom: 5px; }
.form-input {
  width: 100%; box-sizing: border-box;
  background: #0d0d0d; border: 1px solid #2a2a2a; color: #f5f5f5;
  padding: 9px 12px; border-radius: 8px; font-size: 0.92rem;
}
.form-input:focus { outline: none; border-color: #C1D82F; }
textarea.form-input { font-family: inherit; resize: vertical; }

.error-msg { background: rgba(220, 60, 60, 0.15); border: 1px solid rgba(220, 60, 60, 0.4); color: #ff8a8a; padding: 8px 12px; border-radius: 8px; font-size: 0.88rem; margin: 8px 0 12px; }

.cta-row { display: flex; justify-content: flex-end; gap: 10px; }
.btn {
  padding: 9px 18px; border-radius: 999px; font-weight: 600;
  border: 1px solid transparent; cursor: pointer; font-size: 0.9rem;
}
.btn-sm { padding: 6px 14px; font-size: 0.83rem; }
.btn-primary { background: #C1D82F; color: #0d0d0d; }
.btn-primary:hover:not(:disabled) { background: #d5ef47; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-ghost { background: transparent; border-color: #2a2a2a; color: #cfcfcf; }
.btn-ghost:hover { border-color: #4a4a4a; color: #fff; }

.my-offer-row { display: flex; align-items: center; gap: 12px; margin: 6px 0 10px; }
.price { font-size: 1.5rem; font-weight: 700; color: #C1D82F; }
.offer-msg { color: #cfcfcf; font-style: italic; margin: 0 0 8px; }

.no-offers { color: #a0a0a0; padding: 20px 0; text-align: center; }

.offers-list { display: grid; gap: 12px; }
.offer-card {
  display: grid; grid-template-columns: 56px 1fr auto;
  gap: 14px; align-items: center;
  background: #0d0d0d; border: 1px solid #242424;
  border-radius: 12px; padding: 14px 18px;
}
.avatar { width: 56px; height: 56px; border-radius: 50%; object-fit: cover; background: #1a1a1a; }
.avatar-placeholder { display: flex; align-items: center; justify-content: center; font-weight: 700; color: #C1D82F; font-size: 1.4rem; border: 1px solid #2a2a2a; }
.offer-head { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.talent-name { color: #fff; font-weight: 600; text-decoration: none; }
.talent-name:hover { text-decoration: underline; color: #C1D82F; }
.tier-badge {
  font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;
  background: #1a1a1a; border: 1px solid #2a2a2a; color: #cfcfcf;
}
.tier-premium { color: #C1D82F; border-color: #C1D82F; }
.tier-pro { color: #a5c6ff; border-color: #a5c6ff44; }
.offer-meta { display: flex; gap: 12px; color: #a0a0a0; font-size: 0.85rem; margin-bottom: 5px; }
.offer-message { color: #cfcfcf; font-size: 0.88rem; font-style: italic; margin: 4px 0 0; }
.offer-right { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.offer-price { font-size: 1.4rem; font-weight: 700; color: #fff; }
.offer-actions { display: flex; gap: 6px; }

@media (max-width: 600px) {
  .offer-card { grid-template-columns: 1fr; }
  .offer-right { align-items: flex-start; }
}

/* Chips de "necesita" */
.requested-row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 12px; }
.requested-label { color: #7a7a7a; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.4px; margin-right: 4px; }
.requested-chip {
  display: inline-flex; align-items: center; padding: 4px 12px;
  border-radius: 999px; font-size: 0.78rem; font-weight: 600;
  background: rgba(193, 216, 47, 0.14); color: #C1D82F;
  border: 1px solid rgba(193, 216, 47, 0.3);
}
.requested-chip.need-sound   { background: rgba(90, 160, 255, 0.13); color: #a5c6ff; border-color: rgba(165, 198, 255, 0.28); }
.requested-chip.need-lights  { background: rgba(255, 180, 60, 0.15); color: #f5c85c; border-color: rgba(245, 200, 92, 0.28); }
.requested-chip.need-booth   { background: rgba(200, 100, 220, 0.15); color: #d4a5ff; border-color: rgba(212, 165, 255, 0.28); }
.requested-chip.need-screens { background: rgba(90, 220, 190, 0.13); color: #7fddc0; border-color: rgba(127, 221, 192, 0.28); }
.requested-chip.need-other   { background: rgba(180, 180, 180, 0.13); color: #cfcfcf; border-color: rgba(200, 200, 200, 0.2); }

/* Ofertas agrupadas por categoría */
.offers-by-category { display: grid; gap: 20px; }
.offer-category { border-top: 1px solid #242424; padding-top: 14px; }
.offer-category:first-child { border-top: 0; padding-top: 0; }
.offer-cat-title {
  display: flex; align-items: center; gap: 10px;
  font-size: 1rem; margin: 0 0 10px; color: #fff;
}
.cat-status { font-size: 0.72rem; padding: 3px 10px; border-radius: 999px; font-weight: 700; }
.cat-status-accepted { background: rgba(60, 180, 130, 0.18); color: #6ee7a7; }
.cat-empty { color: #7a7a7a; font-size: 0.85rem; padding: 8px 0 4px; }

.offer-card.offer-accepted { border-color: rgba(60, 180, 130, 0.55); background: rgba(60, 180, 130, 0.05); }
.offer-card.offer-rejected { opacity: 0.55; }

/* Partner form blocks */
.partner-offer-block, .partner-my-offer {
  border-top: 1px solid #242424;
  padding-top: 14px; margin-top: 14px;
}
.partner-offer-block:first-of-type, .partner-my-offer:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
.partner-offer-title { font-weight: 600; color: #fff; margin-bottom: 10px; display: flex; align-items: center; }
.partner-price { font-size: 1.4rem; color: #C1D82F; font-weight: 700; margin: 4px 0; }
</style>
