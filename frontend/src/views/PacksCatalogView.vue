<template>
  <div class="packs-catalog">
    <div class="container">
      <header class="catalog-header">
        <span class="hero-tag">Aliados de producción</span>
        <h1>Producción para tu evento</h1>
        <p class="catalog-sub">
          Renta packs verificados de sonido, luces, pantallas y más.
          Pagas solo cuando el evento se confirma — protección Pulsar.
        </p>
        <div class="trust-strip">
          <div class="trust-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            <div><strong>Pago en custodia</strong><span>Tu dinero protegido hasta el evento</span></div>
          </div>
          <div class="trust-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
            <div><strong>Aliados verificados</strong><span>Equipo revisado por Pulsar</span></div>
          </div>
          <div class="trust-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <div><strong>Confirma rápido</strong><span>Respuesta en menos de 24h</span></div>
          </div>
        </div>
        <router-link :to="{ name: 'service-booking' }" class="btn btn-primary catalog-cta">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>
          Armar mi reserva de servicios (con o sin DJ) →
        </router-link>
      </header>

      <div class="catalog-layout">
        <!-- Filters -->
        <aside class="filters-side">
          <h3>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:4px;color:var(--color-primary)"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            Filtros
          </h3>

          <div class="filter-group">
            <label class="filter-label">Categoría</label>
            <div class="chip-grid">
              <button
                v-for="c in CATEGORIES"
                :key="c.value"
                type="button"
                class="filter-chip"
                :class="{ active: filters.category === c.value }"
                @click="toggleCategory(c.value)"
              >
                <span class="chip-icon" v-html="c.icon"></span> {{ c.label }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">Tamaño del evento</label>
            <div class="chip-grid">
              <button
                v-for="s in EVENT_SIZES"
                :key="s.value"
                type="button"
                class="filter-chip"
                :class="{ active: filters.event_size === s.value }"
                @click="toggleEventSize(s.value)"
              >
                {{ s.label }}
              </button>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">Proveedor</label>
            <div class="chip-grid">
              <button
                type="button"
                class="filter-chip"
                :class="{ active: !filters.vendor_type }"
                @click="filters.vendor_type = ''; fetchPacks()"
              >Todos</button>
              <button
                type="button"
                class="filter-chip"
                :class="{ active: filters.vendor_type === 'dj' }"
                @click="filters.vendor_type = 'dj'; fetchPacks()"
              >DJ + equipo</button>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">¿Incluye DJ?</label>
            <div class="chip-grid">
              <button
                type="button"
                class="filter-chip"
                :class="{ active: !filters.includes_dj }"
                @click="filters.includes_dj = ''; fetchPacks()"
              >Cualquiera</button>
              <button
                type="button"
                class="filter-chip"
                :class="{ active: filters.includes_dj === 'true' }"
                @click="filters.includes_dj = 'true'; fetchPacks()"
              >Con DJ (turnkey)</button>
              <button
                type="button"
                class="filter-chip"
                :class="{ active: filters.includes_dj === 'false' }"
                @click="filters.includes_dj = 'false'; fetchPacks()"
              >Sólo equipo</button>
            </div>
          </div>

          <div class="filter-group">
            <label class="filter-label">Precio máximo (USD)</label>
            <input v-model.number="filters.max_price" type="number" min="0" class="input-field" placeholder="Sin límite" @change="fetchPacks" />
          </div>
        </aside>

        <!-- Grid -->
        <main class="packs-main">
          <!-- Barra de resultados (siempre visible cuando no cargando) -->
          <div v-if="!loading" class="results-bar">
            <div class="results-count">
              <strong>{{ sortedPacks.length }}</strong>
              {{ sortedPacks.length === 1 ? 'pack encontrado' : 'packs encontrados' }}
              <span v-if="activeFiltersCount" class="active-filters-tag">· {{ activeFiltersCount }} {{ activeFiltersCount === 1 ? 'filtro activo' : 'filtros activos' }}</span>
            </div>
            <div class="results-controls">
              <button v-if="activeFiltersCount" class="btn-link" @click="resetFilters">Limpiar filtros</button>
              <select v-model="sort" class="sort-select">
                <option value="popular">Más populares</option>
                <option value="price_asc">Precio: menor a mayor</option>
                <option value="price_desc">Precio: mayor a menor</option>
                <option value="rating">Mejor calificados</option>
              </select>
            </div>
          </div>

          <div v-if="loading" class="loading-state">
            <div v-for="i in 4" :key="i" class="skeleton-card"></div>
          </div>
          <div v-else-if="!sortedPacks.length" class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--color-text-muted);opacity:0.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
            <h3>Sin resultados</h3>
            <p>No encontramos packs con esos filtros. Prueba con otros criterios.</p>
            <button class="btn btn-outline" @click="resetFilters">Limpiar todos los filtros</button>
          </div>
          <div v-else>
            <!-- Bundles destacados primero (si hay) -->
            <div v-if="bundles.length" class="bundles-row">
              <h3 class="bundles-h3">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-2px;margin-right:4px"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                Bundles · Combos con descuento
              </h3>
              <div class="bundles-grid">
                <div v-for="b in bundles" :key="'bundle-' + b.id" class="bundle-card">
                  <div class="bundle-banner">
                    -{{ Number(b.discount_percentage).toFixed(0) }}% · BUNDLE
                  </div>
                  <div class="bundle-body">
                    <div class="bundle-name">{{ b.name }}</div>
                    <div class="bundle-vendor">
                      Por
                      <router-link v-if="b.vendor?.id" :to="`/aliado/${b.vendor.id}`" class="vendor-link">
                        <strong>{{ b.vendor?.name }}</strong>
                      </router-link>
                      <strong v-else>{{ b.vendor?.name }}</strong>
                    </div>
                    <div class="bundle-pack-list">
                      <span v-for="p in b.packs" :key="p.id" class="bundle-pack-chip">
                        <span class="chip-icon" v-html="categoryIcon(p.category)"></span> {{ p.name }}
                      </span>
                    </div>
                    <div class="bundle-price-row">
                      <span class="bundle-price-current">${{ formatMoney(b.discounted_price) }}</span>
                      <span class="bundle-price-old">${{ formatMoney(b.base_price) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="packs-grid">
              <div v-for="p in sortedPacks" :key="p.id" class="pack-card" @click="openDetail(p)">
                <div class="pack-card-thumb">
                  <img v-if="p.cover_image" :src="p.cover_image" :alt="p.name" />
                  <span v-else class="pack-emoji" v-html="categoryIcon(p.category)"></span>
                  <span class="vendor-badge" :class="{ dj: p.vendor?.is_dj_partner }">
                    {{ p.vendor?.is_dj_partner ? 'DJ + equipo' : 'Aliado' }}
                  </span>
                  <span v-if="p.includes_dj" class="dj-pack-badge" title="Pack incluye DJ — turnkey">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                    Con DJ
                  </span>
                  <span class="cat-pill" v-html="categoryIcon(p.category)"></span>
                </div>
                <div class="pack-card-body">
                  <div class="pack-card-name">{{ p.name }}</div>
                  <div class="pack-card-vendor">
                    Por
                    <router-link v-if="p.vendor?.id" :to="`/aliado/${p.vendor.id}`" class="vendor-link" @click.stop>
                      <strong>{{ p.vendor?.name }}</strong>
                    </router-link>
                    <strong v-else>{{ p.vendor?.name }}</strong>
                    <span v-if="p.vendor?.city"> · {{ p.vendor.city }}</span>
                  </div>
                  <!-- Preview de items incluidos -->
                  <div v-if="p.equipment_items?.length" class="pack-items-preview">
                    <span v-for="(item, idx) in p.equipment_items.slice(0, 2)" :key="idx" class="item-chip">{{ stripBullet(item) }}</span>
                    <span v-if="p.equipment_items.length > 2" class="item-chip more">+{{ p.equipment_items.length - 2 }}</span>
                  </div>
                  <div class="pack-card-price-row">
                    <div class="pack-card-price">${{ formatMoney(p.price) }}</div>
                    <div v-if="p.rating_avg && Number(p.rating_avg) > 0" class="pack-rating">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" style="color:#f59e0b"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                      {{ Number(p.rating_avg).toFixed(1) }}
                    </div>
                  </div>
                  <div class="pack-card-meta">
                    <span>{{ p.event_size_display }}</span>
                    <span v-if="p.includes_technician" class="meta-item">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" style="color:#f59e0b"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                      Técnico incl.
                    </span>
                    <span v-if="p.rentals_count" class="meta-item">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
                      {{ p.rentals_count }} rentas
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      <!-- Detail modal -->
      <Teleport to="body">
        <div v-if="detail.open" class="detail-backdrop" @click.self="closeDetail">
          <div class="detail-modal">
            <button class="detail-close" @click="closeDetail" aria-label="Cerrar">×</button>
            <div class="detail-hero">
              <img v-if="detail.pack?.cover_image" :src="detail.pack.cover_image" :alt="detail.pack?.name" />
              <span v-else class="pack-emoji-lg" v-html="categoryIcon(detail.pack?.category)"></span>
            </div>
            <div class="detail-body">
              <div class="detail-header">
                <div class="detail-header-text">
                  <h2>{{ detail.pack?.name }}</h2>
                  <div class="detail-vendor">
                    Por
                    <router-link v-if="detail.pack?.vendor?.id" :to="`/aliado/${detail.pack.vendor.id}`" class="vendor-link" @click="closeDetail">
                      <strong>{{ detail.pack?.vendor?.name }}</strong>
                    </router-link>
                    <strong v-else>{{ detail.pack?.vendor?.name }}</strong>
                    <span v-if="detail.pack?.vendor?.is_dj_partner" class="vendor-tag">DJ + equipo</span>
                  </div>
                </div>
                <div class="detail-price-pill">
                  <span class="price-label">Desde</span>
                  <span class="price-value">${{ formatMoney(detail.pack?.price) }}</span>
                </div>
              </div>

              <p v-if="detail.pack?.short_description" class="detail-desc">{{ detail.pack.short_description }}</p>

              <!-- Extras / features como badges destacados -->
              <div v-if="hasFeatures(detail.pack)" class="feature-badges">
                <span v-if="detail.pack?.includes_dj" class="feature-badge feature-dj">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                  <div>
                    <strong>DJ incluido</strong>
                    <small v-if="detail.pack?.dj_name">{{ detail.pack.dj_name }}</small>
                  </div>
                </span>
                <span v-if="detail.pack?.includes_technician" class="feature-badge">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
                  <div><strong>Técnico in-situ</strong><small>Operador del equipo</small></div>
                </span>
                <span v-if="detail.pack?.includes_setup" class="feature-badge">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  <div><strong>Montaje incluido</strong><small>Setup y desmontaje</small></div>
                </span>
              </div>

              <h4 class="detail-section-h">Equipo del pack</h4>
              <ul class="equipment-list">
                <li v-for="(item, idx) in detail.pack?.equipment_items || []" :key="idx">
                  <span class="equip-check">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  </span>
                  <span>{{ stripBullet(item) }}</span>
                </li>
                <li v-if="!detail.pack?.equipment_items?.length" class="empty-equip">El aliado no detalló los items.</li>
              </ul>

              <div class="detail-info-grid">
                <div class="info-pill">
                  <span class="info-pill-label">Tamaño evento</span>
                  <strong>{{ detail.pack?.event_size_display }}</strong>
                </div>
                <div class="info-pill">
                  <span class="info-pill-label">Setup</span>
                  <strong>{{ detail.pack?.setup_hours_before }}h antes</strong>
                </div>
              </div>

              <div class="detail-note" :class="{ 'detail-note-dj': detail.pack?.includes_dj }">
                <template v-if="detail.pack?.includes_dj">
                  Este pack es <strong>turnkey</strong> — incluye el DJ. También puedes reservarlo desde el perfil del aliado.
                </template>
                <template v-else>
                  Reserva este servicio solo, o suma un DJ y otros servicios en el mismo evento.
                </template>
              </div>

              <div class="detail-actions">
                <button class="btn btn-ghost" @click="closeDetail">Cerrar</button>
                <router-link v-if="detail.pack?.vendor?.id" :to="`/aliado/${detail.pack.vendor.id}`" class="btn btn-outline" @click="closeDetail">Ver perfil del aliado</router-link>
                <router-link :to="{ name: 'service-booking', query: { pack: detail.pack?.id } }" class="btn btn-primary" @click="closeDetail">Reservar este servicio →</router-link>
              </div>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api'

const SVG_O = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
const ICON_PACK = `${SVG_O}<path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`

const CATEGORIES = [
  { value: 'sound',    label: 'Sonido',         icon: `${SVG_O}<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>` },
  { value: 'lights',   label: 'Iluminación',    icon: `${SVG_O}<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>` },
  { value: 'screens',  label: 'Pantallas',      icon: `${SVG_O}<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>` },
  { value: 'mics',     label: 'Microfonía',     icon: `${SVG_O}<path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>` },
  { value: 'dj_booth', label: 'DJ Booth',       icon: `${SVG_O}<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>` },
  { value: 'fx',       label: 'FX',             icon: `${SVG_O}<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><path d="M12 3v3"/><path d="M12 18v3"/><path d="M3 12h3"/><path d="M18 12h3"/></svg>` },
]
const EVENT_SIZES = [
  { value: 'small',  label: '<80' },
  { value: 'medium', label: '80-300' },
  { value: 'large',  label: '300+' },
]

const loading = ref(true)
const packs = ref([])
const bundles = ref([])
const sort = ref('popular')
const filters = reactive({
  category: '',
  event_size: '',
  vendor_type: '',
  includes_dj: '',
  max_price: null,
})
const detail = reactive({ open: false, pack: null })

const activeFiltersCount = computed(() => {
  let c = 0
  if (filters.category) c++
  if (filters.event_size) c++
  if (filters.vendor_type) c++
  if (filters.includes_dj) c++
  if (filters.max_price) c++
  return c
})

const sortedPacks = computed(() => {
  const list = [...packs.value]
  switch (sort.value) {
    case 'price_asc':  return list.sort((a, b) => Number(a.price) - Number(b.price))
    case 'price_desc': return list.sort((a, b) => Number(b.price) - Number(a.price))
    case 'rating':     return list.sort((a, b) => Number(b.rating_avg || 0) - Number(a.rating_avg || 0))
    case 'popular':
    default:           return list.sort((a, b) => (b.rentals_count || 0) - (a.rentals_count || 0))
  }
})

function categoryIcon(c) {
  return CATEGORIES.find(x => x.value === c)?.icon || ICON_PACK
}

function toggleCategory(v) {
  filters.category = filters.category === v ? '' : v
  fetchPacks()
}

function toggleEventSize(v) {
  filters.event_size = filters.event_size === v ? '' : v
  fetchPacks()
}

function resetFilters() {
  filters.category = ''
  filters.event_size = ''
  filters.vendor_type = ''
  filters.includes_dj = ''
  filters.max_price = null
  fetchPacks()
}

function openDetail(pack) {
  detail.pack = pack
  detail.open = true
}
function closeDetail() {
  detail.open = false
  detail.pack = null
}

function formatMoney(v) {
  return parseFloat(v || 0).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function hasFeatures(pack) {
  if (!pack) return false
  return !!(pack.includes_dj || pack.includes_technician || pack.includes_setup)
}

function stripBullet(item) {
  // Algunos aliados escriben los items con "•" o "-" delante; los limpiamos para mostrar más prolijo.
  return String(item || '').replace(/^\s*[•·\-*]\s*/, '').trim()
}

async function fetchPacks() {
  loading.value = true
  const params = {}
  if (filters.category) params.category = filters.category
  if (filters.event_size) params.event_size = filters.event_size
  if (filters.vendor_type) params.vendor_type = filters.vendor_type
  if (filters.includes_dj) params.includes_dj = filters.includes_dj
  if (filters.max_price) params.max_price = filters.max_price
  try {
    const { data } = await api.get('/production-packs/', { params })
    packs.value = Array.isArray(data) ? data : []
  } catch {
    packs.value = []
  }
  loading.value = false
}

async function fetchBundles() {
  try {
    const { data } = await api.get('/production-bundles/')
    bundles.value = Array.isArray(data) ? data : []
  } catch {
    bundles.value = []
  }
}

onMounted(() => {
  fetchPacks()
  fetchBundles()
})
</script>

<style scoped>
.packs-catalog { padding-top: 84px; padding-bottom: var(--space-12); min-height: 100vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 var(--space-4); }

.catalog-header { margin-bottom: var(--space-5); }
.catalog-cta { margin-top: var(--space-5); display: inline-flex; align-items: center; gap: 8px; }
.catalog-header h1 { font-family: 'Poppins', sans-serif; font-size: 2.2rem; margin-bottom: var(--space-2); }
.catalog-sub { color: var(--color-text-muted); max-width: 600px; line-height: 1.55; }

.hero-tag {
  display: inline-block;
  padding: 5px 14px;
  border-radius: 999px;
  background: rgba(193,216,47,0.10);
  border: 1px solid rgba(193,216,47,0.3);
  color: var(--color-primary);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-4);
  text-transform: uppercase;
}

.trust-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-5);
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}
.trust-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--color-text-secondary);
}
.trust-item > svg {
  flex-shrink: 0;
  color: var(--color-primary);
}
.trust-item strong { display: block; color: var(--color-text-primary); font-size: 0.9rem; }
.trust-item span { font-size: 0.78rem; color: var(--color-text-muted); }

