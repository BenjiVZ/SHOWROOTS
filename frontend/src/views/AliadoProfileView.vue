<template>
  <div class="aliado-page">
    <!-- Loading -->
    <div v-if="loading" class="container loading-state">
      <div class="skeleton-hero"></div>
      <div class="skeleton-card" v-for="i in 3" :key="i"></div>
    </div>

    <!-- Not found -->
    <div v-else-if="!profile" class="container not-found">
      <h2>Aliado no encontrado</h2>
      <p>Puede que el aliado haya desactivado su perfil o que la URL esté mal.</p>
      <router-link to="/packs" class="btn btn-primary">Volver al catálogo</router-link>
    </div>

    <template v-else>
      <!-- Hero -->
      <section class="hero">
        <div class="container">
          <div class="hero-inner">
            <div class="hero-avatar">
              <img v-if="profile.avatar" :src="profile.avatar" :alt="profile.full_name" />
              <span v-else class="avatar-fallback">{{ initial }}</span>
            </div>
            <div class="hero-info">
              <div class="hero-badges">
                <span class="badge-verified">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Aliado verificado
                </span>
                <span v-if="profile.is_dj_partner" class="badge-dj">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                  DJ + equipo
                </span>
              </div>
              <h1>{{ profile.full_name }}</h1>
              <div class="hero-meta">
                <span v-if="profile.main_city" class="meta-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                  {{ profile.main_city }} · {{ profile.coverage_radius_km }} km
                </span>
                <span class="meta-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
                  {{ profile.stats.total_packs }} {{ profile.stats.total_packs === 1 ? 'pack' : 'packs' }}
                </span>
                <span v-if="profile.stats.total_rentals" class="meta-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                  {{ profile.stats.total_rentals }} eventos cubiertos
                </span>
                <span v-if="profile.stats.rating_avg" class="meta-item rating">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                  {{ profile.stats.rating_avg }}
                </span>
              </div>
              <p v-if="profile.bio" class="hero-bio">{{ profile.bio }}</p>

              <!-- Categorías chips -->
              <div v-if="profile.categories?.length" class="cat-chips">
                <span v-for="c in profile.categories" :key="c" class="cat-chip">
                  <span v-html="categoryIcon(c)"></span>
                  {{ categoryLabel(c) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="container content-grid">
        <!-- Main -->
        <main class="main-col">
          <!-- Galería de equipo -->
          <section v-if="profile.photos?.length" class="card">
            <h2>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              Equipo
            </h2>
            <div class="photos-grid">
              <button
                v-for="(ph, idx) in profile.photos"
                :key="ph.id"
                type="button"
                class="photo-tile"
                @click="openLightbox(idx)"
              >
                <img :src="ph.file" :alt="ph.caption || 'Equipo'" />
                <span class="photo-tile-zoom">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                </span>
              </button>
            </div>
          </section>

          <!-- Bundles destacados -->
          <section v-if="profile.bundles?.length" class="card">
            <h2>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="color:#f59e0b"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              Bundles con descuento
            </h2>
            <div class="bundles-list">
              <div v-for="b in profile.bundles" :key="'b-' + b.id" class="bundle-row">
                <div class="bundle-discount">-{{ Number(b.discount_percentage).toFixed(0) }}%</div>
                <div class="bundle-info">
                  <strong>{{ b.name }}</strong>
                  <small v-if="b.description">{{ b.description }}</small>
                </div>
                <div class="bundle-price">
                  <span class="bundle-price-old">${{ formatMoney(b.base_price) }}</span>
                  <span class="bundle-price-new">${{ formatMoney(b.discounted_price) }}</span>
                </div>
              </div>
            </div>
          </section>

          <!-- Packs -->
          <section class="card">
            <h2>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
              Packs disponibles
            </h2>
            <div v-if="!profile.packs?.length" class="empty">
              Este aliado todavía no publicó packs.
            </div>
            <div v-else class="packs-grid">
              <div v-for="p in profile.packs" :key="p.id" class="pack-card" @click="openPack(p)">
                <div class="pack-thumb">
                  <img v-if="p.cover_image" :src="p.cover_image" :alt="p.name" />
                  <span v-else class="pack-icon" v-html="categoryIcon(p.category)"></span>
                  <span v-if="p.includes_dj" class="dj-pack-badge">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                    Con DJ
                  </span>
                </div>
                <div class="pack-body">
                  <div class="pack-name">{{ p.name }}</div>
                  <div class="pack-meta">
                    <span>{{ categoryLabel(p.category) }}</span>
                    <span>· {{ p.event_size_display }}</span>
                  </div>
                  <div class="pack-price-row">
                    <strong class="pack-price">${{ formatMoney(p.price) }}</strong>
                    <span v-if="p.rating_avg && Number(p.rating_avg) > 0" class="pack-rating">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor" style="color:#f59e0b"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                      {{ Number(p.rating_avg).toFixed(1) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>

        <!-- Sidebar -->
        <aside class="side-col">
          <section class="card sticky">
            <h3>Cobertura</h3>
            <CoverageMap
              :city="profile.main_city || 'Ciudad de Panamá'"
              :radius="Number(profile.coverage_radius_km) || 50"
            />
            <ul class="info-list">
              <li>
                <span>Ciudad base</span>
                <strong>{{ profile.main_city || '—' }}</strong>
              </li>
              <li>
                <span>Radio de cobertura</span>
                <strong>{{ profile.coverage_radius_km }} km</strong>
              </li>
              <li v-if="profile.travel_fee_extra">
                <span>Fee fuera de área</span>
                <strong>${{ profile.travel_fee_extra }}</strong>
              </li>
              <li>
                <span>Capacidad / noche</span>
                <strong>{{ profile.max_simultaneous_events }} evento{{ profile.max_simultaneous_events > 1 ? 's' : '' }}</strong>
              </li>
            </ul>

            <div class="how-to">
              <strong>¿Cómo lo contrato?</strong>
              <p>Los packs de aliados se agregan a una reserva con un DJ — primero elige al DJ y desde el booking sumas el equipo.</p>
              <router-link to="/search" class="btn btn-primary btn-full">Buscar DJ →</router-link>
            </div>
          </section>
        </aside>
      </div>
    </template>

    <!-- Lightbox de fotos del equipo -->
    <Teleport to="body">
      <Transition name="lb-fade">
        <div v-if="lightbox.open" class="lb-backdrop" @click.self="closeLightbox" @keydown.esc="closeLightbox" tabindex="0">
          <button class="lb-close" @click="closeLightbox" aria-label="Cerrar">×</button>
          <button
            v-if="profile?.photos?.length > 1"
            class="lb-nav lb-prev"
            @click.stop="prevPhoto"
            aria-label="Anterior"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div class="lb-content" @click.stop>
            <img :src="currentPhoto?.file" :alt="currentPhoto?.caption || 'Equipo'" />
            <div v-if="currentPhoto?.caption" class="lb-caption">{{ currentPhoto.caption }}</div>
            <div v-if="profile?.photos?.length > 1" class="lb-counter">
              {{ lightbox.index + 1 }} / {{ profile.photos.length }}
            </div>
          </div>
          <button
            v-if="profile?.photos?.length > 1"
            class="lb-nav lb-next"
            @click.stop="nextPhoto"
            aria-label="Siguiente"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- Modal de detalle del pack -->
    <Teleport to="body">
      <div v-if="packDetail.open" class="detail-backdrop" @click.self="packDetail.open = false">
        <div class="detail-modal">
          <button class="detail-close" @click="packDetail.open = false" aria-label="Cerrar">×</button>
          <div class="detail-hero">
            <img v-if="packDetail.pack?.cover_image" :src="packDetail.pack.cover_image" :alt="packDetail.pack?.name" />
            <span v-else class="pack-icon-lg" v-html="categoryIcon(packDetail.pack?.category)"></span>
          </div>
          <div class="detail-body">
            <div class="detail-header">
              <div class="detail-header-text">
                <h2>{{ packDetail.pack?.name }}</h2>
                <div v-if="packDetail.pack?.event_size_display" class="detail-vendor">{{ packDetail.pack.event_size_display }}</div>
              </div>
              <div class="detail-price-pill">
                <span class="price-label">Desde</span>
                <span class="price-value">${{ formatMoney(packDetail.pack?.price) }}</span>
              </div>
            </div>

            <p v-if="packDetail.pack?.short_description" class="detail-desc">{{ packDetail.pack.short_description }}</p>

            <div v-if="hasFeatures(packDetail.pack)" class="feature-badges">
              <span v-if="packDetail.pack?.includes_dj" class="feature-badge feature-dj">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                <div>
                  <strong>DJ incluido</strong>
                  <small v-if="packDetail.pack?.dj_name">{{ packDetail.pack.dj_name }}</small>
                </div>
              </span>
              <span v-if="packDetail.pack?.includes_technician" class="feature-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
                <div><strong>Técnico in-situ</strong><small>Operador del equipo</small></div>
              </span>
              <span v-if="packDetail.pack?.includes_setup" class="feature-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                <div><strong>Montaje incluido</strong><small>Setup y desmontaje</small></div>
              </span>
            </div>

            <h4 class="detail-section-h">Equipo del pack</h4>
            <ul class="equipment-list">
              <li v-for="(item, idx) in packDetail.pack?.equipment_items || []" :key="idx">
                <span class="equip-check">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                <span>{{ stripBullet(item) }}</span>
              </li>
              <li v-if="!packDetail.pack?.equipment_items?.length" class="empty-equip">El aliado no detalló los items.</li>
            </ul>

            <div class="detail-info-grid">
              <div class="info-pill">
                <span class="info-pill-label">Tamaño evento</span>
                <strong>{{ packDetail.pack?.event_size_display }}</strong>
              </div>
              <div class="info-pill">
                <span class="info-pill-label">Setup</span>
                <strong>{{ packDetail.pack?.setup_hours_before }}h antes</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, reactive } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import CoverageMap from '@/components/common/CoverageMap.vue'

const SVG_O = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
const CATEGORY_META = {
  sound:    { label: 'Sonido',     icon: `${SVG_O}<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>` },
  lights:   { label: 'Iluminación',icon: `${SVG_O}<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>` },
  screens:  { label: 'Pantallas',  icon: `${SVG_O}<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>` },
  mics:     { label: 'Microfonía', icon: `${SVG_O}<path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>` },
  dj_booth: { label: 'DJ Booth',   icon: `${SVG_O}<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>` },
  fx:       { label: 'FX',         icon: `${SVG_O}<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/></svg>` },
}

const route = useRoute()
const profile = ref(null)
const loading = ref(true)
const packDetail = reactive({ open: false, pack: null })

// ── Lightbox de fotos del equipo ──
const lightbox = reactive({ open: false, index: 0 })
const currentPhoto = computed(() => profile.value?.photos?.[lightbox.index] || null)

function openLightbox(idx) {
  lightbox.index = idx
  lightbox.open = true
  document.body.style.overflow = 'hidden'
}
function closeLightbox() {
  lightbox.open = false
  document.body.style.overflow = ''
}
function nextPhoto() {
  const total = profile.value?.photos?.length || 0
  if (!total) return
  lightbox.index = (lightbox.index + 1) % total
}
function prevPhoto() {
  const total = profile.value?.photos?.length || 0
  if (!total) return
  lightbox.index = (lightbox.index - 1 + total) % total
}

function onLbKey(e) {
  if (!lightbox.open) return
  if (e.key === 'Escape') closeLightbox()
  else if (e.key === 'ArrowRight') nextPhoto()
  else if (e.key === 'ArrowLeft') prevPhoto()
}

const initial = computed(() => (profile.value?.full_name || '?').charAt(0).toUpperCase())

function categoryLabel(c) { return CATEGORY_META[c]?.label || c }
function categoryIcon(c) { return CATEGORY_META[c]?.icon || '' }
function formatMoney(v) {
  return parseFloat(v || 0).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function hasFeatures(pack) {
  if (!pack) return false
  return !!(pack.includes_dj || pack.includes_technician || pack.includes_setup)
}

function stripBullet(item) {
  return String(item || '').replace(/^\s*[•·\-*]\s*/, '').trim()
}
function openPack(p) {
  packDetail.pack = p
  packDetail.open = true
}

async function fetchProfile() {
  loading.value = true
  try {
    const { data } = await api.get(`/aliado/${route.params.userId}/`)
    profile.value = data
  } catch {
    profile.value = null
  }
  loading.value = false
}

watch(() => route.params.userId, fetchProfile)
onMounted(() => {
  fetchProfile()
  window.addEventListener('keydown', onLbKey)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onLbKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.aliado-page {
  padding-top: 80px;
  padding-bottom: var(--space-12);
  min-height: 100vh;
  background: var(--color-bg-primary);
}

/* Loading / not found */
.loading-state { display: flex; flex-direction: column; gap: var(--space-4); padding-top: var(--space-6); }
.skeleton-hero { height: 240px; background: var(--color-bg-card); border-radius: var(--radius-xl); animation: shimmer 1.4s infinite; }
.skeleton-card { height: 180px; background: var(--color-bg-card); border-radius: var(--radius-xl); animation: shimmer 1.4s infinite; }
@keyframes shimmer { 0%, 100% { opacity: 0.7; } 50% { opacity: 0.4; } }
.not-found { text-align: center; padding: var(--space-12) var(--space-4); }
.not-found h2 { margin-bottom: var(--space-2); }
.not-found p { color: var(--color-text-muted); margin-bottom: var(--space-4); }

/* Hero */
.hero {
  background: linear-gradient(135deg, rgba(193,216,47,0.08), rgba(245,158,11,0.04));
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-8) 0;
  margin-bottom: var(--space-6);
}
.hero-inner { display: flex; align-items: center; gap: var(--space-6); flex-wrap: wrap; }
.hero-avatar {
  width: 120px; height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--color-primary);
  background: var(--color-bg-card);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-fallback {
  font-family: 'Poppins', sans-serif;
  font-size: 2.4rem;
  font-weight: 700;
  color: var(--color-primary);
}
.hero-info { flex: 1; min-width: 260px; }
.hero-badges { display: flex; gap: 8px; margin-bottom: var(--space-2); flex-wrap: wrap; }
.badge-verified, .badge-dj {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.badge-verified {
  background: rgba(193,216,47,0.12);
  color: var(--color-primary);
  border: 1px solid rgba(193,216,47,0.35);
}
.badge-dj {
  background: rgba(245,158,11,0.12);
  color: #f59e0b;
  border: 1px solid rgba(245,158,11,0.35);
}
.hero-info h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 2rem;
  margin: 0 0 var(--space-2);
  color: var(--color-text-primary);
}
.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: var(--space-3);
  color: var(--color-text-muted);
  font-size: 0.88rem;
}
.meta-item { display: inline-flex; align-items: center; gap: 5px; }
.meta-item svg { color: var(--color-primary); }
.meta-item.rating { color: var(--color-text-primary); font-weight: 600; }
.meta-item.rating svg { color: #f59e0b; }
.hero-bio { color: var(--color-text-secondary); line-height: 1.55; margin: 0 0 var(--space-3); max-width: 640px; }

.cat-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.cat-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  font-size: 0.78rem;
  color: var(--color-text-secondary);
}
.cat-chip span { display: inline-flex; align-items: center; color: var(--color-text-muted); }

/* Content grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-6);
  align-items: start;
}
.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  margin-bottom: var(--space-4);
}
.card h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  margin: 0 0 var(--space-4);
  color: var(--color-text-primary);
}
.card h2 svg { color: var(--color-primary); }
.empty { color: var(--color-text-muted); font-size: 0.92rem; padding: var(--space-4) 0; }

/* Photos */
.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}
.photo-tile {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  padding: 0;
  cursor: zoom-in;
  transition: transform 0.2s, box-shadow 0.2s;
}
.photo-tile:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 22px rgba(0,0,0,0.18);
}
.photo-tile img { width: 100%; height: 100%; object-fit: cover; display: block; }
.photo-tile-zoom {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%) scale(0.85);
  width: 40px; height: 40px;
  border-radius: 50%;
  background: rgba(0,0,0,0.55);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s;
  pointer-events: none;
  backdrop-filter: blur(4px);
}
.photo-tile:hover .photo-tile-zoom { opacity: 1; transform: translate(-50%, -50%) scale(1); }

