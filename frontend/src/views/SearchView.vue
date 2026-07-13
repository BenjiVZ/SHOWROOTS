<template>
  <div class="search-page">
    <div class="container search-layout">
      <!-- Sidebar -->
      <aside class="filters-sidebar glass">
        <div class="filters-header">
          <h3>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            Filtros
          </h3>
          <button class="btn btn-ghost btn-sm" @click="clearFilters">Limpiar</button>
        </div>

        <div class="filter-group">
          <label class="label">Tipo de talento</label>
          <select v-model="filters.talent_type" class="input-field" @change="fetchTalents">
            <option value="">Todos</option>
            <option value="dj">DJ</option>
            <option value="musician">Músico</option>
            <option value="band">Banda</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="label">Género musical</label>
          <select v-model="filters.genre" class="input-field" @change="fetchTalents">
            <option value="">Todos</option>
            <option v-for="g in genres" :key="g.id" :value="g.slug">{{ g.name }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="label">Ciudad</label>
          <input v-model="filters.city" class="input-field" placeholder="Ej: Panamá" @input="debounceSearch" />
        </div>

        <div class="filter-group">
          <label class="label">Precio máximo ($)</label>
          <input v-model="filters.price_max" type="number" class="input-field" placeholder="Sin límite" @input="debounceSearch" />
        </div>

        <div class="filter-group">
          <label class="label">Rating mínimo</label>
          <select v-model="filters.min_rating" class="input-field" @change="fetchTalents">
            <option value="">Cualquiera</option>
            <option value="3">3+ estrellas</option>
            <option value="4">4+ estrellas</option>
            <option value="4.5">4.5+ estrellas</option>
          </select>
        </div>

        <!-- Tier -->
        <div class="filter-group">
          <label class="label">Tier</label>
          <div class="chip-row">
            <button v-for="t in tierOptions" :key="t.value" type="button"
              class="filter-chip" :class="{ active: filters.talent_level === t.value }"
              @click="toggleTier(t.value)">{{ t.label }}</button>
          </div>
        </div>

        <!-- Experience level -->
        <div class="filter-group">
          <label class="label">Experiencia</label>
          <select v-model="filters.experience_level" class="input-field" @change="fetchTalents">
            <option value="">Cualquiera</option>
            <option value="beginner">Principiante</option>
            <option value="semi_professional">Semiprofesional</option>
            <option value="professional">Profesional</option>
            <option value="expert">Experto</option>
          </select>
        </div>

        <!-- Languages -->
        <div class="filter-group">
          <label class="label">Idiomas</label>
          <div class="chip-row">
            <button v-for="lang in languageOptions" :key="lang" type="button"
              class="filter-chip" :class="{ active: filters.languagesArr.includes(lang) }"
              @click="toggleMulti('languagesArr', lang)">{{ lang }}</button>
          </div>
        </div>

        <!-- Event types -->
        <div class="filter-group">
          <label class="label">Tipo de evento</label>
          <div class="chip-row">
            <button v-for="et in eventTypeOptions" :key="et.value" type="button"
              class="filter-chip filter-chip-event" :class="{ active: filters.eventTypesArr.includes(et.value) }"
              @click="toggleMulti('eventTypesArr', et.value)">
              <span class="et-icon" v-html="et.icon"></span> {{ et.label }}
            </button>
          </div>
        </div>

        <!-- Mood -->
        <div class="filter-group">
          <label class="label">Vibe / mood</label>
          <div class="chip-row">
            <button v-for="m in moodOptions" :key="m" type="button"
              class="filter-chip filter-chip-mood" :class="{ active: filters.moodsArr.includes(m) }"
              @click="toggleMulti('moodsArr', m)">{{ m }}</button>
          </div>
        </div>
      </aside>

      <!-- Results -->
      <main class="results">
        <div class="results-header">
          <h1 class="section-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            Buscar Talentos
          </h1>
          <div class="sort-control" ref="sortRef">
            <label class="label" style="margin: 0">Ordenar por</label>
            <div class="custom-select" :class="{ open: sortOpen }">
              <button type="button" class="custom-select-trigger" @click="sortOpen = !sortOpen">
                <span class="cs-icon" v-html="activeSortOption.icon"></span>
                <span class="cs-label">{{ activeSortOption.label }}</span>
                <svg class="cs-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
              </button>
              <Transition name="cs-fade">
                <ul v-if="sortOpen" class="custom-select-menu" role="listbox">
                  <li
                    v-for="opt in sortOptions"
                    :key="opt.value"
                    class="custom-select-option"
                    :class="{ selected: filters.ordering === opt.value }"
                    @click="selectSort(opt.value)"
                  >
                    <span class="cs-icon" v-html="opt.icon"></span>
                    <span class="cs-option-text">
                      <strong>{{ opt.label }}</strong>
                      <small>{{ opt.desc }}</small>
                    </span>
                    <svg v-if="filters.ordering === opt.value" class="cs-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </li>
                </ul>
              </Transition>
            </div>
          </div>
        </div>

        <p class="results-count" v-if="!loading">{{ totalCount }} resultados encontrados</p>

        <!-- Banner: publicar solicitud abierta -->
        <router-link to="/open-gig/new" class="open-gig-banner">
          <div class="ogb-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
          </div>
          <div class="ogb-text">
            <strong>¿No sabes a quién elegir?</strong>
            <span>Publica tu solicitud y los DJs te enviarán ofertas — Premium primero, después Pro y Standard.</span>
          </div>
          <span class="ogb-cta">
            Publicar
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
          </span>
        </router-link>

        <!-- Loading skeleton -->
        <div v-if="loading" class="talents-grid">
          <div v-for="i in 6" :key="i" class="skeleton-card">
            <div class="skeleton" style="height: 220px;"></div>
            <div style="padding: var(--space-4);">
              <div class="skeleton" style="height: 20px; width: 70%; margin-bottom: var(--space-3);"></div>
              <div class="skeleton" style="height: 16px; width: 90%; margin-bottom: var(--space-2);"></div>
              <div class="skeleton" style="height: 16px; width: 50%;"></div>
            </div>
          </div>
        </div>

        <!-- Results grid -->
        <div v-else-if="talents.length" class="talents-grid">
          <TalentCard v-for="talent in talents" :key="talent.id" :talent="talent" />
        </div>

        <div v-else class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--color-text-muted); margin-bottom: var(--space-4);"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
          <h3>No se encontraron resultados</h3>
          <p>Prueba con otros filtros o busca en todas las categorías.</p>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button class="btn btn-secondary btn-sm" :disabled="page <= 1" @click="goPage(page - 1)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
            Anterior
          </button>
          <span class="page-info">{{ page }} / {{ totalPages }}</span>
          <button class="btn btn-secondary btn-sm" :disabled="page >= totalPages" @click="goPage(page + 1)">
            Siguiente
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import TalentCard from '@/components/talent/TalentCard.vue'

