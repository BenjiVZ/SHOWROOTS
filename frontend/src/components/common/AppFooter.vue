<template>
  <footer class="app-footer">
    <div class="container footer-inner">
      <div class="footer-brand">
        <div class="footer-logo">
          <span class="footer-logo-text">PULSAR</span>
        </div>
        <p class="footer-desc">La plataforma que conecta talentos musicales con clientes que buscan la mejor experiencia para sus eventos.</p>
      </div>
      <div class="footer-links">
        <div class="footer-col">
          <h4>Explora</h4>
          <router-link to="/search">Buscar Talentos</router-link>
          <!-- Venues — oculto temporalmente -->
          <router-link v-if="false" to="/venues">Venues</router-link>
          <router-link to="/search?talent_type=dj">DJs</router-link>
          <router-link to="/search?talent_type=band">Bandas</router-link>
        </div>
        <div class="footer-col">
          <h4>Cuenta</h4>
          <router-link to="/login">Iniciar Sesión</router-link>
          <router-link to="/register">Registrarse</router-link>
          <router-link to="/dashboard">Dashboard</router-link>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="container footer-bottom-inner">
        <p>&copy; {{ new Date().getFullYear() }} Pulsar — Todos los derechos reservados.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.app-footer {
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-16);
  margin-top: var(--space-16);
  background: var(--color-bg-primary);
}

.footer-inner {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: var(--space-12);
  padding-bottom: var(--space-12);
}

.footer-brand {
  max-width: 360px;
}

.footer-logo {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: var(--space-4);
}

.footer-logo-text {
  font-family: 'Righteous', sans-serif;
  font-size: 1.4rem;
  letter-spacing: 3px;
  color: var(--color-text-primary);
  opacity: 0.85;
}

.footer-logo-sub {
  font-family: 'Poppins', sans-serif;
  font-size: 0.55rem;
  color: var(--color-text-muted);
  letter-spacing: 1px;
  opacity: 0.5;
}

.footer-desc {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  line-height: 1.7;
  font-weight: 300;
}

.footer-links {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-8);
}

.footer-col h4 {
  font-family: var(--font-heading);
  font-size: var(--font-size-base);
  margin-bottom: var(--space-4);
  color: var(--color-text-primary);
}

.footer-col a {
  display: block;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  padding: var(--space-1) 0;
  transition: color var(--transition-fast);
  text-decoration: none;
  cursor: pointer;
}

.footer-col a:hover {
  color: var(--color-primary-light);
}

.footer-bottom {
  border-top: 1px solid var(--color-border);
  padding: var(--space-6) 0;
}

.footer-bottom-inner {
  text-align: center;
}

.footer-bottom p {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .footer-inner {
    grid-template-columns: 1fr;
    gap: var(--space-8);
  }
}
</style>
