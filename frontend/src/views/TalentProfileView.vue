<template>
  <div v-if="talent" class="profile-page">
    <!-- Cover -->
    <div ref="coverRef" class="profile-cover">
      <img :src="talent.cover_photo || placeholderCover" :alt="talent.stage_name" @error="onImgError" />
      <div v-if="talent.cover_photo" class="cover-frost" :style="{ opacity: coverFrost }"></div>
      <div class="cover-overlay"></div>
      <div class="hero-badges">
        <span class="hero-trust-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          Pago protegido por Pulsar
        </span>
        <button class="hero-share-btn" @click="shareProfile">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
          {{ shareLabel === 'Compartir perfil' ? 'Compartir' : shareLabel }}
        </button>
      </div>
    </div>

    <div class="container profile-layout">
      <!-- Sidebar -->
      <aside class="profile-sidebar animate-fade-in-up">
        <div class="profile-card glass" :class="`tier-card-${talent.talent_level || 'standard'}`">
          <div class="avatar-wrap">
            <img :src="talent.user?.avatar || placeholderAvatar" :alt="talent.stage_name" class="avatar" @error="onImgError" />
            <span v-if="talent.is_available" class="status-dot" title="Disponible"></span>
          </div>
          <h1>{{ talent.stage_name }}</h1>
          <p class="talent-type-label">
            <span class="badge" :class="typeClass">{{ typeLabel }}</span>
            <span v-if="talent.talent_level" class="badge tier-badge premium-tooltip-wrap" :class="`tier-${talent.talent_level}`">
              {{ tierLabel }}
              <span v-if="talent.talent_level === 'premium'" class="premium-tooltip">
                Talento verificado · 20+ eventos completados · Top performer · Curado por Pulsar
              </span>
              <span v-else-if="talent.talent_level === 'pro'" class="premium-tooltip">
                10+ eventos completados · Rating ≥ 4.5 · Comisión reducida
              </span>
            </span>
          </p>
          <div v-if="talent.total_reviews > 0" class="profile-rating">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <strong>{{ Number(talent.rating_avg).toFixed(1) }}</strong>
            <span>({{ talent.total_reviews }} reseñas)</span>
          </div>

          <!-- Stats row dentro del sidebar (matching mockup) -->
          <div v-if="sidebarStats.length" class="sidebar-stats-row">
            <div v-for="s in sidebarStats" :key="s.label" class="sidebar-stat">
              <div class="sidebar-stat-num">{{ s.value }}</div>
              <div class="sidebar-stat-label">{{ s.label }}</div>
            </div>
          </div>

          <div class="profile-details">
            <div v-if="talent.city" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ talent.city }}
            </div>
            <div v-if="talent.years_experience" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              {{ talent.years_experience }} años de experiencia
            </div>
            <!-- Pricing block destacado (matching mockup) -->
            <div v-if="talent.hourly_rate || talent.price_min" class="pricing-block">
              <div class="pricing-main">
                <strong v-if="talent.price_min">${{ Number(talent.price_min).toFixed(0) }}</strong>
                <strong v-else>${{ Number(talent.hourly_rate * 4).toFixed(0) }}</strong>
                <span>desde / 4 hrs</span>
              </div>
              <div class="pricing-sub">
                ${{ Number(talent.hourly_rate || 0).toFixed(0) }}/hr adicional · Add-ons cotizan aparte
                <span v-if="isHighSeasonPremium" class="high-season-pill" title="Alta temporada: +15% según política Pulsar">+15% alta temp.</span>
              </div>
            </div>
            <div v-if="talent.price_min" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
              Desde <strong>${{ talent.price_min }}</strong>{{ talent.price_max ? ` — $${talent.price_max}` : '' }}
            </div>
            <div v-if="talent.total_bookings" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              {{ talent.total_bookings }} eventos realizados
            </div>
            <div v-if="languagesList.length" class="detail-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
              {{ languagesList.join(', ') }}
            </div>
          </div>

          <!-- Disponibilidad rápida -->
          <div v-if="quickAvailability" class="quick-avail">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            Disponible: {{ quickAvailability }}
          </div>

          <router-link :to="`/talent/${talent.id}/book`" class="btn btn-cta btn-lg sidebar-cta">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Reservar Ahora
          </router-link>
          <button class="btn btn-ghost sidebar-cta-secondary" @click="openInquiry">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            Enviar consulta
          </button>

          <div class="sidebar-trust">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            <span>Tu pago queda en custodia hasta 24h después del evento. Si no se presenta, reembolso 100%.</span>
          </div>
        </div>
      </aside>

      <!-- Main -->
      <main class="profile-main animate-fade-in-up" style="animation-delay: 0.1s">
        <!-- Stats Dashboard -->
        <section v-if="stats.length" class="stats-strip">
          <div v-for="s in stats" :key="s.key" class="stat-card-public">
            <div class="stat-icon-wrap" v-html="s.icon"></div>
            <div class="stat-content">
              <div class="stat-value-public">{{ s.value }}<span v-if="s.suffix" class="stat-suffix">{{ s.suffix }}</span></div>
              <div class="stat-label-public">{{ s.label }}</div>
            </div>
          </div>
        </section>

        <!-- Video en vivo -->
        <section v-if="videoMedia.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
            Video en vivo
            <span class="section-count">{{ videoMedia.length }}</span>
          </h2>
          <div class="video-grid">
            <div v-for="vid in videoMedia" :key="vid.id" class="video-card">
              <div class="video-iframe-wrap">
                <iframe
                  v-if="videoEmbedUrl(vid.url)"
                  :src="videoEmbedUrl(vid.url)"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                  loading="lazy"
                ></iframe>
                <a v-else :href="vid.url" target="_blank" rel="noopener" class="video-fallback">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                  Ver video
                </a>
              </div>
              <p v-if="vid.title" class="video-title">{{ vid.title }}</p>
            </div>
          </div>
        </section>

        <!-- Mixes / Audio -->
        <section v-if="audioMedia.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            Escucha mis sets
            <span class="section-count">{{ audioMedia.length }}</span>
            <a v-if="audioMedia.length > 3 && talent.soundcloud" :href="talent.soundcloud" target="_blank" rel="noopener" class="section-link-action">Ver todos →</a>
          </h2>
          <div class="mixes-list">
            <div v-for="mix in audioMedia" :key="mix.id" class="mix-embed" :class="{ 'mix-featured': mix.is_cover && talent.talent_level === 'premium' }">
              <div v-if="mix.is_cover && talent.talent_level === 'premium'" class="mix-featured-badge">
                ★ MIX DESTACADO
              </div>
              <div v-if="mix.title" class="mix-title-bar">{{ mix.title }}</div>
              <div class="mix-iframe-wrap" :class="embedClass(mix.url)">
                <iframe
                  v-if="embedUrl(mix.url)"
                  :src="embedUrl(mix.url)"
                  frameborder="0"
                  allow="autoplay; encrypted-media"
                  allowfullscreen
                  loading="lazy"
                ></iframe>
                <a v-else :href="mix.url" target="_blank" rel="noopener" class="mix-fallback">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                  Escuchar en {{ embedProvider(mix.url) || 'plataforma externa' }}
                </a>
              </div>
            </div>
          </div>
        </section>

        <!-- Bio -->
        <section v-if="talent.bio" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>
            Sobre mí
          </h2>
          <p>{{ talent.bio }}</p>
        </section>

        <!-- Tipos de eventos -->
        <section v-if="eventTypeTags.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Tipos de eventos
          </h2>
          <div class="genres-list">
            <span v-for="e in eventTypeTags" :key="e.value" class="badge badge-event">
              <span class="badge-event-icon">{{ e.icon }}</span>{{ e.label }}
            </span>
          </div>
        </section>

        <!-- Paquetes -->
        <section v-if="packs.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
            Paquetes
            <router-link :to="`/talent/${talent.id}/book`" class="section-link-action">Personalizar →</router-link>
          </h2>
          <div class="packs-grid">
            <div v-for="p in packs" :key="p.id" class="pack-card" :class="{ featured: p.is_featured }">
              <div v-if="p.is_featured" class="pack-popular">POPULAR</div>
              <div class="pack-name">{{ p.name }}</div>
              <div class="pack-price">
                <span v-if="p.price">${{ Number(p.price).toFixed(0) }}</span>
                <span v-else>{{ p.price_label || 'Cotizar' }}</span>
                <span v-if="p.duration_hours" class="pack-duration"> · {{ Number(p.duration_hours) }} hrs</span>
              </div>
              <ul v-if="p.included_items && p.included_items.length" class="pack-includes">
                <li v-for="(item, idx) in p.included_items" :key="idx">{{ item }}</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Genres & Mood -->
        <section v-if="talent.genres?.length || moodTags.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            Géneros & estilo
          </h2>
          <div v-if="talent.genres?.length" class="tag-block">
            <span class="tag-block-label">Géneros</span>
            <div class="genres-list">
              <span v-for="g in talent.genres" :key="g.id" class="badge">{{ g.name }}</span>
            </div>
          </div>
          <div v-if="moodTags.length" class="tag-block">
            <span class="tag-block-label">Vibe / mood</span>
            <div class="genres-list">
              <span v-for="m in moodTags" :key="m" class="badge badge-mood">{{ m }}</span>
            </div>
          </div>
        </section>

        <!-- Equipamiento split -->
        <section v-if="equipmentBrings.length || equipmentNotIncluded.length || talent.equipment_description" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>
            Equipamiento
          </h2>
          <div class="equip-split">
            <div v-if="equipmentBrings.length" class="equip-col equip-yes">
              <h4>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                Yo traigo
              </h4>
              <ul>
                <li v-for="(item, idx) in equipmentBrings" :key="'b'+idx">{{ item }}</li>
              </ul>
            </div>
            <div v-if="equipmentNotIncluded.length" class="equip-col equip-no">
              <h4>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                No incluido
              </h4>
              <ul>
                <li v-for="(item, idx) in equipmentNotIncluded" :key="'n'+idx">{{ item }}</li>
              </ul>
            </div>
          </div>
          <p v-if="talent.equipment_description" class="equip-description">{{ talent.equipment_description }}</p>
        </section>

        <!-- Calendario público de disponibilidad -->
        <section v-if="hasAvailabilityData" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Disponibilidad
          </h2>
          <div class="public-cal">
            <div class="public-cal-head">
              <button class="cal-nav-btn" @click="publicCalMonth--; normalizePublicMonth()" aria-label="Anterior">‹</button>
              <span class="public-cal-month">{{ monthNames[publicCalMonth] }} {{ publicCalYear }}</span>
              <button class="cal-nav-btn" @click="publicCalMonth++; normalizePublicMonth()" aria-label="Siguiente">›</button>
            </div>
            <div class="public-cal-weekdays">
              <span v-for="d in ['L','M','M','J','V','S','D']" :key="d">{{ d }}</span>
            </div>
            <div class="public-cal-grid">
              <div v-for="(day, i) in publicCalendarDays" :key="i" :class="['public-cal-day', day.statusClass, { 'is-today': day.isToday }]">
                <span v-if="day.day">{{ day.day }}</span>
              </div>
            </div>
            <div class="public-cal-legend">
              <span><span class="cal-legend-dot dot-available"></span>Disponible</span>
              <span><span class="cal-legend-dot dot-busy"></span>Ocupado</span>
            </div>
          </div>
        </section>

        <!-- Location + Coverage zones (matching mockup section 9) -->
        <section v-if="talentCoords" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
            Cobertura + Idiomas
          </h2>

          <!-- Info pair (texto) -->
          <div class="coverage-info-pair">
            <div>
              <div class="coverage-label">📍 Zonas de cobertura</div>
              <div class="coverage-value">
                <span v-if="serviceZonesList.length">{{ serviceZonesList.join(', ') }}</span>
                <span v-else>{{ talent.city }}<span v-if="talent.coverage_radius_km"> · radio {{ talent.coverage_radius_km }} km</span></span>
                <div v-if="talent.travel_fee_extra" class="coverage-extra">
                  Fuera del área: +${{ Number(talent.travel_fee_extra).toFixed(0) }} traslado
                </div>
              </div>
            </div>
            <div v-if="languagesList.length">
              <div class="coverage-label">🌐 Idiomas en MC</div>
              <div class="coverage-value">{{ languagesList.join(', ') }}</div>
            </div>
          </div>

          <div class="location-meta">
            <div class="location-pill">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ talent.city }}<span v-if="talent.country">, {{ talent.country }}</span>
            </div>
            <div v-if="talent.coverage_radius_km" class="location-pill">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
              Cobertura: <strong>{{ talent.coverage_radius_km }} km</strong>
            </div>
          </div>
          <div class="map-wrapper">
            <div ref="mapContainer" class="map-container"></div>
          </div>
        </section>

        <!-- Gallery -->
        <section v-if="photoGallery.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
            Galería
            <span class="section-count">{{ photoGallery.length }}</span>
            <button v-if="photoGallery.length > 8" class="section-link-action" @click="openLightbox(0)">Ver todas ({{ photoGallery.length }}) →</button>
          </h2>
          <div class="public-gallery">
            <button
              v-for="(photo, i) in photoGallery"
              :key="photo.id"
              class="gallery-thumb"
              @click="openLightbox(i)"
            >
              <img :src="photo.file" :alt="photo.title || 'Foto de evento'" loading="lazy" @error="onImgError" />
              <span v-if="photo.title" class="gallery-caption">{{ photo.title }}</span>
            </button>
          </div>
        </section>

        <!-- Reviews -->
        <section class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            Reseñas
            <span v-if="reviews.length" class="section-count">{{ reviews.length }}</span>
            <select v-if="reviews.length > 1" v-model="reviewFilter" class="section-link-select">
              <option value="recent">Filtrar ↓ Más recientes</option>
              <option value="highest">Mejor calificadas</option>
              <option value="lowest">Peor calificadas</option>
              <option value="verified">Solo verificadas</option>
            </select>
          </h2>

          <!-- Score grande + breakdown por dimensión -->
          <div v-if="reviews.length" class="review-summary">
            <div class="review-big">
              <div class="review-num">{{ Number(talent.rating_avg || 0).toFixed(1) }}</div>
              <div class="review-stars-big">
                <svg v-for="i in 5" :key="i" width="16" height="16" viewBox="0 0 24 24" :fill="i <= Math.round(talent.rating_avg) ? '#FBBF24' : 'transparent'" stroke="#FBBF24" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              </div>
              <div class="review-count-label">{{ reviews.length }} {{ reviews.length === 1 ? 'reseña' : 'reseñas' }}</div>
            </div>
            <div v-if="hasDimensionalReviews" class="review-breakdown">
              <div v-for="dim in dimensionBars" :key="dim.key" class="review-bar">
                <span class="bar-label">{{ dim.label }}</span>
                <span class="bar-track"><span class="bar-fill" :style="{ width: (dim.avg / 5 * 100) + '%' }"></span></span>
                <span class="bar-num">{{ dim.avg.toFixed(1) }}</span>
              </div>
            </div>
          </div>

          <div v-if="filteredReviews.length" class="reviews-list">
            <div v-for="review in filteredReviews" :key="review.id" class="review-item glass">
              <div class="review-header review-head-rich">
                <div class="reviewer-block">
                  <div class="reviewer-avatar">{{ (review.client_name || 'C')[0].toUpperCase() }}</div>
                  <div>
                    <strong>{{ review.client_name || 'Cliente' }}</strong>
                    <span v-if="reviewMetaText(review)" class="reviewer-meta">{{ reviewMetaText(review) }}</span>
                  </div>
                </div>
                <div class="review-header-right">
                  <span v-if="review.is_verified" class="verified-tag">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                    Verificada
                  </span>
                </div>
              </div>
              <div class="review-stars">
                <svg v-for="i in review.rating" :key="i" width="14" height="14" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              </div>
              <p>{{ review.comment }}</p>

              <!-- Respuesta pública del DJ (visible siempre si existe) -->
              <div v-if="review.response" class="review-response">
                <div class="response-header">
                  <strong>{{ talent.stage_name }}</strong>
                  <span class="response-tag">Respuesta del talento</span>
                </div>
                <p>{{ review.response }}</p>
              </div>

              <!-- Inline editor (solo si soy dueño Premium y no he respondido) -->
              <div v-if="canRespondToReviews && !review.response" class="response-editor">
                <button v-if="respondingTo !== review.id" class="btn btn-ghost btn-sm" @click="openResponse(review.id)">
                  Responder a esta reseña
                </button>
                <div v-else>
                  <textarea v-model="responseDraft" rows="3" class="input-field" placeholder="Tu respuesta pública..."></textarea>
                  <div class="response-actions">
                    <button class="btn btn-ghost btn-sm" @click="respondingTo = null">Cancelar</button>
                    <button class="btn btn-primary btn-sm" :disabled="!responseDraft.trim() || submittingResponse" @click="submitResponse(review)">
                      {{ submittingResponse ? 'Enviando...' : 'Publicar respuesta' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-reviews">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <strong>Sé el primero en reseñar a {{ talent.stage_name }}</strong>
            <p>Los clientes que ya contrataron este talento podrán dejar su reseña aquí.</p>
          </div>
        </section>

        <!-- Cómo funciona (Escrow trust) -->
        <section class="content-section trust-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-success, #10b981)" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Cómo funciona contratar a {{ talent.stage_name }}
          </h2>
          <div class="trust-steps">
            <div v-for="(step, i) in trustSteps" :key="i" class="trust-step">
              <div class="trust-num">{{ i + 1 }}</div>
              <div class="trust-text" v-html="step"></div>
            </div>
          </div>
        </section>

        <!-- FAQ -->
        <section v-if="talent.faqs && talent.faqs.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            Preguntas frecuentes
          </h2>
          <div class="faq-list">
            <div v-for="(faq, i) in talent.faqs" :key="faq.id" class="faq-item" :class="{ open: faqOpen[i] }">
              <button class="faq-q" @click="faqOpen[i] = !faqOpen[i]">
                <span>{{ faq.question }}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: faqOpen[i] }"><polyline points="6 9 12 15 18 9"/></svg>
              </button>
              <div v-if="faqOpen[i]" class="faq-a">{{ faq.answer }}</div>
            </div>
          </div>
        </section>

        <!-- Redes sociales -->
        <section v-if="socialLinks.length" class="content-section">
          <h2>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
            Redes
          </h2>
          <div class="social-row">
            <div v-for="s in socialLinks" :key="s.label" class="social-item">
              <span v-html="s.icon"></span>
              <span class="social-label">{{ s.label }}</span>
            </div>
          </div>
          <p class="social-note">Para coordinar tu evento, usa el botón "Reservar Ahora". Nunca contactes al talento por fuera de Pulsar antes de confirmar tu reserva.</p>
        </section>
      </main>
    </div>

    <!-- Inquiry Modal (Enviar consulta) -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="inquiryModal.open" class="inquiry-backdrop" @click.self="inquiryModal.open = false">
          <div class="inquiry-modal glass">
            <button class="inquiry-close" @click="inquiryModal.open = false" aria-label="Cerrar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
            <h3>Enviar consulta a {{ talent?.stage_name }}</h3>
            <p class="inquiry-sub">Pregunta lo que quieras antes de reservar. El talento recibirá una notificación.</p>

            <div v-if="inquiryModal.success" class="inquiry-success">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <p>Consulta enviada. El talento responderá pronto.</p>
            </div>

            <template v-else>
              <textarea
                v-model="inquiryModal.message"
                rows="5"
                class="inquiry-textarea"
                placeholder="Ej: ¿Tienes disponibilidad para una boda de 200 invitados el 15 de junio en Casco Antiguo?"
              ></textarea>
              <p class="inquiry-warn">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                Toda comunicación queda en Pulsar. No incluyas teléfono ni email.
              </p>

              <p v-if="inquiryModal.error" class="inquiry-error">{{ inquiryModal.error }}</p>

              <div class="inquiry-actions">
                <button class="btn btn-ghost btn-sm" @click="inquiryModal.open = false">Cancelar</button>
                <button class="btn btn-primary btn-sm" :disabled="inquiryModal.loading" @click="sendInquiry">
                  {{ inquiryModal.loading ? 'Enviando...' : 'Enviar consulta' }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="lightboxIndex !== null" class="lightbox-backdrop" @click.self="closeLightbox" @keydown.esc="closeLightbox">
          <button class="lightbox-close" @click="closeLightbox" aria-label="Cerrar">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          <button v-if="photoGallery.length > 1" class="lightbox-nav prev" @click.stop="prevPhoto" aria-label="Anterior">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
          </button>
          <div class="lightbox-content" @click.stop>
            <img :src="photoGallery[lightboxIndex].file" :alt="photoGallery[lightboxIndex].title || ''" @error="onImgError" />
            <p v-if="photoGallery[lightboxIndex].title" class="lightbox-caption">{{ photoGallery[lightboxIndex].title }}</p>
          </div>
          <button v-if="photoGallery.length > 1" class="lightbox-nav next" @click.stop="nextPhoto" aria-label="Siguiente">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- Quote Modal -->
    <Teleport to="body">
      <div v-if="showQuoteModal" class="modal-backdrop" @click.self="showQuoteModal = false">
        <div class="modal glass animate-fade-in-up">
          <div class="modal-header">
            <h2>Solicitar Cotización</h2>
            <button class="btn btn-ghost btn-icon" @click="showQuoteModal = false" aria-label="Cerrar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <form @submit.prevent="submitQuote" class="modal-body">
            <div class="field">
              <label class="label" for="event_type">Tipo de evento</label>
              <select id="event_type" v-model="quoteForm.event_type" class="input-field" required>
                <option value="">Seleccionar...</option>
                <option value="wedding">Boda</option>
                <option value="birthday">Cumpleaños</option>
                <option value="corporate">Corporativo</option>
                <option value="club">Club / Discoteca</option>
                <option value="festival">Festival</option>
                <option value="private">Fiesta Privada</option>
                <option value="other">Otro</option>
              </select>
            </div>
            <div class="field-row">
              <div class="field">
                <label class="label" for="event_date">Fecha</label>
                <input id="event_date" v-model="quoteForm.event_date" type="date" class="input-field" required />
              </div>
              <div class="field">
                <label class="label" for="event_time">Hora</label>
                <input id="event_time" v-model="quoteForm.event_time" type="time" class="input-field" />
              </div>
            </div>
            <div class="field">
              <label class="label" for="event_location">Ubicación</label>
              <input id="event_location" v-model="quoteForm.event_location" type="text" class="input-field" placeholder="Ciudad, Venue..." required />
            </div>
            <div class="field">
              <label class="label" for="client_notes">Detalles adicionales</label>
              <textarea id="client_notes" v-model="quoteForm.client_notes" class="input-field" rows="3" placeholder="Describe tu evento..."></textarea>
            </div>
            <p v-if="quoteError" class="error-msg">{{ quoteError }}</p>
            <p v-if="quoteSuccess" class="success-msg">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Cotización enviada con éxito
            </p>
            <button type="submit" class="btn btn-cta btn-lg" style="width:100%;" :disabled="quoteSending">
              {{ quoteSending ? 'Enviando...' : 'Enviar Cotización' }}
            </button>
          </form>
        </div>
      </div>
    </Teleport>
  </div>

  <!-- Loading state -->
  <div v-else class="profile-page loading-page">
    <div class="container">
      <div class="skeleton" style="height: 300px; border-radius: var(--radius-xl); margin: var(--space-24) 0 var(--space-8);"></div>
      <div class="skeleton" style="height: 400px; border-radius: var(--radius-xl);"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import L from 'leaflet'

const route = useRoute()
const themeStore = useThemeStore()
const auth = useAuthStore()
const talent = ref(null)
const reviews = ref([])
const showQuoteModal = ref(false)
const quoteSending = ref(false)
const quoteError = ref('')
const quoteSuccess = ref(false)

const quoteForm = ref({
  event_type: '',
  event_date: '',
  event_time: '',
  event_location: '',
  client_notes: '',
})

const placeholderCover = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400"%3E%3Cdefs%3E%3ClinearGradient id="g" x1="0" y1="0" x2="1" y2="1"%3E%3Cstop offset="0%25" stop-color="%23C1D82F" stop-opacity="0.15"/%3E%3Cstop offset="100%25" stop-color="%23E85D4A" stop-opacity="0.08"/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill="%230A0A0A" width="1200" height="400"/%3E%3Crect fill="url(%23g)" width="1200" height="400"/%3E%3C/svg%3E'

const placeholderAvatar = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"%3E%3Crect fill="%230A0A0A" width="120" height="120" rx="60"/%3E%3Ccircle cx="60" cy="45" r="20" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3Cpath d="M30 95a30 30 0 0160 0" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3C/svg%3E'

// Placeholder cuando una imagen falla al cargar (broken URL, 404, CORS, etc)
const placeholderBroken = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"%3E%3Crect fill="%23141414" width="200" height="200"/%3E%3Cg transform="translate(100,100)" stroke="%23555" stroke-width="2" fill="none"%3E%3Crect x="-30" y="-25" width="60" height="50" rx="4"/%3E%3Ccircle cx="-12" cy="-10" r="4"/%3E%3Cpath d="M-25 15l15-15L5 15l10-10 10 15"/%3E%3C/g%3E%3Ctext x="100" y="170" text-anchor="middle" font-family="sans-serif" font-size="10" fill="%23555"%3EImagen no disponible%3C/text%3E%3C/svg%3E'

function onImgError(e) {
  if (e.target && e.target.src !== placeholderBroken) {
    e.target.src = placeholderBroken
  }
}

// ── Location map ──
const panamaCities = [
  { name: 'Ciudad de Panamá', lat: 8.9824, lng: -79.5199 },
  { name: 'San Miguelito', lat: 9.0504, lng: -79.4713 },
  { name: 'David', lat: 8.4333, lng: -82.4333 },
  { name: 'Colón', lat: 9.3547, lng: -79.9017 },
  { name: 'Santiago', lat: 8.1000, lng: -80.9833 },
  { name: 'Chitré', lat: 7.9667, lng: -80.4333 },
  { name: 'Penonomé', lat: 8.5167, lng: -80.3500 },
  { name: 'Aguadulce', lat: 8.2453, lng: -80.5431 },
  { name: 'La Chorrera', lat: 8.8789, lng: -79.7822 },
  { name: 'Arraiján', lat: 8.9500, lng: -79.6500 },
  { name: 'Bocas del Toro', lat: 9.3404, lng: -82.2418 },
  { name: 'Las Tablas', lat: 7.7647, lng: -80.2750 },
]

const TILE_DARK = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_LIGHT = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

const mapContainer = ref(null)
let mapInstance = null
let tileLayer = null
let coverageCircle = null
let resizeObserver = null

const talentCoords = computed(() => {
  if (!talent.value) return null
  if (talent.value.latitude && talent.value.longitude) {
    return { lat: Number(talent.value.latitude), lng: Number(talent.value.longitude) }
  }
  const city = panamaCities.find(c => c.name === talent.value.city)
  return city ? { lat: city.lat, lng: city.lng } : null
})

function currentTileUrl() {
  return themeStore.theme === 'light' ? TILE_LIGHT : TILE_DARK
}

function buildLocationMap() {
  if (!mapContainer.value || mapInstance || !talentCoords.value) return
  const { lat, lng } = talentCoords.value
  const radius = (talent.value?.coverage_radius_km || 50) * 1000

  mapInstance = L.map(mapContainer.value, {
    center: [lat, lng],
    zoom: 9,
    zoomControl: false,
    attributionControl: false,
    scrollWheelZoom: false,
    dragging: true,
  })

  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance)

  const markerIcon = L.divIcon({
    className: 'custom-marker',
    html: '<div class="marker-dot active"></div>',
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
  L.marker([lat, lng], { icon: markerIcon }).addTo(mapInstance)

  coverageCircle = L.circle([lat, lng], {
    radius,
    color: '#C1D82F',
    fillColor: '#C1D82F',
    fillOpacity: 0.10,
    weight: 1.5,
    dashArray: '6 4',
  }).addTo(mapInstance)

  // Fit so the whole coverage circle is visible
  mapInstance.fitBounds(coverageCircle.getBounds(), { padding: [20, 20] })

  resizeObserver = new ResizeObserver(() => mapInstance?.invalidateSize())
  resizeObserver.observe(mapContainer.value)
  requestAnimationFrame(() => mapInstance?.invalidateSize())
}

function destroyLocationMap() {
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (mapInstance) { mapInstance.remove(); mapInstance = null }
  tileLayer = null
  coverageCircle = null
}

// Build map once container + talent data are both ready
watch([mapContainer, talentCoords], ([el, coords]) => {
  if (el && coords && !mapInstance) {
    requestAnimationFrame(() => buildLocationMap())
  }
})

// Re-tile on theme change
watch(() => themeStore.theme, () => {
  if (!mapInstance || !tileLayer) return
  mapInstance.removeLayer(tileLayer)
  tileLayer = L.tileLayer(currentTileUrl(), { maxZoom: 19 }).addTo(mapInstance)
})

// Frost effect: fades out as user scrolls past the cover
const coverRef = ref(null)
const coverFrost = ref(1)
let scrollHandler = null

function updateFrost() {
  if (!coverRef.value) return
  const rect = coverRef.value.getBoundingClientRect()
  const coverH = coverRef.value.offsetHeight
  // frost = 1 at top, 0 when cover is half scrolled away
  const progress = Math.max(0, Math.min(1, rect.bottom / coverH))
  coverFrost.value = progress
}

onUnmounted(() => {
  if (scrollHandler) window.removeEventListener('scroll', scrollHandler)
  window.removeEventListener('keydown', onLightboxKey)
  destroyLocationMap()
})

// ── Alta temporada (sólo Premium) ──
// Meses por defecto: nov, dic, ene. Si el backend expone PlatformConfig, podría leerse
// de ahí — por ahora hardcodeado matching default del backend.
const HIGH_SEASON_MONTHS = [11, 12, 1]
const isHighSeasonPremium = computed(() => {
  if (talent.value?.talent_level !== 'premium') return false
  const currentMonth = new Date().getMonth() + 1
  return HIGH_SEASON_MONTHS.includes(currentMonth)
})

// ── Sidebar stats row (3 cells matching mockup) ──
const sidebarStats = computed(() => {
  if (!talent.value) return []
  const items = []
  if (Number(talent.value.total_bookings) > 0) {
    items.push({ value: talent.value.total_bookings, label: 'Eventos' })
  }
  if (talent.value.response_time_hours != null) {
    items.push({ value: `${talent.value.response_time_hours}h`, label: 'Responde en' })
  }
  if (talent.value.created_at) {
    items.push({ value: new Date(talent.value.created_at).getFullYear(), label: 'Miembro desde' })
  }
  // Premium adicional: repeat rate
  if (talent.value.repeat_rate != null && talent.value.talent_level === 'premium') {
    items.push({ value: `${talent.value.repeat_rate}%`, label: 'Repite' })
  }
  return items
})

// ── Service zones list ──
const serviceZonesList = computed(() => {
  const v = talent.value?.service_zones
  return Array.isArray(v) ? v : []
})

// ── Reviews filter ──
const reviewFilter = ref('recent')

const filteredReviews = computed(() => {
  const list = [...reviews.value]
  switch (reviewFilter.value) {
    case 'highest': return list.sort((a, b) => b.rating - a.rating)
    case 'lowest': return list.sort((a, b) => a.rating - b.rating)
    case 'verified': return list.filter(r => r.is_verified)
    default: return list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
})

const MONTH_NAMES_SHORT = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
function reviewMetaText(review) {
  const parts = []
  if (review.event_type_display) parts.push(review.event_type_display)
  if (review.event_guest_count) parts.push(`${review.event_guest_count} invitados`)
  if (review.event_date) {
    const d = new Date(review.event_date + 'T00:00:00')
    parts.push(`${MONTH_NAMES_SHORT[d.getMonth()]} ${d.getFullYear()}`)
  }
  return parts.join(' · ')
}

// ── Inquiry modal ──
const inquiryModal = ref({ open: false, message: '', loading: false, error: '', success: false })
function openInquiry() {
  inquiryModal.value = { open: true, message: '', loading: false, error: '', success: false }
}
async function sendInquiry() {
  if (inquiryModal.value.message.trim().length < 10) {
    inquiryModal.value.error = 'Escribe al menos 10 caracteres.'
    return
  }
  inquiryModal.value.loading = true
  inquiryModal.value.error = ''
  try {
    await api.post(`/talents/${talent.value.id}/inquire/`, {
      message: inquiryModal.value.message.trim(),
    })
    inquiryModal.value.success = true
    setTimeout(() => { inquiryModal.value.open = false }, 1800)
  } catch (err) {
    inquiryModal.value.error = err.response?.data?.error || 'No se pudo enviar la consulta.'
  } finally {
    inquiryModal.value.loading = false
  }
}

// ── Tier label ──
const tierLabel = computed(() => {
  const level = talent.value?.talent_level
  if (level === 'premium') return '★★ Premium'
  if (level === 'pro') return '★ Pro'
  return 'Standard'
})

// ── Video media (YouTube / Vimeo embed) ──
const videoMedia = computed(() => {
  const media = talent.value?.media || []
  return media.filter(m => m.media_type === 'video' && (m.url || m.file))
})

function videoEmbedUrl(url) {
  if (!url) return null
  const yt = url.match(/(?:v=|youtu\.be\/|youtube\.com\/embed\/)([A-Za-z0-9_-]{11})/)
  if (yt) return `https://www.youtube.com/embed/${yt[1]}`
  const vimeo = url.match(/vimeo\.com\/(\d+)/)
  if (vimeo) return `https://player.vimeo.com/video/${vimeo[1]}`
  return null
}

// ── Event types ──
const EVENT_TYPE_LABELS = {
  wedding: { icon: '💍', label: 'Bodas' },
  corporate: { icon: '🏢', label: 'Corporativo' },
  birthday: { icon: '🎂', label: 'Cumpleaños' },
  cocktail: { icon: '🍸', label: 'Cocktail / Brunch' },
  club: { icon: '🪩', label: 'Club / Residencia' },
  launch: { icon: '🚀', label: 'Lanzamiento' },
  graduation: { icon: '🎓', label: 'Graduación' },
  festival: { icon: '🎪', label: 'Festival' },
  private: { icon: '🎉', label: 'Fiesta Privada' },
  anniversary: { icon: '💐', label: 'Aniversario' },
}

const eventTypeTags = computed(() => {
  const types = talent.value?.event_types
  if (!Array.isArray(types)) return []
  return types.map(value => ({
    value,
    icon: EVENT_TYPE_LABELS[value]?.icon || '📅',
    label: EVENT_TYPE_LABELS[value]?.label || value,
  }))
})

// ── Equipment lists ──
const equipmentBrings = computed(() => {
  const v = talent.value?.equipment_brings
  return Array.isArray(v) ? v : []
})
const equipmentNotIncluded = computed(() => {
  const v = talent.value?.equipment_not_included
  return Array.isArray(v) ? v : []
})

// ── Languages ──
const languagesList = computed(() => {
  const v = talent.value?.languages
  return Array.isArray(v) ? v : []
})

// ── Packs ──
const packs = computed(() => talent.value?.packs || [])

// ── FAQ open state ──
const faqOpen = ref({})

// ── Social links (mostrar sin link directo — anti-desintermediación) ──
const socialLinks = computed(() => {
  if (!talent.value) return []
  const links = []
  if (talent.value.instagram) links.push({
    label: '@' + talent.value.instagram.replace(/^@/, ''),
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>',
  })
  if (talent.value.tiktok) links.push({
    label: 'TikTok',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-5.2 1.74 2.89 2.89 0 012.31-4.64 2.93 2.93 0 01.88.13V9.4a6.84 6.84 0 00-1-.05A6.33 6.33 0 005.8 20.1a6.34 6.34 0 0010.86-4.43V8.5a8.16 8.16 0 004.77 1.52v-3.4a4.85 4.85 0 01-1.84-.93z"/></svg>',
  })
  if (talent.value.soundcloud) links.push({
    label: 'SoundCloud',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="#FF5500"><path d="M1.18 16.84c.05-.04.07-.1.07-.16v-3.86c0-.06-.02-.12-.07-.16-.05-.04-.1-.06-.16-.04-.06.02-.1.07-.1.13v3.96c0 .06.04.11.1.13.06.02.11 0 .16-.04z"/></svg>',
  })
  if (talent.value.spotify) links.push({
    label: 'Spotify',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="#1DB954"><circle cx="12" cy="12" r="10"/></svg>',
  })
  if (talent.value.mixcloud) links.push({
    label: 'Mixcloud',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="#52ABFF"><circle cx="12" cy="12" r="10"/></svg>',
  })
  if (talent.value.youtube) links.push({
    label: 'YouTube',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="#FF0000"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z"/></svg>',
  })
  if (talent.value.website) links.push({
    label: 'Web',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/></svg>',
  })
  return links
})

// ── Public availability calendar ──
const monthNames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const publicCalMonth = ref(new Date().getMonth())
const publicCalYear = ref(new Date().getFullYear())

function normalizePublicMonth() {
  if (publicCalMonth.value > 11) { publicCalMonth.value = 0; publicCalYear.value++ }
  else if (publicCalMonth.value < 0) { publicCalMonth.value = 11; publicCalYear.value-- }
}

const hasAvailabilityData = computed(() => {
  const av = talent.value?.availability
  return Array.isArray(av) && av.length > 0
})

// Las próximas 3 fechas disponibles, formato corto "15, 22, 29 may"
const quickAvailability = computed(() => {
  const av = talent.value?.availability || []
  const today = new Date(); today.setHours(0,0,0,0)
  const upcoming = av
    .filter(a => a.status === 'available' && new Date(a.date) >= today)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(0, 3)
  if (!upcoming.length) return null
  const months = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
  // Si todas son del mismo mes, "15, 22, 29 may"
  const dates = upcoming.map(a => new Date(a.date))
  const sameMonth = dates.every(d => d.getMonth() === dates[0].getMonth())
  if (sameMonth) {
    return dates.map(d => d.getDate()).join(', ') + ' ' + months[dates[0].getMonth()]
  }
  return dates.map(d => `${d.getDate()} ${months[d.getMonth()]}`).join(', ')
})

const publicCalendarDays = computed(() => {
  const av = talent.value?.availability || []
  const byDate = {}
  av.forEach(a => { byDate[a.date] = a.status })
  const firstDay = new Date(publicCalYear.value, publicCalMonth.value, 1)
  const lastDay = new Date(publicCalYear.value, publicCalMonth.value + 1, 0)
  const startWeekday = firstDay.getDay() || 7
  const days = []
  for (let i = 1; i < startWeekday; i++) days.push({ day: null, statusClass: 'empty' })
  const today = new Date()
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${publicCalYear.value}-${String(publicCalMonth.value + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const status = byDate[dateStr]
    const isToday = today.getFullYear() === publicCalYear.value && today.getMonth() === publicCalMonth.value && today.getDate() === d
    let statusClass = 'empty'
    if (status === 'available') statusClass = 'available'
    else if (status === 'booked' || status === 'blocked') statusClass = 'busy'
    days.push({ day: d, statusClass, isToday })
  }
  return days
})

// ── Audio mixes (embed providers) ──
const audioMedia = computed(() => {
  const media = talent.value?.media || []
  const all = media.filter(m => m.media_type === 'audio' && (m.url || m.file))
  // Premium: mix destacado primero (is_cover=true)
  if (talent.value?.talent_level === 'premium') {
    return [...all].sort((a, b) => (b.is_cover ? 1 : 0) - (a.is_cover ? 1 : 0))
  }
  return all
})

function embedProvider(url) {
  if (!url) return null
  if (/soundcloud\.com/i.test(url)) return 'soundcloud'
  if (/spotify\.com/i.test(url)) return 'spotify'
  if (/mixcloud\.com/i.test(url)) return 'mixcloud'
  if (/youtube\.com|youtu\.be/i.test(url)) return 'youtube'
  return null
}

function embedClass(url) {
  return `mix-${embedProvider(url) || 'generic'}`
}

function embedUrl(url) {
  if (!url) return null
  const provider = embedProvider(url)
  if (provider === 'soundcloud') {
    return `https://w.soundcloud.com/player/?url=${encodeURIComponent(url)}&color=%23C1D82F&auto_play=false&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false&visual=false`
  }
  if (provider === 'spotify') {
    // Espera URL tipo https://open.spotify.com/track/... → conviértela a /embed/...
    return url.replace('open.spotify.com/', 'open.spotify.com/embed/')
  }
  if (provider === 'mixcloud') {
    // Mixcloud necesita el path después del dominio. Ej: https://www.mixcloud.com/user/mix/
    const match = url.match(/mixcloud\.com\/([^?#]+)/i)
    if (!match) return null
    return `https://www.mixcloud.com/widget/iframe/?light=1&hide_cover=1&feed=${encodeURIComponent('/' + match[1])}`
  }
  if (provider === 'youtube') {
    // Acepta watch?v=ID o youtu.be/ID
    const m = url.match(/(?:v=|youtu\.be\/)([A-Za-z0-9_-]{11})/)
    if (!m) return null
    return `https://www.youtube.com/embed/${m[1]}`
  }
  return null
}

// ── Mood tags ──
const moodTags = computed(() => {
  const tags = talent.value?.mood_tags
  return Array.isArray(tags) ? tags : []
})

// ── Respuesta del DJ a reseñas (gated Premium) ──
const isOwnerOfProfile = computed(() => {
  return auth.isLoggedIn && talent.value?.user?.id === auth.user?.id
})
const canRespondToReviews = computed(() => {
  return isOwnerOfProfile.value && talent.value?.talent_level === 'premium'
})

const respondingTo = ref(null)
const responseDraft = ref('')
const submittingResponse = ref(false)

function openResponse(reviewId) {
  respondingTo.value = reviewId
  responseDraft.value = ''
}

async function submitResponse(review) {
  if (!responseDraft.value.trim()) return
  submittingResponse.value = true
  try {
    const { data } = await api.patch(`/reviews/${review.id}/response/`, {
      response: responseDraft.value.trim(),
    })
    // Update in place
    review.response = data.response
    review.response_at = data.response_at
    respondingTo.value = null
    responseDraft.value = ''
  } catch (err) {
    alert(err.response?.data?.error || 'No se pudo publicar la respuesta.')
  } finally {
    submittingResponse.value = false
  }
}

// ── Review dimension breakdown ──
const dimensionDefs = [
  { key: 'rating_punctuality', label: 'Puntualidad' },
  { key: 'rating_music_selection', label: 'Selección musical' },
  { key: 'rating_crowd_reading', label: 'Lectura del público' },
  { key: 'rating_technique', label: 'Técnica' },
  { key: 'rating_communication', label: 'Comunicación' },
]

const dimensionBars = computed(() => {
  return dimensionDefs.map(def => {
    const scores = reviews.value
      .map(r => r[def.key])
      .filter(v => v != null && v > 0)
    const avg = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
    return { key: def.key, label: def.label, avg, count: scores.length }
  }).filter(d => d.count > 0)
})

const hasDimensionalReviews = computed(() => dimensionBars.value.length > 0)

// ── Trust / "Cómo funciona" steps ──
const trustSteps = computed(() => [
  `Envías la solicitud con los detalles de tu evento. <strong>Gratis, sin compromiso.</strong>`,
  `${talent.value?.stage_name || 'El talento'} revisa y te envía una <strong>propuesta personalizada</strong>.`,
  `Pagas a <strong>Pulsar</strong> (no directamente al talento). Tu dinero queda en custodia.`,
  `Día del evento: el talento se presenta. <strong>Si no llega, te reembolsamos 100%.</strong>`,
  `24h después del evento, se libera el pago al talento y dejas tu reseña.`,
])

// Stats dashboard — solo entran al array si tienen data real (nada de ceros)
const stats = computed(() => {
  if (!talent.value) return []
  const t = talent.value
  const items = []

  if (Number(t.total_bookings) > 0) {
    items.push({
      key: 'bookings',
      value: t.total_bookings,
      label: 'Eventos realizados',
      icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    })
  }

  if (Number(t.rating_avg) > 0 && Number(t.total_reviews) > 0) {
    items.push({
      key: 'rating',
      value: Number(t.rating_avg).toFixed(1),
      label: `${t.total_reviews} ${t.total_reviews === 1 ? 'reseña' : 'reseñas'}`,
      icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    })
  }

  if (Number(t.experience_years) > 0) {
    items.push({
      key: 'experience',
      value: t.experience_years,
      label: t.experience_years === 1 ? 'Año de experiencia' : 'Años de experiencia',
      icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    })
  }

  if (photoGallery.value.length > 0) {
    items.push({
      key: 'photos',
      value: photoGallery.value.length,
      label: photoGallery.value.length === 1 ? 'Foto' : 'Fotos',
      icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>',
    })
  }

  // "Miembro desde" solo si la cuenta tiene > 30 días — evita mostrar "2026" cuando se registró ayer
  if (t.created_at) {
    const created = new Date(t.created_at)
    const daysSince = (Date.now() - created.getTime()) / (1000 * 60 * 60 * 24)
    if (daysSince >= 30) {
      items.push({
        key: 'member',
        value: created.getFullYear(),
        label: 'Miembro desde',
        icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
      })
    }
  }

  return items
})

const typeLabel = computed(() => {
  const map = { dj: 'DJ', musician: 'Músico', band: 'Banda' }
  return map[talent.value?.talent_type] || ''
})

const typeClass = computed(() => {
  const map = { dj: '', musician: 'badge-cyan', band: 'badge-accent' }
  return map[talent.value?.talent_type] || ''
})

// ── Gallery & lightbox ──
const photoGallery = computed(() => {
  const media = talent.value?.media || []
  return media.filter(m => m.media_type === 'photo' && m.file)
})

const lightboxIndex = ref(null)
function openLightbox(i) { lightboxIndex.value = i }
function closeLightbox() { lightboxIndex.value = null }
function nextPhoto() {
  if (lightboxIndex.value === null) return
  lightboxIndex.value = (lightboxIndex.value + 1) % photoGallery.value.length
}
function prevPhoto() {
  if (lightboxIndex.value === null) return
  lightboxIndex.value = (lightboxIndex.value - 1 + photoGallery.value.length) % photoGallery.value.length
}

function onLightboxKey(e) {
  if (lightboxIndex.value === null) return
  if (e.key === 'Escape') closeLightbox()
  else if (e.key === 'ArrowRight') nextPhoto()
  else if (e.key === 'ArrowLeft') prevPhoto()
}

// ── Share profile ──
const shareLabel = ref('Compartir perfil')

async function shareProfile() {
  const url = window.location.href
  const title = `${talent.value?.stage_name || 'Talento'} en Pulsar`
  const text = `Mira este talento en Pulsar: ${talent.value?.stage_name || ''}`
  // Web Share API (mobile + algunos desktops)
  if (navigator.share) {
    try {
      await navigator.share({ title, text, url })
      return
    } catch (err) {
      // Usuario canceló — no hacemos fallback porque ya tuvo intención de cerrar
      if (err.name === 'AbortError') return
    }
  }
  // Fallback: copiar al portapapeles
  try {
    await navigator.clipboard.writeText(url)
    shareLabel.value = '✓ Link copiado'
    setTimeout(() => { shareLabel.value = 'Compartir perfil' }, 2000)
  } catch {
    window.prompt('Copia este link:', url)
  }
}

async function submitQuote() {
  quoteSending.value = true
  quoteError.value = ''
  quoteSuccess.value = false
  try {
    await api.post('/bookings/create/', {
      talent: talent.value.id,
      ...quoteForm.value,
    })
    quoteSuccess.value = true
    setTimeout(() => { showQuoteModal.value = false; quoteSuccess.value = false }, 2000)
  } catch (err) {
    quoteError.value = err.response?.data?.detail || 'Error al enviar la cotización. Asegúrate de estar autenticado.'
  } finally {
    quoteSending.value = false
  }
}

onMounted(async () => {
  try {
    const [talentRes, reviewsRes] = await Promise.all([
      api.get(`/talents/${route.params.id}/`),
      api.get(`/talents/${route.params.id}/reviews/`),
    ])
    talent.value = talentRes.data
    reviews.value = reviewsRes.data.results || reviewsRes.data
  } catch (err) {
    console.error('Profile load error:', err)
  }
  // Setup scroll-driven frost fade
  scrollHandler = updateFrost
  window.addEventListener('scroll', scrollHandler, { passive: true })
  window.addEventListener('keydown', onLightboxKey)
  updateFrost()
})
</script>

<style scoped>
.profile-page { padding-bottom: var(--space-16); margin-top: calc(-80px - var(--space-4)); }

.profile-cover {
  position: relative;
  height: 340px;
  overflow: hidden;
}


.profile-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
}

/* Frosted top overlay — fades out on scroll */
.cover-frost {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: opacity 0.05s linear;
  pointer-events: none;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      to bottom,
      transparent 40%,
      rgba(0, 0, 0, 0.1) 60%,
      rgba(0, 0, 0, 0.3) 75%,
      var(--color-bg-primary) 100%
    );
  pointer-events: none;
}

.profile-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: var(--space-8);
  margin-top: -80px;
  position: relative;
  z-index: 1;
}

.profile-sidebar { position: sticky; top: 100px; align-self: flex-start; }

.profile-card {
  padding: var(--space-6);
  border-radius: var(--radius-xl);
  text-align: center;
}

.avatar-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto var(--space-4);
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-full);
  object-fit: cover;
  border: 3px solid var(--color-primary);
}

.status-dot {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: var(--color-accent);
  border-radius: 50%;
  border: 3px solid var(--color-bg-glass);
}

.profile-card h1 {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--space-2);
}

.talent-type-label { margin-bottom: var(--space-3); }

.profile-rating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  font-size: var(--font-size-sm);
}

.profile-rating span { color: var(--color-text-muted); }

.profile-details {
  text-align: left;
  padding: var(--space-4) 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-5);
}

