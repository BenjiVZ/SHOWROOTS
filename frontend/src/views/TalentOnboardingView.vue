<template>
  <div class="onboarding-view">
    <!-- Save & Exit -->
    <button v-if="currentStep > 0 && currentStep < 10" class="save-exit-btn" @click="saveAndExit">
      Guardar y salir
    </button>

    <!-- Progress bar -->
    <div v-if="currentStep > 0 && currentStep < 10" class="progress-bar">
      <div class="progress-fill" :style="{ width: ((currentStep) / 10 * 100) + '%' }"></div>
    </div>

    <div class="onboarding-container">
      <!-- LEFT PANEL (hidden on mobile for steps > 0) -->
      <div class="onboarding-left" :class="{ 'hide-on-mobile': currentStep > 0 }">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="left-content">
          <transition name="fade-text" mode="out-in">
            <div :key="currentStep">
              <!-- Step 0: Welcome -->
              <template v-if="currentStep === 0">
                <span class="step-badge">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px; margin-right:4px"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                  Registro de Talentos
                </span>
                <h1>Únete a <span class="text-accent">Pulsar</span> y lleva tu talento a más escenarios</h1>
                <p class="step-subtitle">Forma parte de una red curada de DJs, músicos y artistas conectados con eventos, marcas y experiencias.</p>
              </template>
              <!-- Step 1 -->
              <template v-else-if="currentStep === 1">
                <h1>Primero, cuéntanos qué tipo de perfil estás creando.</h1>
              </template>
              <!-- Step 2 -->
              <template v-else-if="currentStep === 2">
                <h1>¿Cómo deberían llamarte?</h1>
              </template>
              <!-- Step 3 -->
              <template v-else-if="currentStep === 3">
                <h1>¿Qué tipo de música tocas?</h1>
                <p class="step-subtitle">Puedes agregar más después.</p>
              </template>
              <!-- Step 4 -->
              <template v-else-if="currentStep === 4">
                <h1>Ahora, agreguemos tu foto de perfil.</h1>
                <p class="step-subtitle">Muestra tu mejor lado.</p>
              </template>
              <!-- Step 5 -->
              <template v-else-if="currentStep === 5">
                <h1>¿Dónde te encuentras?</h1>
                <p class="step-subtitle">Recibirás oportunidades cerca de tu ubicación.</p>
              </template>
              <!-- Step 6 -->
              <template v-else-if="currentStep === 6">
                <h1>¿Cuánta experiencia tienes?</h1>
              </template>
              <!-- Step 7 -->
              <template v-else-if="currentStep === 7">
                <h1>Definamos tu tarifa.</h1>
              </template>
              <!-- Step 8 -->
              <template v-else-if="currentStep === 8">
                <h1>Ahora, creemos tu biografía.</h1>
                <p class="step-subtitle">Menciona experiencias previas y en qué tipo de eventos sueles tocar.</p>
              </template>
              <!-- Step 9 -->
              <template v-else-if="currentStep === 9">
                <h1>Una última pregunta.</h1>
              </template>
              <!-- Step 10: Welcome -->
              <template v-else-if="currentStep === 10">
                <h1>¡Bienvenido, {{ form.first_name || 'artista' }}!</h1>
                <p class="step-subtitle">Los artistas son lo que hace especial a Pulsar, y estamos emocionados de tenerte a bordo.</p>
                <p class="founder-quote">— Equipo Pulsar</p>
              </template>
            </div>
          </transition>

          <div v-if="currentStep > 0 && currentStep < 10" class="step-indicator">
            <span class="step-num">{{ currentStep }}</span> / 9
          </div>

          <div v-if="currentStep === 0" class="benefits-grid">
            <div class="benefit-card">
              <div class="benefit-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg></div>
              <strong>Más oportunidades</strong><span>Bodas, corporativos, fiestas.</span>
            </div>
            <div class="benefit-card">
              <div class="benefit-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg></div>
              <strong>Tú decides</strong><span>Acepta los gigs que van contigo.</span>
            </div>
            <div class="benefit-card">
              <div class="benefit-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>
              <strong>Perfil profesional</strong><span>Música, fotos, géneros y tarifas.</span>
            </div>
            <div class="benefit-card">
              <div class="benefit-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg></div>
              <strong>Crece</strong><span>Showcases, workshops y networking.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT PANEL -->
      <div class="onboarding-right">
        <!-- Mobile step title (shown only on mobile) -->
        <div v-if="currentStep > 0 && currentStep <= 10" class="mobile-step-header">
          <span v-if="currentStep < 10" class="mobile-step-num">Paso {{ currentStep }} de 9</span>
          <h2>{{ mobileStepTitle }}</h2>
          <p v-if="mobileStepSubtitle" class="step-subtitle">{{ mobileStepSubtitle }}</p>
        </div>

        <transition name="slide-step" mode="out-in">
          <div :key="currentStep" class="step-content">

            <!-- STEP 0: Welcome CTA -->
            <div v-if="currentStep === 0" class="step-welcome">
              <button class="btn-cta-onboard" @click="currentStep = 1">Crear mi perfil artístico</button>
              <button class="btn-ghost-onboard" @click="currentStep = 1">Conocer cómo funciona</button>
            </div>

            <!-- STEP 1: Profile Type -->
            <div v-else-if="currentStep === 1" class="step-form">
              <p class="form-label">¿Qué te describe mejor?</p>
              <div class="option-list">
                <button v-for="t in talentTypes" :key="t.value" class="option-card" :class="{ selected: form.talent_type === t.value }" @click="form.talent_type = t.value">
                  <span>{{ t.label }}</span>
                  <span class="option-icon">
                    <!-- Headphones -->
                    <svg v-if="t.icon === 'headphones'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0118 0v6"/><path d="M21 19a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3a2 2 0 012-2h3zM3 19a2 2 0 002 2h1a2 2 0 002-2v-3a2 2 0 00-2-2H3z"/></svg>
                    <!-- Drum -->
                    <svg v-else-if="t.icon === 'drum'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="10" rx="9" ry="5"/><path d="M3 10v4c0 2.76 4.03 5 9 5s9-2.24 9-5v-4"/><line x1="3" y1="10" x2="8" y2="19"/><line x1="21" y1="10" x2="16" y2="19"/></svg>
                    <!-- Music -->
                    <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                  </span>
                </button>
              </div>
            </div>

            <!-- STEP 2: Name -->
            <div v-else-if="currentStep === 2" class="step-form">
              <div class="form-group">
                <label>Tu nombre completo</label>
                <input v-model="form.first_name" type="text" class="onboard-input" placeholder="Ej: Carlos Mejía" />
              </div>
              <div class="form-group">
                <label>¿Tienes un nombre artístico?</label>
                <input v-model="form.stage_name" type="text" class="onboard-input" placeholder="Ej: DJ Carlos" />
              </div>
            </div>

            <!-- STEP 3: Genres -->
            <div v-else-if="currentStep === 3" class="step-form">
              <p class="form-label">Géneros musicales</p>
              <div class="genre-grid">
                <button v-for="g in genres" :key="g.id" class="genre-tag" :class="{ selected: form.genre_ids.includes(g.id) }" @click="toggleGenre(g.id)">
                  {{ g.name }}
                </button>
              </div>
            </div>

            <!-- STEP 4: Photo -->
            <div v-else-if="currentStep === 4" class="step-form step-photo">
              <div class="photo-upload" @click="$refs.avatarInput.click()">
                <img v-if="avatarPreview" :src="avatarPreview" class="photo-preview" />
                <div v-else class="photo-placeholder">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                  <span class="photo-cta-text">Sube tu foto</span>
                </div>
              </div>
              <input ref="avatarInput" type="file" accept="image/*" hidden @change="onAvatarPick" />
              <ImageCropper
                :file="pendingAvatar"
                :aspect-ratio="1"
                :max-output="800"
                title="Ajusta tu foto de perfil"
                @cropped="onAvatarCropped"
                @cancel="pendingAvatar = null"
              />
              <div class="photo-guidelines">
                <div class="guideline ok">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary, #C1D82F)" stroke-width="2"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>
                  Nítida y alta resolución
                </div>
                <div class="guideline ok">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary, #C1D82F)" stroke-width="2"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>
                  Muestra tu rostro
                </div>
                <div class="guideline no">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E85D4A" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  Sin gráficos ni texto
                </div>
              </div>
            </div>

            <!-- STEP 5: Location -->
            <div v-else-if="currentStep === 5" class="step-form step-location">
              <div class="form-group">
                <label>Tu ciudad</label>
                <select v-model="form.city" class="onboard-input" @change="onCityChange">
                  <option value="" disabled>Selecciona tu ciudad</option>
                  <option v-for="c in panamaCities" :key="c.name" :value="c.name">{{ c.name }}</option>
                </select>
              </div>
              <div class="map-wrapper">
                <div class="map-hint">Toca una ciudad en el mapa</div>
                <div ref="mapContainer" class="map-container"></div>
              </div>
              <div class="form-group">
                <label>Radio de cobertura: <strong>{{ form.coverage_radius_km }} km</strong></label>
                <input v-model.number="form.coverage_radius_km" type="range" min="10" max="300" step="10" class="range-slider" />
              </div>
              <div class="form-group">
                <label>País</label>
                <input :value="form.country" type="text" class="onboard-input onboard-input--locked" readonly disabled aria-readonly="true" />
                <span class="field-hint">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px; margin-right:3px"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                  Pulsar opera únicamente en Panamá.
                </span>
              </div>
            </div>

            <!-- STEP 6: Experience -->
            <div v-else-if="currentStep === 6" class="step-form">
              <p class="form-label">Elige uno</p>
              <div class="option-list">
                <button v-for="e in experienceLevels" :key="e.value" class="option-card" :class="{ selected: form.experience_level === e.value }" @click="form.experience_level = e.value">
                  <span>{{ e.label }}</span>
                </button>
              </div>
            </div>

            <!-- STEP 7: Pricing -->
            <div v-else-if="currentStep === 7" class="step-form">
              <div class="pricing-row">
                <div class="form-group flex-1">
                  <label>Tarifa por hora</label>
                  <input v-model.number="form.hourly_rate" type="number" min="0" class="onboard-input" placeholder="0" />
                </div>
                <div class="form-group" style="width:120px">
                  <label>Moneda</label>
                  <select v-model="form.price_currency" class="onboard-input">
                    <option value="USD">USD</option>
                    <option value="PAB">PAB</option>
                    <option value="EUR">EUR</option>
                  </select>
                </div>
              </div>
              <p class="hint-text">Puedes cambiar esto en cualquier momento.</p>
            </div>

            <!-- STEP 8: Bio -->
            <div v-else-if="currentStep === 8" class="step-form">
              <div class="form-group">
                <label>Crea tu biografía</label>
                <textarea v-model="form.description" class="onboard-textarea" rows="6" placeholder="Cuéntanos sobre ti, tu experiencia y el tipo de eventos en los que sueles tocar..."></textarea>
              </div>
            </div>

            <!-- STEP 9: Survey -->
            <div v-else-if="currentStep === 9" class="step-form">
              <p class="form-label">¿Cómo descubriste Pulsar?</p>
              <div class="option-list">
                <button v-for="s in discoverySources" :key="s.value" class="option-card" :class="{ selected: form.discovery_source === s.value }" @click="form.discovery_source = s.value">
                  <span>{{ s.label }}</span>
                </button>
              </div>
            </div>

            <!-- STEP 10: Done -->
            <div v-else-if="currentStep === 10" class="step-form step-done">
              <div class="done-celebration"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary, #C1D82F)" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></div>
              <h2>¿Qué sigue?</h2>
              <div class="next-steps">
                <div class="next-item">
                  <span class="next-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg></span>
                  <div><strong>Revisaremos tu perfil</strong><br><span>Una vez aprobado, comenzarás a aparecer en la plataforma.</span></div>
                </div>
                <div class="next-item">
                  <span class="next-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></span>
                  <div><strong>Completa tu perfil</strong><br><span>Haz que tu perfil luzca profesional — la clave para gigs.</span></div>
                </div>
                <div class="next-item">
                  <span class="next-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg></span>
                  <div><strong>Consigue tu primer gig</strong><br><span>Responde a las consultas de los organizadores.</span></div>
                </div>
              </div>
              <button class="btn-cta-onboard" @click="goToProfile">Ir a mi perfil</button>
            </div>

          </div>
        </transition>

        <!-- Navigation Buttons -->
        <div v-if="currentStep > 0 && currentStep < 10" class="nav-buttons">
          <button v-if="currentStep > 1" class="btn-back" @click="currentStep--">Atrás</button>
          <div v-else></div>
          <button class="btn-next" :disabled="saving" :class="{ 'btn-next-pending': !canAdvance }" @click="nextStep">
            <span v-if="saving">Guardando...</span>
            <span v-else>{{ currentStep === 9 ? 'Finalizar' : 'Siguiente' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Error toast -->
    <transition name="fade">
      <div v-if="error" class="error-toast-onboard">{{ error }}</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import api from '@/api'
import L from 'leaflet'
import ImageCropper from '@/components/common/ImageCropper.vue'

const router = useRouter()
const auth = useAuthStore()
const themeStore = useThemeStore()

const currentStep = ref(0)
const saving = ref(false)
const error = ref('')
const genres = ref([])
const avatarPreview = ref(null)
const avatarFile = ref(null)

const form = ref({
  talent_type: 'dj',
  first_name: auth.user?.first_name || '',
  last_name: auth.user?.last_name || '',
  stage_name: '',
  genre_ids: [],
  city: auth.user?.city || 'Ciudad de Panamá',
  country: 'Panamá',
  coverage_radius_km: 50,
  experience_level: 'beginner',
  hourly_rate: 0,
  price_currency: 'USD',
  description: '',
  discovery_source: '',
})

const talentTypes = [
  { value: 'dj', label: 'DJ', icon: 'headphones' },
  { value: 'band', label: 'Banda', icon: 'drum' },
  { value: 'musician', label: 'Músico Solista', icon: 'music' },
]

const experienceLevels = [
  { value: 'beginner', label: 'Principiante' },
  { value: 'semi_professional', label: 'Semiprofesional' },
  { value: 'professional', label: 'Profesional' },
  { value: 'expert', label: 'Experto' },
]

const discoverySources = [
  { value: 'friend', label: 'De un amigo o colega' },
  { value: 'search_engine', label: 'Buscadores (Google, Yahoo, etc.)' },
  { value: 'social_media', label: 'Redes sociales (Instagram, Facebook, etc.)' },
  { value: 'website', label: 'Un sitio web, blog o foro' },
  { value: 'event', label: 'Un evento o showcase' },
  { value: 'other', label: 'Otro...' },
]

// Validación por paso: devuelve { valid, message } — message es el motivo si falta algo
const stepValidation = computed(() => {
  switch (currentStep.value) {
    case 1:
      return form.value.talent_type
        ? { valid: true }
        : { valid: false, message: 'Selecciona qué tipo de talento eres (DJ, banda o músico solista) para continuar.' }
    case 2:
      return form.value.first_name.trim()
        ? { valid: true }
        : { valid: false, message: 'Necesitamos tu nombre completo para crear tu perfil.' }
    case 3:
      return form.value.genre_ids.length > 0
        ? { valid: true }
        : { valid: false, message: 'Elige al menos 1 género musical. Podrás agregar más después.' }
    case 4:
      return avatarPreview.value
        ? { valid: true }
        : { valid: false, message: 'Sube tu foto de perfil. Es lo primero que ven los clientes.' }
    case 5:
      return form.value.city.trim()
        ? { valid: true }
        : { valid: false, message: 'Selecciona tu ciudad para que los clientes cercanos te encuentren.' }
    case 6:
      return form.value.experience_level
        ? { valid: true }
        : { valid: false, message: 'Elige tu nivel de experiencia.' }
    case 7:
      return form.value.hourly_rate >= 0
        ? { valid: true }
        : { valid: false, message: 'Ingresa tu tarifa por hora (puede ser 0 si prefieres cotizar caso por caso).' }
    case 8:
      return form.value.description && form.value.description.trim().length >= 20
        ? { valid: true }
        : { valid: false, message: 'Escribe al menos 20 caracteres en tu biografía. Cuéntale al cliente quién eres.' }
    case 9:
      return form.value.discovery_source
        ? { valid: true }
        : { valid: false, message: 'Selecciona cómo descubriste Pulsar. Esto nos ayuda a mejorar.' }
    default:
      return { valid: true }
  }
})

const canAdvance = computed(() => stepValidation.value.valid)

function toggleGenre(id) {
  const idx = form.value.genre_ids.indexOf(id)
  if (idx >= 0) form.value.genre_ids.splice(idx, 1)
  else form.value.genre_ids.push(id)
}

// Foto en bruto seleccionada — se manda al cropper antes de aceptarse
const pendingAvatar = ref(null)

function onAvatarPick(e) {
  const file = e.target.files[0]
  e.target.value = '' // reset para permitir re-seleccionar la misma foto
  if (!file) return
  pendingAvatar.value = file
}

function onAvatarCropped(croppedFile) {
  avatarFile.value = croppedFile
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarPreview.value = URL.createObjectURL(croppedFile)
  pendingAvatar.value = null
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  const fd = new FormData()
  fd.append('avatar', avatarFile.value)
  await api.post('/auth/me/avatar/', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

async function nextStep() {
  error.value = ''
  // Validar antes de avanzar — si falta algo, mostrar mensaje claro
  if (!stepValidation.value.valid) {
    error.value = stepValidation.value.message
    setTimeout(() => { error.value = '' }, 5000)
    return
  }
  saving.value = true
  try {
    // Upload avatar at step 4
    if (currentStep.value === 4 && avatarFile.value) {
      await uploadAvatar()
    }
    // Update user name at step 2
    if (currentStep.value === 2) {
      await api.patch('/auth/me/', {
        first_name: form.value.first_name,
        last_name: form.value.last_name,
      })
    }
    // Save discovery source at step 9
    if (currentStep.value === 9 && form.value.discovery_source) {
      await api.patch('/auth/me/', {
        discovery_source: form.value.discovery_source,
      })
    }
    // Final step: create talent profile
    if (currentStep.value === 9) {
      await createTalentProfile()
      currentStep.value = 10
    } else {
      currentStep.value++
    }
  } catch (err) {
    error.value = extractErrorMessage(err) || 'Error al guardar. Intenta de nuevo.'
    setTimeout(() => error.value = '', 6000)
  } finally {
    saving.value = false
  }
}

function extractErrorMessage(err) {
  const data = err.response?.data
  if (!data) return null
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  if (data.error) return data.error
  if (data.non_field_errors?.length) return data.non_field_errors.join(' ')
  // Field-level errors (DRF format): { stage_name: ["This field is required."] }
  const fieldErrors = []
  for (const [field, msgs] of Object.entries(data)) {
    if (Array.isArray(msgs)) fieldErrors.push(`${field}: ${msgs.join(', ')}`)
    else if (typeof msgs === 'string') fieldErrors.push(`${field}: ${msgs}`)
  }
  return fieldErrors.length ? fieldErrors.join(' · ') : null
}

async function createTalentProfile() {
  // Fallback: si el DJ no puso nombre artístico, usar su nombre real
  const stageName = (form.value.stage_name || '').trim() || (form.value.first_name || '').trim() || 'Sin nombre'
  const payload = {
    talent_type: form.value.talent_type,
    stage_name: stageName,
    genre_ids: form.value.genre_ids,
    city: form.value.city,
    country: form.value.country,
    coverage_radius_km: form.value.coverage_radius_km,
    experience_level: form.value.experience_level,
    hourly_rate: form.value.hourly_rate || 0,
    price_currency: form.value.price_currency,
    description: form.value.description,
    onboarding_completed: true,
    is_available: true,
  }
  await api.post('/talents/create/', payload)
}

async function saveAndExit() {
  router.push('/talent-dashboard')
}

function goToProfile() {
  router.push('/talent-dashboard')
}

// ── Panama Cities ──
const panamaCities = [
  { name: 'Ciudad de Panamá', lat: 8.9824, lng: -79.5199 },
  { name: 'San Miguelito', lat: 9.0504, lng: -79.4713 },
  { name: 'David', lat: 8.4333, lng: -82.4333 },
  { name: 'Colón', lat: 9.3547, lng: -79.9017 },
  { name: 'Santiago', lat: 8.1000, lng: -80.9833 },
  { name: 'Chitré', lat: 7.9667, lng: -80.4333 },
  { name: 'Penonomé', lat: 8.5167, lng: -80.3500 },
  { name: 'Aguadulce', lat: 8.2453, lng: -80.5431 },
  { name: 'La Chorrera', lat: 8.8789, lng: -79.7822 },
  { name: 'Arraiján', lat: 8.9500, lng: -79.6500 },
  { name: 'Bocas del Toro', lat: 9.3404, lng: -82.2418 },
  { name: 'Las Tablas', lat: 7.7647, lng: -80.2750 },
]

// ── Map Logic ──
const mapContainer = ref(null)
let mapInstance = null
let coverageCircle = null
let tileLayer = null
let cityMarkers = []
let resizeObserver = null

const TILE_DARK = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

function currentTileUrl() {
  return themeStore.theme === 'light' ? TILE_LIGHT : TILE_DARK
}

function makeMarkerIcon(active = false) {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div class="marker-dot${active ? ' active' : ''}"></div>`,
    iconSize: [active ? 18 : 12, active ? 18 : 12],
    iconAnchor: [active ? 9 : 6, active ? 9 : 6],
  })
}

function selectCityOnMap(cityName) {
  form.value.city = cityName
  const city = panamaCities.find(c => c.name === cityName)
  if (!city || !mapInstance) return
  mapInstance.flyTo([city.lat, city.lng], 9, { duration: 0.8 })
  coverageCircle?.setLatLng([city.lat, city.lng])
  // Update marker styles: only the selected one is "active"
  cityMarkers.forEach(({ marker, name }) => {
    marker.setIcon(makeMarkerIcon(name === cityName))
  })
}

function buildMap() {
  if (!mapContainer.value || mapInstance) return

  const initial = panamaCities.find(c => c.name === form.value.city) || panamaCities[0]

  mapInstance = L.map(mapContainer.value, {
    center: [initial.lat, initial.lng],
    zoom: 8,
    zoomControl: false,
    attributionControl: false,
    scrollWheelZoom: false,
  })

  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance)

  // Markers for every city, clickable
  cityMarkers = panamaCities.map(c => {
    const isActive = c.name === form.value.city
    const marker = L.marker([c.lat, c.lng], { icon: makeMarkerIcon(isActive) })
      .addTo(mapInstance)
      .bindTooltip(c.name, { direction: 'top', offset: [0, -8], className: 'city-tooltip' })
    marker.on('click', () => selectCityOnMap(c.name))
    return { marker, name: c.name }
  })

  // Coverage circle around the selected city
  coverageCircle = L.circle([initial.lat, initial.lng], {
    radius: form.value.coverage_radius_km * 1000,
    color: '#C1D82F',
    fillColor: '#C1D82F',
    fillOpacity: 0.10,
    weight: 1.5,
    dashArray: '6 4',
  }).addTo(mapInstance)

  // Make sure tiles render once the container has real dimensions
  resizeObserver = new ResizeObserver(() => {
    mapInstance?.invalidateSize()
  })
  resizeObserver.observe(mapContainer.value)

  // Belt-and-suspenders: a couple of explicit invalidations during the
  // Vue transition (350ms) so tiles paint reliably.
  requestAnimationFrame(() => mapInstance?.invalidateSize())
  setTimeout(() => mapInstance?.invalidateSize(), 400)
}

function destroyMap() {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
  coverageCircle = null
  tileLayer = null
  cityMarkers = []
}

function onCityChange() {
  selectCityOnMap(form.value.city)
}

// Coverage radius slider → update circle live
watch(() => form.value.coverage_radius_km, (val) => {
  if (coverageCircle) coverageCircle.setRadius(val * 1000)
})

// Swap tile layer when theme changes
watch(() => themeStore.theme, () => {
  if (!mapInstance || !tileLayer) return
  mapInstance.removeLayer(tileLayer)
  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
})

// Build / tear down the map as the user enters / leaves step 5.
// We can't rely on nextTick alone — the <transition mode="out-in"> means
// the step-5 DOM (and the mapContainer ref) only exists AFTER the previous
// step finishes leaving (~350ms). So we trigger build from a ref watcher
// that fires the moment the container element actually mounts.
watch(currentStep, (step) => {
  if (step !== 5 && mapInstance) destroyMap()
  if (step === 5 && !form.value.city) form.value.city = 'Ciudad de Panamá'
})

watch(mapContainer, (el) => {
  if (el && currentStep.value === 5 && !mapInstance) {
    // One frame so the transition's enter animation has applied real layout
    requestAnimationFrame(() => buildMap())
  }
})

onMounted(() => {
  // If somehow we land already on step 5 (deep link / refresh), build it
  if (currentStep.value === 5 && mapContainer.value && !mapInstance) {
    requestAnimationFrame(() => buildMap())
  }
})

onBeforeUnmount(() => destroyMap())

onMounted(async () => {
  try {
    const { data } = await api.get('/genres/')
    genres.value = data
  } catch { /* ignore */ }
})

// Mobile step titles
const stepTitles = {
  1: 'Primero, cuéntanos qué tipo de perfil estás creando.',
  2: '¿Cómo deberían llamarte?',
  3: '¿Qué tipo de música tocas?',
  4: 'Ahora, agreguemos tu foto de perfil.',
  5: '¿Dónde te encuentras?',
  6: '¿Cuánta experiencia tienes?',
  7: 'Definamos tu tarifa.',
  8: 'Ahora, creemos tu biografía.',
  9: 'Una última pregunta.',
  10: `¡Bienvenido, ${form.value.first_name || 'artista'}!`,
}
const stepSubtitles = {
  3: 'Puedes agregar más después.',
  4: 'Muestra tu mejor lado.',
  5: 'Recibirás oportunidades cerca de tu ubicación.',
  8: 'Menciona experiencias previas y en qué tipo de eventos sueles tocar.',
}
const mobileStepTitle = computed(() => stepTitles[currentStep.value] || '')
const mobileStepSubtitle = computed(() => stepSubtitles[currentStep.value] || '')
</script>

<style scoped>
.onboarding-view {
  min-height: 100vh;
  background: var(--color-bg-primary);
  position: relative;
  overflow-x: hidden;
  padding-top: 72px;
}

/* ── Decorative Orbs ── */
.orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.35; pointer-events: none; animation: orbDrift 20s infinite ease-in-out; }
.orb-1 { width: 400px; height: 400px; background: rgba(193,216,47,0.15); top: -10%; left: -10%; }
.orb-2 { width: 300px; height: 300px; background: rgba(193,216,47,0.08); bottom: -5%; right: -5%; animation-delay: -10s; }
@keyframes orbDrift {
  0%,100% { transform: translate(0,0) scale(1); }
  50% { transform: translate(30px,-20px) scale(1.05); }
}

/* ── Save & Exit ── */
.save-exit-btn { position: fixed; top: 80px; right: 20px; z-index: 50; padding: 8px 20px; border-radius: 20px; border: 1px solid var(--color-border); background: var(--color-bg-card); backdrop-filter: blur(12px); color: var(--color-text-muted); font-size: 0.82rem; font-weight: 500; cursor: pointer; transition: all 0.25s; }
.save-exit-btn:hover { background: var(--color-bg-card-hover); color: var(--color-text-primary); border-color: var(--color-border-hover); }

/* ── Progress Bar ── */
.progress-bar { position: fixed; top: 0; left: 0; right: 0; height: 3px; background: rgba(255,255,255,0.06); z-index: 60; }
.progress-fill { height: 100%; background: var(--color-primary, #C1D82F); transition: width 0.5s cubic-bezier(0.22,1,0.36,1); border-radius: 0 2px 2px 0; box-shadow: 0 0 12px rgba(193,216,47,0.4); }

/* ── Container ── */
.onboarding-container { display: grid; grid-template-columns: 1fr 1fr; min-height: calc(100vh - 72px); border-radius: 20px 20px 0 0; overflow: hidden; position: relative; }
.onboarding-container::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 40px; background: linear-gradient(to bottom, var(--color-bg-primary), transparent); z-index: 3; pointer-events: none; border-radius: 20px 20px 0 0; }

/* ── LEFT PANEL ── */
/* Left panel: ALWAYS dark, never changes with theme */
.onboarding-left { display: flex; align-items: center; justify-content: center; padding: 60px 48px; background: linear-gradient(160deg, #0a0a0a 0%, #111110 50%, #0a0a0a 100%) !important; position: relative; overflow: hidden; color: #fff !important; }
.onboarding-left::after { content: ''; position: absolute; top: 0; right: 0; width: 80px; height: 100%; background: linear-gradient(to right, transparent, #0a0a0a); z-index: 1; pointer-events: none; }
.onboarding-left * { color: inherit; }
.onboarding-left .step-badge { color: #C1D82F !important; }
.onboarding-left .text-accent { color: #C1D82F !important; }
.onboarding-left .step-subtitle { color: rgba(255,255,255,0.55) !important; }
.onboarding-left .benefit-card strong { color: rgba(255,255,255,0.9) !important; }
.onboarding-left .benefit-card span { color: rgba(255,255,255,0.4) !important; }
.onboarding-left .benefit-icon { color: #C1D82F !important; }

.left-content { position: relative; z-index: 2; max-width: 440px; }

.step-badge { display: inline-block; padding: 6px 16px; background: rgba(193,216,47,0.1); border: 1px solid rgba(193,216,47,0.2); color: var(--color-primary, #C1D82F); border-radius: 20px; font-size: 0.78rem; font-weight: 600; margin-bottom: 24px; letter-spacing: 0.5px; }

.text-accent { color: var(--color-primary, #C1D82F); }

.left-content h1 { font-family: 'Poppins', sans-serif; font-size: 2.2rem; font-weight: 700; color: #fff; line-height: 1.2; margin-bottom: 14px; }

.step-subtitle { color: rgba(255,255,255,0.5); font-size: 0.95rem; line-height: 1.6; }

.founder-quote { color: rgba(255,255,255,0.3); font-style: italic; margin-top: 12px; font-size: 0.9rem; }

/* ── Step Indicator ── */
.step-indicator { margin-top: 32px; font-size: 0.85rem; color: rgba(255,255,255,0.35); font-weight: 500; }
.step-num { color: var(--color-primary, #C1D82F); font-weight: 700; font-size: 1.1rem; }

/* ── Benefits Grid ── */
.benefits-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 32px; }
.benefit-card { padding: 18px; background: rgba(255,255,255,0.02); border: none; border-radius: 16px; display: flex; flex-direction: column; gap: 8px; transition: all 0.3s; }
.benefit-card:hover { background: rgba(255,255,255,0.04); transform: translateY(-2px); }
.benefit-icon { width: 36px; height: 36px; border-radius: 10px; background: rgba(193,216,47,0.1); display: flex; align-items: center; justify-content: center; margin-bottom: 4px; color: var(--color-primary, #C1D82F); }
.benefit-card strong { color: rgba(255,255,255,0.9); font-size: 0.85rem; }
.benefit-card span { color: rgba(255,255,255,0.4); font-size: 0.78rem; line-height: 1.4; }

/* ── Mobile Step Header ── */
.mobile-step-header { display: none; }
.mobile-step-num { font-size: 0.75rem; color: var(--color-primary, #C1D82F); font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }

/* ── RIGHT PANEL ── */
/* Right panel: responds to theme */
.onboarding-right { display: flex; flex-direction: column; justify-content: center; padding: 60px 48px; background: var(--color-bg-primary); position: relative; color: var(--color-text-primary); }

.step-content { flex: 1; display: flex; flex-direction: column; justify-content: center; max-width: 480px; margin: 0 auto; width: 100%; }

/* ── Welcome Buttons ── */
.step-welcome { display: flex; flex-direction: column; gap: 14px; align-items: flex-start; }

.btn-cta-onboard { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 16px 32px; background: var(--color-primary, #C1D82F); color: #0a0a0a; font-size: 1rem; font-weight: 600; border: none; border-radius: 14px; cursor: pointer; transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1); width: 100%; max-width: 340px; }
.btn-cta-onboard:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 36px rgba(193,216,47,0.35); }

.btn-ghost-onboard { padding: 14px 24px; background: transparent; color: var(--color-text-muted); font-size: 0.9rem; font-weight: 500; border: 1.5px solid var(--color-border); border-radius: 14px; cursor: pointer; transition: all 0.25s; width: 100%; max-width: 340px; }
.btn-ghost-onboard:hover { border-color: var(--color-primary); color: var(--color-primary); }

/* ── Form Elements ── */
.step-form { display: flex; flex-direction: column; gap: 20px; }
.form-label { font-size: 0.92rem; font-weight: 600; color: var(--color-text-secondary); margin-bottom: 4px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 0.85rem; font-weight: 500; color: var(--color-text-muted); }

.onboard-input { padding: 14px 16px; background: var(--color-bg-card); border: 1.5px solid var(--color-border); border-radius: 12px; color: var(--color-text-primary); font-size: 0.95rem; font-family: inherit; transition: all 0.25s; outline: none; width: 100%; }
.onboard-input:focus { border-color: var(--color-primary); box-shadow: 0 0 0 3px rgba(193,216,47,0.08); }
.onboard-input::placeholder { color: var(--color-text-muted); }
.onboard-input--locked { opacity: 0.75; cursor: not-allowed; background: var(--color-bg); border-style: dashed; }
.field-hint { display: block; margin-top: 6px; font-size: 0.8rem; color: var(--color-text-muted); }

select.onboard-input { appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='rgba(255,255,255,0.5)' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 16px center; padding-right: 40px; cursor: pointer; }
select.onboard-input option { background: #1a1a1a; color: #fff; padding: 12px; }

.onboard-textarea { padding: 14px 16px; background: var(--color-bg-card); border: 1.5px solid var(--color-border); border-radius: 12px; color: var(--color-text-primary); font-size: 0.95rem; font-family: inherit; resize: vertical; outline: none; transition: border-color 0.25s; width: 100%; }
.onboard-textarea:focus { border-color: var(--color-primary); }

/* ── Option Cards ── */
.option-list { display: flex; flex-direction: column; gap: 10px; }
.option-card { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; background: var(--color-bg-card); border: 1.5px solid var(--color-border); border-radius: 14px; color: var(--color-text-primary); font-size: 0.95rem; cursor: pointer; transition: all 0.25s; }
.option-card:hover { border-color: var(--color-border-hover); background: var(--color-bg-card-hover); }
.option-card.selected { border-color: var(--color-primary); background: var(--color-primary-ultra-light); box-shadow: 0 0 0 3px rgba(193,216,47,0.08); }
.option-icon { display: flex; align-items: center; color: var(--color-text-muted); }
.option-card.selected .option-icon { color: var(--color-primary); }

/* ── Genre Tags ── */
.genre-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.genre-tag { padding: 10px 20px; border-radius: 12px; border: 1.5px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-secondary); font-size: 0.88rem; cursor: pointer; transition: all 0.2s; }
.genre-tag:hover { border-color: var(--color-border-hover); }
.genre-tag.selected { border-color: var(--color-primary); background: var(--color-primary-ultra-light); color: var(--color-primary); font-weight: 600; }

/* ── Photo Upload ── */
.step-photo { align-items: center; gap: 24px; }
.photo-upload { position: relative; width: 200px; height: 200px; border-radius: 24px; background: var(--color-bg-card); border: 2px dashed var(--color-border); cursor: pointer; display: flex; align-items: center; justify-content: center; overflow: hidden; transition: all 0.3s; }
.photo-upload:hover { border-color: var(--color-primary); background: var(--color-bg-card-hover); box-shadow: 0 0 32px rgba(193,216,47,0.08); }
.photo-preview { width: 100%; height: 100%; object-fit: cover; }
.photo-placeholder { display: flex; flex-direction: column; align-items: center; gap: 12px; color: var(--color-text-muted); }
.photo-cta-text { font-size: 0.85rem; font-weight: 500; color: var(--color-text-muted); }
.photo-upload:hover .photo-placeholder { color: var(--color-primary); }
.photo-upload:hover .photo-cta-text { color: var(--color-primary); }
.photo-guidelines { display: flex; flex-direction: column; gap: 10px; }
.guideline { display: flex; align-items: center; gap: 8px; font-size: 0.84rem; color: var(--color-text-muted); }

/* ── Range Slider ── */
.range-slider { -webkit-appearance: none; width: 100%; height: 6px; border-radius: 3px; background: var(--color-border); outline: none; margin-top: 8px; }
.range-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: var(--color-primary); cursor: pointer; box-shadow: 0 2px 8px rgba(193,216,47,0.3); }

/* ── Pricing ── */
.pricing-row { display: flex; gap: 12px; }
.flex-1 { flex: 1; }
.hint-text { font-size: 0.82rem; color: var(--color-primary, #C1D82F); text-align: center; opacity: 0.7; }

/* ── Done Step ── */
.done-celebration { font-size: 3rem; text-align: center; margin-bottom: 8px; animation: celebrateBounce 0.6s cubic-bezier(0.34,1.56,0.64,1); }
@keyframes celebrateBounce { 0% { transform: scale(0); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.step-done h2 { font-family: 'Poppins', sans-serif; font-size: 1.6rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: 24px; text-align: center; }
.next-steps { display: flex; flex-direction: column; gap: 18px; margin-bottom: 32px; }
.next-item { display: flex; gap: 14px; align-items: flex-start; padding: 14px 16px; background: var(--color-bg-card); border-radius: 12px; border: none; }
.next-icon { flex-shrink: 0; width: 36px; height: 36px; border-radius: 10px; background: var(--color-primary-ultra-light); display: flex; align-items: center; justify-content: center; color: var(--color-primary); }
.next-item strong { color: var(--color-text-primary); font-size: 0.92rem; }
.next-item span { color: var(--color-text-muted); font-size: 0.83rem; }

/* ── Nav Buttons ── */
.nav-buttons { display: flex; justify-content: space-between; align-items: center; padding-top: 24px; max-width: 480px; margin: 0 auto; width: 100%; }
.btn-back { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; background: transparent; color: var(--color-text-muted); border: none; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: color 0.2s; }
.btn-back:hover { color: var(--color-text-primary); }
.btn-next { display: inline-flex; align-items: center; gap: 8px; padding: 12px 28px; background: var(--color-primary, #C1D82F); color: #0a0a0a; font-size: 0.95rem; font-weight: 600; border: none; border-radius: 12px; cursor: pointer; transition: all 0.25s; }
.btn-next:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(193,216,47,0.3); }
.btn-next:disabled { opacity: 0.35; cursor: not-allowed; }
.btn-next-pending { opacity: 0.55; }
.btn-next-pending:hover:not(:disabled) { opacity: 0.7; transform: none; box-shadow: none; }

/* ── Error Toast ── */
.error-toast-onboard { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); padding: 12px 24px; background: var(--color-error, #E85D4A); color: #fff; border-radius: 12px; font-size: 0.88rem; font-weight: 500; z-index: 100; box-shadow: 0 8px 24px rgba(232,93,74,0.3); }

/* ── Transitions ── */
.fade-text-enter-active, .fade-text-leave-active { transition: all 0.35s ease; }
.fade-text-enter-from { opacity: 0; transform: translateY(12px); }
.fade-text-leave-to { opacity: 0; transform: translateY(-12px); }
.slide-step-enter-active, .slide-step-leave-active { transition: all 0.35s ease; }
.slide-step-enter-from { opacity: 0; transform: translateX(20px); }
.slide-step-leave-to { opacity: 0; transform: translateX(-20px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .onboarding-container { grid-template-columns: 1fr; min-height: auto; }
  .onboarding-left { padding: 28px 20px 20px; min-height: auto; }
  .onboarding-left::after { display: none; }
  .onboarding-left.hide-on-mobile { display: none; }
  .left-content h1 { font-size: 1.4rem; margin-bottom: 10px; }
  .step-badge { margin-bottom: 16px; font-size: 0.72rem; }
  .step-subtitle { font-size: 0.85rem; }
  .benefits-grid { grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 20px; }
  .benefit-card { padding: 14px; }
  .benefit-icon { width: 30px; height: 30px; border-radius: 8px; }
  .benefit-icon svg { width: 16px; height: 16px; }
  .benefit-card strong { font-size: 0.78rem; }
  .benefit-card span { font-size: 0.7rem; }
  .onboarding-right { padding: 24px 20px; min-height: auto; }
  .step-content { max-width: 100%; }
  .step-welcome { align-items: stretch; padding-top: 8px; }
  .btn-cta-onboard, .btn-ghost-onboard { max-width: 100%; }
  .btn-cta-onboard { padding: 14px 24px; font-size: 0.92rem; }
  .btn-ghost-onboard { padding: 12px 20px; font-size: 0.85rem; }
  .mobile-step-header { display: block; padding: 0 0 16px; }
  .mobile-step-header h2 { font-family: 'Poppins', sans-serif; font-size: 1.3rem; font-weight: 700; color: #fff; margin-bottom: 4px; }
  .mobile-step-header .step-subtitle { font-size: 0.85rem; }
  .save-exit-btn { top: 70px; right: 10px; padding: 6px 14px; font-size: 0.78rem; }
  .nav-buttons { padding-top: 16px; }
  .btn-next { padding: 12px 24px; font-size: 0.88rem; }
  .pricing-row { flex-direction: column; }
  .pricing-row .form-group { width: 100% !important; }
  .photo-upload { width: 160px; height: 160px; border-radius: 20px; }
  .option-card { padding: 14px 16px; font-size: 0.88rem; }
  .genre-tag { padding: 8px 14px; font-size: 0.82rem; }
  .orb { display: none; }
  .map-container { height: 180px; }
}

/* ── Map ── */
.step-location { gap: 16px; }
.map-wrapper {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  position: relative;
}
.map-container {
  width: 100%;
  height: 260px;
  background: var(--color-bg-card);
}
.map-hint {
  position: absolute;
  top: 10px;
  left: 12px;
  z-index: 400;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.72rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  backdrop-filter: blur(8px);
  pointer-events: none;
}

/* Leaflet styles (not scoped - Leaflet injects into body) */
:deep(.custom-marker) { background: none !important; border: none !important; }
:deep(.marker-dot) {
  width: 12px;
  height: 12px;
  background: var(--color-bg-primary);
  border: 2px solid var(--color-primary, #C1D82F);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--color-bg-card), 0 0 8px rgba(193,216,47,0.4);
  transition: all 0.2s ease;
  cursor: pointer;
}
:deep(.marker-dot:hover) {
  transform: scale(1.3);
  background: var(--color-primary, #C1D82F);
}
:deep(.marker-dot.active) {
  width: 18px;
  height: 18px;
  background: var(--color-primary, #C1D82F);
  box-shadow: 0 0 0 4px rgba(193,216,47,0.25), 0 0 16px rgba(193,216,47,0.6);
  animation: markerPulse 2s ease-in-out infinite;
}
@keyframes markerPulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(193,216,47,0.25), 0 0 16px rgba(193,216,47,0.6); }
  50% { box-shadow: 0 0 0 8px rgba(193,216,47,0.10), 0 0 20px rgba(193,216,47,0.7); }
}

:deep(.city-tooltip) {
  background: var(--color-bg-card) !important;
  color: var(--color-text-primary) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: 8px !important;
  padding: 4px 10px !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
}
:deep(.city-tooltip::before),
:deep(.leaflet-tooltip-top::before) { display: none !important; }

:deep(.leaflet-control-zoom) {
  border: none !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
  margin: 12px !important;
}
:deep(.leaflet-control-zoom a) {
  background: var(--color-bg-card) !important;
  color: var(--color-text-secondary) !important;
  border: 1px solid var(--color-border) !important;
  width: 30px !important;
  height: 30px !important;
  line-height: 28px !important;
  font-size: 16px !important;
}
:deep(.leaflet-control-zoom a:hover) {
  background: var(--color-bg-card-hover) !important;
  color: var(--color-primary, #C1D82F) !important;
  border-color: var(--color-primary, #C1D82F) !important;
}
:deep(.leaflet-control-zoom-in) { border-radius: 8px 8px 0 0 !important; }
:deep(.leaflet-control-zoom-out) { border-radius: 0 0 8px 8px !important; border-top: none !important; }

/* Map background while tiles load */
:deep(.leaflet-container) {
  background: var(--color-bg-card) !important;
  font-family: inherit !important;
  outline: none !important;
}

</style>
