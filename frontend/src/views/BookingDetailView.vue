<template>
  <div class="detail-page">
    <div class="container">
      <router-link to="/dashboard" class="back-link animate-fade-in-up">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al Dashboard
      </router-link>

      <div v-if="loading" class="loading-state">
        <div v-for="i in 4" :key="i" class="skeleton" style="height:60px;margin-bottom:var(--space-3);border-radius:var(--radius-lg);"></div>
      </div>

      <div v-else-if="booking" class="detail-layout animate-fade-in-up" style="animation-delay:0.1s">
        <!-- Left: Main Content -->
        <div class="detail-main">
          <!-- Header -->
          <div class="detail-header glass">
            <div class="header-top">
              <div>
                <h1>{{ booking.event_name || booking.event_type_display }}</h1>
                <p class="event-date">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  {{ formatDate(booking.event_date) }} · {{ booking.event_time_start?.slice(0,5) }} - {{ booking.event_time_end?.slice(0,5) }}
                </p>
              </div>
              <span class="status-badge" :class="statusClass(booking.status)">{{ statusLabel(booking.status) }}</span>
            </div>
          </div>

          <!-- Event Details -->
          <div class="info-card glass">
            <h3>Detalles del Evento</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Ubicación</span>
                <span>{{ booking.event_location }}</span>
              </div>
              <div v-if="booking.event_city" class="info-item">
                <span class="info-label">Ciudad</span>
                <span>{{ booking.event_city }}</span>
              </div>
              <div v-if="booking.guest_count" class="info-item">
                <span class="info-label">Invitados</span>
                <span>{{ booking.guest_count }}</span>
              </div>
              <div v-if="booking.event_duration_hours" class="info-item">
                <span class="info-label">Duración</span>
                <span>{{ booking.event_duration_hours }} horas</span>
              </div>
            </div>
            <div v-if="booking.description" class="info-description">
              <span class="info-label">Descripción</span>
              <p>{{ booking.description }}</p>
            </div>
          </div>

          <!-- Additional Services (from multi-step booking) -->
          <div v-if="booking.additional_services && Object.keys(booking.additional_services).length" class="info-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
              Servicios de Producción
            </h3>
            <div class="services-grid">
              <div v-for="(config, service) in booking.additional_services" :key="service" class="service-item">
                <div class="service-header">
                  <span class="service-icon">{{ serviceIcons[service] || '🎵' }}</span>
                  <strong>{{ serviceLabels[service] || service }}</strong>
                </div>
                <div v-if="typeof config === 'object'" class="service-details">
                  <div v-for="(val, key) in config" :key="key" class="service-detail-row">
                    <span class="info-label">{{ formatDetailKey(key) }}</span>
                    <span>{{ val }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="booking.additional_services_notes" class="info-description" style="margin-top:var(--space-4)">
              <span class="info-label">Notas de producción</span>
              <p>{{ booking.additional_services_notes }}</p>
            </div>
          </div>

          <!-- Talent Actions (accept/reject/adjust) -->
          <div v-if="isTalentView && canTalentAct" class="action-card glass">
            <h3>Responder Solicitud</h3>
            <div class="action-form">
              <div class="form-group">
                <label class="form-label">Precio Final ($)</label>
                <input v-model.number="quotedPrice" type="number" class="form-input" :placeholder="booking.precio_estimado || '0.00'" min="0" step="0.01">
              </div>
              <div class="form-group">
                <label class="form-label">Notas para el cliente</label>
                <textarea v-model="talentNotes" class="form-input" rows="3" placeholder="Detalles de tu propuesta..."></textarea>
              </div>
              <div class="action-buttons">
                <button @click="updateStatus('aceptada')" class="btn btn-primary" :disabled="actionLoading">
                  ✓ Aceptar
                </button>
                <button @click="updateStatus('rechazada')" class="btn btn-ghost btn-danger" :disabled="actionLoading">
                  ✕ Rechazar
                </button>
              </div>
            </div>
          </div>

          <!-- Client Actions (pay) -->
          <div v-if="isClientView && booking.status === 'pendiente_pago'" class="action-card glass">
            <h3>Confirmar Reserva</h3>
            <p class="action-desc">El talento aceptó tu solicitud. Realiza el pago para confirmar.</p>
            <div class="price-final">
              <span>Total a pagar</span>
              <span class="price-big">${{ booking.quoted_price || booking.precio_estimado }}</span>
            </div>
            <div v-if="booking.talent_notes" class="talent-notes-box">
              <strong>Notas del talento:</strong>
              <p>{{ booking.talent_notes }}</p>
            </div>
            <div class="action-buttons">
              <button @click="processPayment('full')" class="btn btn-primary" :disabled="actionLoading">
                Pagar Total
              </button>
              <button @click="processPayment('deposit')" class="btn btn-ghost" :disabled="actionLoading">
                Pagar 50% Depósito
              </button>
            </div>
          </div>

          <!-- Review (if completed) -->
          <div v-if="isClientView && booking.status === 'completada' && !booking.review" class="action-card glass">
            <h3>Deja tu Reseña</h3>
            <div class="review-form">
              <div class="star-rating">
                <button v-for="s in 5" :key="s" @click="reviewRating = s" class="star-btn" :class="{ active: s <= reviewRating }">★</button>
              </div>
              <textarea v-model="reviewComment" class="form-input" rows="3" placeholder="¿Cómo fue tu experiencia?"></textarea>
              <button @click="submitReview" class="btn btn-primary" :disabled="actionLoading || !reviewRating">
                Enviar Reseña
              </button>
            </div>
          </div>

          <!-- Admin/Talent: Mark as completed -->
          <div v-if="canMarkComplete" class="action-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Marcar como Completado
            </h3>
            <p class="action-desc">El evento ya fue realizado. Marcar como completado habilita las reseñas y actualiza las estadísticas del talento.</p>
            <button @click="updateStatus('completada')" class="btn btn-primary" :disabled="actionLoading">
              ✓ Completar Evento
            </button>
          </div>

          <!-- Existing Review -->
          <div v-if="booking.review" class="info-card glass">
            <h3>Reseña</h3>
            <div class="review-display">
              <div class="stars">{{ '★'.repeat(booking.review.rating) }}{{ '☆'.repeat(5 - booking.review.rating) }}</div>
              <p>{{ booking.review.comment }}</p>
            </div>
          </div>

          <!-- Chat Section -->
          <div class="chat-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              Chat
            </h3>
            <div class="chat-messages" ref="chatContainer">
              <div v-if="!messages.length" class="chat-empty">
                <p>Aún no hay mensajes. Inicia la conversación.</p>
              </div>
              <div v-for="msg in messages" :key="msg.id" class="chat-msg" :class="{ mine: msg.sender === auth.user?.id }">
                <div class="msg-bubble">
                  <span class="msg-sender">{{ msg.sender === auth.user?.id ? 'Tú' : msg.sender_name }}</span>
                  <p>{{ msg.content }}</p>
                  <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
                </div>
              </div>
            </div>
            <div class="chat-input-row">
              <input v-model="newMessage" @keyup.enter="sendMessage" type="text" class="form-input" placeholder="Escribe un mensaje...">
              <button @click="sendMessage" class="btn btn-primary btn-send" :disabled="!newMessage.trim()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Right: Sidebar -->
        <div class="detail-sidebar">
          <!-- Counterpart Info -->
          <div class="sidebar-card glass">
            <h4>{{ isTalentView ? 'Cliente' : 'Talento' }}</h4>
            <div class="person-info">
              <div class="person-avatar">
                {{ (isTalentView ? booking.client?.first_name : booking.talent?.stage_name)?.[0] || '?' }}
              </div>
              <div>
                <strong>{{ isTalentView ? `${booking.client?.first_name} ${booking.client?.last_name}` : booking.talent?.stage_name }}</strong>
                <p v-if="!isTalentView && booking.talent?.talent_level" class="talent-level">
                  {{ booking.talent.talent_level === 'premium' ? '⭐ Premium' : 'Standard' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Pricing Info -->
          <div class="sidebar-card glass">
            <h4>Precios</h4>
            <div class="price-rows">
              <div v-if="booking.precio_estimado" class="price-row">
                <span>Estimado</span><span>${{ booking.precio_estimado }}</span>
              </div>
              <div v-if="booking.quoted_price" class="price-row">
                <span>Precio Final</span><span class="text-primary">${{ booking.quoted_price }}</span>
              </div>
              <div v-if="booking.budget" class="price-row">
                <span>Presupuesto</span><span>${{ booking.budget }}</span>
              </div>
              <div class="price-divider"></div>
              <div class="price-row">
                <span>Pagado</span><span class="text-success">${{ booking.amount_paid || '0.00' }}</span>
              </div>
              <div v-if="booking.remaining_balance > 0" class="price-row">
                <span>Pendiente</span><span class="text-warning">${{ booking.remaining_balance }}</span>
              </div>
            </div>
          </div>

          <!-- Payments History -->
          <div v-if="booking.payments?.length" class="sidebar-card glass">
            <h4>Pagos</h4>
            <div v-for="p in booking.payments" :key="p.id" class="payment-item">
              <div>
                <strong>${{ p.amount }}</strong>
                <span class="payment-type">{{ p.payment_type === 'deposit' ? 'Depósito' : 'Total' }}</span>
              </div>
              <span class="payment-status" :class="p.payment_status === 'completed' ? 'text-success' : 'text-warning'">
                {{ p.payment_status === 'completed' ? '✓' : '⏳' }}
              </span>
            </div>
          </div>

          <!-- Cancel -->
          <div v-if="canCancel" class="sidebar-card glass">
            <button @click="updateStatus('cancelada')" class="btn btn-ghost btn-danger btn-full" :disabled="actionLoading">
              Cancelar Reserva
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const booking = ref(null)
const messages = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const newMessage = ref('')
const quotedPrice = ref(null)
const talentNotes = ref('')
const reviewRating = ref(0)
const reviewComment = ref('')
const chatContainer = ref(null)

const serviceLabels = {
  sonido: 'Sonido',
  iluminacion: 'Iluminación',
  tarima: 'Tarima / Booth',
  pantallas: 'Pantallas LED',
  efectos: 'Efectos Especiales',
}
const serviceIcons = {
  sonido: '🔊',
  iluminacion: '💡',
  tarima: '🎪',
  pantallas: '📺',
  efectos: '✨',
}

function formatDetailKey(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const isTalentView = computed(() => auth.user?.role === 'talent')
const isClientView = computed(() => auth.user?.role === 'client' || auth.user?.role === 'partner')

const canTalentAct = computed(() =>
  ['solicitud_enviada', 'pendiente_respuesta'].includes(booking.value?.status)
)

const canCancel = computed(() =>
  ['solicitud_enviada', 'pendiente_respuesta', 'aceptada', 'pendiente_pago'].includes(booking.value?.status)
)

const isAdminView = computed(() => auth.user?.role === 'admin')

const canMarkComplete = computed(() => {
  if (!booking.value || booking.value.status !== 'confirmada') return false
  // Show for admin always, for talent only after event date
  if (isAdminView.value) return true
  if (isTalentView.value) {
    const eventDate = new Date(booking.value.event_date + 'T23:59:59')
    return new Date() > eventDate
  }
  return false
})

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

function statusClass(s) { return statusMap[s]?.class || '' }
function statusLabel(s) { return statusMap[s]?.label || s }

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-VE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })
}

async function updateStatus(newStatus) {
  actionLoading.value = true
  try {
    const payload = { status: newStatus }
    if (quotedPrice.value) payload.quoted_price = quotedPrice.value
    if (talentNotes.value) payload.talent_notes = talentNotes.value

    const { data } = await api.patch(`/bookings/${booking.value.id}/status/`, payload)
    booking.value = data
  } catch (e) {
    alert(e.response?.data?.error || 'Error al actualizar el estado.')
  } finally {
    actionLoading.value = false
  }
}

async function processPayment(type) {
  actionLoading.value = true
  try {
    const finalPrice = parseFloat(booking.value.quoted_price || booking.value.precio_estimado || 0)
    const amount = type === 'deposit' ? finalPrice * 0.5 : finalPrice

    await api.post('/payments/create/', {
      booking: booking.value.id,
      amount: amount.toFixed(2),
      payment_type: type === 'deposit' ? 'deposit' : 'full',
      payment_method: 'card',
    })
    // Reload booking
    const { data } = await api.get(`/bookings/${booking.value.id}/`)
    booking.value = data
  } catch (e) {
    const msg = e.response?.data
    alert(typeof msg === 'object' ? Object.values(msg).flat().join(' ') : 'Error al procesar el pago.')
  } finally {
    actionLoading.value = false
  }
}

async function sendMessage() {
  if (!newMessage.value.trim()) return
  try {
    const { data } = await api.post('/messages/send/', {
      booking: booking.value.id,
      content: newMessage.value.trim(),
    })
    messages.value.push(data)
    newMessage.value = ''
    await nextTick()
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  } catch (e) {
    console.error(e)
  }
}

async function submitReview() {
  actionLoading.value = true
  try {
    await api.post(`/bookings/${booking.value.id}/review/`, {
      rating: reviewRating.value,
      comment: reviewComment.value,
    })
    const { data } = await api.get(`/bookings/${booking.value.id}/`)
    booking.value = data
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al enviar la reseña.')
  } finally {
    actionLoading.value = false
  }
}

onMounted(async () => {
  try {
    const [bookRes, msgRes] = await Promise.all([
      api.get(`/bookings/${route.params.id}/`),
      api.get(`/bookings/${route.params.id}/messages/`),
    ])
    booking.value = bookRes.data
    messages.value = msgRes.data.results || msgRes.data
    // Mark messages as read
    await api.post(`/bookings/${route.params.id}/messages/read/`)
    await nextTick()
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  padding-top: var(--space-4);
  min-height: 100vh;
  padding-bottom: var(--space-16);
}

.back-link {
  display: inline-flex; align-items: center; gap: var(--space-2);
  color: var(--color-text-muted); font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--color-primary); }

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: var(--space-8);
  align-items: start;
}

.detail-main { display: flex; flex-direction: column; gap: var(--space-6); }

/* Header */
.detail-header { padding: var(--space-6); border-radius: var(--radius-xl); }
.header-top { display: flex; justify-content: space-between; align-items: flex-start; }
.detail-header h1 { font-size: var(--font-size-2xl); margin-bottom: var(--space-2); }
.event-date { display: flex; align-items: center; gap: var(--space-2); color: var(--color-text-muted); font-size: var(--font-size-sm); }

/* Info Card */
.info-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.info-card h3 { font-size: var(--font-size-base); margin-bottom: var(--space-5); }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); }
.info-item { display: flex; flex-direction: column; gap: 2px; }
.info-label { font-size: var(--font-size-xs); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.info-description { margin-top: var(--space-4); }
.info-description p { margin-top: var(--space-2); color: var(--color-text-secondary); font-size: var(--font-size-sm); }

/* Action Card */
.action-card { padding: var(--space-6); border-radius: var(--radius-xl); border-color: var(--color-primary) !important; }
.action-card h3 { font-size: var(--font-size-base); margin-bottom: var(--space-4); }
.action-desc { color: var(--color-text-muted); font-size: var(--font-size-sm); margin-bottom: var(--space-4); }
.action-form { display: flex; flex-direction: column; gap: var(--space-4); }
.action-buttons { display: flex; gap: var(--space-3); }
.btn-danger { color: var(--color-accent) !important; border-color: var(--color-accent) !important; }
.btn-danger:hover { background: rgba(232,93,74,0.1) !important; }
.btn-full { width: 100%; }

.form-group { display: flex; flex-direction: column; gap: var(--space-2); }
.form-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-secondary); }
.form-input {
  background: var(--color-bg-elevated); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-sm); color: var(--color-text-primary);
  font-family: var(--font-body);
  transition: border-color var(--transition-fast);
}
.form-input:focus { outline: none; border-color: var(--color-primary); }