/* Results bar */
.results-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}
.results-count { font-size: 0.92rem; color: var(--color-text-secondary); }
.results-count strong { color: var(--color-text-primary); font-size: 1.05rem; margin-right: 4px; }
.active-filters-tag { color: var(--color-primary); font-weight: 600; font-size: 0.85rem; }
.results-controls { display: flex; align-items: center; gap: var(--space-3); }
.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 0.85rem;
  cursor: pointer;
  text-decoration: underline;
  padding: 4px 0;
  font-weight: 600;
}
.btn-link:hover { opacity: 0.8; }
.sort-select {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  font-family: inherit;
}
.sort-select:focus { outline: none; border-color: var(--color-primary); }

/* Skeleton loading */
.loading-state { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--space-4); }
.skeleton-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  height: 360px;
  position: relative;
  overflow: hidden;
}
.skeleton-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
  animation: skeleton-shimmer 1.4s infinite;
}
@keyframes skeleton-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-12) var(--space-4);
  text-align: center;
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
}
.empty-state h3 { font-size: 1.1rem; color: var(--color-text-primary); margin: 0; }
.empty-state p { color: var(--color-text-muted); margin: 0; max-width: 400px; }

.catalog-layout { display: grid; grid-template-columns: 240px 1fr; gap: var(--space-6); align-items: flex-start; }

