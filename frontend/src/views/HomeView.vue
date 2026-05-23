<template>
  <div class="home-page">
    <!-- HERO SECTION -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-orb hero-orb-1"></div>
        <div class="hero-orb hero-orb-2"></div>
        <div class="hero-orb hero-orb-3"></div>
      </div>
      <div class="container hero-content">
        <div class="hero-badge animate-fade-in-up">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          La plataforma #1 de talentos musicales
        </div>
        <h1 class="animate-fade-in-up" style="animation-delay: 0.1s">
          Encuentra el<br>
          <span class="hero-highlight">
            <span class="hero-highlight-glow"></span>
            <span class="text-gradient hero-shimmer">talento perfecto</span>
          </span>
          <br>para tu evento
        </h1>
        <p class="hero-subtitle animate-fade-in-up" style="animation-delay: 0.2s">
          Conectamos DJs, músicos y bandas con personas que buscan la mejor experiencia musical.
        </p>

        <!-- Search Bar — Primary CTA -->
        <div class="hero-search glass animate-fade-in-up" style="animation-delay: 0.3s">
          <div class="search-field">
            <label>Tipo de talento</label>
            <select v-model="searchType" class="input-field">
              <option value="">Todos</option>
              <option value="dj">DJ</option>
              <option value="musician">Músico</option>
              <option value="band">Banda</option>
            </select>
          </div>
          <div class="search-field">
            <label>Ciudad</label>
            <input v-model="searchCity" type="text" class="input-field" placeholder="Ej: Panamá" />
          </div>
          <div class="search-field hide-mobile">
            <label>Género musical</label>
            <select v-model="searchGenre" class="input-field">
              <option value="">Todos</option>
              <option v-for="g in genres" :key="g.id" :value="g.slug">{{ g.name }}</option>
            </select>
          </div>
          <button class="btn btn-cta btn-lg search-btn" @click="doSearch">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            Buscar
          </button>
        </div>

        <!-- Stats -->
        <div class="hero-stats animate-fade-in-up" style="animation-delay: 0.4s">
          <div class="stat">
            <strong>{{ stats.total_talents || '—' }}</strong>
            <span>Talentos</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <strong>{{ stats.total_genres || '—' }}</strong>
            <span>Géneros</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <strong>{{ stats.total_bookings || '—' }}</strong>
            <span>Eventos</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CATEGORIES — Large block cards -->
    <section class="section categories-section">
      <div class="container">
        <h2 class="section-title text-center">Explora por categoría</h2>
        <p class="section-subtitle text-center mx-auto">Encuentra el artista ideal para cada ocasión</p>
        <div class="categories-grid">
          <router-link to="/search?talent_type=dj" class="category-card">
            <div class="category-icon-wrap">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 18v-6a9 9 0 0118 0v6"/><path d="M21 19a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3a2 2 0 012-2h3zM3 19a2 2 0 002 2h1a2 2 0 002-2v-3a2 2 0 00-2-2H3z"/>
              </svg>
            </div>
            <h3>DJs</h3>
            <p>{{ stats.total_djs || 0 }} disponibles</p>
            <span class="category-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </router-link>
          <router-link to="/search?talent_type=musician" class="category-card">
            <div class="category-icon-wrap">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
              </svg>
            </div>
            <h3>Músicos</h3>
            <p>{{ stats.total_musicians || 0 }} disponibles</p>
            <span class="category-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </router-link>
          <router-link to="/search?talent_type=band" class="category-card">
            <div class="category-icon-wrap">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
              </svg>
            </div>
            <h3>Bandas</h3>
            <p>{{ stats.total_bands || 0 }} disponibles</p>
            <span class="category-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- FEATURED TALENTS -->
    <section class="section featured-section">
      <div class="container">
        <div class="section-header">
          <div>
            <h2 class="section-title">Talentos <span class="text-gradient">Destacados</span></h2>
            <p class="section-subtitle">Los artistas mejor valorados de la plataforma</p>
          </div>
          <router-link to="/search" class="btn btn-outline">
            Ver todos
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </router-link>
        </div>
        <div class="talents-grid" v-if="featured.length">
          <TalentCard v-for="talent in featured" :key="talent.id" :talent="talent" />
        </div>
        <div v-else class="empty-state">
          <div class="skeleton" style="height:280px;border-radius:var(--radius-xl);"></div>
        </div>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section class="section how-section">
      <div class="container">
        <h2 class="section-title text-center">Cómo <span class="text-gradient-cta">funciona</span></h2>
        <p class="section-subtitle text-center mx-auto">Reserva tu talento en 3 simples pasos</p>
        <div class="steps-grid">
          <div class="step-card glass">
            <div class="step-number">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            </div>
            <h3>Explora</h3>
            <p>Busca entre cientos de DJs, músicos y bandas. Filtra por género, ciudad y presupuesto.</p>
          </div>
          <div class="step-connector">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </div>
          <div class="step-card glass">
            <div class="step-number step-number-accent">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </div>
            <h3>Cotiza</h3>
            <p>Envía los detalles de tu evento y recibe una cotización personalizada del talento.</p>
          </div>
          <div class="step-connector">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" opacity="0.3"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </div>
          <div class="step-card glass">
            <div class="step-number step-number-green">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            </div>
            <h3>Disfruta</h3>
            <p>Confirma la reserva y disfruta de música profesional en tu evento.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="section cta-section">
      <div class="container">
        <div class="cta-card">
          <div class="cta-glow"></div>
          <div class="cta-content">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--color-primary); margin-bottom: var(--space-4);">
              <path d="M3 18v-6a9 9 0 0118 0v6"/><path d="M21 19a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3a2 2 0 012-2h3zM3 19a2 2 0 002 2h1a2 2 0 002-2v-3a2 2 0 00-2-2H3z"/>
            </svg>
            <h2>¿Eres DJ, músico o banda?</h2>
            <p>Únete a Pulsar y conecta con miles de clientes buscando talento como el tuyo.</p>
            <router-link to="/register" class="btn btn-cta btn-lg">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
              Registrarme como Talento
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import TalentCard from '@/components/talent/TalentCard.vue'

