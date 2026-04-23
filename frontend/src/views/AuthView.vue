<template>
  <div class="auth-view">
    <!-- Animated background -->
    <div class="auth-bg">
      <div class="bg-orb bg-orb-1"></div>
      <div class="bg-orb bg-orb-2"></div>
      <div class="bg-orb bg-orb-3"></div>
    </div>

    <div class="auth-container" :class="{ 'register-mode': isRegister }">
      <!-- Left Panel — Branding -->
      <div class="auth-panel-left">
        <div class="panel-content">
          <div class="panel-logo">
            <span class="panel-logo-text">PULSAR</span>
            <span class="panel-logo-sub">by ShowRoots</span>
          </div>

          <div class="panel-text">
            <transition name="slide-text" mode="out-in">
              <div v-if="!isRegister" key="login-text">
                <h2>Bienvenido de vuelta</h2>
                <p>Accede a tu cuenta y continúa descubriendo el mejor talento musical para tus eventos</p>
              </div>
              <div v-else key="register-text">
                <h2>Únete a la comunidad</h2>
                <p>Crea tu cuenta y conecta con DJs, músicos y bandas de toda la región</p>
              </div>
            </transition>
          </div>

          <div class="panel-features">
            <div class="feature-item">
              <div class="feature-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
              </div>
              <span>Descubre talentos verificados</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </div>
              <span>Reservas seguras y protegidas</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
              </div>
              <span>La mejor experiencia musical</span>
            </div>
          </div>
        </div>

        <!-- Decorative pattern -->
        <div class="panel-pattern">
          <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="none" stroke="rgba(193,216,47,0.1)" stroke-width="0.5"/>
            <circle cx="100" cy="100" r="60" fill="none" stroke="rgba(193,216,47,0.08)" stroke-width="0.5"/>
            <circle cx="100" cy="100" r="40" fill="none" stroke="rgba(193,216,47,0.06)" stroke-width="0.5"/>
          </svg>
        </div>
      </div>

      <!-- Right Panel — Form -->
      <div class="auth-panel-right">
        <div class="form-wrapper">
          <!-- Mode Switcher -->
          <div class="mode-switcher">
            <button
              class="mode-btn"
              :class="{ active: !isRegister }"
              @click="switchMode(false)"
            >
              Iniciar Sesión
            </button>
            <button
              class="mode-btn"
              :class="{ active: isRegister }"
              @click="switchMode(true)"
            >
              Crear Cuenta
            </button>
            <div class="mode-indicator" :class="{ right: isRegister }"></div>
          </div>

          <!-- Form Content -->
          <transition name="form-swap" mode="out-in">
            <!-- LOGIN FORM -->
            <form v-if="!isRegister" key="login" @submit.prevent="handleLogin" class="auth-form">
              <div class="form-fields">
                <div class="input-group full">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    <input
                      id="login-user"
                      v-model="loginForm.username"
                      type="text"
                      class="input-modern"
                      placeholder=" "
                      required
                      autocomplete="username"
                    />
                    <label for="login-user" class="input-label-float">Usuario</label>
                  </div>
                </div>

                <div class="input-group full">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                    <input
                      id="login-pass"
                      v-model="loginForm.password"
                      :type="showPassword ? 'text' : 'password'"
                      class="input-modern"
                      placeholder=" "
                      required
                      autocomplete="current-password"
                    />
                    <label for="login-pass" class="input-label-float">Contraseña</label>
                    <button type="button" class="toggle-pass" @click="showPassword = !showPassword" tabindex="-1">
                      <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                      <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Error Message -->
              <transition name="fade-slide">
                <div v-if="error" class="error-toast">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  {{ error }}
                </div>
              </transition>

              <div class="forgot-link-row">
                <router-link to="/forgot-password" class="forgot-link">¿Olvidaste tu contraseña?</router-link>
              </div>

              <button type="submit" class="btn-submit" :disabled="loading">
                <span v-if="!loading">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
                  Ingresar
                </span>
                <span v-else class="loading-spinner">
                  <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
                  Ingresando...
                </span>
              </button>
            </form>

            <!-- REGISTER FORM -->
            <form v-else key="register" @submit.prevent="handleRegister" class="auth-form">
              <!-- Role Selector -->
              <div class="role-grid">
                <button
                  v-for="r in roles"
                  :key="r.value"
                  type="button"
                  class="role-card"
                  :class="{ active: regForm.role === r.value }"
                  @click="regForm.role = r.value"
                >
                  <div class="role-icon" v-html="r.icon"></div>
                  <span class="role-label">{{ r.label }}</span>
                  <span class="role-desc">{{ r.desc }}</span>
                </button>
              </div>

              <div class="form-fields">
                <!-- Row 1: Nombre + Apellido -->
                <div class="input-group half">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    <input
                      id="reg-fname"
                      v-model="regForm.first_name"
                      type="text"
                      class="input-modern"
                      placeholder=" "
                      required
                    />
                    <label for="reg-fname" class="input-label-float">Nombre</label>
                  </div>
                </div>
                <div class="input-group half">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    <input
                      id="reg-lname"
                      v-model="regForm.last_name"
                      type="text"
                      class="input-modern"
                      placeholder=" "
                      required
                    />
                    <label for="reg-lname" class="input-label-float">Apellido</label>
                  </div>
                </div>

                <!-- Row 2: Usuario + Email -->
                <div class="input-group half">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 006 0v-1a10 10 0 10-3.92 7.94"/></svg>
                    <input
                      id="reg-user"
                      v-model="regForm.username"
                      type="text"
                      class="input-modern"
                      placeholder=" "
                      required
                    />
                    <label for="reg-user" class="input-label-float">Usuario</label>
                  </div>
                </div>
                <div class="input-group half">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                    <input
                      id="reg-email"
                      v-model="regForm.email"
                      type="email"
                      class="input-modern"
                      placeholder=" "
                      required
                    />
                    <label for="reg-email" class="input-label-float">Email</label>
                  </div>
                </div>

                <!-- Row 3: Contraseña (full width) -->
                <div class="input-group full">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                    <input
                      id="reg-pass"
                      v-model="regForm.password"
                      :type="showPassword ? 'text' : 'password'"
                      class="input-modern"
                      placeholder=" "
                      minlength="6"
                      required
                    />
                    <label for="reg-pass" class="input-label-float">Contraseña</label>
                    <button type="button" class="toggle-pass" @click="showPassword = !showPassword" tabindex="-1">
                      <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                      <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                    </button>
                  </div>
                </div>

                <!-- Row 4: Confirmar Contraseña -->
                <div class="input-group full">
                  <div class="input-wrapper">
                    <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                    <input
                      id="reg-pass-confirm"
                      v-model="regForm.password_confirm"
                      :type="showPassword ? 'text' : 'password'"
                      class="input-modern"
                      placeholder=" "
                      minlength="6"
                      required
                    />
                    <label for="reg-pass-confirm" class="input-label-float">Confirmar Contraseña</label>
                  </div>
                </div>
              </div>

              <!-- Error Message -->
              <transition name="fade-slide">
                <div v-if="error" class="error-toast">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  {{ error }}
                </div>
              </transition>

              <button type="submit" class="btn-submit btn-register" :disabled="loading">
                <span v-if="!loading">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
                  Crear Cuenta
                </span>
                <span v-else class="loading-spinner">
                  <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>
                  Registrando...
                </span>
              </button>
            </form>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const isRegister = ref(route.name === 'register')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Login form