.detail-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail-row svg { color: var(--color-primary-light); flex-shrink: 0; }
.detail-row strong { color: var(--color-accent); }

/* Main content */
.profile-main {
  padding-top: var(--space-10);
}

.content-section {
  margin-bottom: var(--space-10);
}

.content-section h2 {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.content-section p {
  color: var(--color-text-secondary);
  line-height: 1.8;
  font-weight: 300;
}

.genres-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.muted-text { color: var(--color-text-muted); font-size: var(--font-size-sm); }

/* Reviews */
.reviews-list { display: flex; flex-direction: column; gap: var(--space-4); }

.review-item {
  padding: var(--space-5);
  border-radius: var(--radius-lg);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.review-stars { display: flex; gap: 2px; }
.review-item p { color: var(--color-text-muted); font-size: var(--font-size-sm); line-height: 1.6; }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
  padding: var(--space-4);
}

.modal {
  width: 100%;
  max-width: 520px;
  border-radius: var(--radius-2xl);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 { font-size: var(--font-size-xl); }

.modal-body {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

textarea.input-field {
  resize: vertical;
  min-height: 80px;
}

.error-msg {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  background: var(--color-error-light);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
}

.success-msg {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-success);
  font-size: var(--font-size-sm);
  background: var(--color-success-light);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
}

.loading-page { padding-top: var(--space-8); }

@media (max-width: 768px) {
  .profile-layout { grid-template-columns: 1fr; }
  .profile-sidebar { position: static; }
  .profile-cover { height: 200px; }
  .field-row { grid-template-columns: 1fr; }
  .map-container { height: 240px; }
}

/* ── Tier visual differentiation ── */
.tier-badge { font-weight: 600; }
.tier-pro {
  background: rgba(193, 216, 47, 0.12);
  color: #C1D82F;
  border: 1px solid rgba(193, 216, 47, 0.4);
}
.tier-premium {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.5);
}
.tier-standard {
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}
.tier-card-pro {
  border: 1px solid rgba(193, 216, 47, 0.35) !important;
  box-shadow: 0 0 0 1px rgba(193, 216, 47, 0.1), 0 8px 24px rgba(193, 216, 47, 0.08);
}
.tier-card-premium {
  border: 1px solid rgba(245, 158, 11, 0.5) !important;
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.15), 0 12px 36px rgba(245, 158, 11, 0.18);
}
.tier-card-premium .avatar { border-color: #f59e0b !important; }
.tier-card-pro .avatar { border-color: #C1D82F !important; }

/* ── Video grid ── */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
}
.video-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.video-iframe-wrap {
  position: relative;
  aspect-ratio: 16 / 9;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.video-iframe-wrap iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
.video-fallback {
  color: var(--color-primary);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  font-weight: 500;
}
.video-title {
  padding: 10px 16px;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* ── Event types ── */
.badge-event {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.badge-event-icon { font-size: 0.9rem; }

/* ── Packs ── */
.packs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
}
.pack-card {
  position: relative;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: all var(--transition-base);
}
.pack-card:hover { border-color: var(--color-border-hover); transform: translateY(-2px); }
.pack-card.featured {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(193,216,47,0.1);
}
.pack-popular {
  position: absolute;
  top: -10px;
  right: 14px;
  background: var(--color-primary);
  color: #0a0a0a;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 1px;
  padding: 3px 10px;
  border-radius: 6px;
}
.pack-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-text-primary);
  margin-bottom: 6px;
}
.pack-price {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-primary);
  margin-bottom: var(--space-3);
}
.pack-duration {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  font-weight: 400;
}
.pack-includes {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.pack-includes li {
  position: relative;
  padding-left: 20px;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}
.pack-includes li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--color-primary);
  font-weight: 700;
}

