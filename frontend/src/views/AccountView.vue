<template>
  <div class="account-page">
    <div class="container">
      <header class="account-header">
        <h1>Mi Perfil</h1>
        <p class="account-sub">Edita tu información de cuenta y preferencias.</p>
      </header>

      <div class="account-layout">
        <!-- Sidebar -->
        <aside class="account-sidebar">
          <button v-for="t in tabs" :key="t.key" class="account-tab" :class="{ active: activeTab === t.key }" @click="activeTab = t.key">
            <span v-html="t.icon"></span>
            {{ t.label }}
          </button>

          <router-link
            v-if="auth.isTalent && talentProfileId"
            :to="`/talent/${talentProfileId}`"
            class="account-public-link"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            Ver mi perfil público
          </router-link>
        </aside>

        <!-- Main panel -->
        <main class="account-main">
          <!-- Información personal -->
          <section v-if="activeTab === 'info'" class="account-section">
            <h2>Información personal</h2>

            <!-- Avatar -->
            <div class="avatar-section">
              <div class="avatar-wrap">
                <img :src="avatarPreview || form.avatar || defaultAvatar" alt="Avatar" class="account-avatar" />
              </div>
              <div>
                <input ref="avatarInput" type="file" accept="image/*" hidden @change="onAvatarPick" />
                <button class="btn btn-ghost btn-sm" @click="$refs.avatarInput.click()">Cambiar foto</button>
                <button v-if="avatarFile" class="btn btn-primary btn-sm" :disabled="uploadingAvatar" @click="uploadAvatar" style="margin-left: var(--space-2)">
                  {{ uploadingAvatar ? 'Subiendo...' : 'Guardar foto' }}
                </button>
                <p class="avatar-hint">JPG o PNG, máx 5MB · podrás recortarla</p>
                <ImageCropper
                  :file="pendingAvatar"
                  :aspect-ratio="1"
                  :max-output="800"
                  title="Ajusta tu foto de perfil"
                  @cropped="onAvatarCropped"
                  @cancel="pendingAvatar = null"
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="label">Nombre</label>
                <input v-model="form.first_name" type="text" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">Apellido</label>
                <input v-model="form.last_name" type="text" class="input-field" />
              </div>
              <div class="form-group full">
                <label class="label">Email</label>
                <input :value="form.email" type="email" class="input-field" disabled />
                <small class="form-note">Contacta soporte para cambiar tu email.</small>
              </div>
              <div class="form-group">
                <label class="label">Teléfono</label>
                <input v-model="form.phone" type="tel" class="input-field" placeholder="+507..." />
              </div>
              <div class="form-group">
                <label class="label">Ciudad</label>
                <input v-model="form.city" type="text" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">País</label>
                <input v-model="form.country" type="text" class="input-field" />
              </div>
              <div class="form-group full">
                <label class="label">Bio</label>
                <textarea v-model="form.bio" rows="3" class="input-field" placeholder="Cuéntanos algo sobre ti..."></textarea>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn btn-primary" :disabled="saving" @click="saveProfile">
                {{ saving ? 'Guardando...' : 'Guardar cambios' }}
              </button>
              <span v-if="saveSuccess" class="save-success">✓ Cambios guardados</span>
            </div>
          </section>

          <!-- Mis roles -->
          <section v-else-if="activeTab === 'roles'" class="account-section">
            <h2>Mis roles en Pulsar</h2>
            <p class="section-sub">Activá las capas que correspondan a lo que ofrecés. Podés tener varios roles al mismo tiempo.</p>

            <!-- Rol primario: Talento o Cliente -->
            <div class="role-card role-card-on">
              <div class="role-card-icon role-card-icon-primary">
                <span v-if="auth.user?.role === 'talent'">🎵</span>
                <span v-else>👤</span>
              </div>
              <div class="role-card-info">
                <div class="role-card-name">{{ primaryRoleLabel }}</div>
                <div class="role-card-desc">{{ primaryRoleDesc }}</div>
              </div>
              <span class="role-status on">✓ Activo</span>
            </div>

            <!-- Rol Aliado / Partner -->
            <div class="role-card" :class="{ 'role-card-on': partnerRole.active }">
              <div class="role-card-icon" :class="{ 'role-card-icon-partner': partnerRole.active }">📦</div>
              <div class="role-card-info">
                <div class="role-card-name">Aliado</div>
                <div class="role-card-desc">
                  Trae clientes a Pulsar y cobra comisión por cada reserva que gestionás. Próximamente: rentar packs de producción y ofrecer venues.
                </div>
              </div>
              <span v-if="partnerRole.active" class="role-status on">✓ Activo</span>
              <span v-else class="role-status off">○ Inactivo</span>
              <button
                class="role-toggle"
                :class="{ on: partnerRole.active }"
                :disabled="partnerRole.saving"
                @click="togglePartnerRole"
                :aria-label="partnerRole.active ? 'Desactivar Aliado' : 'Activar Aliado'"
              ></button>
            </div>

            <!-- Sub-opciones cuando Aliado está activo -->
            <div v-if="partnerRole.active" class="role-suboptions">
              <div class="role-suboptions-title">→ Sub-opciones disponibles:</div>
              <label class="suboption suboption-on">
                <input type="checkbox" :checked="partnerRole.offers.includes('referral')" disabled />
                <div>
                  <strong>Traer clientes (referral)</strong>
                  <div class="suboption-desc">Gestionás reservas en nombre de tus clientes y cobrás comisión.</div>
                </div>
              </label>
              <button
                type="button"
                class="suboption suboption-interactive"
                :class="{ 'suboption-on': productionStatus === 'verified', 'suboption-pending': productionStatus === 'pending' }"
                @click="openProductionOnboarding"
              >
                <input type="checkbox" :checked="productionStatus === 'verified'" :indeterminate.prop="productionStatus === 'pending'" tabindex="-1" />
                <div class="suboption-body">
                  <strong>
                    Packs de producción
                    <span v-if="productionStatus === 'pending'" class="status-tag pending">En verificación</span>
                    <span v-else-if="productionStatus === 'verified'" class="status-tag verified">Verificado ✓</span>
                    <span v-else-if="productionStatus === 'rejected'" class="status-tag rejected">Rechazado</span>
                    <span v-else-if="productionStatus === 'draft'" class="status-tag draft">En progreso</span>
                  </strong>
                  <div class="suboption-desc">
                    <span v-if="productionStatus === 'pending'">Un admin revisará tu solicitud en máximo 48h.</span>
                    <span v-else-if="productionStatus === 'verified'">Ya podés publicar packs de equipo.</span>
                    <span v-else-if="productionStatus === 'rejected'">Tu solicitud fue rechazada. Tocá para revisar y reenviar.</span>
                    <span v-else-if="productionStatus === 'draft'">Continúa donde lo dejaste.</span>
                    <span v-else>Renta de equipo (sonido, luces, DJ booth). Requiere verificación. Tocá para empezar →</span>
                  </div>
                </div>
              </button>
              <label class="suboption suboption-locked">
                <input type="checkbox" disabled />
                <div>
                  <strong>Venue <span class="soon-tag">próximamente</span></strong>
                  <div class="suboption-desc">Ofrecé tu espacio físico (terraza, salón, club) en Pulsar.</div>
                </div>
              </label>

              <router-link to="/partner" class="btn btn-primary btn-sm role-cta">
                Ir al dashboard de Aliado →
              </router-link>
            </div>

            <p v-if="partnerRole.error" class="role-error">{{ partnerRole.error }}</p>
            <p v-if="partnerRole.success" class="save-success">✓ Cambios guardados</p>
          </section>

          <!-- Cambiar contraseña -->
          <section v-else-if="activeTab === 'password'" class="account-section">
            <h2>Cambiar contraseña</h2>
            <p class="section-sub">Para cambiar tu contraseña, te enviaremos un email con un link de reset.</p>
            <button class="btn btn-primary" :disabled="sendingReset" @click="sendPasswordReset">
              {{ sendingReset ? 'Enviando...' : 'Enviar email de reset' }}
            </button>
            <p v-if="resetSent" class="save-success">✓ Email enviado. Revisa tu bandeja.</p>
          </section>

          <!-- Notificaciones / cuenta -->
          <section v-else-if="activeTab === 'danger'" class="account-section">
            <h2>Zona de riesgo</h2>
            <div class="danger-block">
              <strong>Cerrar todas las sesiones</strong>
              <p>Si crees que alguien más tiene acceso a tu cuenta, ciérralas en todos los dispositivos.</p>
              <button class="btn btn-ghost btn-sm" @click="logoutEverywhere">Cerrar todas las sesiones</button>
            </div>
            <div class="danger-block">
              <strong>Eliminar cuenta</strong>
              <p>Esta acción es permanente. Tu nombre, email y avatar se eliminan; las reservas pasadas quedan como "Usuario eliminado". Si tienes reservas activas, debes cancelarlas o esperar a que terminen.</p>
              <button class="btn btn-ghost btn-sm btn-danger" @click="deleteModal.open = true">Eliminar mi cuenta</button>
            </div>
          </section>
        </main>
      </div>
    </div>

    <!-- Delete account modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="deleteModal.open" class="del-backdrop" @click.self="closeDeleteModal">
          <div class="del-modal">
            <h3>Eliminar cuenta</h3>
            <p class="del-warn">
              Esta acción <strong>no se puede deshacer</strong>. Se anonimizarán tus datos personales,
              se cerrará tu sesión y no podrás volver a entrar con esta cuenta.
            </p>
            <ul class="del-list">
              <li>Tu nombre, email, teléfono y avatar serán eliminados.</li>
              <li>Las reservas pasadas se conservan como "Usuario eliminado".</li>
              <li>Si eres talento, tu perfil dejará de aparecer en búsqueda.</li>
            </ul>

            <div class="form-group" style="margin-top: var(--space-4)">
              <label class="label">Para confirmar, escribe tu email <strong>{{ form.email }}</strong></label>
              <input
                v-model="deleteModal.confirmEmail"
                type="email"
                class="input-field"
                placeholder="tu@email.com"
                autocomplete="off"
              />
            </div>

            <p v-if="deleteModal.error" class="del-error">{{ deleteModal.error }}</p>

            <div class="del-actions">
              <button class="btn btn-ghost btn-sm" @click="closeDeleteModal" :disabled="deleteModal.loading">
                Cancelar
              </button>
              <button
                class="btn btn-sm btn-danger-solid"
                :disabled="!canConfirmDelete || deleteModal.loading"
                @click="confirmDelete"
              >
                {{ deleteModal.loading ? 'Eliminando...' : 'Eliminar definitivamente' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/api'
import ImageCropper from '@/components/common/ImageCropper.vue'

const auth = useAuthStore()
const router = useRouter()

const activeTab = ref('info')
const saving = ref(false)
const saveSuccess = ref(false)
const sendingReset = ref(false)
const resetSent = ref(false)
const avatarFile = ref(null)
const avatarPreview = ref(null)
const uploadingAvatar = ref(false)
const talentProfileId = ref(null)

const defaultAvatar = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"%3E%3Crect fill="%230A0A0A" width="120" height="120" rx="60"/%3E%3Ccircle cx="60" cy="45" r="20" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3Cpath d="M30 95a30 30 0 0160 0" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3C/svg%3E'

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  city: '',
  country: '',
  bio: '',
  avatar: '',
})