const router = useRouter()
const genres = ref([])
const featured = ref([])
const stats = ref({})

const searchType = ref('')
const searchCity = ref('')
const searchGenre = ref('')

function doSearch() {
  const query = {}
  if (searchType.value) query.talent_type = searchType.value
  if (searchCity.value) query.city = searchCity.value
  if (searchGenre.value) query.genre = searchGenre.value
  router.push({ name: 'search', query })
}

onMounted(async () => {
  try {
    const [genresRes, featuredRes, statsRes] = await Promise.all([
      api.get('/genres/'),
      api.get('/featured/'),
      api.get('/stats/'),
    ])
    genres.value = genresRes.data
    featured.value = featuredRes.data
    stats.value = statsRes.data
  } catch (err) {
    console.error('Error loading home data:', err)
  }
})
</script>

<style scoped>
/* ---- HERO ---- */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: var(--space-24) 0 var(--space-16);
  overflow: hidden;
  margin-top: calc(-80px - var(--space-4));
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: var(--color-bg-primary);
  z-index: 0;
}

.hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.hero-orb-1 {
  width: 600px;
  height: 600px;
  top: -15%;
  left: -10%;
  background: rgba(193, 216, 47, 0.12);
  animation: float 8s ease-in-out infinite;
}

.hero-orb-2 {
  width: 400px;
  height: 400px;
  top: 10%;
  right: -5%;
  background: rgba(232, 93, 74, 0.1);
  animation: float 10s ease-in-out infinite 1s;
}

.hero-orb-3 {
  width: 300px;
  height: 300px;
  bottom: 10%;
  left: 30%;
  background: rgba(215, 214, 196, 0.06);
  animation: float 12s ease-in-out infinite 2s;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary-ultra-light);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-primary-light);
  margin-bottom: var(--space-8);
}

.hero h1 {
  font-size: var(--font-size-6xl);
  line-height: 1.05;
  margin-bottom: var(--space-6);
  letter-spacing: 0.02em;
}

.hero-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
  max-width: 540px;
  margin: 0 auto var(--space-12);
  font-weight: 300;
  line-height: 1.7;
}

/* Hero Highlight — Shimmer + Glow Effect */
.hero-highlight {
  position: relative;
  display: inline-block;
}

.hero-highlight-glow {
  position: absolute;
  inset: -8px -16px;
  background: radial-gradient(
    ellipse at center,
    rgba(193, 216, 47, 0.2) 0%,
    rgba(193, 216, 47, 0.05) 50%,
    transparent 70%
  );
  border-radius: var(--radius-xl);
  filter: blur(16px);
  animation: glow-pulse 3s ease-in-out infinite;
  pointer-events: none;
}

