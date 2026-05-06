<template>
  <nav class="navbar" :class="{ scrolled: isScrolled, 'navbar--force-dark': forceDarkNav, 'menu-open': menuOpen }">
    <div class="container navbar-inner">
      <router-link to="/" class="logo" aria-label="Pulsar Home">
        <span class="logo-text">PULSAR</span>
        <span class="logo-sub">by ShowRoots</span>
      </router-link>

      <div class="nav-links" :class="{ open: menuOpen }">
        <router-link to="/search" @click="menuOpen = false">
          <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          Talentos
        </router-link>
        <router-link to="/venues" @click="menuOpen = false">
          <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          Venues
        </router-link>

        <template v-if="auth.isLoggedIn">
          <router-link v-if="auth.user?.role === 'admin'" to="/admin" @click="menuOpen = false">
            <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Admin
          </router-link>
          <router-link v-else-if="auth.user?.role === 'partner'" to="/partner" @click="menuOpen = false">
            <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
            Partner
          </router-link>
          <router-link v-else :to="auth.user?.role === 'talent' ? '/talent-dashboard' : '/dashboard'" @click="menuOpen = false">
            <svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            Dashboard
          </router-link>
          <NotificationDropdown />
          <div class="user-menu-wrap">
            <div class="user-pill" @click="showUserMenu = !showUserMenu">
              <span class="user-initial">{{ auth.user?.first_name?.[0] || auth.user?.username?.[0] || '?' }}</span>
              <span class="user-name-nav">{{ auth.user?.first_name || auth.user?.username }}</span>
            </div>
            <div v-if="showUserMenu" class="user-dropdown glass">
              <div class="dropdown-header">
                <strong>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</strong>
                <span class="dropdown-role">{{ auth.roleLabel }}</span>
              </div>
              <router-link to="/dashboard" class="dropdown-item" @click="showUserMenu = false">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                Mi Dashboard
              </router-link>
              <button class="dropdown-item" @click="handleLogout">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                Cerrar Sesión
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-ghost btn-sm" @click="menuOpen = false">Iniciar Sesión</router-link>
          <router-link to="/register" class="btn btn-cta btn-sm" @click="menuOpen = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
            Registrarse
          </router-link>
        </template>
      </div>

      <!-- Theme Toggle -->
      <button class="theme-toggle" @click="themeStore.toggle()" :aria-label="themeStore.isDark() ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'">
        <svg v-if="themeStore.isDark()" class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
        </svg>
      </button>

      <button class="menu-toggle" @click="menuOpen = !menuOpen" aria-label="Toggle menu">
        <span :class="{ active: menuOpen }"></span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import NotificationDropdown from '@/components/common/NotificationDropdown.vue'


const auth = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()
const route = useRoute()
const isScrolled = ref(false)
const menuOpen = ref(false)
// unreadCount moved to NotificationDropdown component
const showUserMenu = ref(false)

// Force dark navbar on talent profile page when global theme is light
// Only while transparent (not scrolled) — once scrolled, revert to light
const forceDarkNav = computed(() => {
  return route.name === 'talent-profile' && !themeStore.isDark() && !isScrolled.value
})

// Lock body scroll when mobile menu is open
watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

function handleLogout() {
  auth.logout()
  menuOpen.value = false
  showUserMenu.value = false
  router.push('/')
}

// Notification fetching now handled by NotificationDropdown component

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Floating Navbar */
.navbar {
  position: fixed;
  top: var(--space-4);
  left: var(--space-4);
  right: var(--space-4);
  z-index: var(--z-sticky);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-2xl);
  transition: all var(--transition-base);
  background: transparent;
  border: 1px solid transparent;
}

.navbar.scrolled {
  background: var(--color-bg-glass);
  backdrop-filter: blur(20px) saturate(1.2);
  -webkit-backdrop-filter: blur(20px) saturate(1.2);
  border-color: var(--color-border);
  box-shadow: var(--shadow-lg);
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: var(--container-max);
  margin: 0 auto;
}

/* Logo */
.logo {
  display: flex;
  align-items: baseline;
  gap: 6px;
  text-decoration: none;
  z-index: 1001;
  transition: all var(--transition-base);
}

.logo-text {
  font-family: 'Righteous', sans-serif;
  font-size: 1.65rem;
  letter-spacing: 3px;
  color: var(--color-text-primary);
  transition: all var(--transition-base);
}