const tabs = computed(() => {
  const base = [
    { key: 'info', label: 'Información', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  ]
  if (auth.user?.role !== 'admin') {
    base.push({ key: 'roles', label: 'Mis roles', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 014-4h4a4 4 0 014 4v2"/><path d="M16 3.13a4 4 0 010 7.75"/><path d="M21 21v-2a4 4 0 00-3-3.87"/></svg>' })
  }
  base.push(
    { key: 'password', label: 'Contraseña', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>' },
    { key: 'danger', label: 'Cuenta', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>' },
  )
  return base
})

const pendingAvatar = ref(null)

// ── Partner role state ──
const partnerRole = reactive({
  active: false,
  offers: [],
  saving: false,
  success: false,
  error: '',
})
const productionStatus = ref(null) // null = no profile, 'draft' | 'pending' | 'verified' | 'rejected'

async function fetchProductionStatus() {
  if (!partnerRole.active) {
    productionStatus.value = null
    return
  }
  try {
    const { data } = await api.get('/partner/production/')
    productionStatus.value = data.status || null
  } catch {
    productionStatus.value = null
  }
}

function openProductionOnboarding() {
  router.push('/partner/onboarding')
}

// Sync from auth store whenever it changes
function syncPartnerFromAuth() {
  partnerRole.active = !!auth.user?.is_partner_active
  partnerRole.offers = Array.isArray(auth.user?.partner_offers) ? [...auth.user.partner_offers] : []
}

const primaryRoleLabel = computed(() => {
  const map = { talent: 'Talento', client: 'Cliente', admin: 'Admin' }
  return map[auth.user?.role] || 'Usuario'
})
const primaryRoleDesc = computed(() => {
  if (auth.user?.role === 'talent') return 'Ofrecés tu performance como DJ, músico o banda.'
  if (auth.user?.role === 'client') return 'Reservás talentos para tus eventos.'
  return 'Cuenta básica de Pulsar.'
})

async function togglePartnerRole() {
  partnerRole.saving = true
  partnerRole.error = ''
  partnerRole.success = false
  const willActivate = !partnerRole.active
  try {
    const { data } = await api.post('/auth/me/partner-role/', {
      active: willActivate,
      offers: willActivate ? ['referral'] : [],
    })
    // Update auth store + localStorage so isPartner / nav reflects el cambio inmediatamente
    auth.user = data
    localStorage.setItem('user', JSON.stringify(data))
    syncPartnerFromAuth()
    fetchProductionStatus()
    partnerRole.success = true
    setTimeout(() => { partnerRole.success = false }, 3000)
  } catch (e) {
    partnerRole.error = e?.response?.data?.detail || 'No se pudo guardar el cambio.'
  }
  partnerRole.saving = false
}

function onAvatarPick(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    alert('La imagen no puede superar 5MB')
    return
  }
  pendingAvatar.value = file
}

function onAvatarCropped(croppedFile) {
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
  avatarFile.value = croppedFile
  avatarPreview.value = URL.createObjectURL(croppedFile)
  pendingAvatar.value = null
}

async function uploadAvatar() {
  if (!avatarFile.value) return
  uploadingAvatar.value = true
  try {
    const fd = new FormData()
    fd.append('avatar', avatarFile.value)
    const { data } = await api.post('/auth/me/avatar/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.avatar = data.avatar
    avatarFile.value = null
    avatarPreview.value = null
    // Refrescar auth store
    if (auth.user) auth.user.avatar = data.avatar
  } catch (e) {
    alert('Error al subir foto: ' + (e.response?.data?.error || 'Intenta de nuevo'))
  }
  uploadingAvatar.value = false
}

async function saveProfile() {
  saving.value = true
  saveSuccess.value = false
  try {
    const { data } = await api.patch('/auth/me/', {
      first_name: form.first_name,
      last_name: form.last_name,
      phone: form.phone,
      city: form.city,
      country: form.country,
      bio: form.bio,
    })
    // Refrescar auth store
    if (auth.user) {
      auth.user.first_name = data.first_name
      auth.user.last_name = data.last_name
    }
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (err) {
    alert('Error al guardar: ' + (err.response?.data?.detail || 'Intenta de nuevo'))
  }
  saving.value = false
}

async function sendPasswordReset() {
  if (!form.email) return
  sendingReset.value = true
  try {
    await api.post('/auth/password-reset/', { email: form.email })
    resetSent.value = true
  } catch {
    alert('No se pudo enviar el email. Intenta de nuevo.')
  }
  sendingReset.value = false
}

function logoutEverywhere() {
  if (!confirm('¿Cerrar todas las sesiones?')) return
  auth.logout()
  router.push('/login')
}

// ── Eliminar cuenta ──
const deleteModal = reactive({
  open: false,
  confirmEmail: '',
  loading: false,
  error: '',
})
const canConfirmDelete = computed(() => {
  return deleteModal.confirmEmail.trim().toLowerCase() === (form.email || '').trim().toLowerCase()
})

function closeDeleteModal() {
  if (deleteModal.loading) return
  deleteModal.open = false
  deleteModal.confirmEmail = ''
  deleteModal.error = ''
}

async function confirmDelete() {
  if (!canConfirmDelete.value) return
  deleteModal.loading = true
  deleteModal.error = ''
  try {
    await api.post('/auth/me/delete/', { confirm_email: deleteModal.confirmEmail })
    auth.logout()
    router.push('/?deleted=1')
  } catch (e) {
    deleteModal.error = e.response?.data?.error || 'No se pudo eliminar la cuenta.'
    deleteModal.loading = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/me/')
    Object.assign(form, {
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      email: data.email || '',
      phone: data.phone || '',
      city: data.city || '',
      country: data.country || '',
      bio: data.bio || '',
      avatar: data.avatar || '',
    })
    // Refresh auth store con los flags nuevos (is_partner_active, partner_offers)
    auth.user = data
    localStorage.setItem('user', JSON.stringify(data))
    syncPartnerFromAuth()
    fetchProductionStatus()
    // Para talent: obtener talent_profile.id para link público
    if (auth.isTalent) {
      try {
        const tp = await api.get('/talents/me/')
        talentProfileId.value = tp.data?.id
      } catch { /* silent */ }
    }
  } catch (err) {
    console.error('Account load error:', err)
  }
})
</script>

<style scoped>
.account-page { padding-top: 100px; padding-bottom: var(--space-12); min-height: 100vh; }

.account-header { margin-bottom: var(--space-8); }
.account-header h1 { font-family: 'Poppins', sans-serif; font-size: 2rem; margin-bottom: var(--space-2); }
.account-sub { color: var(--color-text-muted); font-size: 0.95rem; }

.account-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: var(--space-6);
  align-items: flex-start;
}

.account-sidebar {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: var(--space-3);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  position: sticky;
  top: 100px;
}
.account-tab {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}
.account-tab:hover { background: rgba(255,255,255,0.03); color: var(--color-text-primary); }
.account-tab.active {
  background: rgba(193,216,47,0.08);
  color: var(--color-primary);
}

.account-public-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  margin-top: var(--space-2);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.82rem;
  transition: color var(--transition-fast);
}
.account-public-link:hover { color: var(--color-primary); }

.account-main {
  padding: var(--space-6);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}
.account-section h2 {
  font-size: 1.3rem;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}
.section-sub { color: var(--color-text-muted); margin-bottom: var(--space-4); font-size: 0.9rem; }

.avatar-section {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding-bottom: var(--space-5);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-5);
}
.avatar-wrap {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--color-primary);
  flex-shrink: 0;
}
.account-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-hint {
  margin-top: 6px;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group.full { grid-column: 1 / -1; }
.label {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
}
.input-field {
  padding: 10px 14px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.92rem;
  outline: none;
  font-family: inherit;
}
.input-field:focus { border-color: var(--color-primary); }
.input-field:disabled { opacity: 0.5; cursor: not-allowed; }
.form-note {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
.save-success {
  color: #10b981;
  font-size: 0.88rem;
  font-weight: 500;
}

.danger-block {
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-3);
}
.danger-block strong {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 4px;
  color: var(--color-text-primary);
}
.danger-block p {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
  line-height: 1.5;
}
.btn-danger {
  color: #E85D4A;
  border-color: rgba(232,93,74,0.3) !important;
}
.btn-danger:hover:not(:disabled) {
  background: rgba(232,93,74,0.08);
}

@media (max-width: 768px) {
  .account-layout { grid-template-columns: 1fr; }
  .account-sidebar { position: static; flex-direction: row; overflow-x: auto; }
  .form-grid { grid-template-columns: 1fr; }
}

/* Delete account modal */
.del-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-4);
}
.del-modal {
  width: 100%;
  max-width: 500px;
  padding: var(--space-6);
  background: var(--color-bg-primary);
  border: 1px solid rgba(232,93,74,0.3);
  border-radius: var(--radius-2xl);
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}
.del-modal h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.25rem;
  margin: 0 0 var(--space-3);
  color: #E85D4A;
}
.del-warn {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  padding: 10px 14px;
  background: rgba(232,93,74,0.06);
  border-left: 3px solid #E85D4A;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
}
.del-list {
  margin: 0 0 var(--space-3);
  padding-left: var(--space-5);
  font-size: 0.85rem;
  color: var(--color-text-muted);
  line-height: 1.7;
}
.del-error {
  margin: var(--space-3) 0 0;
  font-size: 0.85rem;
  color: #E85D4A;
}
.del-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-5);
}
.btn-danger-solid {
  background: #E85D4A;
  color: white;
  border: 1px solid #E85D4A;
}
.btn-danger-solid:hover:not(:disabled) {
  background: #d14a37;
  border-color: #d14a37;
}
.btn-danger-solid:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Roles section ── */
.role-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  margin-bottom: var(--space-3);
  transition: all var(--transition-fast);
}
.role-card-on {
  border-color: var(--color-primary);
  background: rgba(193, 216, 47, 0.04);
}
.role-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(193, 216, 47, 0.12);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}
.role-card-icon-primary { background: var(--color-primary); color: var(--color-bg); }
.role-card-icon-partner { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.role-card-info { flex: 1; min-width: 0; }
.role-card-name { color: var(--color-text-primary); font-weight: 700; font-size: 15px; margin-bottom: 4px; }
.role-card-desc { color: var(--color-text-muted); font-size: 13px; line-height: 1.5; }
.role-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.role-status.on { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.role-status.off { background: rgba(140, 140, 140, 0.12); color: var(--color-text-muted); }

.role-toggle {
  width: 44px;
  height: 24px;
  background: var(--color-border);
  border-radius: 999px;
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
  border: none;
  padding: 0;
  transition: background 0.2s;
}
.role-toggle::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: left 0.2s, background 0.2s;
}
.role-toggle.on { background: var(--color-primary); }
.role-toggle.on::after { left: 22px; background: var(--color-bg); }
.role-toggle:disabled { opacity: 0.6; cursor: not-allowed; }

.role-suboptions {
  margin-top: var(--space-3);
  margin-left: 64px;
  padding-left: var(--space-4);
  border-left: 2px solid var(--color-primary);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.role-suboptions-title {
  color: var(--color-primary);
  font-size: 12px;
  margin-bottom: var(--space-1);
  font-weight: 600;
}
.suboption {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-primary);
}
.suboption input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-top: 3px;
  accent-color: var(--color-primary);
}
.suboption-on {
  border-color: rgba(193, 216, 47, 0.4);
  background: rgba(193, 216, 47, 0.05);
}
.suboption-locked { opacity: 0.55; }

.suboption-interactive {
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
  width: 100%;
  transition: all var(--transition-fast);
}
.suboption-interactive:hover {
  border-color: var(--color-primary);
  background: rgba(193, 216, 47, 0.04);
}
.suboption-pending {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.05);
}
.suboption-body { flex: 1; }
.suboption-body strong { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.status-tag.draft    { background: rgba(140,140,140,0.15); color: var(--color-text-muted); }
.status-tag.pending  { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.status-tag.verified { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.status-tag.rejected { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.suboption-desc {
  color: var(--color-text-muted);
  font-size: 12px;
  margin-top: 3px;
  font-weight: 400;
}
.soon-tag {
  background: rgba(193, 216, 47, 0.12);
  color: var(--color-text-muted);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.7em;
  font-weight: 500;
  margin-left: 6px;
  letter-spacing: 0.5px;
}
.role-cta { margin-top: var(--space-2); align-self: flex-start; }
.role-error {
  color: #ef4444;
  font-size: 13px;
  margin-top: var(--space-3);
}
</style>
