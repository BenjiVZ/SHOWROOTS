<template>
  <div class="open-gig-page">
    <div class="container">
      <router-link to="/search" class="back-link">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al buscador
      </router-link>

      <div class="hero-banner">
        <div class="hero-icon">
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
        </div>
        <div>
          <h1>Publica tu solicitud</h1>
          <p class="hero-sub">
            Cuéntanos qué necesitas y recibe ofertas de DJs y Aliados de producción.
            Puedes pedir solo un DJ, solo un pack de sonido, un combo completo… lo que quieras.
          </p>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="form-card">
        <h2 class="section-title">¿Qué necesitas?</h2>
        <p class="section-hint">
          Elige uno o varios. Recibirás ofertas separadas por cada categoría — puedes aceptar
          un DJ + un pack de luces + uno de sonido, por ejemplo.
        </p>
        <div class="form-group">
          <div class="need-tiles">
            <button v-for="n in needs" :key="n.value" type="button"
              class="need-tile" :class="{ selected: form.requested_items.includes(n.value) }"
              @click="toggleNeed(n.value)">
              <span class="need-check">
                <svg v-if="form.requested_items.includes(n.value)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              <span class="need-icon" v-html="n.icon"></span>
              <span class="need-label">{{ n.label }}</span>
              <span class="need-desc">{{ n.desc }}</span>
            </button>
          </div>
          <p v-if="needsError" class="need-error">Elige al menos una opción.</p>
        </div>

        <h2 class="section-title" style="margin-top:24px">Detalles del evento</h2>

        <div class="form-group">
          <label class="form-label">Tipo de evento <span class="req">*</span></label>
          <div class="event-tiles">
            <button v-for="t in eventTypeTiles" :key="t.value" type="button"
              class="event-tile" :class="{ selected: form.event_type === t.value }"
              @click="form.event_type = t.value">
              <span class="event-tile-icon" v-html="t.icon"></span>
              <span>{{ t.label }}</span>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Nombre del evento <span class="optional">(opcional)</span></label>
          <input v-model="form.event_name" type="text" class="form-input" placeholder="Ej: Boda de María y Pedro">
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Fecha <span class="req">*</span></label>
            <input v-model="form.event_date" type="date" class="form-input" :min="minDate" required>
          </div>
          <div class="form-group">
            <label class="form-label">Hora inicio <span class="req">*</span></label>
            <input v-model="form.event_time_start" type="time" class="form-input" required @change="syncEnd">
          </div>
          <div class="form-group">
            <label class="form-label">Duración <span class="req">*</span></label>
            <select v-model.number="form.event_duration_hours" class="form-input" @change="syncEnd" required>
              <option v-for="h in [2,3,4,5,6,8]" :key="h" :value="h">{{ h }} horas</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group" style="flex:2">
            <label class="form-label">Ubicación <span class="req">*</span></label>
            <input v-model="form.event_location" type="text" class="form-input" placeholder="Dirección del evento" required>
          </div>
          <div class="form-group" style="flex:1">
            <label class="form-label">Ciudad <span class="req">*</span></label>
            <input v-model="form.event_city" type="text" class="form-input" placeholder="Panamá" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Invitados aprox.</label>
            <input v-model.number="form.guest_count" type="number" class="form-input" placeholder="150" min="1">
          </div>
          <div class="form-group">
            <label class="form-label">Espacio</label>
            <div class="toggle-row">
              <button type="button" class="toggle-btn" :class="{ active: form.event_indoor }" @click="form.event_indoor = true">Interior</button>
              <button type="button" class="toggle-btn" :class="{ active: !form.event_indoor }" @click="form.event_indoor = false">Exterior</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Presupuesto <span class="optional">(USD, opcional)</span></label>
            <input v-model.number="form.budget" type="number" class="form-input" placeholder="500" min="0" step="10">
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Género / ambiente</label>
          <div class="chip-row">
            <button type="button" v-for="g in genres" :key="g"
              class="chip" :class="{ active: form.genre_preference === g }"
              @click="form.genre_preference = g">{{ g }}</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Descripción / requerimientos</label>
          <textarea v-model="form.description" class="form-input" rows="4"
            placeholder="Detalles del ambiente que buscas, canciones especiales, requerimientos técnicos…"></textarea>
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <div class="cta-row">
          <button type="button" class="btn btn-ghost" @click="$router.back()">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="submitting || !isValid">
            <span v-if="submitting">Publicando…</span>
            <span v-else>Publicar solicitud</span>
          </button>
        </div>

        <p class="fine-print">
          Si pides DJ, los Premium reciben la notificación al instante, los Pro a los 3 min y los Standard a los 6.
          Los Aliados aprobados reciben la notificación al instante. La solicitud expira a las 24 horas.
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const form = reactive({
  requested_items: ['dj'],   // por defecto solo DJ (comportamiento previo)
  event_type: '',
  event_name: '',
  event_date: '',
  event_time_start: '',
  event_time_end: '',
  event_duration_hours: 4,
  event_location: '',
  event_city: 'Panamá',
  event_indoor: true,
  guest_count: null,
  budget: null,
  description: '',
  genre_preference: '',
  additional_services: [],
})

