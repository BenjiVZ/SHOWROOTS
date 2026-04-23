<template>
  <div class="venues-page">
    <div class="container">
      <div class="venues-header animate-fade-in-up">
        <h1 class="section-title">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          Venues
        </h1>
        <p class="section-subtitle">Encuentra el lugar perfecto para tu evento</p>
      </div>

      <!-- Filters -->
      <div class="venues-filters glass animate-fade-in-up" style="animation-delay: 0.1s">
        <div class="filter-item">
          <label class="label">Tipo</label>
          <select v-model="filters.venue_type" class="input-field" @change="fetchVenues">
            <option value="">Todos</option>
            <option value="club">Club</option>
            <option value="salon">Salón</option>
            <option value="hotel">Hotel</option>
            <option value="restaurant">Restaurante</option>
            <option value="outdoor">Aire libre</option>
            <option value="other">Otro</option>
          </select>
        </div>
        <div class="filter-item">
          <label class="label">Ciudad</label>
          <input v-model="filters.city" type="text" class="input-field" placeholder="Buscar ciudad..." @input="debounceSearch" />
        </div>
        <div class="filter-item">
          <label class="label">Capacidad mínima</label>
          <input v-model="filters.capacity_min" type="number" class="input-field" placeholder="0" @input="debounceSearch" />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="venues-grid">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <div class="skeleton" style="height: 200px;"></div>
          <div style="padding: var(--space-4);">
            <div class="skeleton" style="height: 20px; width: 60%; margin-bottom: var(--space-3);"></div>
            <div class="skeleton" style="height: 16px; width: 80%;"></div>
          </div>
        </div>
      </div>

      <!-- Venues Grid -->
      <div v-else-if="venues.length" class="venues-grid animate-fade-in-up" style="animation-delay: 0.2s">
        <div v-for="venue in venues" :key="venue.id" class="venue-card card">
          <div class="venue-image">
            <img :src="venue.photos?.[0] || placeholderVenue" :alt="venue.name" loading="lazy" />
            <span class="badge venue-type-badge">{{ venueTypeLabel(venue.venue_type) }}</span>
          </div>
          <div class="venue-body">
            <h3>{{ venue.name }}</h3>
            <div class="venue-meta">
              <span class="venue-location">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ venue.city }}
              </span>
              <span class="venue-capacity">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
                {{ venue.capacity }} personas
              </span>
            </div>
            <p v-if="venue.description" class="venue-desc">{{ venue.description }}</p>
            <div class="venue-amenities" v-if="venue.amenities?.length">
              <span v-for="(a, i) in venue.amenities.slice(0, 4)" :key="i" class="badge badge-cyan">{{ a }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--color-text-muted); margin-bottom: var(--space-4);"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <h3>No se encontraron venues</h3>
        <p>Prueba con otros filtros de búsqueda.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const venues = ref([])
const loading = ref(true)
let debounceTimer = null

const filters = ref({ venue_type: '', city: '', capacity_min: '' })

const placeholderVenue = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250"%3E%3Cdefs%3E%3ClinearGradient id="g" x1="0" y1="0" x2="1" y2="1"%3E%3Cstop offset="0%25" stop-color="%23C1D82F" stop-opacity="0.1"/%3E%3Cstop offset="100%25" stop-color="%23E85D4A" stop-opacity="0.06"/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill="%230A0A0A" width="400" height="250"/%3E%3Crect fill="url(%23g)" width="400" height="250"/%3E%3Cpath d="M175 100l25-20 25 20v30a3 3 0 01-3 3h-44a3 3 0 01-3-3z" fill="none" stroke="%23C1D82F" stroke-width="1.5" opacity="0.5"/%3E%3C/svg%3E'

function venueTypeLabel(type) {
  const map = { club: 'Club', salon: 'Salón', hotel: 'Hotel', restaurant: 'Restaurante', outdoor: 'Aire libre', other: 'Otro' }
  return map[type] || type
}

async function fetchVenues() {
  loading.value = true
  try {
    const params = {}
    Object.entries(filters.value).forEach(([k, v]) => { if (v) params[k] = v })
    const res = await api.get('/venues/', { params })
    venues.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchVenues, 400)
}

onMounted(fetchVenues)
</script>

<style scoped>
.venues-page {
  padding-top: var(--space-4);
  min-height: 100vh;
  padding-bottom: var(--space-16);
}

.venues-header {
  margin-bottom: var(--space-8);
}

.venues-header h1 {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.venues-filters {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-10);
}

.venues-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--space-6);
}

.skeleton-card {
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
}

.venue-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.venue-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.venue-card:hover .venue-image img {
  transform: scale(1.04);
}

.venue-type-badge {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
}

.venue-body {
  padding: var(--space-5);
}

.venue-body h3 {
  font-size: var(--font-size-lg);
  margin-bottom: var(--space-3);
}

.venue-meta {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-3);
}

.venue-location,
.venue-capacity {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.venue-location svg { color: var(--color-primary-light); }
.venue-capacity svg { color: var(--color-secondary); }

.venue-desc {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  margin-bottom: var(--space-4);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 300;
}

.venue-amenities {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.empty-state {
  text-align: center;
  padding: var(--space-16);
}

.empty-state h3 { font-size: var(--font-size-xl); margin-bottom: var(--space-2); }
.empty-state p { color: var(--color-text-muted); font-size: var(--font-size-sm); }

@media (max-width: 768px) {
  .venues-filters { grid-template-columns: 1fr; }
  .venues-grid { grid-template-columns: 1fr; }
}
</style>