const loginForm = ref({ username: '', password: '' })

// Register form
const regForm = ref({
  role: 'client',
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
})

const roles = [
  {
    value: 'client',
    label: 'Cliente',
    desc: 'Busco talento',
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>'
  },
  {
    value: 'talent',
    label: 'Talento',
    desc: 'Soy artista',
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>'
  },
  {
    value: 'partner',
    label: 'Partner',
    desc: 'Soy venue',
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>'
  }
]

function switchMode(toRegister) {
  if (isRegister.value === toRegister) return
  error.value = ''
  showPassword.value = false
  isRegister.value = toRegister
  router.replace(toRegister ? '/register' : '/login')
}

// Sync with route changes (back/forward nav)
watch(() => route.name, (name) => {
  isRegister.value = name === 'register'
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(loginForm.value.username, loginForm.value.password)
    const redirect = route.query.redirect || (
      auth.user?.role === 'admin' ? '/admin' :
      auth.user?.role === 'partner' ? '/partner' :
      auth.user?.role === 'talent' ? '/talent-dashboard' :
      '/dashboard'
    )
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Credenciales incorrectas.'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(regForm.value)
    const role = regForm.value.role
    const dest = role === 'talent' ? '/talent-dashboard' : role === 'partner' ? '/partner' : '/dashboard'
    router.push(dest)
  } catch (err) {
    const data = err.response?.data
    error.value = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Error al registrar.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ========================
   FULL AUTH VIEW
   ======================== */
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background: #000;
  position: relative;
  overflow: hidden;
}

/* Animated Background Orbs */
.auth-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}