/* ── Lightbox ── */
.lb-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  padding: var(--space-4);
  outline: none;
}
.lb-content {
  max-width: min(1200px, 92vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}
.lb-content img {
  max-width: 100%;
  max-height: 82vh;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  object-fit: contain;
}
.lb-caption {
  color: rgba(255,255,255,0.85);
  font-size: 0.95rem;
  text-align: center;
  max-width: 600px;
  line-height: 1.5;
}
.lb-counter {
  color: rgba(255,255,255,0.6);
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 1px;
}
.lb-close {
  position: absolute;
  top: 16px; right: 16px;
  width: 44px; height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.12);
  border: none;
  color: #fff;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  z-index: 2;
  transition: background 0.15s;
}
.lb-close:hover { background: rgba(255,255,255,0.22); }
.lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px; height: 50px;
  border-radius: 50%;
  background: rgba(255,255,255,0.12);
  border: none;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  transition: background 0.15s, transform 0.15s;
}
.lb-nav:hover { background: rgba(255,255,255,0.22); transform: translateY(-50%) scale(1.06); }
.lb-prev { left: 20px; }
.lb-next { right: 20px; }
@media (max-width: 640px) {
  .lb-prev { left: 8px; }
  .lb-next { right: 8px; }
  .lb-nav { width: 42px; height: 42px; }
}
.lb-fade-enter-active, .lb-fade-leave-active { transition: opacity 0.2s ease; }
.lb-fade-enter-from, .lb-fade-leave-to { opacity: 0; }