.filters-side {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}
.filters-side h3 { font-size: 1rem; margin-bottom: var(--space-3); }
.filter-group { margin-bottom: var(--space-4); }
.filter-label { display: block; color: var(--color-text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: var(--space-2); }
.chip-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.filter-chip {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.filter-chip:hover { border-color: var(--color-primary); }
.filter-chip.active { background: var(--color-primary); color: var(--color-bg); border-color: var(--color-primary); font-weight: 600; }
.input-field {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 8px 10px;
  color: var(--color-text-primary);
  font-size: 0.85rem;
  width: 100%;
}

.packs-main { min-width: 0; }
.packs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--space-4); }
.loading-state, .empty-state { text-align: center; color: var(--color-text-muted); padding: var(--space-8); }

.pack-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.pack-card:hover {
  transform: translateY(-3px);
  border-color: var(--color-primary);
  box-shadow: 0 14px 32px rgba(0,0,0,0.18);
}
.cat-pill {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(255,255,255,0.92);
  color: #0d0d0d;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.cat-pill svg { width: 16px; height: 16px; }

.pack-items-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}
.item-chip {
  font-size: 0.72rem;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(193,216,47,0.07);
  color: var(--color-text-secondary);
  border: 1px solid rgba(193,216,47,0.18);
  white-space: nowrap;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: border-color 0.15s, color 0.15s;
}
.pack-card:hover .item-chip { border-color: rgba(193,216,47,0.35); color: var(--color-text-primary); }
.item-chip.more {
  color: var(--color-primary);
  font-weight: 700;
  background: rgba(193,216,47,0.14);
  border-color: rgba(193,216,47,0.4);
}