const route = useRoute()
const genres = ref([])
const talents = ref([])
const loading = ref(true)
const page = ref(1)
const totalCount = ref(0)
const totalPages = ref(1)
let debounceTimer = null

// Custom sort dropdown
const sortRef = ref(null)
const sortOpen = ref(false)
const sortOptions = [
  {
    value: '-rating_avg',
    label: 'Mejor valorados',
    desc: 'Por rating de reseñas',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
  },
  {
    value: '-total_bookings',
    label: 'Más reservados',
    desc: 'Por número de eventos',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
  },
  {
    value: 'price_min',
    label: 'Menor precio',
    desc: 'Más económicos primero',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
  },
  {
    value: '-price_min',
    label: 'Mayor precio',
    desc: 'Premium primero',
    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
  },
]
const activeSortOption = computed(() =>
  sortOptions.find(o => o.value === filters.value.ordering) || sortOptions[0]
)

function selectSort(value) {
  filters.value.ordering = value
  sortOpen.value = false
  fetchTalents()
}

function onSortDocClick(e) {
  if (!sortOpen.value) return
  if (sortRef.value && !sortRef.value.contains(e.target)) sortOpen.value = false
}

onMounted(() => document.addEventListener('mousedown', onSortDocClick))
onUnmounted(() => document.removeEventListener('mousedown', onSortDocClick))