/* ── Equipment split ── */
.equip-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
}
.equip-col h4 {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: var(--space-3);
}
.equip-yes h4 { color: #10b981; }
.equip-no h4 { color: #ef4444; }
.equip-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.equip-col li {
  position: relative;
  padding-left: 18px;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.equip-yes li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #10b981;
}
.equip-no li::before {
  content: '✕';
  position: absolute;
  left: 0;
  color: #ef4444;
}
.equip-description {
  margin-top: var(--space-4);
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

/* ── Public calendar ── */
.public-cal {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}
.public-cal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}
.public-cal-month {
  font-weight: 600;
  color: var(--color-text-primary);
}
.cal-nav-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 1rem;
  transition: all var(--transition-fast);
}
.cal-nav-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.public-cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 6px;
}
.public-cal-weekdays span {
  text-align: center;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.public-cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}
.public-cal-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}
.public-cal-day.available {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  font-weight: 600;
}
.public-cal-day.busy {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  text-decoration: line-through;
}
.public-cal-day.is-today {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}
.public-cal-legend {
  display: flex;
  gap: var(--space-4);
  margin-top: var(--space-3);
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.cal-legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 3px;
  margin-right: 4px;
  vertical-align: middle;
}
.dot-available { background: rgba(16, 185, 129, 0.4); }
.dot-busy { background: rgba(239, 68, 68, 0.4); }