.logo-sub {
  font-family: 'Poppins', sans-serif;
  font-size: 0.6rem;
  color: var(--color-text-muted);
  letter-spacing: 1px;
  opacity: 0.6;
  transition: opacity var(--transition-base);
}

.logo:hover .logo-text {
  color: var(--color-primary);
  text-shadow: 0 0 20px rgba(193, 216, 47, 0.4);
}

.logo:hover .logo-sub {
  opacity: 1;
}

/* Nav Links */
.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.nav-links a:not(.btn) {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.nav-links a:not(.btn):hover,
.nav-links a:not(.btn).router-link-active {
  color: var(--color-primary);
  background: rgba(193, 216, 47, 0.06);
  border-color: var(--color-primary);
}

.nav-links a.router-link-active .nav-icon {
  color: var(--color-primary);
}

.nav-icon {
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}

.nav-links a:hover .nav-icon {
  opacity: 1;
}

/* Notification Bell */
.notif-nav-btn {
  position: relative;
  padding: var(--space-2) !important;
}
.notif-count {
  position: absolute;
  top: 0; right: 0;
  background: var(--color-accent);
  color: white;
  font-size: 10px;
  font-weight: 700;
  width: 16px; height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

/* User Pill */
.user-pill {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3) var(--space-1) var(--space-1);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.user-pill:hover { border-color: var(--color-primary); }
.user-initial {
  width: 28px; height: 28px;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: 700;
}
.user-name-nav {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* User Dropdown */
.user-menu-wrap { position: relative; }
.user-dropdown {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  min-width: 200px;
  border-radius: var(--radius-xl);
  padding: var(--space-2);
  z-index: 100;
}
.dropdown-header {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-1);
}
.dropdown-header strong { display: block; font-size: var(--font-size-sm); }
.dropdown-role { font-size: var(--font-size-xs); color: var(--color-primary); }
.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-decoration: none;
  border: none;
  background: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.dropdown-item:hover {
  background: rgba(193,216,47,0.08);
  color: var(--color-primary);
}

/* Hamburger */
.menu-toggle {
  display: none;
  background: none;
  width: 24px;
  height: 24px;
  position: relative;
  z-index: 1001;
  padding: 0;
  flex-shrink: 0;
}

.menu-toggle span {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--color-text-primary);
  border-radius: 2px;
  transition: all var(--transition-base);
  position: relative;
}

.menu-toggle span::before,
.menu-toggle span::after {
  content: '';
  display: block;
  width: 100%;
  height: 2px;
  background: var(--color-text-primary);
  border-radius: 2px;
  transition: all var(--transition-base);
  position: absolute;
  left: 0;
}

.menu-toggle span::before { top: -7px; }
.menu-toggle span::after { top: 7px; }

.menu-toggle span.active {
  background: transparent;
}
.menu-toggle span.active::before {
  transform: rotate(45deg);
  top: 0;
}
.menu-toggle span.active::after {
  transform: rotate(-45deg);
  top: 0;
}

@media (max-width: 768px) {
  .navbar {
    top: var(--space-2);
    left: var(--space-2);
    right: var(--space-2);
    padding: var(--space-3) var(--space-4);
    transition: all var(--transition-base);
  }

  /* When menu is open, expand navbar to cover entire viewport */
  .navbar.menu-open,
  .navbar.menu-open.scrolled {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 0;
    background: var(--color-bg-primary) !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border-color: transparent !important;
    box-shadow: none !important;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .navbar.menu-open .navbar-inner {
    flex-shrink: 0;
    padding-top: var(--space-2);
  }

  /* Nav links fills the entire expanded navbar and centers content */
  .navbar.menu-open .nav-links.open {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    padding-top: 80px;
  }

  .logo-text {
    font-size: 1.35rem;
    letter-spacing: 2px;
  }

  .logo-sub {
    font-size: 0.5rem;
  }

  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .theme-toggle {
    width: 32px;
    height: 32px;
    margin-left: auto;
    margin-right: var(--space-3);
  }

  .nav-links {
    display: none;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-8);
    flex: 1;
  }

  .nav-links.open {
    display: flex;
  }

  .nav-links a:not(.btn) {
    font-size: var(--font-size-lg);
    padding: var(--space-3) var(--space-5);
    width: 100%;
    max-width: 280px;
    justify-content: center;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
  }

  .nav-links .btn {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }

  .user-menu-wrap {
    width: 100%;
    max-width: 280px;
  }

  .user-pill {
    width: 100%;
    justify-content: center;
    padding: var(--space-3);
  }

  .user-dropdown {
    position: relative;
    top: var(--space-2);
    width: 100%;
  }
}

/* Theme Toggle */
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-left: var(--space-2);
  flex-shrink: 0;
  z-index: 1001;
}

