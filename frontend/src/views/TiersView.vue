<template>
  <div class="tiers-page">
    <div class="container">
      <!-- Hero -->
      <header class="tiers-hero animate-fade-in-up">
        <span class="hero-tag">Planes para talentos</span>
        <h1>Sube de nivel en <span class="text-accent">Pulsar</span></h1>
        <p class="hero-sub">3 Planes, cada uno con beneficios crecientes. Empiezas como Standard y vas escalando según tu performance.</p>
      </header>

      <!-- Tier cards -->
      <div class="tiers-grid">
        <div v-for="t in tiers" :key="t.key" class="tier-card" :class="`tier-card-${t.key}`">
          <div class="tier-badge">{{ t.badge }}</div>
          <h2 class="tier-name">
            <span v-if="t.stars" class="tier-stars">
              <svg v-for="i in t.stars" :key="i" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            </span>
            {{ t.name }}
          </h2>
          <div class="tier-commission">
            <strong>{{ t.commission }}</strong>
            <span>comisión Pulsar</span>
          </div>
          <p class="tier-access">{{ t.access }}</p>
          <ul class="tier-features">
            <li v-for="f in t.features" :key="f">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              <span>{{ f }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Side-by-side comparison table -->
      <section class="comparison-section">
        <h2>Comparación completa de Planes</h2>
        <div class="comparison-table">
          <!-- Header con los 3 planes -->
          <div class="comp-header">
            <div class="comp-cell comp-header-cell">Categoría</div>
            <div class="comp-cell comp-header-cell comp-h-standard">Standard</div>
            <div class="comp-cell comp-header-cell comp-h-pro">
              <svg class="cell-star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              Pro
            </div>
            <div class="comp-cell comp-header-cell comp-h-premium">
              <svg class="cell-star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <svg class="cell-star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              Premium
            </div>
          </div>

          <div v-for="row in comparisonRows" :key="row.feature" class="comp-row">
            <div class="comp-cell comp-feature">{{ row.feature }}</div>
            <div class="comp-cell">
              <svg v-if="row.standard === false" class="cell-no" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              <span v-else>{{ row.standard }}</span>
            </div>
            <div class="comp-cell">
              <svg v-if="row.pro === false" class="cell-no" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              <span v-else>{{ row.pro }}</span>
            </div>
            <div class="comp-cell">
              <svg v-if="row.premium === false" class="cell-no" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              <span v-else>{{ row.premium }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Progression ladder -->
      <section class="ladder-section">
        <h2>Cómo subir de Plan</h2>
        <div class="ladder">
          <div class="ladder-step">
            <div class="ladder-num std">1</div>
            <div class="ladder-content">
              <strong>STANDARD</strong>
              <p>Aplicas y pasas la evaluación inicial. Comisión 22%.</p>
            </div>
          </div>
          <div class="ladder-arrow">
            <div class="ladder-arrow-line"></div>
            <div class="ladder-arrow-criteria">
              <strong>10+ eventos completados</strong>
              <span>Rating ≥ 4.5</span>
              <span>0 cancelaciones en 6 meses</span>
            </div>
          </div>
          <div class="ladder-step">
            <div class="ladder-num pro">2</div>
            <div class="ladder-content">
              <strong>
                <svg class="ladder-star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                PRO
              </strong>
              <p>Promoción automática. Comisión 15%, prioridad en búsqueda, badge para tus redes.</p>
            </div>
          </div>
          <div class="ladder-arrow">
            <div class="ladder-arrow-line"></div>
            <div class="ladder-arrow-criteria">
              <strong>20+ eventos completados</strong>
              <span>Rating ≥ 4.7</span>
              <span>0 cancelaciones en 6 meses</span>
              <span class="ladder-invite">+ Invitación de Pulsar</span>
            </div>
          </div>
          <div class="ladder-step">
            <div class="ladder-num premium">3</div>
            <div class="ladder-content">
              <strong>
                <svg class="ladder-star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                <svg class="ladder-star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                PREMIUM
              </strong>
              <p>Por invitación de Pulsar. Comisión 12%, slot permanente en home, fotos profesionales, music supervisor.</p>
            </div>
          </div>
        </div>
        <p class="ladder-note">
          <strong>Premium es siempre por invitación.</strong> Preservamos la marca "curado por Pulsar" — nuestro equipo evalúa caso por caso y se reserva el derecho de admisión.
        </p>
      </section>

      <!-- Protections row -->
      <section class="protections">
        <h3>Protecciones en todos los Planes</h3>
        <div class="protections-grid">
          <div class="protection-item">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            <strong>Escrow</strong>
            <span>Pago en custodia 24h post-evento</span>
          </div>
          <div class="protection-item">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
            <strong>Anti-desintermediación</strong>
            <span>Comunicación protegida en chat</span>
          </div>
          <div class="protection-item">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <strong>Reembolso 100%</strong>
            <span>Si el talento no se presenta</span>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="tiers-cta">
        <h2>¿Listo para subir tu carrera?</h2>
        <p>Crea tu perfil hoy y empieza a recibir oportunidades.</p>
        <router-link to="/talent-onboarding" class="btn btn-cta btn-lg">Crear mi perfil artístico</router-link>
      </section>
    </div>
  </div>
</template>

<script setup>
const comparisonRows = [
  { feature: 'Comisión Pulsar', standard: '22%', pro: '15%', premium: '12%' },
  { feature: 'Card en búsqueda', standard: 'Sin badge, "Nuevo"', pro: 'Badge Pro lime', premium: 'Badge dorado + "CURADO POR PULSAR"' },
  { feature: 'Banner del perfil', standard: 'Gradiente default', pro: 'Banner propio + borde lime', premium: 'Foto pro Pulsar + glow dorado' },
  { feature: 'Stats visibles', standard: 'Solo $/hora', pro: 'Eventos + tiempo de respuesta', premium: 'Eventos + respuesta + % repite' },
  { feature: 'Mixes audio', standard: '1-2 máx', pro: 'Hasta 4', premium: 'Ilimitado + mix destacado' },
  { feature: 'Video en vivo', standard: false, pro: '1 clip', premium: 'Hasta 4 + video bio' },
  { feature: 'Bio (caracteres)', standard: '200', pro: '500', premium: 'Ilimitado + video bio' },
  { feature: 'Paquetes de precio', standard: 'Solo tarifa/hora', pro: '1 pack custom', premium: 'Ilimitados + pricing dinámico' },
  { feature: 'Galería', standard: '3-5 fotos', pro: 'Hasta 10', premium: 'Ilimitado + sesión pro gratis' },
  { feature: 'Géneros + Mood + Eventos', standard: 'Solo géneros (3)', pro: 'Géneros + mood', premium: 'Géneros + mood + tipos de evento' },
  { feature: 'Reseñas', standard: 'Sin breakdown', pro: 'Breakdown por dimensión', premium: 'Breakdown + respuesta del DJ' },
  { feature: 'Calendario', standard: 'Disponible / Ocupado', pro: '+ Bloqueo por tipo de evento', premium: '+ Sync Google/Apple Calendar' },
  { feature: 'FAQ', standard: false, pro: 'Hasta 3 preguntas', premium: 'Ilimitadas + Pulsar ayuda a redactar' },
  { feature: 'Lead alerts', standard: 'Soporte email 48h', pro: '24h antes + badge IG + soporte 12h', premium: '48h antes + corporativos + WhatsApp manager' },
  { feature: 'Marketing Pulsar', standard: 'Búsqueda orgánica', pro: 'Prioridad búsqueda + posts ocasionales', premium: 'Slot home + top 3 + kit co-branded + reels mensuales' },
  { feature: 'Soporte humano', standard: '—', pro: '—', premium: 'Music supervisor + 1-on-1 cofounder' },
]

const tiers = [
  {
    key: 'standard',
    name: 'Standard',
    stars: 0,
    badge: 'Entrada',
    commission: '22%',
    access: 'Aplicación + evaluación inicial',
    features: [
      'Búsqueda orgánica',
      'Leads básicos',
      'Hasta 5 fotos en perfil',
      'Hasta 2 mixes',
      'Bio hasta 200 caracteres',
      'Soporte email 48h',
    ],
  },
  {
    key: 'pro',
    name: 'Pro',
    stars: 1,
    badge: 'Promoción automática',
    commission: '15%',
    access: '10+ eventos · Rating ≥ 4.5 · 0 cancelaciones',
    features: [
      'Prioridad en búsqueda',
      'Lead alerts 24h antes',
      'Hasta 10 fotos',
      'Hasta 4 mixes + 1 video',
      'Bio hasta 500 caracteres',
      '1 paquete custom',
      'Hasta 3 FAQs',
      'Badge Pro para tus redes',
      'Soporte 12h',
    ],
  },
  {
    key: 'premium',
    name: 'Premium',
    stars: 2,
    badge: 'Por invitación',
    commission: '12%',
    access: 'Curado por Pulsar — siempre por invitación',
    features: [
      'Slot permanente en home',
      'Top 3 en búsquedas',
      'Lead alerts 48h antes + corporativos',
      'Fotos profesionales gratis',
      'Mixes, fotos y paquetes ilimitados',
      'Hasta 4 videos + video bio',
      'Pricing dinámico (+15% alta temporada)',
      'Respuesta del talento a reseñas',
      'Sync Google/Apple Calendar',
      'Kit marketing co-branded',
      'Music supervisor + 1-on-1 con cofounder',
    ],
  },
]
</script>

<style scoped>
.tiers-page {
  padding-top: 100px;
  padding-bottom: var(--space-16);
  min-height: 100vh;
  background: var(--color-bg-primary);
}

.tiers-hero {
  text-align: center;
  margin-bottom: var(--space-12);
}
.hero-tag {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 999px;
  background: rgba(193,216,47,0.1);
  border: 1px solid rgba(193,216,47,0.3);
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-4);
}
.tiers-hero h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 2.6rem;
  font-weight: 700;
  margin-bottom: var(--space-3);
}
.text-accent { color: var(--color-primary); }
.hero-sub {
  font-size: 1.05rem;
  color: var(--color-text-muted);
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.5;
}

.tiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-12);
  padding-top: var(--space-3);
}
.tier-card {
  position: relative;
  padding: var(--space-6);
  border-radius: var(--radius-2xl);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  transition: border-color var(--transition-base);
}
.tier-card:hover { border-color: var(--color-primary); }
.tier-card-pro { border-color: rgba(193, 216, 47, 0.4); }
.tier-card-premium {
  border-color: rgba(245,158,11,0.5);
  box-shadow: 0 0 0 1px rgba(245,158,11,0.15), 0 16px 48px rgba(245,158,11,0.15);
}
.tier-badge {
  position: absolute;
  top: -10px;
  left: var(--space-5);
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}
.tier-card-pro .tier-badge { color: #C1D82F; border-color: rgba(193, 216, 47, 0.5); }
.tier-card-premium .tier-badge { color: #f59e0b; border-color: rgba(245,158,11,0.6); }
.tier-name {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: var(--space-3);
  margin-top: var(--space-2);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.tier-stars { display: inline-flex; gap: 2px; }
.tier-card-pro .tier-stars { color: #C1D82F; }
.tier-card-premium .tier-stars { color: #f59e0b; }
.ladder-star { flex-shrink: 0; }
.ladder-num.pro + .ladder-content .ladder-star { color: #C1D82F; }
.ladder-num.premium + .ladder-content .ladder-star { color: #f59e0b; }
.tier-commission {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: var(--space-2);
}
.tier-commission strong {
  font-family: 'Poppins', sans-serif;
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--color-primary);
}
.tier-card-pro .tier-commission strong { color: #C1D82F; }
.tier-card-premium .tier-commission strong { color: #f59e0b; }
.tier-commission span { color: var(--color-text-muted); font-size: 0.85rem; }
.tier-access {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}
.tier-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.tier-features li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
}
.tier-features svg {
  flex-shrink: 0;
  margin-top: 3px;
  color: var(--color-primary);
}
.tier-card-pro .tier-features svg { color: #C1D82F; }
.tier-card-premium .tier-features svg { color: #f59e0b; }

/* Side-by-side comparison table */
.comparison-section { margin-bottom: var(--space-12); }
.comparison-section h2 {
  text-align: center;
  font-size: 1.6rem;
  margin-bottom: var(--space-6);
}
.comparison-table {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
}
.comp-header {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  background: var(--color-bg-card);
  border-bottom: 2px solid var(--color-border);
}
.comp-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  border-bottom: 1px solid var(--color-border);
}
.comp-row:last-child { border-bottom: none; }
.comp-row:hover { background: rgba(255,255,255,0.02); }

.comp-cell {
  padding: var(--space-3) var(--space-4);
  font-size: 0.82rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
  border-right: 1px solid var(--color-border);
  display: flex;
  align-items: center;
}
.comp-cell:last-child { border-right: none; }
.comp-feature {
  font-weight: 600;
  color: var(--color-text-primary);
  background: rgba(0,0,0,0.15);
}

.comp-header-cell {
  font-weight: 700;
  font-size: 0.92rem;
  padding: var(--space-4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.comp-h-standard { color: var(--color-text-muted); }
.comp-h-pro { color: #C1D82F; background: rgba(193, 216, 47, 0.05); display: inline-flex; align-items: center; gap: 6px; }
.comp-h-premium { color: #f59e0b; background: rgba(245,158,11,0.05); display: inline-flex; align-items: center; gap: 4px; }
.cell-star { flex-shrink: 0; }
.cell-no {
  color: #E85D4A;
  opacity: 0.85;
}

@media (max-width: 768px) {
  .comp-header, .comp-row { grid-template-columns: 1fr; }
  .comp-cell {
    border-right: none;
    border-bottom: 1px dashed rgba(255,255,255,0.05);
  }
  .comp-cell::before {
    content: attr(data-label);
    font-weight: 700;
    color: var(--color-primary);
    margin-right: 8px;
  }
  .comp-feature { background: var(--color-primary); color: #0a0a0a !important; font-size: 0.95rem; }
}

/* Ladder */
.ladder-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-8) var(--space-6);
  margin-bottom: var(--space-10);
}
.ladder-section h2 {
  text-align: center;
  margin-bottom: var(--space-6);
  font-size: 1.6rem;
}
.ladder {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 640px;
  margin: 0 auto;
}
.ladder-step {
  display: flex;
  gap: var(--space-4);
  align-items: center;
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
}
.ladder-num {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.2rem;
  color: #fff;
}
.ladder-num.std { background: var(--color-text-muted); }
.ladder-num.pro { background: #C1D82F; color: #0a0a0a; }
.ladder-num.premium { background: #f59e0b; color: #0a0a0a; }
.ladder-content strong { display: inline-flex; align-items: center; gap: 6px; font-size: 0.92rem; }
.ladder-content p { margin: 4px 0 0; font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.4; }

.ladder-arrow {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-left: 22px;
}
.ladder-arrow-line {
  width: 2px;
  height: 32px;
  background: var(--color-border);
  position: relative;
}
.ladder-arrow-line::after {
  content: '↓';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  color: var(--color-border);
  font-size: 1.4rem;
}
.ladder-arrow-criteria {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ladder-arrow-criteria strong { color: var(--color-text-primary); margin-bottom: 2px; }
.ladder-invite { color: #f59e0b !important; font-weight: 600; margin-top: 4px; }

.ladder-note {
  margin-top: var(--space-5);
  padding: var(--space-3) var(--space-4);
  background: rgba(245,158,11,0.06);
  border-left: 3px solid #f59e0b;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.ladder-note strong { color: #f59e0b; }

/* Protections */
.protections {
  text-align: center;
  margin-bottom: var(--space-10);
}
.protections h3 {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
  font-weight: 500;
}
.protections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
  max-width: 760px;
  margin: 0 auto;
}
.protection-item {
  padding: var(--space-5);
  background: var(--color-bg-card);
  border: 1px solid rgba(16,185,129,0.2);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}
.protection-item strong {
  font-size: 0.95rem;
  color: var(--color-text-primary);
}
.protection-item span {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

/* CTA */
.tiers-cta {
  text-align: center;
  padding: var(--space-10);
  background: linear-gradient(135deg, rgba(193,216,47,0.1), rgba(193,216,47,0.02));
  border: 1px solid rgba(193,216,47,0.25);
  border-radius: var(--radius-2xl);
}
.tiers-cta h2 {
  font-size: 1.8rem;
  margin-bottom: var(--space-2);
}
.tiers-cta p {
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
}

@media (max-width: 768px) {
  .tiers-hero h1 { font-size: 1.8rem; }
}
</style>