const filters = ref({
  talent_type: route.query.talent_type || '',
  genre: route.query.genre || '',
  city: route.query.city || '',
  price_max: '',
  min_rating: '',
  ordering: '-rating_avg',
  talent_level: route.query.tier || '',
  experience_level: '',
  languagesArr: [],
  eventTypesArr: [],
  moodsArr: [],
})

const tierOptions = [
  { value: 'standard', label: 'Standard' },
  { value: 'pro', label: '★ Pro' },
  { value: 'premium', label: '★★ Premium' },
]
const languageOptions = ['Español', 'Inglés', 'Portugués', 'Francés']
const _et = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
const eventTypeOptions = [
  { value: 'wedding',   icon: `${_et}<circle cx="9" cy="15" r="5"/><circle cx="16" cy="15" r="5"/><path d="M7 9l2-5h6l2 5"/></svg>`,                                                                       label: 'Bodas' },
  { value: 'corporate', icon: `${_et}<rect x="4" y="2" width="16" height="20"/><line x1="8" y1="6" x2="8" y2="6.01"/><line x1="12" y1="6" x2="12" y2="6.01"/><line x1="16" y1="6" x2="16" y2="6.01"/></svg>`, label: 'Corporativo' },
  { value: 'birthday',  icon: `${_et}<path d="M20 21v-8a2 2 0 00-2-2H6a2 2 0 00-2 2v8"/><path d="M4 16s1.5-2 4-2 3.5 2 4 2 1.5-2 4-2 4 2 4 2"/><line x1="2" y1="21" x2="22" y2="21"/><line x1="12" y1="4" x2="12" y2="11"/></svg>`, label: 'Cumpleaños' },
  { value: 'cocktail',  icon: `${_et}<path d="M5 3h14l-7 9z"/><path d="M12 12v9"/><path d="M8 21h8"/></svg>`,                                                                                              label: 'Cocktail' },
  { value: 'club',      icon: `${_et}<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/></svg>`,                                                                                                 label: 'Club' },
  { value: 'launch',    icon: `${_et}<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>`, label: 'Lanzamiento' },
]
const moodOptions = ['Boda elegante', 'After party', 'Cocktail formal', 'Cumpleaños hype', 'Lounge', 'High energy']

function toggleTier(value) {
  filters.value.talent_level = filters.value.talent_level === value ? '' : value
  fetchTalents()
}

function toggleMulti(key, value) {
  const arr = filters.value[key]
  const idx = arr.indexOf(value)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(value)
  fetchTalents()
}

async function fetchTalents() {
  loading.value = true
  try {
    const params = { page: page.value }
    // Mapeo: arrays → CSV; resto directo
    const simpleKeys = ['talent_type', 'genre', 'city', 'price_max', 'min_rating', 'ordering', 'talent_level', 'experience_level']
    simpleKeys.forEach(k => {
      if (filters.value[k]) params[k] = filters.value[k]
    })
    if (filters.value.languagesArr.length) params.languages = filters.value.languagesArr.join(',')
    if (filters.value.eventTypesArr.length) params.event_types = filters.value.eventTypesArr.join(',')
    if (filters.value.moodsArr.length) params.moods = filters.value.moodsArr.join(',')

    const res = await api.get('/talents/', { params })
    talents.value = res.data.results || res.data
    totalCount.value = res.data.count || talents.value.length
    totalPages.value = Math.ceil(totalCount.value / 12)
  } catch (err) {
    console.error('Search error:', err)
  } finally {
    loading.value = false
  }
}

function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchTalents, 400)
}

function clearFilters() {
  filters.value = {
    talent_type: '', genre: '', city: '', price_max: '', min_rating: '', ordering: '-rating_avg',
    talent_level: '', experience_level: '',
    languagesArr: [], eventTypesArr: [], moodsArr: [],
  }
  page.value = 1
  fetchTalents()
}

function goPage(p) {
  page.value = p
  fetchTalents()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  try {
    const res = await api.get('/genres/')
    genres.value = res.data
  } catch (e) { console.error(e) }
  fetchTalents()
})
</script>