.theme-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: rotate(15deg);
}

.theme-icon {
  transition: transform var(--transition-base);
}

.theme-toggle:active .theme-icon {
  transform: scale(0.85);
}

/* ---- Light Mode Overrides ---- */
[data-theme="light"] .navbar.scrolled {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(0, 0, 0, 0.08);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

[data-theme="light"] .nav-links a:not(.btn):hover,
[data-theme="light"] .nav-links a:not(.btn).router-link-active {
  background: rgba(107, 138, 15, 0.08);
  border-color: var(--color-primary);
}

[data-theme="light"] .user-pill {
  background: #FFFFFF;
}

[data-theme="light"] .dropdown-item:hover {
  background: rgba(107, 138, 15, 0.06);
}

[data-theme="light"] .theme-toggle {
  background: #FFFFFF;
  border-color: rgba(0, 0, 0, 0.1);
}

[data-theme="light"] .logo:hover .logo-text {
  text-shadow: none;
}

/* =============================================
   Force Dark NavBar (Talent Profile in Light Mode)
   ============================================= */
.navbar--force-dark .logo-text {
  color: #FFFFFF;
}
.navbar--force-dark .logo-sub {
  color: rgba(255, 255, 255, 0.5);
}
.navbar--force-dark .logo:hover .logo-text {
  color: #C1D82F;
  text-shadow: 0 0 20px rgba(193, 216, 47, 0.4);
}

.navbar--force-dark .nav-links a:not(.btn) {
  color: rgba(255, 255, 255, 0.8);
}
.navbar--force-dark .nav-links a:not(.btn):hover,
.navbar--force-dark .nav-links a:not(.btn).router-link-active {
  color: #C1D82F;
  background: rgba(193, 216, 47, 0.06);
  border-color: #C1D82F;
}

.navbar--force-dark .user-pill {
  background: rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.2);
}
.navbar--force-dark .user-name-nav {
  color: rgba(255, 255, 255, 0.85);
}

.navbar--force-dark .theme-toggle {
  background: rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
}
.navbar--force-dark .theme-toggle:hover {
  border-color: #C1D82F;
  color: #C1D82F;
}

.navbar--force-dark .btn-ghost {
  color: rgba(255, 255, 255, 0.8);
}
.navbar--force-dark .btn-ghost:hover {
  color: #FFFFFF;
  background: rgba(255, 255, 255, 0.08);
}

.navbar--force-dark .btn-cta {
  color: #0d0d0d;
}

.navbar--force-dark :deep(.notif-bell) {
  color: rgba(255, 255, 255, 0.8);
}
.navbar--force-dark :deep(.notif-bell:hover) {
  color: #C1D82F;
  background: rgba(193, 216, 47, 0.08);
}
.navbar--force-dark :deep(.notif-badge) {
  border-color: transparent;
}

.navbar--force-dark.scrolled {
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(20px) saturate(1.2);
  -webkit-backdrop-filter: blur(20px) saturate(1.2);
  border-color: rgba(193, 216, 47, 0.18);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
}

.navbar--force-dark .menu-toggle span,
.navbar--force-dark .menu-toggle span::before,
.navbar--force-dark .menu-toggle span::after {
  background: #FFFFFF;
}
.navbar--force-dark .menu-toggle span.active {
  background: transparent;
}

.navbar--force-dark .dropdown-header strong {
  color: #FFFFFF;
}
.navbar--force-dark .user-dropdown {
  background: rgba(10, 10, 10, 0.95);
  border-color: rgba(193, 216, 47, 0.18);
}
.navbar--force-dark .dropdown-item {
  color: rgba(255, 255, 255, 0.7);
}
.navbar--force-dark .dropdown-item:hover {
  background: rgba(193, 216, 47, 0.08);
  color: #C1D82F;
}

@media (max-width: 768px) {
  .navbar--force-dark .nav-links {
    background: #000000;
  }

  .navbar--force-dark .menu-toggle span,
  .navbar--force-dark .menu-toggle span::before,
  .navbar--force-dark .menu-toggle span::after {
    background: #FFFFFF;
  }
  .navbar--force-dark .menu-toggle span.active {
    background: transparent;
  }
}
</style>
