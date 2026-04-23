<template>
  <router-link :to="`/talent/${talent.id}`" class="talent-card card" :aria-label="`Ver perfil de ${talent.stage_name}`">
    <div class="card-image">
      <img :src="talent.cover_photo || placeholderImg" :alt="talent.stage_name" loading="lazy" />
      <div class="card-overlay">
        <span class="talent-type badge" :class="typeClass">{{ typeLabel }}</span>
        <span v-if="talent.is_featured" class="featured-badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          Destacado
        </span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-header">
        <h3 class="stage-name">{{ talent.stage_name }}</h3>
        <div class="rating" v-if="talent.total_reviews > 0">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          <span class="rating-value">{{ Number(talent.rating_avg).toFixed(1) }}</span>
          <span class="rating-count">({{ talent.total_reviews }})</span>
        </div>
      </div>

      <p class="tagline" v-if="talent.tagline">{{ talent.tagline }}</p>

      <div class="genres" v-if="talent.genres?.length">
        <span v-for="genre in talent.genres.slice(0, 3)" :key="genre.id" class="badge">
          {{ genre.name }}
        </span>
        <span v-if="talent.genres.length > 3" class="badge badge-cyan">
          +{{ talent.genres.length - 3 }}
        </span>
      </div>

      <div class="card-footer">
        <div class="location" v-if="talent.city">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          {{ talent.city }}
        </div>
        <div class="price" v-if="talent.price_min">
          Desde <strong>${{ talent.price_min }}</strong>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  talent: { type: Object, required: true }
})

const placeholderImg = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Cdefs%3E%3ClinearGradient id="g" x1="0" y1="0" x2="1" y2="1"%3E%3Cstop offset="0%25" stop-color="%23C1D82F" stop-opacity="0.15"/%3E%3Cstop offset="100%25" stop-color="%23E85D4A" stop-opacity="0.08"/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill="%230A0A0A" width="400" height="300"/%3E%3Crect fill="url(%23g)" width="400" height="300"/%3E%3Cpath d="M175 135v-6a25 25 0 0150 0v6M225 139a5 5 0 01-5 5h-3a5 5 0 01-5-5v-8a5 5 0 015-5h8zM175 139a5 5 0 005 5h3a5 5 0 005-5v-8a5 5 0 00-5-5h-8z" fill="none" stroke="%23C1D82F" stroke-width="1.5" opacity="0.5"/%3E%3C/svg%3E'

const typeLabel = computed(() => {
  const labels = { dj: 'DJ', musician: 'Músico', band: 'Banda' }
  return labels[props.talent.talent_type] || props.talent.talent_type
})

const typeClass = computed(() => {
  const classes = { dj: '', musician: 'badge-cyan', band: 'badge-accent' }
  return classes[props.talent.talent_type] || ''
})
</script>

<style scoped>
.talent-card {
  display: block;
  text-decoration: none;
  color: inherit;
}

.card-image {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.talent-card:hover .card-image img {
  transform: scale(1.06);
}

.card-overlay {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  right: var(--space-3);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.featured-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: #FBBF24;
  background: rgba(0, 0, 0, 0.6);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  backdrop-filter: blur(8px);
}

.card-body {
  padding: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.stage-name {
  font-family: var(--font-heading);
  font-size: var(--font-size-lg);
}

.rating {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-shrink: 0;
}

.rating-value { font-weight: 600; font-size: var(--font-size-sm); }
.rating-count { color: var(--color-text-muted); font-size: var(--font-size-xs); }

.tagline {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 300;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.location {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.location svg { color: var(--color-primary-light); }

.price {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.price strong {
  color: var(--color-accent);
  font-weight: 700;
}
</style>