/* ── FAQ ── */
.faq-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.faq-item {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.faq-item.open { border-color: var(--color-primary); }
.faq-q {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
}
.faq-q svg.rotated { transform: rotate(180deg); }
.faq-q svg { transition: transform var(--transition-fast); }
.faq-a {
  padding: 0 var(--space-4) var(--space-4);
  color: var(--color-text-muted);
  font-size: 0.88rem;
  line-height: 1.6;
}

/* ── Social row ── */
.social-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.social-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 10px 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  font-size: 0.88rem;
}
.social-label { font-weight: 500; }
.social-note {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  font-style: italic;
  margin-top: var(--space-2);
}

/* High season indicator (Premium) */
.high-season-pill {
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.4);
  text-transform: uppercase;
  cursor: help;
}

/* ── Disponibilidad rápida pill ── */
.quick-avail {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  margin-bottom: var(--space-3);
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}

/* ── Sidebar trust card ── */
.sidebar-trust {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3);
  margin-top: var(--space-3);
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-md);
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}
.sidebar-trust svg { flex-shrink: 0; margin-top: 1px; }

@media (max-width: 768px) {
  .equip-split { grid-template-columns: 1fr; }
}

/* ── Hero share button (matching mockup) ── */
.hero-share-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.18);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.2s;
}
.hero-share-btn:hover {
  background: rgba(0,0,0,0.65);
  border-color: rgba(255,255,255,0.35);
}

