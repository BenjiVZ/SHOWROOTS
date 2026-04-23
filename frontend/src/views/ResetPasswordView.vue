<template>
  <div class="auth-view">
    <div class="auth-bg">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
    </div>

    <div class="reset-container animate-fade-in-up">
      <div class="reset-card glass">
        <div class="reset-header">
          <div class="lock-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
          </div>
          <h1>Nueva Contraseña</h1>
          <p>Ingresa tu nueva contraseña para restablecer tu acceso.</p>
        </div>

        <form v-if="!success" @submit.prevent="handleReset" class="reset-form">
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
            <input
              v-model="newPassword"
              :type="showPass ? 'text' : 'password'"
              class="input-modern"
              placeholder=" "
              minlength="6"
              required
            />
            <label class="input-label-float">Nueva Contraseña</label>
            <button type="button" class="toggle-pass" @click="showPass = !showPass" tabindex="-1">
              <svg v-if="!showPass" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>

          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
            <input
              v-model="confirmPassword"
              :type="showPass ? 'text' : 'password'"
              class="input-modern"
              placeholder=" "
              minlength="6"
              required
            />
            <label class="input-label-float">Confirmar Contraseña</label>
          </div>

          <div v-if="error" class="error-toast">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            {{ error }}
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="!loading">Restablecer Contraseña</span>
            <span v-else class="loading-spinner">
              <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
              Procesando...
            </span>
          </button>
        </form>

        <!-- Success -->
        <div v-else class="success-state">
          <div class="success-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h3>¡Contraseña Restablecida!</h3>
          <p>Ya puedes iniciar sesión con tu nueva contraseña.</p>
          <router-link to="/login" class="btn btn-primary" style="margin-top:16px">Iniciar Sesión</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()

const newPassword = ref('')
const confirmPassword = ref('')
const showPass = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleReset() {
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await api.post('/auth/password-reset/confirm/', {
      uid: route.query.uid,
      token: route.query.token,
      new_password: newPassword.value,
      new_password_confirm: confirmPassword.value,
    })
    success.value = true
  } catch (e) {
    const data = e.response?.data
    if (data?.detail) error.value = data.detail
    else error.value = 'El enlace ha expirado o es inválido.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.auth-bg { position: absolute; inset: 0; z-index: 0; }
.bg-orb {
  position: absolute; border-radius: 50%;
  filter: blur(100px); animation: float 8s ease-in-out infinite;
}
.bg-orb-1 { width: 400px; height: 400px; background: rgba(193,216,47,0.08); top: -100px; right: -100px; }
.bg-orb-2 { width: 350px; height: 350px; background: rgba(232,93,74,0.06); bottom: -100px; left: -100px; animation-delay: -4s; }
@keyframes float { 0%,100% { transform: translate(0,0); } 50% { transform: translate(30px,-30px); } }

.reset-container { position: relative; z-index: 1; width: 100%; max-width: 440px; padding: var(--space-6); }
.reset-card { padding: var(--space-8); border-radius: var(--radius-2xl); }

.reset-header { text-align: center; margin-bottom: var(--space-8); }
.lock-icon {
  width: 60px; height: 60px; border-radius: 50%;
  background: var(--color-primary-ultra-light); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto var(--space-4);
}
.reset-header h1 { font-size: var(--font-size-xl); margin-bottom: var(--space-2); }
.reset-header p { color: var(--color-text-muted); font-size: var(--font-size-sm); }

.reset-form { display: flex; flex-direction: column; gap: var(--space-5); }

.input-wrapper { position: relative; }
.input-icon {
  position: absolute; left: var(--space-4); top: 50%; transform: translateY(-50%);
  color: var(--color-text-muted); pointer-events: none; z-index: 1; transition: color var(--transition-fast);
}
.input-modern {
  width: 100%; padding: 18px 44px 6px 44px;
  background: var(--color-bg-elevated); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); font-size: var(--font-size-base);
  color: var(--color-text-primary); font-family: var(--font-body); transition: all var(--transition-fast);
}
.input-modern:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--color-primary-ultra-light); }
.input-modern:focus ~ .input-icon { color: var(--color-primary); }
.input-label-float {
  position: absolute; left: 44px; top: 50%; transform: translateY(-50%);
  color: var(--color-text-muted); font-size: var(--font-size-sm); pointer-events: none; transition: all var(--transition-fast);
}
.input-modern:focus ~ .input-label-float,
.input-modern:not(:placeholder-shown) ~ .input-label-float {
  top: 10px; font-size: 10px; color: var(--color-primary);
}

.toggle-pass {
  position: absolute; right: var(--space-4); top: 50%; transform: translateY(-50%);
  background: none; border: none; color: var(--color-text-muted); cursor: pointer; padding: var(--space-2);
}
.toggle-pass:hover { color: var(--color-primary); }

.error-toast {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(232,93,74,0.1); color: var(--color-accent);
  border-radius: var(--radius-lg); font-size: var(--font-size-sm);
}

.btn-submit {
  width: 100%; padding: var(--space-4);
  border-radius: var(--radius-lg); background: var(--color-primary);
  color: var(--color-bg-primary); font-weight: 700; font-size: var(--font-size-base);
  border: none; cursor: pointer; font-family: var(--font-body); transition: all var(--transition-fast);
}
.btn-submit:hover { background: var(--color-primary-light); transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-submit span { display: flex; align-items: center; justify-content: center; gap: var(--space-2); }

.loading-spinner { display: flex; align-items: center; justify-content: center; gap: var(--space-2); }
.spin { animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.success-state { text-align: center; }
.success-icon { color: var(--color-primary); margin-bottom: var(--space-4); }
.success-state h3 { margin-bottom: var(--space-3); }
.success-state p { color: var(--color-text-muted); }
</style>
