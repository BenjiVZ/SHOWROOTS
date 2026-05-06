<template>
  <div v-if="talent" class="profile-page">
    <!-- Cover -->
    <div class="profile-cover">
      <img :src="talent.cover_photo || placeholderCover" :alt="talent.stage_name" />
      <div class="cover-overlay"></div>
    </div>

    <div class="container profile-layout">
      <!-- Sidebar -->
      <aside class="profile-sidebar animate-fade-in-up">
        <div class="profile-card glass">
          <div class="avatar-wrap">
            <img :src="talent.profile_photo || placeholderAvatar" :alt="talent.stage_name" class="avatar" />
            <span v-if="talent.is_available" class="status-dot" title="Disponible"></span>
          </div>
          <h1>{{ talent.stage_name }}</h1>
          <p class="talent-type-label">
            <span class="badge" :class="typeClass">{{ typeLabel }}</span>
            <span v-if="talent.talent_level" class="badge" :class="talent.talent_level === 'premium' ? 'badge-accent' : ''">{{ talent.talent_level === 'premium' ? '⭐ Premium' : 'Standard' }}</span>
          </p>
          <div v-if="talent.total_reviews > 0" class="profile-rating">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <strong>{{ Number(talent.rating_avg).toFixed(1) }}</strong>
            <span>({{ talent.total_reviews }} reseñas)</span>
          </div>

          <div class="profile-details">
            <div v-if="talent.city" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ talent.city }}
            </div>
            <div v-if="talent.years_experience" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {{ talent.years_experience }} años de experiencia
            </div>
            <div v-if="talent.hourly_rate" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
              <strong>${{ talent.hourly_rate }}</strong>/hora
            </div>
            <div v-if="talent.price_min" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
              Desde <strong>${{ talent.price_min }}</strong>{{ talent.price_max ? ` — $${talent.price_max}` : '' }}
            </div>
            <div v-if="talent.total_bookings" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              {{ talent.total_bookings }} eventos realizados
            </div>
          </div>

          <router-link :to="`/talent/${talent.id}/book`" class="btn btn-cta btn-lg" style="width:100%;text-align:center;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Reservar Ahora
          </router-link>
        </div>
      </aside>

      <!-- Main -->
      <main class="profile-main animate-fade-in-up" style="animation-delay: 0.1s">
        <!-- Bio -->
        <section v-if="talent.bio" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>
            Sobre mí
          </h2>
          <p>{{ talent.bio }}</p>
        </section>

        <!-- Genres -->
        <section v-if="talent.genres?.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            Géneros
          </h2>
          <div class="genres-list">
            <span v-for="g in talent.genres" :key="g.id" class="badge">{{ g.name }}</span>
          </div>
        </section>

        <!-- Equipment -->
        <section v-if="talent.equipment" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>
            Equipo
          </h2>
          <p>{{ talent.equipment }}</p>
        </section>

        <!-- Reviews -->
        <section class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            Reseñas
          </h2>
          <div v-if="reviews.length" class="reviews-list">
            <div v-for="review in reviews" :key="review.id" class="review-item glass">
              <div class="review-header">
                <strong>{{ review.client_name || 'Cliente' }}</strong>
                <div class="review-stars">
                  <svg v-for="i in review.rating" :key="i" width="14" height="14" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                </div>
              </div>
              <p>{{ review.comment }}</p>
            </div>
          </div>
          <p v-else class="muted-text">Sin reseñas aún.</p>
        </section>
      </main>
    </div>

    <!-- Quote Modal -->
    <Teleport to="body">
      <div v-if="showQuoteModal" class="modal-backdrop" @click.self="showQuoteModal = false">
        <div class="modal glass animate-fade-in-up">
          <div class="modal-header">
            <h2>Solicitar Cotización</h2>
            <button class="btn btn-ghost btn-icon" @click="showQuoteModal = false" aria-label="Cerrar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <form @submit.prevent="submitQuote" class="modal-body">
            <div class="field">
              <label class="label" for="event_type">Tipo de evento</label>
              <select id="event_type" v-model="quoteForm.event_type" class="input-field" required>
                <option value="">Seleccionar...</option>
                <option value="wedding">Boda</option>
                <option value="birthday">Cumpleaños</option>
                <option value="corporate">Corporativo</option>
                <option value="club">Club / Discoteca</option>
                <option value="festival">Festival</option>
                <option value="private">Fiesta Privada</option>
                <option value="other">Otro</option>
              </select>
            </div>
            <div class="field-row">
              <div class="field">
                <label class="label" for="event_date">Fecha</label>
                <input id="event_date" v-model="quoteForm.event_date" type="date" class="input-field" required />
              </div>
              <div class="field">
                <label class="label" for="event_time">Hora</label>
                <input id="event_time" v-model="quoteForm.event_time" type="time" class="input-field" />
              </div>
            </div>
            <div class="field">
              <label class="label" for="event_location">Ubicación</label>
              <input id="event_location" v-model="quoteForm.event_location" type="text" class="input-field" placeholder="Ciudad, Venue..." required />
            </div>
            <div class="field">
              <label class="label" for="client_notes">Detalles adicionales</label>
              <textarea id="client_notes" v-model="quoteForm.client_notes" class="input-field" rows="3" placeholder="Describe tu evento..."></textarea>
            </div>
            <p v-if="quoteError" class="error-msg">{{ quoteError }}</p>
            <p v-if="quoteSuccess" class="success-msg">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Cotización enviada con éxito
            </p>
            <button type="submit" class="btn btn-cta btn-lg" style="width:100%;" :disabled="quoteSending">
              {{ quoteSending ? 'Enviando...' : 'Enviar Cotización' }}
            </button>
          </form>
        </div>
      </div>
    </Teleport>
  </div>

  <!-- Loading state -->
  <div v-else class="profile-page loading-page">
    <div class="container">
      <div class="skeleton" style="height: 300px; border-radius: var(--radius-xl); margin: var(--space-24) 0 var(--space-8);"></div>
      <div class="skeleton" style="height: 400px; border-radius: var(--radius-xl);"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const talent = ref(null)
