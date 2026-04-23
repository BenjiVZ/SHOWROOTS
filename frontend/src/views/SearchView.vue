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
          <input v-model="filters.city" class="input-field" placeholder="Ej: Caracas" @input="debounceSearch" />
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
      </aside>

      <!-- Results -->
      <main class="results">
        <div class="results-header">
          <h1 class="section-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            Buscar Talentos
          </h1>
          <div class="sort-control">
            <label class="label" style="margin: 0">Ordenar por</label>
            <select v-model="filters.ordering" class="input-field" @change="fetchTalents" style="min-width: 180px">
              <option value="-rating_avg">Mejor valorados</option>
              <option value="-total_bookings">Más reservados</option>
              <option value="price_min">Menor precio</option>
              <option value="-price_min">Mayor precio</option>
            </select>
          </div>
        </div>

        <p class="results-count" v-if="!loading">{{ totalCount }} resultados encontrados</p>

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
import { ref, onMounted } from 'vue'
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

const filters = ref({
  talent_type: route.query.talent_type || '',
  genre: route.query.genre || '',
  city: route.query.city || '',
  price_max: '',
  min_rating: '',
  ordering: '-rating_avg',
})

async function fetchTalents() {
  loading.value = true
  try {
    const params = { page: page.value }
    Object.entries(filters.value).forEach(([k, v]) => { if (v) params[k] = v })
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
  filters.value = { talent_type: '', genre: '', city: '', price_max: '', min_rating: '', ordering: '-rating_avg' }
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
</style>