const submitting = ref(false)
const error = ref('')
const needsError = ref(false)

const needs = [
  { value: 'dj',      label: 'DJ',        desc: 'Un DJ para el evento', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>' },
  { value: 'sound',   label: 'Sonido',    desc: 'Parlantes, mixer, cableado', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>' },
  { value: 'lights',  label: 'Luces',     desc: 'Iluminación, láser, moving heads', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' },
  { value: 'booth',   label: 'DJ Booth',  desc: 'Cabina profesional para el DJ', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>' },
  { value: 'screens', label: 'Pantallas', desc: 'LED, proyectores, video', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>' },
  { value: 'other',   label: 'Otro',      desc: 'Micrófonos, FX, otras cosas', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' },
]

function toggleNeed(v) {
  const i = form.requested_items.indexOf(v)
  if (i === -1) form.requested_items.push(v)
  else form.requested_items.splice(i, 1)
  needsError.value = false
}

const minDate = new Date(Date.now() + 86400000).toISOString().split('T')[0]

const genres = ['House', 'Open Format', 'Reggaetón', 'Lounge', 'Afro House', 'Comercial', 'Latin', 'Tech House', 'Otro']

const eventTypeTiles = [
  { value: 'wedding',    label: 'Boda',        icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="15" r="5"/><circle cx="16" cy="15" r="5"/><path d="M7 9l2-5h6l2 5"/></svg>' },
  { value: 'corporate',  label: 'Corporativo', icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20"/><line x1="8" y1="6" x2="8" y2="6.01"/><line x1="12" y1="6" x2="12" y2="6.01"/><line x1="16" y1="6" x2="16" y2="6.01"/><line x1="8" y1="10" x2="8" y2="10.01"/><line x1="12" y1="10" x2="12" y2="10.01"/><line x1="16" y1="10" x2="16" y2="10.01"/></svg>' },
  { value: 'birthday',   label: 'Cumpleaños',  icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-8a2 2 0 00-2-2H6a2 2 0 00-2 2v8"/><path d="M4 16s1.5-2 4-2 3.5 2 4 2 1.5-2 4-2 4 2 4 2"/><line x1="2" y1="21" x2="22" y2="21"/><line x1="12" y1="4" x2="12" y2="11"/></svg>' },
  { value: 'private',    label: 'Privado',     icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 22h8"/><path d="M12 11v11"/><path d="M19 3l-7 8-7-8"/><path d="M5 3h14"/></svg>' },
  { value: 'festival',   label: 'Festival',    icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20h20"/><path d="M12 3L4 20"/><path d="M12 3l8 17"/></svg>' },
  { value: 'club',       label: 'Club',        icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/></svg>' },
  { value: 'graduation', label: 'Graduación',  icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10L12 5 2 10l10 5 10-5z"/><path d="M6 12v5c0 1.1 2.7 3 6 3s6-1.9 6-3v-5"/></svg>' },
  { value: 'other',      label: 'Otro',        icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' },
]

function syncEnd() {
  if (!form.event_time_start || !form.event_duration_hours) return
  const [h, m] = form.event_time_start.split(':').map(Number)
  const totalMin = h * 60 + m + form.event_duration_hours * 60
  const eh = Math.floor(totalMin / 60) % 24
  const em = totalMin % 60
  form.event_time_end = `${String(eh).padStart(2, '0')}:${String(em).padStart(2, '0')}`
}

const isValid = computed(() =>
  form.requested_items.length > 0 &&
  form.event_type && form.event_date && form.event_time_start &&
  form.event_duration_hours && form.event_location && form.event_city
)

async function handleSubmit() {
  if (!form.requested_items.length) {
    needsError.value = true
    error.value = 'Elige al menos qué necesitas (DJ, sonido, luces, etc.).'
    return
  }
  if (!isValid.value) {
    error.value = 'Completa los campos obligatorios.'
    return
  }
  error.value = ''
  submitting.value = true
  syncEnd()
  try {
    const payload = { ...form }
    // limpiar nulls
    if (!payload.budget) delete payload.budget
    if (!payload.guest_count) delete payload.guest_count
    const { data } = await api.post('/open-gigs/', payload)
    router.push({ name: 'open-gig-detail', params: { id: data.id } })
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.response?.data?.error || 'No se pudo publicar la solicitud.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.open-gig-page {
  min-height: 100vh;
  background: var(--color-bg-primary);
  padding: var(--space-6) 0 var(--space-16);
  color: var(--color-text-primary);
}
.container { max-width: 900px; margin: 0 auto; padding: 0 var(--space-5); }

.back-link {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--color-primary); text-decoration: none; font-weight: 600;
  margin-bottom: var(--space-5); font-size: var(--font-size-sm);
}
.back-link:hover { text-decoration: underline; }

/* ── Hero: usa los DOS colores de marca (primary → accent) ── */
.hero-banner {
  position: relative; overflow: hidden;
  display: flex; gap: var(--space-5); align-items: center;
  background:
    linear-gradient(135deg, var(--color-primary-ultra-light), transparent 60%),
    linear-gradient(300deg, var(--color-accent-light), transparent 55%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}
.hero-icon {
  flex-shrink: 0; width: 72px; height: 72px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: var(--color-bg-primary);
  box-shadow: 0 8px 24px var(--color-accent-light);
}
.hero-banner h1 { margin: 0; font-size: 1.7rem; color: var(--color-text-primary); }
.hero-sub { margin: 6px 0 0; color: var(--color-text-secondary); font-size: 0.95rem; line-height: 1.55; }
.hero-sub strong { color: var(--color-primary); }

.form-card {
  background: var(--color-bg-card);
  backdrop-filter: blur(12px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-8);
  box-shadow: 0 8px 30px rgba(0,0,0,0.18);
}

/* Título de sección con barra de acento (segundo color con rol claro) */
.section-title {
  position: relative; padding-left: 14px;
  font-size: 1.15rem; margin: 0 0 8px; color: var(--color-text-primary);
}
.section-title::before {
  content: ''; position: absolute; left: 0; top: 3px; bottom: 3px;
  width: 4px; border-radius: var(--radius-full);
  background: linear-gradient(180deg, var(--color-primary), var(--color-accent));
}
.section-hint { margin: 0 0 var(--space-4); color: var(--color-text-muted); font-size: 0.88rem; line-height: 1.5; }

.need-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
}
.need-tile {
  position: relative;
  display: flex; flex-direction: column; align-items: flex-start; gap: 6px;
  background: var(--color-bg-elevated); border: 1.5px solid var(--color-border);
  border-radius: var(--radius-lg); padding: 16px 14px 14px;
  color: var(--color-text-secondary); cursor: pointer; text-align: left;
  transition: all var(--transition-fast, 0.15s);
}
.need-tile:hover { border-color: var(--color-border-hover); transform: translateY(-2px); }
.need-tile.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-ultra-light);
  color: var(--color-text-primary);
  box-shadow: 0 0 0 3px var(--color-primary-ultra-light);
}
.need-check {
  position: absolute; top: 10px; right: 10px;
  width: 20px; height: 20px; border-radius: 6px;
  border: 1.5px solid var(--color-border);
  display: flex; align-items: center; justify-content: center;
  color: var(--color-bg-primary); background: transparent;
  transition: all var(--transition-fast, 0.15s);
}
.need-tile.selected .need-check { background: var(--color-primary); border-color: var(--color-primary); }
.need-icon { color: var(--color-primary); }
.need-label { font-weight: 700; font-size: 0.98rem; }
.need-desc { color: var(--color-text-muted); font-size: 0.8rem; line-height: 1.35; }
.need-error { color: var(--color-accent); font-size: 0.85rem; margin: 8px 0 0; font-weight: 500; }

.form-group { margin-bottom: var(--space-5); }
.form-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-4);
  margin-bottom: 6px;
}
.form-label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--color-text-secondary); margin-bottom: 6px; }
.form-label :deep(*) { pointer-events: none; }
.optional { color: var(--color-text-muted); font-weight: 400; font-size: 0.8rem; }
.req { color: var(--color-accent); font-weight: 700; }
.form-input {
  width: 100%; box-sizing: border-box;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  padding: 11px 13px; border-radius: var(--radius-md);
  font-size: 0.92rem; font-family: inherit;
  transition: border-color var(--transition-fast, 0.15s), box-shadow var(--transition-fast, 0.15s);
}
.form-input:focus {
  outline: none; border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-ultra-light);
}
textarea.form-input { resize: vertical; }

.event-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: var(--space-3);
}
.event-tile {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  background: var(--color-bg-elevated); border: 1.5px solid var(--color-border);
  border-radius: var(--radius-lg); padding: 16px 8px;
  color: var(--color-text-secondary); font-size: 0.85rem; cursor: pointer;
  transition: all var(--transition-fast, 0.15s);
}
.event-tile:hover { border-color: var(--color-border-hover); transform: translateY(-2px); }
.event-tile.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-ultra-light);
  color: var(--color-text-primary);
}
.event-tile-icon { color: var(--color-primary); }

.toggle-row { display: flex; gap: 8px; }
.toggle-btn {
  flex: 1; background: var(--color-bg-elevated); border: 1px solid var(--color-border);
  color: var(--color-text-secondary); padding: 11px; border-radius: var(--radius-md); cursor: pointer;
  font-family: inherit; transition: all var(--transition-fast, 0.15s);
}
.toggle-btn.active { border-color: var(--color-primary); background: var(--color-primary-ultra-light); color: var(--color-text-primary); }

.chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  background: var(--color-bg-elevated); border: 1px solid var(--color-border); color: var(--color-text-secondary);
  padding: 8px 15px; border-radius: var(--radius-full); font-size: 0.85rem; cursor: pointer;
  font-family: inherit; transition: all var(--transition-fast, 0.15s);
}
.chip:hover { border-color: var(--color-border-hover); }
.chip.active { border-color: var(--color-primary); background: var(--color-primary-ultra-light); color: var(--color-primary); font-weight: 600; }

.error-msg {
  background: var(--color-accent-light); border: 1px solid var(--color-accent);
  color: var(--color-accent); padding: 11px 15px; border-radius: var(--radius-md); font-size: 0.9rem;
  margin-bottom: var(--space-4);
}

.cta-row {
  display: flex; justify-content: flex-end; gap: 10px;
  margin-top: var(--space-6); padding-top: var(--space-5); border-top: 1px solid var(--color-border);
}
.btn {
  padding: 12px 24px; border-radius: var(--radius-full); font-weight: 700; cursor: pointer;
  border: 1px solid transparent; font-size: 0.92rem; font-family: inherit;
  transition: all var(--transition-fast, 0.15s);
}
.btn-primary { background: var(--color-primary); color: var(--color-bg-primary); }
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); transform: translateY(-1px); box-shadow: 0 6px 18px var(--color-primary-ultra-light); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost { background: transparent; border-color: var(--color-border); color: var(--color-text-secondary); }
.btn-ghost:hover { border-color: var(--color-border-hover); color: var(--color-text-primary); }

.fine-print {
  margin-top: var(--space-4);
  color: var(--color-text-muted); font-size: 0.78rem; text-align: center; line-height: 1.5;
}

@media (max-width: 600px) {
  .hero-banner { flex-direction: column; text-align: center; }
  .form-card { padding: var(--space-5); }
}
</style>