.pack-card-price-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 6px;
}
.pack-rating {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  color: var(--color-text-secondary);
  font-weight: 600;
}
.pack-card-thumb {
  aspect-ratio: 16/10;
  background: linear-gradient(135deg, #2a1a3e, #1a3a2e);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.pack-card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.pack-emoji,
.pack-emoji-lg {
  opacity: 0.5;
  color: var(--color-text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.pack-emoji svg { width: 56px; height: 56px; }
.pack-emoji-lg svg { width: 96px; height: 96px; }
.chip-icon { display: inline-flex; align-items: center; vertical-align: -3px; margin-right: 2px; }
.chip-icon svg { width: 14px; height: 14px; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.vendor-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}
.vendor-badge.dj { background: rgba(245,158,11,0.85); color: #0d0d0d; }
.dj-pack-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(245,158,11,0.92);
  color: #0d0d0d;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.detail-note-dj {
  background: rgba(245,158,11,0.08);
  border-left: 3px solid #f59e0b;
  padding: 10px 12px;
  border-radius: 0 6px 6px 0;
  color: var(--color-text-secondary);
}
.detail-note-dj strong { color: #f59e0b; }
.detail-items li.ok.dj { color: #f59e0b; font-weight: 600; }
.pack-card-body { padding: var(--space-3); flex: 1; }
.pack-card-name { color: var(--color-text-primary); font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
.pack-card-vendor { color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px; }
.vendor-link {
  color: inherit;
  text-decoration: none;
  border-bottom: 1px dashed transparent;
  transition: color 0.15s, border-color 0.15s;
}
.vendor-link:hover {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.pack-card-price { color: var(--color-primary); font-weight: 800; font-size: 1.5rem; margin-bottom: 6px; }
.pack-card-meta { color: var(--color-text-muted); font-size: 0.75rem; display: flex; flex-wrap: wrap; gap: 8px; }
.pack-card-actions { padding: 0 var(--space-3) var(--space-3); }
.pack-card-actions .btn { width: 100%; }

/* Detail modal */
.detail-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.78);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-6) var(--space-4);
  overflow-y: auto;
}
.detail-modal {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  max-width: 640px;
  width: 100%;
  overflow: hidden;
  position: relative;
}
.detail-close {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 2;
  background: rgba(0,0,0,0.6);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
}
.detail-hero {
  aspect-ratio: 16/9;
  background: linear-gradient(135deg, #2a1a3e, #1a3a2e);
  display: flex;
  align-items: center;
  justify-content: center;
}
.detail-hero img { width: 100%; height: 100%; object-fit: cover; }
.detail-body { padding: var(--space-5) var(--space-5) var(--space-4); }
.detail-header { display: flex; align-items: flex-start; gap: var(--space-3); margin-bottom: var(--space-3); }
.detail-header-text { flex: 1; min-width: 0; }
.detail-body h2 { font-size: 1.5rem; margin: 0 0 4px; line-height: 1.2; }
.detail-vendor { color: var(--color-text-muted); font-size: 0.88rem; }
.vendor-tag { background: rgba(245,158,11,0.15); color: #f59e0b; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 6px; font-weight: 600; }

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

/* Features destacados (DJ / Técnico / Montaje) */
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
.feature-badge strong { font-size: 0.85rem; font-weight: 600; color: var(--color-text-primary); line-height: 1.15; }
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

/* Equipment list — clean checked items */
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

/* Info pills (tamaño / setup) */
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
.detail-note {
  background: rgba(193,216,47,0.06);
  border-left: 3px solid var(--color-primary);
  padding: var(--space-3);
  margin-top: var(--space-4);
  font-size: 0.85rem;
  color: var(--color-text-muted);
  border-radius: 0 8px 8px 0;
}
.detail-actions { display: flex; gap: var(--space-3); margin-top: var(--space-4); justify-content: flex-end; }

/* Bundles section */
.bundles-row { margin-bottom: var(--space-6); }
.bundles-h3 { color: #f59e0b; font-size: 1.1rem; margin-bottom: var(--space-3); }
.bundles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}
.bundle-card {
  background: var(--color-bg-card);
  border: 1px solid #f59e0b;
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
  box-shadow: 0 0 24px rgba(245,158,11,0.1);
}
.bundle-banner {
  background: linear-gradient(90deg, #f59e0b, #fb923c);
  color: #0d0d0d;
  padding: 8px var(--space-3);
  font-weight: 800;
  font-size: 0.78rem;
  letter-spacing: 2px;
  text-align: center;
}
.bundle-body { padding: var(--space-3); }
.bundle-name { color: var(--color-text-primary); font-weight: 700; font-size: 1.05rem; margin-bottom: 4px; }
.bundle-vendor { color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: var(--space-2); }
.bundle-pack-list { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: var(--space-3); }
.bundle-pack-chip { background: rgba(255,255,255,0.04); border: 1px solid var(--color-border); padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; color: var(--color-text-primary); }
.bundle-price-row { display: flex; align-items: baseline; gap: 10px; }
.bundle-price-current { color: var(--color-primary); font-weight: 800; font-size: 1.6rem; }
.bundle-price-old { color: var(--color-text-muted); text-decoration: line-through; font-size: 0.95rem; }

@media (max-width: 800px) {
  .catalog-layout { grid-template-columns: 1fr; }
}
</style>