.price-final { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.price-big { font-size: var(--font-size-3xl); font-weight: 800; color: var(--color-primary); }

.talent-notes-box { background: var(--color-bg-elevated); border-radius: var(--radius-lg); padding: var(--space-4); margin-bottom: var(--space-4); font-size: var(--font-size-sm); }
.talent-notes-box p { color: var(--color-text-secondary); margin-top: var(--space-1); }

/* Review */
.review-form { display: flex; flex-direction: column; gap: var(--space-4); }
.star-rating { display: flex; gap: var(--space-1); }
.star-btn {
  background: none; border: none; font-size: 28px;
  color: var(--color-border); cursor: pointer;
  transition: color var(--transition-fast);
}
.star-btn.active, .star-btn:hover { color: #FFD700; }
.review-display .stars { font-size: 20px; color: #FFD700; margin-bottom: var(--space-2); }
.review-display p { color: var(--color-text-secondary); font-size: var(--font-size-sm); }

/* Chat */
.chat-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.chat-card h3 { display: flex; align-items: center; gap: var(--space-2); font-size: var(--font-size-base); margin-bottom: var(--space-4); }
.chat-messages { max-height: 400px; overflow-y: auto; margin-bottom: var(--space-4); display: flex; flex-direction: column; gap: var(--space-3); }
.chat-empty { text-align: center; padding: var(--space-8); color: var(--color-text-muted); font-size: var(--font-size-sm); }
.chat-msg { display: flex; }
.chat-msg.mine { justify-content: flex-end; }
.msg-bubble {
  max-width: 70%; padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg); background: var(--color-bg-elevated);
}
.chat-msg.mine .msg-bubble { background: rgba(193,216,47,0.15); }
.msg-sender { font-size: var(--font-size-xs); font-weight: 600; color: var(--color-primary); display: block; margin-bottom: 2px; }
.msg-bubble p { font-size: var(--font-size-sm); }
.msg-time { font-size: 10px; color: var(--color-text-muted); margin-top: 2px; display: block; }

.chat-input-row { display: flex; gap: var(--space-2); }
.chat-input-row .form-input { flex: 1; }
.btn-send { padding: var(--space-3); flex-shrink: 0; }

/* Sidebar */
.detail-sidebar { display: flex; flex-direction: column; gap: var(--space-4); position: sticky; top: 100px; }
.sidebar-card { padding: var(--space-5); border-radius: var(--radius-xl); }
.sidebar-card h4 { font-size: var(--font-size-sm); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: var(--space-4); }

.person-info { display: flex; align-items: center; gap: var(--space-3); }
.person-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: var(--color-primary-ultra-light); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: var(--font-size-lg);
}
.talent-level { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: 2px; }

.price-rows { display: flex; flex-direction: column; gap: var(--space-3); }
.price-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); }
.price-divider { height: 1px; background: var(--color-border); }
.text-primary { color: var(--color-primary); font-weight: 700; }
.text-success { color: var(--color-success); font-weight: 600; }
.text-warning { color: var(--color-warning); font-weight: 600; }

