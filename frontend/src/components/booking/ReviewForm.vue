<template>
  <div class="review-form-wrap">
    <h3 class="rf-title">Tu reseña para <span class="rf-talent">{{ talentName }}</span></h3>
    <p class="rf-sub">Tu reseña libera el pago al talento y te da <strong>$50 de crédito Pulsar</strong> para tu próxima reserva.</p>

    <!-- Rating general -->
    <div class="rf-field">
      <label class="rf-label">Calificación general</label>
      <div class="rf-stars" @mouseleave="hoverRating = 0">
        <button
          v-for="i in 5" :key="i" type="button"
          class="rf-star" :class="{ active: (hoverRating || form.rating) >= i }"
          @mouseenter="hoverRating = i"
          @click="form.rating = i"
          aria-label="Estrella"
        >
          <svg width="32" height="32" viewBox="0 0 24 24" :fill="(hoverRating || form.rating) >= i ? '#FBBF24' : 'transparent'" stroke="#FBBF24" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </button>
      </div>
    </div>

    <!-- Dimension ratings -->
    <div class="rf-dimensions">
      <div v-for="dim in dimensions" :key="dim.key" class="rf-dim-row">
        <span class="rf-dim-label">{{ dim.label }}</span>
        <div class="rf-dim-stars">
          <button
            v-for="i in 5" :key="i" type="button"
            class="rf-mini-star"
            :class="{ active: form[dim.key] >= i }"
            @click="form[dim.key] = i"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" :fill="form[dim.key] >= i ? '#FBBF24' : 'transparent'" stroke="#FBBF24" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Comment -->
    <div class="rf-field">
      <label class="rf-label">
        Tu comentario
        <span class="rf-count" :class="{ low: form.comment.length < 30 }">{{ form.comment.length }} / 30 mín</span>
      </label>
      <textarea
        v-model="form.comment"
        class="rf-textarea"
        :class="{ 'rf-warn': commentViolations.length }"
        rows="4"
        placeholder="¿Cómo fue tu experiencia? Menciona la música, la energía, la profesionalidad..."
      ></textarea>
      <p v-if="commentViolationMsg" class="rf-disinter-warn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ commentViolationMsg }}
      </p>
    </div>

    <p v-if="error" class="rf-error">{{ error }}</p>

    <div class="rf-actions">
      <button class="btn btn-ghost btn-sm" @click="$emit('cancel')">Cancelar</button>
      <button class="btn btn-primary" :disabled="!canSubmit || submitting" @click="submit">
        <span v-if="submitting">Enviando...</span>
        <span v-else>Enviar reseña · gana $50 crédito</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import api from '@/api'
import { scan as antiScan, violationsMessage } from '@/utils/antiDisinter'

const props = defineProps({
  bookingId: { type: [Number, String], required: true },
  talentName: { type: String, default: 'el talento' },
})
const emit = defineEmits(['submitted', 'cancel'])

const hoverRating = ref(0)
const submitting = ref(false)
const error = ref('')

const dimensions = [
  { key: 'rating_punctuality', label: 'Puntualidad' },
  { key: 'rating_music_selection', label: 'Selección musical' },
  { key: 'rating_crowd_reading', label: 'Lectura del público' },
  { key: 'rating_technique', label: 'Técnica' },
  { key: 'rating_communication', label: 'Comunicación pre-evento' },
]

const form = reactive({
  rating: 0,
  rating_punctuality: 0,
  rating_music_selection: 0,
  rating_crowd_reading: 0,
  rating_technique: 0,
  rating_communication: 0,
  comment: '',
})

const commentViolations = ref([])
watch(() => form.comment, (val) => {
  commentViolations.value = antiScan(val)
})
const commentViolationMsg = computed(() => violationsMessage(commentViolations.value))

const canSubmit = computed(() => {
  return form.rating > 0
    && form.comment.trim().length >= 30
    && commentViolations.value.length === 0
})

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form }
    // No mandar dimensiones que el usuario no marcó (mantener null)
    dimensions.forEach(d => {
      if (!payload[d.key]) delete payload[d.key]
    })
    const { data } = await api.post(`/bookings/${props.bookingId}/review/`, payload)
    emit('submitted', data)
  } catch (err) {
    error.value = err.response?.data?.detail
      || err.response?.data?.non_field_errors?.[0]
      || 'No se pudo enviar la reseña. Intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.review-form-wrap {
  padding: var(--space-6);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}
.rf-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: var(--space-2);
  color: var(--color-text-primary);
}
.rf-talent { color: var(--color-primary); }
.rf-sub {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
}
.rf-sub strong { color: var(--color-primary); }

.rf-field { margin-bottom: var(--space-5); }
.rf-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}
.rf-count { font-size: 0.72rem; color: var(--color-text-muted); font-weight: 400; }
.rf-count.low { color: #E85D4A; }

.rf-stars {
  display: flex;
  gap: 4px;
  justify-content: center;
}
.rf-star {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  transition: transform var(--transition-fast);
}
.rf-star:hover { transform: scale(1.1); }

.rf-dimensions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-5);
}
.rf-dim-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
}
.rf-dim-label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.rf-dim-stars {
  display: flex;
  gap: 2px;
}
.rf-mini-star {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 2px;
  display: flex;
}

.rf-textarea {
  width: 100%;
  padding: 12px 14px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.92rem;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast);
}
.rf-textarea:focus { border-color: var(--color-primary); }
.rf-textarea.rf-warn { border-color: #E85D4A; }

.rf-disinter-warn {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 8px 12px;
  background: rgba(232, 93, 74, 0.08);
  border: 1px solid rgba(232, 93, 74, 0.3);
  border-radius: 8px;
  color: #E85D4A;
  font-size: 0.78rem;
}

.rf-error {
  padding: 10px 14px;
  background: rgba(232, 93, 74, 0.1);
  color: #E85D4A;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  margin-bottom: var(--space-3);
}

.rf-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}
</style>