.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  animation: orbFloat 20s infinite ease-in-out;
}

.bg-orb-1 {
  width: 500px;
  height: 500px;
  background: rgba(193, 216, 47, 0.15);
  top: -10%;
  left: -10%;
  animation-delay: 0s;
}

.bg-orb-2 {
  width: 400px;
  height: 400px;
  background: rgba(232, 93, 74, 0.1);
  bottom: -10%;
  right: -5%;
  animation-delay: -7s;
  animation-duration: 25s;
}

.bg-orb-3 {
  width: 300px;
  height: 300px;
  background: rgba(193, 216, 47, 0.08);
  top: 50%;
  left: 60%;
  animation-delay: -14s;
  animation-duration: 30s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(40px, -30px) scale(1.1); }
  50% { transform: translate(-20px, 40px) scale(0.95); }
  75% { transform: translate(30px, 20px) scale(1.05); }
}

/* ========================
   CONTAINER
   ======================== */
.auth-container {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  max-width: 1000px;
  min-height: 620px;
  background: rgba(10, 10, 10, 0.7);
  backdrop-filter: blur(40px) saturate(1.3);
  -webkit-backdrop-filter: blur(40px) saturate(1.3);
  border: 1px solid rgba(193, 216, 47, 0.12);
  border-radius: 24px;
  overflow: hidden;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.03),
    0 32px 64px rgba(0,0,0,0.5),
    0 0 120px rgba(193, 216, 47, 0.04);
  transition: all 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

/* ========================
   LEFT PANEL — BRANDING
   ======================== */
.auth-panel-left {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--space-10);
  background: linear-gradient(160deg, rgba(193, 216, 47, 0.06) 0%, rgba(0,0,0,0.4) 60%, rgba(232, 93, 74, 0.04) 100%);
  border-right: 1px solid rgba(193, 216, 47, 0.08);
  overflow: hidden;
}

.panel-content {
  position: relative;
  z-index: 2;
}

.panel-logo {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: var(--space-10);
}

.panel-logo-text {
  font-family: 'Righteous', sans-serif;
  font-size: 2.2rem;
  letter-spacing: 4px;
  color: #fff;
  text-shadow: 0 0 30px rgba(193, 216, 47, 0.3);
}

.panel-logo-sub {
  font-family: 'Poppins', sans-serif;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  letter-spacing: 1px;
  opacity: 0.6;
}

.panel-text {
  margin-bottom: var(--space-10);
}

.panel-text h2 {
  font-family: var(--font-heading);
  font-size: 28px;
  color: var(--color-text-primary);
  margin-bottom: var(--space-4);
  line-height: 1.2;
}

.panel-text p {
  color: var(--color-text-muted);
  font-size: var(--font-size-base);
  line-height: 1.7;
  max-width: 300px;
}

/* Features */
.panel-features {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.feature-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: rgba(193, 216, 47, 0.1);
  color: var(--color-primary);
  flex-shrink: 0;
}

.feature-item span {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 400;
}

/* Decorative Pattern */
.panel-pattern {
  position: absolute;
  bottom: -40px;
  right: -40px;
  width: 220px;
  height: 220px;
  opacity: 0.5;
  z-index: 1;
  animation: patternSpin 60s linear infinite;
}

@keyframes patternSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========================
   RIGHT PANEL — FORM
   ======================== */
.auth-panel-right {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8) var(--space-10);
}

.form-wrapper {
  width: 100%;
  max-width: 420px;
}

/* Mode Switcher */
.mode-switcher {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: var(--radius-xl);
  padding: 4px;
  margin-bottom: var(--space-8);
}

.mode-btn {
  position: relative;
  z-index: 2;
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-sm);
  font-weight: 600;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-lg);
  transition: color 0.35s ease;
}

.mode-btn.active {
  color: #000;
}

.mode-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: var(--color-primary);
  border-radius: var(--radius-lg);
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
  z-index: 1;
}

.mode-indicator.right {
  transform: translateX(100%);
}

/* ========================
   FORM
   ======================== */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.form-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.input-group.full {
  grid-column: 1 / -1;
}

.input-group.half {
  grid-column: span 1;
}

/* Modern Input */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  color: var(--color-text-muted);
  pointer-events: none;
  transition: color 0.3s;
  z-index: 2;
}

.input-modern {
  width: 100%;
  padding: 16px 16px 16px 46px;
  background: rgba(255,255,255,0.04);
  border: 1.5px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-body);
  transition: all 0.3s ease;
  outline: none;
}