/* Premium tooltip on badge */
.premium-tooltip-wrap { position: relative; cursor: help; }
.premium-tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: #000;
  color: #fff;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.72rem;
  font-weight: 400;
  width: 220px;
  text-align: center;
  z-index: 10;
  line-height: 1.4;
  pointer-events: none;
  transition: opacity 0.15s, visibility 0.15s;
}
.premium-tooltip-wrap:hover .premium-tooltip { visibility: visible; opacity: 1; }

/* Sidebar stats row (matching mockup) */
.sidebar-stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  padding: var(--space-4) 0;
  margin: var(--space-3) 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}
.sidebar-stat { text-align: center; }
.sidebar-stat-num {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  color: var(--color-text-primary);
  font-size: 1rem;
}
.sidebar-stat-label {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

/* Pricing block (sidebar) — matching mockup */
.pricing-block {
  background: rgba(193,216,47,0.05);
  border: 1px solid rgba(193,216,47,0.2);
  padding: 12px 14px;
  border-radius: 12px;
  margin: var(--space-3) 0;
}
.pricing-main {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 4px;
}
.pricing-main strong {
  font-family: 'Poppins', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--color-text-primary);
}
.pricing-main span {
  color: var(--color-text-muted);
  font-size: 0.82rem;
}
.pricing-sub {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  line-height: 1.3;
}