.hero-shimmer {
  position: relative;
  display: inline-block;
  background: linear-gradient(
    90deg,
    #8BA320 0%,
    #C1D82F 30%,
    #E8E4B0 50%,
    #C1D82F 70%,
    #8BA320 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer-sweep 4s ease-in-out infinite;
}

@keyframes shimmer-sweep {
  0%, 100% { background-position: 100% 50%; }
  50% { background-position: 0% 50%; }
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

/* Search Bar CTA */
.hero-search {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  padding: var(--space-5);
  border-radius: var(--radius-2xl);
  max-width: 880px;
  margin: 0 auto var(--space-12);
}

.search-field {
  flex: 1;
  text-align: left;
}

.search-field label {
  display: block;
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.search-btn {
  flex-shrink: 0;
  height: 46px;
}

/* Stats */
.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-10);
}

.stat { text-align: center; }

.stat strong {
  display: block;
  font-family: var(--font-heading);
  font-size: var(--font-size-4xl);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat span {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  font-weight: 300;
}

.stat-divider {
  width: 1px;
  height: 48px;
  background: var(--color-border);
}

/* ---- SECTIONS ---- */
.section {
  padding: var(--space-24) 0;
}

.text-center { text-align: center; }

.mx-auto {
  margin-left: auto;
  margin-right: auto;
  margin-bottom: var(--space-12);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--space-12);
}

/* ---- CATEGORIES — Big block cards ---- */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}

.category-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-12) var(--space-8);
  background: var(--gradient-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-base);
  cursor: pointer;
  text-align: center;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.category-card:hover {
  border-color: var(--color-primary-light);
  transform: translateY(-8px);
  box-shadow: var(--shadow-neon);
}

.category-card:hover::before {
  opacity: 0.06;
}

.category-icon-wrap {
  position: relative;
  z-index: 1;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-ultra-light);
  border-radius: var(--radius-xl);
  color: var(--color-primary-light);
  transition: all var(--transition-base);
}

.category-card:hover .category-icon-wrap {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-glow);
}

.category-card h3 {
  position: relative;
  z-index: 1;
  font-size: var(--font-size-2xl);
}

.category-card p {
  position: relative;
  z-index: 1;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.category-arrow {
  position: relative;
  z-index: 1;
  color: var(--color-text-muted);
  opacity: 0;
  transform: translateX(-8px);
  transition: all var(--transition-base);
}

.category-card:hover .category-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--color-primary-light);
}

/* ---- TALENTS GRID ---- */
.talents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-6);
}

/* ---- HOW IT WORKS ---- */
.steps-grid {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.step-card {
  flex: 1;
  max-width: 320px;
  text-align: center;
  padding: var(--space-10) var(--space-6);
  border-radius: var(--radius-2xl);
  transition: all var(--transition-base);
}

.step-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-neon);
  border-color: var(--color-border-hover);
}

.step-number {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-xl);
  background: var(--gradient-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-6);
  transition: box-shadow var(--transition-base);
}

.step-card:hover .step-number {
  box-shadow: var(--shadow-glow);
}

.step-number-accent {
  background: var(--color-primary);
}

.step-card:hover .step-number-accent {
  box-shadow: var(--shadow-glow-accent);
}

.step-number-green {
  background: var(--color-primary);
}

.step-card:hover .step-number-green {
  box-shadow: var(--shadow-glow-cyan);
}

.step-card h3 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-3);
}

.step-card p {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  line-height: 1.7;
  font-weight: 300;
}

.step-connector {
  display: flex;
  align-items: center;
  color: var(--color-text-muted);
}

/* ---- CTA ---- */
.cta-card {
  position: relative;
  border-radius: var(--radius-2xl);
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
}

.cta-glow {
  position: absolute;
  top: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  background: var(--gradient-glow);
  filter: blur(100px);
  pointer-events: none;
}

.cta-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: var(--space-20) var(--space-8);
}

.cta-content h2 {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--space-4);
}

.cta-content p {
  color: var(--color-text-muted);
  font-size: var(--font-size-lg);
  margin-bottom: var(--space-8);
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
  font-weight: 300;
}

.empty-state {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-muted);
}