<style scoped>
.et-icon { display: inline-flex; align-items: center; margin-right: 4px; color: var(--color-primary); vertical-align: -3px; }

.search-page {
  padding-top: var(--space-4);
  min-height: 100vh;
}

.search-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: var(--space-8);
  align-items: flex-start;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.filter-chip:hover { border-color: var(--color-border-hover); }
.filter-chip.active {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(193,216,47,0.08);
}
.filter-chip-event.active {
  border-color: #f59e0b;
  color: #f59e0b;
  background: rgba(245,158,11,0.08);
}
.filter-chip-mood.active {
  border-color: #ec4899;
  color: #ec4899;
  background: rgba(236,72,153,0.08);
}

.filters-sidebar {
  position: sticky;
  top: 100px;
  padding: var(--space-6);
  border-radius: var(--radius-xl);
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.filters-header h3 {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-base);
}

.filter-group {
  margin-bottom: var(--space-5);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.results-header h1 {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-2xl);
}

.sort-control {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
}

/* Custom select dropdown — Ordenar por */
.custom-select { position: relative; min-width: 220px; }
.custom-select-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: var(--color-bg-card);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.custom-select-trigger:hover { border-color: var(--color-border-hover); }
.custom-select.open .custom-select-trigger {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(193,216,47,0.08);
}
.cs-icon {
  display: flex;
  align-items: center;
  color: var(--color-text-muted);
  flex-shrink: 0;
}
.cs-label { flex: 1; text-align: left; }
.cs-chevron {
  color: var(--color-text-muted);
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}
.custom-select.open .cs-chevron {
  transform: rotate(180deg);
  color: var(--color-primary);
}

.custom-select-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 100;
  margin: 0;
  padding: 6px;
  list-style: none;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 12px 32px rgba(0,0,0,0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.custom-select-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.custom-select-option:hover {
  background: rgba(193,216,47,0.06);
  color: var(--color-text-primary);
}
.custom-select-option:hover .cs-icon { color: var(--color-primary); }
.custom-select-option.selected {
  background: rgba(193,216,47,0.1);
  color: var(--color-primary);
}
.custom-select-option.selected .cs-icon { color: var(--color-primary); }
.cs-option-text { flex: 1; min-width: 0; }
.cs-option-text strong {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 1px;
}
.cs-option-text small {
  display: block;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}
.custom-select-option.selected .cs-option-text small { color: rgba(193,216,47,0.7); }
.cs-check {
  color: var(--color-primary);
  flex-shrink: 0;
}

.cs-fade-enter-active, .cs-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.cs-fade-enter-from, .cs-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.results-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-6);
}

.talents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-6);
}

.skeleton-card {
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
}

.empty-state {
  text-align: center;
  padding: var(--space-16);
}

.empty-state h3 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-2);
}

.empty-state p {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-12) 0;
}

.page-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .search-layout {
    grid-template-columns: 1fr;
  }
  .filters-sidebar {
    position: static;
  }
}

/* Banner de solicitud abierta */
.open-gig-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  margin: 16px 0 24px;
  border-radius: var(--radius-xl, 14px);
  background:
    linear-gradient(135deg, var(--color-primary-ultra-light), transparent 60%),
    linear-gradient(300deg, var(--color-accent-light), transparent 55%);
  border: 1px solid var(--color-border);
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s, border-color 0.15s;
}
.open-gig-banner:hover {
  transform: translateY(-1px);
  border-color: var(--color-border-hover);
}
.ogb-icon {
  flex-shrink: 0;
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  border-radius: 50%;
  color: var(--color-bg-primary);
}
.ogb-text { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ogb-text strong { color: var(--color-text-primary); font-size: 0.98rem; }
.ogb-text span { color: var(--color-text-muted); font-size: 0.85rem; line-height: 1.4; }
.ogb-cta {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--color-primary); color: var(--color-bg-primary);
  padding: 8px 14px; border-radius: 999px;
  font-weight: 700; font-size: 0.85rem;
  white-space: nowrap;
}
@media (max-width: 600px) {
  .open-gig-banner { flex-direction: column; text-align: center; }
}
</style>