/* Sidebar CTAs */
.sidebar-cta {
  width: 100%;
  text-align: center;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: var(--space-2);
}
.sidebar-cta-secondary {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: var(--radius-lg);
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: var(--space-3);
  transition: all 0.2s;
}
.sidebar-cta-secondary:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(193,216,47,0.04);
}

/* Section header action links */
.section-link-action {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-primary);
  text-decoration: none;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}
.section-link-action:hover { text-decoration: underline; }
.section-link-select {
  margin-left: auto;
  padding: 4px 10px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-primary);
  font-size: 0.72rem;
  cursor: pointer;
}

/* Coverage info pair (matching mockup) */
.coverage-info-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}
.coverage-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}
.coverage-value {
  font-size: 0.92rem;
  color: var(--color-text-primary);
  line-height: 1.5;
}
.coverage-extra {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-top: 4px;
}
@media (max-width: 768px) {
  .coverage-info-pair { grid-template-columns: 1fr; gap: var(--space-3); }
}

/* Review meta (matching mockup) */
.review-head-rich {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}
.reviewer-block {
  display: flex;
  align-items: center;
  gap: 10px;
}
.reviewer-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(193,216,47,0.15);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.92rem;
  flex-shrink: 0;
}
.reviewer-block strong {
  display: block;
  color: var(--color-text-primary);
  font-size: 0.88rem;
}
.reviewer-meta {
  display: block;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  margin-top: 2px;
}
.verified-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: #10b981;
  font-weight: 500;
}

