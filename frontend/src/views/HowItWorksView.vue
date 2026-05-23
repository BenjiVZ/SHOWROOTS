<template>
  <div class="hiw-page">
    <div class="container">
      <header class="hiw-hero animate-fade-in-up">
        <span class="hero-tag">🛡 Cómo funciona Pulsar</span>
        <h1>Reserva sin sorpresas. <span class="text-accent">Pagas, queda en custodia, llega.</span></h1>
        <p class="hero-sub">Pulsar es un marketplace curado de DJs, músicos y bandas en Panamá. Tu pago está protegido hasta 24h después del evento.</p>
      </header>

      <!-- Para clientes -->
      <section class="hiw-section">
        <h2>Si vas a contratar un talento</h2>
        <div class="hiw-steps">
          <div v-for="(step, i) in clientSteps" :key="i" class="hiw-step">
            <div class="hiw-num">{{ i + 1 }}</div>
            <div>
              <strong>{{ step.title }}</strong>
              <p>{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Escrow -->
      <section class="hiw-escrow">
        <div class="escrow-hero">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <h3>Tu pago está en custodia, no en manos del talento</h3>
          <p>Pulsar retiene el dinero. Solo lo libera 24h después de que el evento se realiza con éxito.</p>
        </div>
        <div class="escrow-timeline">
          <div class="escrow-stage">
            <div class="es-icon">💳</div>
            <strong>Hoy</strong>
            <span>Pagás a Pulsar. No al talento directamente.</span>
          </div>
          <div class="escrow-arrow">→</div>
          <div class="escrow-stage">
            <div class="es-icon">🛡</div>
            <strong>En custodia</strong>
            <span>El dinero queda retenido hasta el día del evento.</span>
          </div>
          <div class="escrow-arrow">→</div>
          <div class="escrow-stage">
            <div class="es-icon">✓</div>
            <strong>24h post-evento</strong>
            <span>Si todo salió bien, se libera el pago. Si no, reembolso 100%.</span>
          </div>
        </div>
      </section>

      <!-- Para talentos -->
      <section class="hiw-section">
        <h2>Si eres un DJ, músico o banda</h2>
        <div class="hiw-steps">
          <div v-for="(step, i) in talentSteps" :key="i" class="hiw-step">
            <div class="hiw-num talent-num">{{ i + 1 }}</div>
            <div>
              <strong>{{ step.title }}</strong>
              <p>{{ step.desc }}</p>
            </div>
          </div>
        </div>
        <div class="hiw-section-cta">
          <router-link to="/talent-onboarding" class="btn btn-cta btn-lg">Crear mi perfil artístico</router-link>
          <router-link to="/tiers" class="btn btn-ghost">Ver Planes y comisiones</router-link>
        </div>
      </section>

      <!-- FAQs -->
      <section class="hiw-faqs">
        <h2>Preguntas frecuentes</h2>
        <div class="faq-list">
          <details v-for="f in faqs" :key="f.q" class="faq-row">
            <summary>{{ f.q }}</summary>
            <p>{{ f.a }}</p>
          </details>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
const clientSteps = [
  { title: 'Buscas y eliges talento', desc: 'Filtras por género, ubicación, presupuesto, idiomas y mood. Cada perfil tiene mixes, fotos y reseñas verificadas.' },
  { title: 'Envías tu solicitud', desc: 'Gratis y sin compromiso. Cuentas tu evento: fecha, lugar, invitados, vibe deseado.' },
  { title: 'El talento te envía propuesta', desc: 'En máximo 48 horas. Te dice precio final, qué incluye, qué no.' },
  { title: 'Pagas a Pulsar (escrow)', desc: 'Con tarjeta, ACH o Yappy. El dinero queda en custodia, no llega al talento aún.' },
  { title: 'Coordinas por chat in-app', desc: 'Listas de canciones, setup, llegada. Todo queda registrado.' },
  { title: 'Día del evento → reseña', desc: 'El talento toca. Si todo bien, dejas tu reseña y se libera el pago. Ganas $50 crédito Pulsar.' },
]

const talentSteps = [
  { title: 'Aplicas y completas tu perfil', desc: 'Wizard de 10 pasos: tipo, géneros, fotos, ubicación, experiencia, tarifa, bio.' },
  { title: 'Pulsar evalúa y aprueba', desc: 'Revisamos calidad de portfolio y referencias. Te aprobamos en Standard tier.' },
  { title: 'Recibes solicitudes', desc: 'Llegan al panel. Tienes 48h para aceptar, ajustar precio o rechazar.' },
  { title: 'Aceptas → cliente paga → confirmas', desc: 'Una vez el cliente pague a Pulsar, tu fecha queda bloqueada.' },
  { title: 'Tocas el evento', desc: 'Coordina con el cliente por chat in-app. Llega puntual, deja huella.' },
  { title: 'Recibes tu payout', desc: '24h después del evento, Pulsar te transfiere el neto (precio menos comisión). Vas escalando tier con cada gig.' },
]

const faqs = [
  { q: '¿Qué pasa si el talento no se presenta?', a: 'Reembolso 100% al cliente. Sancionamos al talento. Es exactamente para evitar esto que existe el escrow.' },
  { q: '¿Puedo contactar al talento directamente?', a: 'No. Toda comunicación va por el chat in-app de Pulsar, incluyendo intercambio de detalles. Si compartes contactos directos, el sistema te bloquea el mensaje.' },
  { q: '¿Cuánto cobra Pulsar?', a: 'Comisión 22% (Standard), 15% (Pro), 12% (Premium). El cliente paga un fee de gestión 5% + ITBMS 7% del total.' },
  { q: '¿Cuándo cobra el talento?', a: '24 horas después del evento, una vez liberamos el pago de custodia. Si hay disputa, se retiene hasta resolver.' },
  { q: '¿Puedo modificar mi reserva?', a: 'Sí, hasta 48 horas antes. El talento debe re-confirmar la nueva fecha.' },
  { q: '¿Política de cancelación?', a: 'Más de 7 días antes: 100% reembolso. Entre 2 y 7 días: 50%. Menos de 48h: sin reembolso.' },
]
</script>

<style scoped>
.hiw-page { padding-top: 100px; padding-bottom: var(--space-16); min-height: 100vh; }

.hiw-hero { text-align: center; margin-bottom: var(--space-12); }
.hero-tag {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 999px;
  background: rgba(16,185,129,0.1);
  border: 1px solid rgba(16,185,129,0.3);
  color: #10b981;
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: var(--space-4);
}
.hiw-hero h1 { font-family: 'Poppins', sans-serif; font-size: 2.4rem; margin-bottom: var(--space-3); }
.text-accent { color: var(--color-primary); }
.hero-sub { font-size: 1.05rem; color: var(--color-text-muted); max-width: 600px; margin: 0 auto; line-height: 1.5; }

.hiw-section { margin-bottom: var(--space-12); }
.hiw-section h2 {
  font-size: 1.6rem;
  margin-bottom: var(--space-6);
  text-align: center;
}
.hiw-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
  max-width: 980px;
  margin: 0 auto;
}
.hiw-step {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}
.hiw-num {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(193,216,47,0.15);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.hiw-num.talent-num { background: rgba(193, 216, 47, 0.15); color: #C1D82F; }
.hiw-step strong {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 4px;
  color: var(--color-text-primary);
}
.hiw-step p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}

.hiw-section-cta {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-6);
  flex-wrap: wrap;
}