const reviews = ref([])
const showQuoteModal = ref(false)
const quoteSending = ref(false)
const quoteError = ref('')
const quoteSuccess = ref(false)

const quoteForm = ref({
  event_type: '',
  event_date: '',
  event_time: '',
  event_location: '',
  client_notes: '',
})

const placeholderCover = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400"%3E%3Cdefs%3E%3ClinearGradient id="g" x1="0" y1="0" x2="1" y2="1"%3E%3Cstop offset="0%25" stop-color="%23C1D82F" stop-opacity="0.15"/%3E%3Cstop offset="100%25" stop-color="%23E85D4A" stop-opacity="0.08"/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill="%230A0A0A" width="1200" height="400"/%3E%3Crect fill="url(%23g)" width="1200" height="400"/%3E%3C/svg%3E'

const placeholderAvatar = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"%3E%3Crect fill="%230A0A0A" width="120" height="120" rx="60"/%3E%3Ccircle cx="60" cy="45" r="20" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3Cpath d="M30 95a30 30 0 0160 0" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3C/svg%3E'

const typeLabel = computed(() => {
  const map = { dj: 'DJ', musician: 'Músico', band: 'Banda' }
  return map[talent.value?.talent_type] || ''
})

const typeClass = computed(() => {
  const map = { dj: '', musician: 'badge-cyan', band: 'badge-accent' }
  return map[talent.value?.talent_type] || ''
})

async function submitQuote() {
  quoteSending.value = true
  quoteError.value = ''
  quoteSuccess.value = false
  try {
    await api.post('/bookings/create/', {
      talent: talent.value.id,
      ...quoteForm.value,
    })
    quoteSuccess.value = true
    setTimeout(() => { showQuoteModal.value = false; quoteSuccess.value = false }, 2000)
  } catch (err) {
    quoteError.value = err.response?.data?.detail || 'Error al enviar la cotización. Asegúrate de estar autenticado.'
  } finally {
    quoteSending.value = false
  }
}

onMounted(async () => {
  try {
    const [talentRes, reviewsRes] = await Promise.all([
      api.get(`/talents/${route.params.id}/`),
      api.get(`/talents/${route.params.id}/reviews/`),
    ])
    talent.value = talentRes.data
    reviews.value = reviewsRes.data.results || reviewsRes.data
  } catch (err) {
    console.error('Profile load error:', err)
  }
})
</script>

<style scoped>
.profile-page { padding-bottom: var(--space-16); margin-top: calc(-80px - var(--space-4)); }

.profile-cover {
  position: relative;
  height: 340px;
  overflow: hidden;
}

.profile-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      to bottom,
      transparent 30%,
      rgba(0, 0, 0, 0.15) 50%,
      rgba(0, 0, 0, 0.3) 65%,
      var(--color-bg-primary) 100%
    );
}

.profile-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: var(--space-8);
  margin-top: -80px;
  position: relative;
  z-index: 1;
}

.profile-sidebar { position: sticky; top: 100px; align-self: flex-start; }

.profile-card {
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  text-align: center;
}

.avatar-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto var(--space-4);
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-full);
  object-fit: cover;
  border: 3px solid var(--color-primary);
}

.status-dot {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: var(--color-accent);
  border-radius: 50%;
  border: 3px solid var(--color-bg-glass);
}

.profile-card h1 {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--space-2);
}

.talent-type-label { margin-bottom: var(--space-3); }

.profile-rating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  font-size: var(--font-size-sm);
}

.profile-rating span { color: var(--color-text-muted); }

.profile-details {
  text-align: left;
  padding: var(--space-4) 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-5);
}

.detail-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail-row svg { color: var(--color-primary-light); flex-shrink: 0; }
.detail-row strong { color: var(--color-accent); }

/* Main content */
.profile-main {
  padding-top: var(--space-10);
}

.content-section {
  margin-bottom: var(--space-10);
}

.content-section h2 {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.content-section p {
  color: var(--color-text-secondary);
  line-height: 1.8;
  font-weight: 300;
}

.genres-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.muted-text { color: var(--color-text-muted); font-size: var(--font-size-sm); }

/* Reviews */
.reviews-list { display: flex; flex-direction: column; gap: var(--space-4); }

.review-item {
  padding: var(--space-5);
  border-radius: var(--radius-lg);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.review-stars { display: flex; gap: 2px; }
.review-item p { color: var(--color-text-muted); font-size: var(--font-size-sm); line-height: 1.6; }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
  padding: var(--space-4);
}

.modal {
  width: 100%;
  max-width: 520px;
  border-radius: var(--radius-2xl);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 { font-size: var(--font-size-xl); }

.modal-body {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

textarea.input-field {
  resize: vertical;
  min-height: 80px;
}

.error-msg {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  background: var(--color-error-light);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
}

.success-msg {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-success);
  font-size: var(--font-size-sm);
  background: var(--color-success-light);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
}

.loading-page { padding-top: var(--space-8); }

@media (max-width: 768px) {
  .profile-layout { grid-template-columns: 1fr; }
  .profile-sidebar { position: static; }
  .profile-cover { height: 200px; }
  .field-row { grid-template-columns: 1fr; }
}
</style>