.payment-item { display: flex; justify-content: space-between; align-items: center; padding: var(--space-2) 0; border-bottom: 1px solid var(--color-border); }
.payment-item:last-child { border: none; }
.payment-type { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-left: var(--space-2); }

/* Status badges */
.status-badge { padding: 4px 12px; border-radius: 20px; font-size: var(--font-size-xs); font-weight: 600; white-space: nowrap; }
.status-info { background: rgba(100,149,237,0.15); color: #6495ed; }
.status-warning { background: var(--color-warning-light); color: var(--color-warning); }
.status-success { background: var(--color-success-light); color: var(--color-success); }
.status-error { background: rgba(232,93,74,0.15); color: var(--color-accent); }
.status-completed { background: rgba(193,216,47,0.15); color: var(--color-primary); }

/* Services Grid */
.services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-4); }
.service-item {
  background: var(--color-bg-elevated); border-radius: var(--radius-lg);
  padding: var(--space-4); border: 1px solid var(--color-border);
}
.service-header { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }
.service-icon { font-size: 20px; }
.service-details { display: flex; flex-direction: column; gap: var(--space-2); }
.service-detail-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); }
.info-card h3 { display: flex; align-items: center; gap: var(--space-2); }

.loading-state { padding: var(--space-8); }

@media (max-width: 900px) {
  .detail-layout { grid-template-columns: 1fr; }
  .detail-sidebar { position: static; }
  .info-grid { grid-template-columns: 1fr; }
}
</style>