.input-modern:focus {
  border-color: var(--color-primary);
  background: rgba(193, 216, 47, 0.04);
  box-shadow: 0 0 0 3px rgba(193, 216, 47, 0.1);
}

.input-modern:focus ~ .input-icon,
.input-modern:not(:placeholder-shown) ~ .input-icon {
  color: var(--color-primary);
}

/* Floating Label */
.input-label-float {
  position: absolute;
  left: 46px;
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  pointer-events: none;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  background: transparent;
  padding: 0 4px;
}

.input-modern:focus ~ .input-label-float,
.input-modern:not(:placeholder-shown) ~ .input-label-float {
  top: 0;
  left: 40px;
  font-size: 11px;
  color: var(--color-primary);
  background: rgba(10, 10, 10, 0.9);
  padding: 0 6px;
}

/* Eye toggle */
.toggle-pass {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.3s;
}

.toggle-pass:hover {
  color: var(--color-primary);
}

/* ========================
   ROLE SELECTOR
   ======================== */
.role-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.role-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: var(--space-4) var(--space-2);
  background: rgba(255,255,255,0.03);
  border: 1.5px solid rgba(255,255,255,0.06);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.role-card:hover {
  border-color: rgba(193, 216, 47, 0.3);
  background: rgba(193, 216, 47, 0.04);
}

.role-card.active {
  border-color: var(--color-primary);
  background: rgba(193, 216, 47, 0.08);
  box-shadow: 0 0 20px rgba(193, 216, 47, 0.1);
}

.role-icon {
  color: var(--color-text-muted);
  transition: color 0.3s;
}

.role-card.active .role-icon {
  color: var(--color-primary);
}

.role-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  transition: color 0.3s;
}

.role-card.active .role-label {
  color: var(--color-primary);
}

.role-desc {
  font-size: 11px;
  color: var(--color-text-muted);
  line-height: 1.3;
}

/* ========================
   SUBMIT BUTTON
   ======================== */
.btn-submit {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: var(--radius-lg);
  background: var(--gradient-primary);
  color: #000;
  font-size: var(--font-size-base);
  font-weight: 700;
  font-family: var(--font-body);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-submit span {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(193, 216, 47, 0.3);
}

.btn-submit:active:not(:disabled) {
  transform: translateY(0);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-submit.btn-register {
  background: var(--color-primary);
  color: #0d0d0d;
}

.loading-spinner {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

@keyframes spinAnim {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spinAnim 1s linear infinite;
}

/* ========================
   ERROR TOAST
   ======================== */
.error-toast {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(232, 93, 74, 0.12);
  border: 1px solid rgba(232, 93, 74, 0.3);
  border-radius: var(--radius-md);
  color: #ff7b6b;
  font-size: var(--font-size-sm);
}

/* ========================
   TRANSITIONS
   ======================== */
/* Form swap */
.form-swap-enter-active,
.form-swap-leave-active {
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.form-swap-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.form-swap-leave-to {
  opacity: 0;
  transform: translateY(-16px);
}

/* Panel text */
.slide-text-enter-active,
.slide-text-leave-active {
  transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.slide-text-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-text-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* Error fade */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ========================
   MOBILE RESPONSIVE
   ======================== */
@media (max-width: 768px) {
  .auth-view {
    padding: 0;
    align-items: flex-start;
  }

  .auth-container {
    grid-template-columns: 1fr;
    border-radius: 0;
    min-height: 100vh;
    max-width: 100%;
    border: none;
  }

  .auth-panel-left {
    display: none;
  }

  .auth-panel-right {
    padding: var(--space-6);
    padding-top: calc(80px + var(--space-6));
    min-height: 100vh;
    align-items: flex-start;
  }

  .form-fields {
    grid-template-columns: 1fr;
  }

  .input-group.half {
    grid-column: 1 / -1;
  }

  .role-grid {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }

  .role-card {
    flex-direction: row;
    text-align: left;
    padding: var(--space-3) var(--space-4);
  }

  .role-desc {
    display: none;
  }
}

@media (max-width: 480px) {
  .auth-panel-right {
    padding: var(--space-4);
    padding-top: calc(80px + var(--space-4));
  }

  .form-wrapper {
    max-width: 100%;
  }
}

.forgot-link-row {
  text-align: right;
}
.forgot-link {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  opacity: 0.8;
  transition: opacity var(--transition-fast);
}
.forgot-link:hover { opacity: 1; text-decoration: underline; }
</style>