/* Inquiry modal (Enviar consulta) */
.inquiry-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(6px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}
.inquiry-modal {
  position: relative;
  width: 100%;
  max-width: 480px;
  padding: var(--space-6);
  border-radius: var(--radius-2xl);
}
.inquiry-close {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.inquiry-close:hover { background: var(--color-bg-card); color: var(--color-text-primary); }
.inquiry-modal h3 { font-size: 1.1rem; margin-bottom: 6px; padding-right: 32px; }
.inquiry-sub {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}
.inquiry-textarea {
  width: 100%;
  padding: 12px 14px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.92rem;
  font-family: inherit;
  resize: vertical;
  outline: none;
  margin-bottom: var(--space-3);
}
.inquiry-textarea:focus { border-color: var(--color-primary); }
.inquiry-warn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(16,185,129,0.06);
  border-radius: var(--radius-md);
  color: #10b981;
  font-size: 0.72rem;
  margin-bottom: var(--space-3);
}
.inquiry-error {
  color: #E85D4A;
  font-size: 0.82rem;
  margin-bottom: var(--space-3);
}
.inquiry-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
.inquiry-success {
  text-align: center;
  padding: var(--space-6);
}
.inquiry-success svg { margin-bottom: var(--space-3); }
.inquiry-success p { color: var(--color-text-primary); font-size: 0.95rem; }

/* ── Hero trust badge ── */
.hero-badges {
  position: absolute;
  top: 96px;
  right: 24px;
  z-index: 4;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.hero-trust-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.55);
  color: #10b981;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.2px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* ── Mixes ── */
