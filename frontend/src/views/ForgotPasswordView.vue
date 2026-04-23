<template>
  <div class="auth-view">
    <div class="auth-bg">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
    </div>

    <div class="forgot-container animate-fade-in-up">
      <div class="forgot-card glass">
        <router-link to="/login" class="back-link">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          Volver al login
        </router-link>

        <div class="forgot-header">
          <div class="lock-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0110 0v4"/>
            </svg>
          </div>
          <h1>¿Olvidaste tu contraseña?</h1>
          <p>Ingresa tu email y te enviaremos instrucciones para restablecerla.</p>
        </div>

        <form v-if="!sent" @submit.prevent="handleSubmit" class="forgot-form">
          <div class="input-wrapper">
            <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
            <input
              v-model="email"
              type="email"
              class="input-modern"
              placeholder=" "
              required
              autocomplete="email"
            />
            <label class="input-label-float">Correo Electrónico</label>
          </div>

          <div v-if="error" class="error-toast">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            {{ error }}
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="!loading">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
              Enviar Instrucciones
            </span>
            <span v-else class="loading-spinner">
              <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
              Enviando...
            </span>
          </button>
        </form>

        <!-- Success State -->
        <div v-else class="success-state">
          <div class="success-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h3>¡Instrucciones Enviadas!</h3>
          <p>Revisa tu bandeja de entrada en <strong>{{ email }}</strong></p>

          <!-- Dev mode: show reset link -->
          <div v-if="devResetUrl" class="dev-link glass">
            <span class="dev-badge">🔧 Dev Only</span>
            <router-link :to="devResetUrl" class="btn btn-primary" style="margin-top:8px">
              Ir al Link de Reset →
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)
const devResetUrl = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/password-reset/', { email: email.value })
    sent.value = true
    // Dev mode: show direct link
    if (data.reset_url) {
      devResetUrl.value = data.reset_url
    }
  } catch (e) {
    const detail = e.response?.data
    if (detail?.email) error.value = detail.email[0] || detail.email
    else error.value = 'Error al enviar. Verifica tu email.'
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

.auth-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  animation: float 8s ease-in-out infinite;
}
.bg-orb-1 {
  width: 400px; height: 400px;
  background: rgba(193, 216, 47, 0.08);
  top: -100px; right: -100px;
}
.bg-orb-2 {
  width: 350px; height: 350px;
  background: rgba(232, 93, 74, 0.06);
  bottom: -100px; left: -100px;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
}

.forgot-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
  padding: var(--space-6);
}

.forgot-card {
  padding: var(--space-8);
  border-radius: var(--radius-2xl);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--color-primary); }

.forgot-header {
  text-align: center;
  margin-bottom: var(--space-8);
}
.lock-icon {
  width: 60px; height: 60px;
  border-radius: 50%;
  background: var(--color-primary-ultra-light);
  color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto var(--space-4);
}
.forgot-header h1 { font-size: var(--font-size-xl); margin-bottom: var(--space-2); }
.forgot-header p { color: var(--color-text-muted); font-size: var(--font-size-sm); }

.forgot-form { display: flex; flex-direction: column; gap: var(--space-5); }

/* Reuse AuthView input styles */
.input-wrapper {
  position: relative;
}
.input-icon {
  position: absolute;
  left: var(--space-4);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
  z-index: 1;
  transition: color var(--transition-fast);
}
.input-modern {
  width: 100%;
  padding: 18px 16px 6px 44px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  font-family: var(--font-body);
  transition: all var(--transition-fast);
}
.input-modern:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-ultra-light);
}
.input-modern:focus ~ .input-icon { color: var(--color-primary); }
.input-label-float {
  position: absolute;
  left: 44px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  pointer-events: none;
  transition: all var(--transition-fast);
}
.input-modern:focus ~ .input-label-float,
.input-modern:not(:placeholder-shown) ~ .input-label-float {
  top: 10px;
  font-size: 10px;
  color: var(--color-primary);
}

.error-toast {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(232,93,74,0.1);
  color: var(--color-accent);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
}

.btn-submit {
  width: 100%;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--color-primary);
  color: var(--color-bg-primary);
  font-weight: 700;
  font-size: var(--font-size-base);
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
  transition: all var(--transition-fast);
}
.btn-submit:hover { background: var(--color-primary-light); transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.btn-submit span { display: flex; align-items: center; justify-content: center; gap: var(--space-2); }

.loading-spinner { display: flex; align-items: center; justify-content: center; gap: var(--space-2); }
.spin { animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Success State */
.success-state { text-align: center; }
.success-icon {
  color: var(--color-primary);
  margin-bottom: var(--space-4);
}
.success-state h3 { margin-bottom: var(--space-3); }
.success-state p { color: var(--color-text-muted); font-size: var(--font-size-sm); }

.dev-link {
  margin-top: var(--space-6);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  text-align: center;
}
.dev-badge {
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  font-weight: 700;
}
</style>