/* Bundles */
.bundles-list { display: flex; flex-direction: column; gap: 10px; }
.bundle-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(245,158,11,0.05);
  border: 1px solid rgba(245,158,11,0.25);
  border-radius: var(--radius-md);
}
.bundle-discount {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  color: #f59e0b;
  background: rgba(245,158,11,0.12);
  padding: 6px 10px;
  border-radius: 8px;
  flex-shrink: 0;
}
.bundle-info { flex: 1; min-width: 0; }
.bundle-info strong { display: block; color: var(--color-text-primary); font-size: 0.95rem; }
.bundle-info small { display: block; color: var(--color-text-muted); font-size: 0.78rem; margin-top: 2px; }
.bundle-price { text-align: right; }
.bundle-price-old { display: block; color: var(--color-text-muted); text-decoration: line-through; font-size: 0.78rem; }
.bundle-price-new { display: block; color: var(--color-primary); font-weight: 800; font-size: 1.05rem; }

/* Packs grid */
.packs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-3);
}
.pack-card {
  background: var(--color-bg-elevated, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.pack-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary);
  box-shadow: 0 10px 24px rgba(0,0,0,0.18);
}
.pack-thumb {
  aspect-ratio: 16/10;
  background: linear-gradient(135deg, #2a1a3e, #1a3a2e);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.4);
}
.pack-thumb { position: relative; }
.pack-thumb img { width: 100%; height: 100%; object-fit: cover; }
.pack-icon svg { width: 36px; height: 36px; }
.dj-pack-badge {
  position: absolute;
  top: 8px; left: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(245,158,11,0.92);
  color: #0d0d0d;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.detail-items li.ok.dj { color: #f59e0b; font-weight: 600; }
.pack-body { padding: var(--space-3); }
.pack-name { font-weight: 700; color: var(--color-text-primary); margin-bottom: 4px; }
.pack-meta { font-size: 0.78rem; color: var(--color-text-muted); margin-bottom: var(--space-2); }
.pack-price-row { display: flex; align-items: baseline; justify-content: space-between; }
.pack-price { font-size: 1.15rem; color: var(--color-primary); font-weight: 800; }
.pack-rating { display: inline-flex; align-items: center; gap: 4px; font-size: 0.78rem; color: var(--color-text-secondary); font-weight: 600; }

/* Sidebar */
.side-col .card.sticky { position: sticky; top: 96px; }
.side-col h3 { font-size: 1rem; margin: 0 0 var(--space-3); }
.info-list { list-style: none; padding: 0; margin: var(--space-3) 0 0; display: flex; flex-direction: column; gap: 8px; }
.info-list li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 8px 0;
  border-bottom: 1px dashed var(--color-border);
  font-size: 0.85rem;
}
.info-list li:last-child { border-bottom: none; }
.info-list span { color: var(--color-text-muted); }
.info-list strong { color: var(--color-text-primary); }
.how-to {
  margin-top: var(--space-4);
  padding: var(--space-3);
  background: var(--color-bg-elevated, rgba(193,216,47,0.05));
  border-radius: var(--radius-md);
  border: 1px solid rgba(193,216,47,0.2);
}
.how-to strong { display: block; color: var(--color-primary); margin-bottom: 4px; font-size: 0.88rem; }
.how-to p { color: var(--color-text-muted); font-size: 0.82rem; line-height: 1.5; margin: 0 0 var(--space-3); }
.btn-full { width: 100%; display: inline-flex; align-items: center; justify-content: center; }

/* Detail modal */
.detail-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.75); backdrop-filter: blur(6px);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; padding: var(--space-4);
}
.detail-modal {
  width: 100%; max-width: 560px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  overflow: hidden;
  position: relative;
}
.detail-close {
  position: absolute; top: 12px; right: 12px;
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(0,0,0,0.6); color: #fff; border: none;
  cursor: pointer; font-size: 20px; line-height: 1;
  z-index: 2;
}
.detail-hero {
  aspect-ratio: 16/9;
  background: linear-gradient(135deg, #2a1a3e, #1a3a2e);
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.4);
}
.detail-hero img { width: 100%; height: 100%; object-fit: cover; }
.pack-icon-lg svg { width: 72px; height: 72px; }
.detail-body { padding: var(--space-5) var(--space-5) var(--space-4); }
.detail-header { display: flex; align-items: flex-start; gap: var(--space-3); margin-bottom: var(--space-3); }
.detail-header-text { flex: 1; min-width: 0; }
.detail-body h2 { margin: 0 0 4px; font-size: 1.5rem; line-height: 1.2; }
.detail-vendor { color: var(--color-text-muted); font-size: 0.85rem; }
.detail-price-pill {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 10px 14px;
  background: rgba(193,216,47,0.10);
  border: 1px solid rgba(193,216,47,0.35);
  border-radius: 14px;
  text-align: right;
}
.detail-price-pill .price-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  line-height: 1;
}
.detail-price-pill .price-value {
  color: var(--color-primary);
  font-family: 'Poppins', sans-serif;
  font-weight: 800;
  font-size: 1.5rem;
  line-height: 1.1;
  margin-top: 2px;
}
.detail-desc {
  color: var(--color-text-secondary);
  font-size: 0.92rem;
  line-height: 1.55;
  margin: 0 0 var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.feature-badges {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  margin-bottom: var(--space-4);
}
.feature-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.28);
  color: var(--color-text-primary);
}
.feature-badge svg {
  flex-shrink: 0;
  width: 22px; height: 22px;
  padding: 5px;
  background: rgba(16,185,129,0.18);
  border-radius: 50%;
  color: #10b981;
  box-sizing: content-box;
}
.feature-badge div { display: flex; flex-direction: column; min-width: 0; }
.feature-badge strong { font-size: 0.85rem; font-weight: 600; line-height: 1.15; }
.feature-badge small { font-size: 0.7rem; color: var(--color-text-muted); margin-top: 2px; }
.feature-badge.feature-dj {
  background: rgba(245,158,11,0.10);
  border-color: rgba(245,158,11,0.35);
}
.feature-badge.feature-dj svg {
  background: rgba(245,158,11,0.22);
  color: #f59e0b;
}
.feature-badge.feature-dj strong { color: #f59e0b; }

.detail-section-h {
  color: var(--color-text-muted) !important;
  font-size: 0.72rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
  margin: 0 0 var(--space-2) !important;
}

.equipment-list { list-style: none; padding: 0; margin: 0 0 var(--space-4); display: grid; grid-template-columns: 1fr; gap: 4px; }
.equipment-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 12px;
  background: var(--color-bg-elevated, rgba(255,255,255,0.025));
  border-radius: 8px;
  font-size: 0.88rem;
  color: var(--color-text-primary);
  line-height: 1.4;
  border: 1px solid transparent;
  transition: border-color 0.15s, background 0.15s;
}
.equipment-list li:hover {
  border-color: var(--color-border);
  background: var(--color-bg-card);
}
.equip-check {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px; height: 20px;
  border-radius: 50%;
  background: rgba(193,216,47,0.18);
  color: var(--color-primary);
  margin-top: 1px;
}
.empty-equip {
  color: var(--color-text-muted) !important;
  font-style: italic;
  background: transparent !important;
  border: 1px dashed var(--color-border) !important;
  justify-content: center;
}

.detail-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 0; }
.info-pill {
  display: flex;
  flex-direction: column;
  padding: 8px 12px;
  background: var(--color-bg-elevated, rgba(255,255,255,0.025));
  border: 1px solid var(--color-border);
  border-radius: 10px;
}
.info-pill-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  margin-bottom: 2px;
}
.info-pill strong { color: var(--color-text-primary); font-size: 0.92rem; font-weight: 600; }

@media (max-width: 900px) {
  .content-grid { grid-template-columns: 1fr; }
  .side-col .card.sticky { position: static; }
  .hero-inner { flex-direction: column; align-items: flex-start; text-align: left; }
}
</style>