.mixes-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.mix-embed {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.mix-title-bar {
  padding: 10px 16px;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
}
.mix-iframe-wrap iframe {
  width: 100%;
  border: 0;
  display: block;
}

/* Mix destacado (Premium only) */
.mix-featured {
  position: relative;
  border-color: rgba(245,158,11,0.5) !important;
  box-shadow: 0 0 0 1px rgba(245,158,11,0.15), 0 8px 24px rgba(245,158,11,0.1);
}
.mix-featured-badge {
  position: absolute;
  top: -10px;
  right: 14px;
  z-index: 1;
  padding: 3px 10px;
  border-radius: 999px;
  background: #f59e0b;
  color: #0a0a0a;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.mix-iframe-wrap.mix-soundcloud iframe { height: 166px; }
.mix-iframe-wrap.mix-spotify iframe { height: 152px; }
.mix-iframe-wrap.mix-mixcloud iframe { height: 180px; }
.mix-iframe-wrap.mix-youtube { aspect-ratio: 16 / 9; }
.mix-iframe-wrap.mix-youtube iframe { height: 100%; aspect-ratio: 16 / 9; }
.mix-fallback {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  color: var(--color-primary);
  font-weight: 500;
  text-decoration: none;
}

/* ── Genres + Mood tag blocks ── */
.tag-block { margin-bottom: var(--space-4); }
.tag-block:last-child { margin-bottom: 0; }
.tag-block-label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}
.badge-mood {
  background: rgba(236, 72, 153, 0.1);
  color: #ec4899;
  border: 1px solid rgba(236, 72, 153, 0.3);
}

/* ── Reviews summary ── */
.review-summary {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: var(--space-8);
  padding: var(--space-5);
  margin-bottom: var(--space-6);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  align-items: center;
}
.review-big { text-align: center; }
.review-num {
  font-family: 'Poppins', sans-serif;
  font-size: 3rem;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1;
}
.review-stars-big {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin: 6px 0;
}
.review-count-label {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.review-breakdown {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.review-bar {
  display: grid;
  grid-template-columns: 140px 1fr 36px;
  gap: var(--space-3);
  align-items: center;
  font-size: 0.78rem;
}
.bar-label { color: var(--color-text-muted); }
.bar-track {
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  display: block;
  height: 100%;
  background: var(--color-primary);
  transition: width 0.4s ease;
}
.bar-num {
  color: var(--color-text-primary);
  text-align: right;
  font-weight: 600;
}

/* DJ response to reviews (Premium only) */
.review-response {
  margin-top: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: rgba(245, 158, 11, 0.06);
  border-left: 3px solid #f59e0b;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}
.response-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: 4px;
}
.response-tag {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.12);
  padding: 2px 8px;
  border-radius: 999px;
}
.review-response p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.response-editor { margin-top: var(--space-3); }
.response-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

/* Empty state for reviews */
.empty-reviews {
  text-align: center;
  padding: var(--space-8) var(--space-4);
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-xl);
  color: var(--color-text-muted);
}
.empty-reviews svg { color: #FBBF24; opacity: 0.7; margin-bottom: var(--space-3); }
.empty-reviews strong {
  display: block;
  color: var(--color-text-primary);
  font-size: 1rem;
  margin-bottom: var(--space-2);
}
.empty-reviews p { font-size: 0.85rem; }

/* ── Trust / Cómo funciona ── */
.trust-section h2 svg { color: #10b981; }
.trust-section {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), rgba(16, 185, 129, 0.01));
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
}
.trust-steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-top: var(--space-2);
}
.trust-step {
  display: flex;
  gap: var(--space-4);
  align-items: flex-start;
}
.trust-num {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #10b981;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.92rem;
}
.trust-text {
  color: var(--color-text-secondary);
  font-size: 0.92rem;
  line-height: 1.6;
  padding-top: 4px;
}
.trust-text strong { color: var(--color-text-primary); }

@media (max-width: 768px) {
  .review-summary { grid-template-columns: 1fr; gap: var(--space-5); }
  .review-bar { grid-template-columns: 110px 1fr 32px; font-size: 0.72rem; }
  .hero-badges { top: 80px; right: 12px; flex-wrap: wrap; max-width: calc(100vw - 24px); justify-content: flex-end; }
}

/* ── Stats strip (dashboard pública) ── */
.stats-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-8);
  margin-top: var(--space-4);
}
.stat-card-public {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
}
.stat-card-public:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
}
.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-lg);
  background: rgba(193,216,47,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}
.stat-content { min-width: 0; }
.stat-value-public {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.1;
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.stat-suffix {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted);
}
.stat-label-public {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-top: 2px;
}

/* ── Share button ── */
.btn-share {
  width: 100%;
  margin-top: var(--space-2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: 10px 16px;
  border-radius: var(--radius-lg);
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-share:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(193,216,47,0.04);
}

/* ── Public gallery ── */
.section-count {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}
.public-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--space-3);
}
.gallery-thumb {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  cursor: pointer;
  padding: 0;
  transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), border-color 0.2s;
}
.gallery-thumb:hover { transform: translateY(-3px); border-color: var(--color-primary); }
.gallery-thumb img {
  width: 100%; height: 100%; object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.gallery-thumb:hover img { transform: scale(1.05); }
.gallery-caption {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 18px 10px 8px;
  background: linear-gradient(transparent, rgba(0,0,0,0.85));
  color: #fff;
  font-size: 0.75rem;
  font-weight: 500;
  text-align: left;
  pointer-events: none;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}

/* ── Lightbox ── */
.lightbox-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0,0,0,0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}
.lightbox-content {
  max-width: 92vw;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}
.lightbox-content img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}
.lightbox-caption {
  color: #fff;
  font-size: 0.9rem;
  text-align: center;
  max-width: 80vw;
}
.lightbox-close,
.lightbox-nav {
  position: absolute;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: #fff;
  border-radius: 50%;
  width: 44px; height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
  backdrop-filter: blur(8px);
}
.lightbox-close:hover,
.lightbox-nav:hover { background: rgba(255,255,255,0.18); transform: scale(1.05); }
.lightbox-close { top: 20px; right: 20px; }
.lightbox-nav.prev { left: 20px; top: 50%; transform: translateY(-50%); }
.lightbox-nav.next { right: 20px; top: 50%; transform: translateY(-50%); }
.lightbox-nav.prev:hover { transform: translateY(-50%) scale(1.05); }
.lightbox-nav.next:hover { transform: translateY(-50%) scale(1.05); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .public-gallery { grid-template-columns: 1fr 1fr; }
  .lightbox-nav { width: 38px; height: 38px; }
  .lightbox-nav.prev { left: 10px; }
  .lightbox-nav.next { right: 10px; }
}

/* ── Location map ── */
.location-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.location-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}
.location-pill svg { color: var(--color-primary); flex-shrink: 0; }
.location-pill strong { color: var(--color-text-primary); }

.map-wrapper {
  border-radius: var(--radius-xl);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  position: relative;
}
.map-container {
  width: 100%;
  height: 320px;
  background: var(--color-bg-card);
}

:deep(.custom-marker) { background: none !important; border: none !important; }
:deep(.marker-dot) {
  width: 12px;
  height: 12px;
  background: var(--color-bg-primary);
  border: 2px solid var(--color-primary, #C1D82F);
  border-radius: 50%;
  box-shadow: 0 0 0 2px var(--color-bg-card), 0 0 8px rgba(193,216,47,0.4);
}
:deep(.marker-dot.active) {
  width: 18px;
  height: 18px;
  background: var(--color-primary, #C1D82F);
  box-shadow: 0 0 0 4px rgba(193,216,47,0.25), 0 0 16px rgba(193,216,47,0.6);
  animation: markerPulse 2s ease-in-out infinite;
}
@keyframes markerPulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(193,216,47,0.25), 0 0 16px rgba(193,216,47,0.6); }
  50% { box-shadow: 0 0 0 8px rgba(193,216,47,0.10), 0 0 20px rgba(193,216,47,0.7); }
}

:deep(.leaflet-control-zoom) {
  border: none !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
  margin: 12px !important;
}
:deep(.leaflet-control-zoom a) {
  background: var(--color-bg-card) !important;
  color: var(--color-text-secondary) !important;
  border: 1px solid var(--color-border) !important;
  width: 30px !important;
  height: 30px !important;
  line-height: 28px !important;
  font-size: 16px !important;
}
:deep(.leaflet-control-zoom a:hover) {
  background: var(--color-bg-card-hover) !important;
  color: var(--color-primary, #C1D82F) !important;
  border-color: var(--color-primary, #C1D82F) !important;
}
:deep(.leaflet-control-zoom-in) { border-radius: 8px 8px 0 0 !important; }
:deep(.leaflet-control-zoom-out) { border-radius: 0 0 8px 8px !important; border-top: none !important; }
:deep(.leaflet-container) {
  background: var(--color-bg-card) !important;
  font-family: inherit !important;
  outline: none !important;
}
</style>