/* Escrow timeline */
.hiw-escrow {
  background: linear-gradient(135deg, rgba(16,185,129,0.06), rgba(16,185,129,0.02));
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: var(--radius-2xl);
  padding: var(--space-8) var(--space-6);
  margin-bottom: var(--space-12);
}
.escrow-hero {
  text-align: center;
  margin-bottom: var(--space-6);
}
.escrow-hero h3 {
  font-size: 1.4rem;
  margin: var(--space-3) 0 var(--space-2);
  color: var(--color-text-primary);
}
.escrow-hero p {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}
.escrow-timeline {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}
.escrow-stage {
  flex: 1;
  min-width: 200px;
  max-width: 240px;
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  text-align: center;
}
.es-icon { font-size: 1.8rem; margin-bottom: var(--space-2); }
.escrow-stage strong {
  display: block;
  color: #10b981;
  margin-bottom: 6px;
  font-size: 0.95rem;
}
.escrow-stage span {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}
.escrow-arrow {
  display: flex;
  align-items: center;
  color: #10b981;
  font-size: 1.4rem;
  font-weight: 700;
}

/* FAQs */
.hiw-faqs h2 { font-size: 1.6rem; text-align: center; margin-bottom: var(--space-6); }
.faq-list {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.faq-row {
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}
.faq-row[open] { border-color: var(--color-primary); }
.faq-row summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--color-text-primary);
  list-style: none;
}
.faq-row summary::-webkit-details-marker { display: none; }
.faq-row summary::after {
  content: '+';
  float: right;
  font-size: 1.4rem;
  color: var(--color-primary);
  line-height: 1;
}
.faq-row[open] summary::after { content: '−'; }
.faq-row p {
  margin: var(--space-3) 0 0;
  font-size: 0.88rem;
  color: var(--color-text-muted);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .escrow-arrow { display: none; }
  .escrow-stage { max-width: 100%; }
}
</style>