/* ---- RESPONSIVE ---- */
@media (max-width: 768px) {
  .hero { padding-top: var(--space-20); }
  .hero h1 { font-size: var(--font-size-4xl); }

  .hero-search {
    flex-direction: column;
    align-items: stretch;
    padding: var(--space-4);
    gap: var(--space-2);
  }

  .hide-mobile { display: none; }
  .search-btn { width: 100%; }

  .categories-grid { grid-template-columns: 1fr; }
  .talents-grid { grid-template-columns: 1fr; }

  .steps-grid { flex-direction: column; align-items: center; }
  .step-connector { transform: rotate(90deg); }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }

  .hero-stats { gap: var(--space-6); }
  .stat strong { font-size: var(--font-size-2xl); }
}

/* ---- Light Mode Overrides — Premium Aesthetics ---- */

/* Hero background: warm sophisticated gradient instead of flat */
[data-theme="light"] .hero-bg {
  background: linear-gradient(
    180deg,
    #FAF8F3 0%,
    #F5F0E8 25%,
    #EDE6D8 50%,
    #F2EDE3 75%,
    #FAF8F3 100%
  );
}

/* Richer, more visible orbs in light mode */
[data-theme="light"] .hero-orb-1 {
  background: rgba(193, 216, 47, 0.15);
  width: 700px;
  height: 700px;
}
[data-theme="light"] .hero-orb-2 {
  background: rgba(232, 93, 74, 0.1);
  width: 500px;
  height: 500px;
}
[data-theme="light"] .hero-orb-3 {
  background: rgba(193, 175, 130, 0.12);
  width: 400px;
  height: 400px;
}

/* Hero badge — warm tinted pill */
[data-theme="light"] .hero-badge {
  background: rgba(193, 216, 47, 0.12);
  border-color: rgba(193, 216, 47, 0.25);
  color: #5a6e10;
}

/* Search bar — frosted glass with warm shadow */
[data-theme="light"] .hero-search {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(193, 216, 47, 0.15);
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.06),
    0 1px 4px rgba(0, 0, 0, 0.03),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

/* Stats — subtle warm background */
[data-theme="light"] .hero-stats {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-2xl);
  padding: var(--space-5) var(--space-8);
}

/* Category cards — elevated with warm shadows */
[data-theme="light"] .category-card {
  background: linear-gradient(145deg, #FFFFFF 0%, #FAFAF5 100%);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.04),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
}
[data-theme="light"] .category-card:hover {
  border-color: rgba(193, 216, 47, 0.3);
  box-shadow:
    0 12px 40px rgba(107, 138, 15, 0.12),
    0 4px 12px rgba(0, 0, 0, 0.06);
}
[data-theme="light"] .category-card::before {
  background: linear-gradient(135deg, rgba(193, 216, 47, 0.08), rgba(107, 138, 15, 0.04));
}
[data-theme="light"] .category-icon-wrap {
  background: linear-gradient(135deg, rgba(193, 216, 47, 0.15), rgba(193, 216, 47, 0.08));
  box-shadow: 0 2px 8px rgba(193, 216, 47, 0.1);
}

/* Step cards — soft elevated style */
[data-theme="light"] .step-card {
  background: linear-gradient(145deg, #FFFFFF 0%, #FDFCF8 100%);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow:
    0 2px 12px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}
[data-theme="light"] .step-card:hover {
  box-shadow:
    0 8px 32px rgba(107, 138, 15, 0.1),
    0 2px 8px rgba(0, 0, 0, 0.04);
  border-color: rgba(193, 216, 47, 0.2);
}

/* CTA card — warm gradient instead of flat white */
[data-theme="light"] .cta-card {
  background: linear-gradient(135deg, #F8F4EC 0%, #F0EADB 50%, #EDE5D3 100%);
  border: 1px solid rgba(193, 175, 130, 0.2);
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
[data-theme="light"] .cta-glow {
  background: radial-gradient(circle, rgba(193, 216, 47, 0.15) 0%, transparent 70%);
}

/* Sections background — alternating warm tones */
[data-theme="light"] .categories-section {
  background: linear-gradient(180deg, #FAF8F3 0%, #F5F1E9 100%);
}
[data-theme="light"] .featured-section {
  background: #FFFFFF;
}
[data-theme="light"] .how-section {
  background: linear-gradient(180deg, #F8F5EE 0%, #FAF8F3 100%);
}
</style>
