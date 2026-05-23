<template>
  <div class="talent-dash" :style="{ paddingTop: '100px' }">
    <div class="container">
      <!-- Header -->
      <header class="dash-header">
        <div class="dash-header-left">
          <h1 class="section-title">Panel de <span class="text-gradient">Talento</span></h1>
          <p class="section-subtitle">Gestiona tu perfil, reservas y disponibilidad</p>
        </div>
        <div class="dash-header-actions">
          <button class="btn btn-secondary btn-sm" @click="showPreview = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            Ver mi perfil público
          </button>
          <button class="btn btn-primary btn-sm" @click="activeTab = 'calendar'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            Bloquear fecha
          </button>
        </div>
      </header>

      <!-- Welcome banner: aparece para DJs nuevos (Standard sin bookings) -->
      <div v-if="showWelcomeBanner" class="welcome-banner">
        <span class="welcome-banner-icon">✓</span>
        <span>
          <strong>Tu perfil está publicado.</strong>
          Ya apareces en búsquedas. Las primeras solicitudes pueden tardar unos días en llegar.
        </span>
        <button class="welcome-dismiss" @click="dismissWelcome" aria-label="Cerrar">×</button>
      </div>

      <!-- "Tu Plan" — progreso hacia el siguiente plan (FIX #4) -->
      <div v-if="planProgress" class="plan-progress-card">
        <div class="plan-pp-badge-block">
          <div class="plan-pp-icon" :class="`plan-icon-${planProgress.currentTier}`">{{ planProgress.iconLetter }}</div>
          <div class="plan-pp-name">{{ planProgress.currentLabel }}</div>
          <div class="plan-pp-comm">Comisión {{ planProgress.commissionPct }}%</div>
        </div>

        <div class="plan-pp-body">
          <div class="plan-pp-headline">
            Tu camino para llegar al plan <span class="plan-pp-next">{{ planProgress.nextLabel }}</span>
          </div>
          <div class="plan-pp-sub">{{ planProgress.subText }}</div>
          <div class="plan-pp-bar">
            <div class="plan-pp-bar-fill" :style="{ width: planProgress.progressPct + '%' }"></div>
          </div>
          <div class="plan-pp-criteria">
            <div v-for="c in planProgress.criteria" :key="c.label" class="plan-pp-item">
              <span :class="['plan-pp-check', c.done ? 'check-done' : 'check-pending']">{{ c.done ? '✓' : '○' }}</span>
              <span>{{ c.label }}</span>
            </div>
          </div>
        </div>

        <div class="plan-pp-cta">
          <router-link to="/tiers" class="plan-pp-link">Ver requisitos completos →</router-link>
        </div>
      </div>

      <!-- Premium Invitation Banner -->
      <div v-if="premiumInvitation" class="premium-invite-banner">
        <div class="premium-invite-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="#f59e0b" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <div class="premium-invite-text">
          <strong>¡Has sido invitado a Pulsar Premium!</strong>
          <p v-if="premiumInvitation.message">{{ premiumInvitation.message }}</p>
          <p v-else>El equipo de Pulsar te invitó al tier más alto. Comisión 12%, slot en home, music supervisor.</p>
        </div>
        <div class="premium-invite-actions">
          <button class="btn btn-ghost btn-sm" :disabled="invitationActing" @click="actInvitation('decline')">No gracias</button>
          <button class="btn btn-primary btn-sm" :disabled="invitationActing" @click="actInvitation('accept')">
            Aceptar
          </button>
        </div>
      </div>

      <!-- Plan upsell — solo aparece cuando el DJ intenta hacer algo bloqueado por su Plan -->
      <Teleport to="body">
        <Transition name="fade">
          <div v-if="pendingUpsell" class="plan-upsell-backdrop" @click.self="pendingUpsell = null">
            <div class="plan-upsell-modal" :class="`plan-upsell-${pendingUpsell.upgradeTarget}`">
              <button class="plan-upsell-close" @click="pendingUpsell = null" aria-label="Cerrar">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
              <div class="plan-upsell-icon-big">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              </div>
              <h3>{{ pendingUpsell.headline }}</h3>
              <p>{{ pendingUpsell.action }}</p>
              <div class="plan-upsell-actions">
                <button class="btn btn-ghost btn-sm" @click="pendingUpsell = null">Ahora no</button>
                <router-link to="/tiers" class="plan-upsell-cta" @click="pendingUpsell = null">
                  {{ pendingUpsell.ctaLabel }}
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                </router-link>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card" v-for="s in statsCards" :key="s.label">
          <div class="stat-icon" :style="{ background: s.bg }">
            <span v-html="s.icon"></span>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ s.value }}</span>
            <span class="stat-label">{{ s.label }}</span>
            <span v-if="s.hint" class="stat-hint" :class="{ 'stat-hint-muted': s.hintMuted }">{{ s.hint }}</span>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <nav class="dash-tabs">
        <button v-for="t in tabs" :key="t.key" :class="['tab-btn', { active: activeTab === t.key, 'tab-locked': t.locked }]" @click="activeTab = t.key">
          <span v-html="t.icon"></span>
          {{ t.label }}
          <small v-if="t.hint && !t.locked" class="tab-hint">{{ t.hint }}</small>
          <span v-if="t.badge" class="tab-badge">{{ t.badge }}</span>
          <span v-if="t.locked" class="tab-lock-badge">{{ t.lockedPlan }} 🔒</span>
        </button>
      </nav>

      <!-- Tab Content -->
      <div class="tab-content">

        <!-- ═══ Solicitudes Pendientes ═══ -->
        <section v-if="activeTab === 'requests'" class="tab-panel animate-fade-in">
          <div v-if="pendingRequests.length === 0" class="empty-state-rich">
            <div class="empty-celebration-icon">🎉</div>
            <h3 class="empty-title">{{ profile ? 'Tu perfil está publicado' : '¡Bienvenido a Pulsar!' }}</h3>
            <p class="empty-desc">
              Las solicitudes empezarán a llegar cuando los clientes te encuentren en búsquedas.
              Mientras tanto, completa estos pasos para aparecer más arriba en los resultados y
              aumentar tus chances de booking.
            </p>

            <div class="empty-actions">
              <button class="btn btn-primary btn-sm" @click="activeTab = 'profile'">Completar mi perfil</button>
              <button class="btn btn-secondary btn-sm" @click="showPreview = true">Ver mi perfil público</button>
            </div>

            <!-- Checklist de primeros pasos -->
            <div class="first-steps">
              <h4>
                Tus primeros pasos
                <span class="first-steps-count">{{ firstStepsDoneCount }} de {{ firstSteps.length }}</span>
              </h4>
              <div v-for="step in firstSteps" :key="step.id" class="step-item" :class="{ done: step.done }">
                <div class="step-check" :class="step.done ? 'step-check-done' : 'step-check-todo'">
                  {{ step.done ? '✓' : '○' }}
                </div>
                <div class="step-text">
                  {{ step.text }}
                  <small v-if="step.note" class="step-note">{{ step.note }}</small>
                </div>
                <button v-if="!step.done && step.actionLabel" class="step-action" @click="step.action">
                  {{ step.actionLabel }} →
                </button>
              </div>
            </div>

            <p class="empty-tip">
              💡 Los DJs con perfil completo reciben <strong>3× más solicitudes</strong> que los incompletos.
            </p>
          </div>
          <div v-else class="request-list">
            <div v-for="b in pendingRequests" :key="b.id" class="request-card glass">
              <div class="request-header">
                <div class="request-client">
                  <div class="client-avatar">{{ b.client_name?.[0] || '?' }}</div>
                  <div>
                    <strong>{{ b.client_name }}</strong>
                    <span class="request-type badge">{{ b.event_type_display }}</span>
                  </div>
                </div>
                <span class="request-date">{{ formatDate(b.event_date) }}</span>
              </div>
              <div class="request-details">
                <div class="detail-chip"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg> {{ b.event_location || b.event_city }}</div>
                <div class="detail-chip"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> {{ b.event_time_start }} - {{ b.event_time_end }}</div>
                <div class="detail-chip"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/></svg> {{ b.guest_count }} personas</div>
                <div v-if="b.precio_estimado" class="detail-chip price"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg> ${{ b.precio_estimado }}</div>
              </div>
              <p v-if="b.description" class="request-desc">{{ b.description }}</p>

              <!-- Adjust Price -->
              <div class="adjust-section" v-if="adjustingId === b.id">
                <div class="adjust-row">
                  <label class="label">Precio propuesto ($)</label>
                  <input v-model.number="adjustPrice" type="number" class="input-field" placeholder="Ej: 500" />
                </div>
                <div class="adjust-row">
                  <label class="label">Notas al cliente</label>
                  <textarea v-model="adjustNotes" class="input-field" rows="2" placeholder="Explica el ajuste..."></textarea>
                </div>
              </div>

              <div class="request-actions">
                <button class="btn btn-primary btn-sm" @click="handleRequest(b.id, 'aceptada')" :disabled="actionLoading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                  Aceptar
                </button>
                <button class="btn btn-outline btn-sm" @click="toggleAdjust(b)" :disabled="actionLoading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  {{ adjustingId === b.id ? 'Enviar ajuste' : 'Ajustar' }}
                </button>
                <button class="btn btn-ghost btn-sm reject-btn" @click="handleRequest(b.id, 'rechazada')" :disabled="actionLoading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  Rechazar
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- ═══ Mis Reservas ═══ -->
        <section v-if="activeTab === 'bookings'" class="tab-panel animate-fade-in">
          <div v-if="allBookings.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <p>No tienes reservas aún</p>
          </div>
          <div v-else class="bookings-table">
            <div class="table-header">
              <span>Cliente</span><span>Evento</span><span>Fecha</span><span>Monto</span><span>Estado</span><span></span>
            </div>
            <div v-for="b in allBookings" :key="b.id" class="table-row" @click="$router.push(`/dashboard/bookings/${b.id}`)">
              <span class="cell-client">{{ b.client_name }}</span>
              <span>{{ b.event_type_display }}</span>
              <span>{{ formatDate(b.event_date) }}</span>
              <span class="cell-price">${{ b.quoted_price || b.precio_estimado || '—' }}</span>
              <span><span :class="['badge', statusBadge(b.status)]">{{ b.status_display }}</span></span>
              <span class="cell-arrow">→</span>
            </div>
          </div>
        </section>

        <!-- ═══ Ingresos ═══ -->
        <section v-if="activeTab === 'earnings'" class="tab-panel animate-fade-in">
          <!-- Tier + Comisión actual -->
          <div v-if="payout" class="payout-summary glass">
            <div class="payout-tier">
              <span class="payout-tier-label">Tu Plan</span>
              <strong :class="`tier-badge tier-${payout.tier}`">{{ tierLabelText(payout.tier) }}</strong>
              <span class="payout-commission">Comisión Pulsar: {{ Math.round(Number(payout.commission_pct)) }}%</span>
            </div>

            <!-- Escalera de progresión -->
            <div v-if="payout.progress && !payout.progress.invitation_only" class="payout-ladder">
              <div class="ladder-row">
                <span>Eventos completados</span>
                <strong>{{ payout.progress.events_done }} / {{ payout.progress.events_needed }}</strong>
              </div>
              <div class="ladder-bar"><div class="ladder-fill" :style="{ width: payout.progress.events_pct + '%' }"></div></div>

              <div class="ladder-row" style="margin-top: var(--space-3)">
                <span>Rating promedio</span>
                <strong>{{ Number(payout.progress.rating_current).toFixed(2) }} / {{ payout.progress.rating_needed }}</strong>
              </div>
              <div class="ladder-bar"><div class="ladder-fill" :style="{ width: payout.progress.rating_pct + '%' }"></div></div>

              <p class="ladder-note" v-if="payout.progress.eligible">
                ✓ Cumples requisitos. La promoción se aplicará al recibir tu próxima reseña.
              </p>
              <p class="ladder-note" v-else>
                Cumple los requisitos para subir automáticamente a <strong>Pro</strong> (comisión 15%).
              </p>
            </div>
            <div v-else-if="payout.progress?.invitation_only" class="payout-ladder">
              <p class="ladder-note premium-note">
                ★★ El siguiente nivel es <strong>Premium</strong> — solo por invitación de Pulsar. Mantén rating alto y entrega impecable.
              </p>
            </div>
          </div>

          <div class="earnings-grid">
            <div class="earnings-card glass">
              <h3>Cobrado (neto)</h3>
              <p class="earnings-amount text-gradient">${{ payout ? Number(payout.total_net).toFixed(2) : '0.00' }}</p>
              <span class="earnings-sub">De {{ completedCount }} eventos completados</span>
            </div>
            <div class="earnings-card glass">
              <h3>Por cobrar (neto)</h3>
              <p class="earnings-amount" style="color: var(--color-warning)">${{ payout ? Number(payout.pending_net).toFixed(2) : '0.00' }}</p>
              <span class="earnings-sub">Reservas confirmadas</span>
            </div>
            <div class="earnings-card glass">
              <h3>Total bruto</h3>
              <p class="earnings-amount" style="color: var(--color-text-muted)">${{ payout ? Number(payout.total_gross).toFixed(2) : '0.00' }}</p>
              <span class="earnings-sub">Antes de comisión</span>
            </div>
            <div class="earnings-card glass">
              <h3>Rating Promedio</h3>
              <p class="earnings-amount text-gradient">{{ profile?.rating_avg || '0.00' }} <span style="font-size:0.5em">★</span></p>
              <span class="earnings-sub">{{ profile?.total_reviews || 0 }} reseñas</span>
            </div>
          </div>

          <!-- Breakdown por booking -->
          <div v-if="payout?.items?.length" class="payout-items">
            <h4>Últimos payouts</h4>
            <div class="payout-table">
              <div class="payout-header">
                <span>Código</span><span>Fecha</span><span>Bruto</span><span>Comisión</span><span>Neto</span><span>Estado</span>
              </div>
              <div v-for="item in payout.items" :key="item.booking_id" class="payout-row">
                <span class="payout-code">{{ item.booking_code }}</span>
                <span>{{ formatDate(item.event_date) }}</span>
                <span>${{ Number(item.gross).toFixed(2) }}</span>
                <span class="payout-comm">−${{ Number(item.commission).toFixed(2) }}</span>
                <strong>${{ Number(item.net).toFixed(2) }}</strong>
                <span><span :class="['badge', item.status === 'completada' ? 'badge-success' : 'badge-warning']">{{ item.status }}</span></span>
              </div>
            </div>
          </div>
        </section>

        <!-- ═══ Calendario ═══ -->
        <section v-if="activeTab === 'calendar'" class="tab-panel animate-fade-in">
          <div class="calendar-container glass">
            <div class="calendar-header">
              <button class="btn btn-ghost btn-sm" @click="changeMonth(-1)">← Anterior</button>
              <h3>{{ monthNames[calMonth] }} {{ calYear }}</h3>
              <button class="btn btn-ghost btn-sm" @click="changeMonth(1)">Siguiente →</button>
            </div>
            <div class="calendar-weekdays">
              <span v-for="d in ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']" :key="d">{{ d }}</span>
            </div>
            <div class="calendar-grid">
              <div v-for="(day, i) in calendarDays" :key="i"
                :class="['cal-day', { 'other-month': !day.current, booked: day.status === 'booked', blocked: day.status === 'blocked', available: day.status === 'available', today: day.isToday }]"
                @click="day.current && toggleAvailability(day)">
                <span class="day-num">{{ day.day }}</span>
                <span v-if="day.status === 'booked'" class="day-tag">Reservado</span>
                <span v-else-if="day.status === 'blocked'" class="day-tag">Bloqueado</span>
              </div>
            </div>
            <div class="calendar-legend">
              <span class="legend-item"><span class="legend-dot" style="background: var(--color-primary)"></span> Disponible</span>
              <span class="legend-item"><span class="legend-dot" style="background: var(--color-accent)"></span> Reservado</span>
              <span class="legend-item"><span class="legend-dot" style="background: var(--color-text-muted)"></span> Bloqueado</span>
            </div>
          </div>
        </section>

        <!-- ═══ Galería ═══ -->
        <section v-if="activeTab === 'gallery'" class="tab-panel animate-fade-in">
          <div class="gallery-header">
            <div>
              <h3 class="gallery-h3">Fotos de eventos</h3>
              <p class="gallery-sub">Sube fotos de tus eventos pasados. Los clientes podrán verlas en tu perfil público.</p>
            </div>
            <button class="btn btn-primary btn-sm" @click="openGalleryPicker" :disabled="uploadingPhotos">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              {{ uploadingPhotos ? `Subiendo ${uploadProgress}...` : 'Agregar fotos' }}
            </button>
            <input ref="galleryInput" type="file" accept="image/*" hidden multiple @change="onGalleryFilesSelected" />
            <ImageCropper
              :file="pendingGalleryPhoto"
              :aspect-ratio="1"
              :max-output="1200"
              :title="galleryQueue.length > 1 ? `Recorta foto (${galleryQueue.length} en cola)` : 'Recorta tu foto'"
              @cropped="onGalleryPhotoCropped"
              @cancel="skipCurrentGalleryPhoto"
            />
          </div>

          <!-- Drop zone (cuando no hay fotos o quieres agregar más) -->
          <div
            class="gallery-dropzone"
            :class="{ dragging: galleryDragging }"
            @dragenter.prevent="galleryDragging = true"
            @dragover.prevent="galleryDragging = true"
            @dragleave.prevent="galleryDragging = false"
            @drop.prevent="onGalleryDrop"
          >
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
            <p>Arrastra fotos aquí o haz click en "Agregar fotos"</p>
            <span class="dropzone-hint">JPG, PNG o WebP — múltiples archivos · podrás recortar cada una</span>
          </div>

          <!-- Grid de fotos existentes -->
          <div v-if="photoMedia.length" class="photos-grid">
            <div v-for="photo in photoMedia" :key="photo.id" class="photo-tile">
              <img :src="photo.file" :alt="photo.title || 'Foto de evento'" />
              <div class="photo-overlay">
                <input
                  type="text"
                  class="photo-caption-input"
                  :value="photo.title"
                  @blur="updatePhotoTitle(photo, $event.target.value)"
                  @keyup.enter="$event.target.blur()"
                  placeholder="Ej: Boda Casco Antiguo · 2026"
                />
                <button class="photo-delete" @click="deletePhoto(photo.id)" title="Eliminar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 01-2 2H9a2 2 0 01-2-2L5 6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
              </div>
            </div>
          </div>
          <div v-else-if="!loadingMedia" class="empty-state" style="padding: var(--space-8)">
            <p style="opacity: 0.6">Aún no has subido fotos. Las primeras 6 fotos son las que los clientes ven primero.</p>
          </div>

          <!-- Mixes / Audio -->
          <div class="gallery-header" style="margin-top: var(--space-10)">
            <div>
              <h3 class="gallery-h3">Mixes & sets</h3>
              <p class="gallery-sub">Pega links de SoundCloud, Spotify, Mixcloud o YouTube. Los clientes podrán escucharlos sin salir de tu perfil.</p>
            </div>
          </div>

          <div class="mix-add-row">
            <input
              v-model="newMixTitle"
              type="text"
              class="input-field"
              placeholder="Título (ej: Wedding Mix · Beach Vibes 2026)"
            />
            <input
              v-model="newMixUrl"
              type="url"
              class="input-field"
              placeholder="https://soundcloud.com/..."
              @keyup.enter="addMix"
            />
            <button class="btn btn-primary btn-sm" :disabled="!newMixUrl || addingMix" @click="addMix">
              {{ addingMix ? 'Agregando...' : 'Agregar' }}
            </button>
          </div>

          <div v-if="audioMedia.length" class="mix-list-dash">
            <div v-for="mix in audioMedia" :key="mix.id" class="mix-row">
              <div class="mix-row-icon" v-html="mixProviderIcon(mix.url)"></div>
              <div class="mix-row-info">
                <strong>{{ mix.title || 'Sin título' }} <span v-if="mix.is_cover && profile?.talent_level === 'premium'" class="mix-featured-tag">★ Destacado</span></strong>
                <a :href="mix.url" target="_blank" rel="noopener" class="mix-row-url">{{ mix.url }}</a>
              </div>
              <button
                v-if="profile?.talent_level === 'premium'"
                class="mix-row-feature"
                :class="{ active: mix.is_cover }"
                @click="toggleMixFeatured(mix)"
                :title="mix.is_cover ? 'Quitar destacado' : 'Marcar como destacado'"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" :fill="mix.is_cover ? '#f59e0b' : 'none'" stroke="#f59e0b" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              </button>
              <button class="mix-row-del" @click="deletePhoto(mix.id)" title="Eliminar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 01-2 2H9a2 2 0 01-2-2L5 6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
              </button>
            </div>
          </div>

          <!-- Video en vivo -->
          <div class="gallery-header" style="margin-top: var(--space-10)">
            <div>
              <h3 class="gallery-h3">
                Video en vivo
                <span v-if="videoLocked" class="inline-lock-badge">Pro 🔒</span>
              </h3>
              <p class="gallery-sub">
                <template v-if="videoLocked">Disponible en plan Pro · Muestra tu show a los clientes.</template>
                <template v-else>Pega links de YouTube o Vimeo. Lo más vendedor: el público bailando, no solo el DJ.</template>
              </p>
            </div>
          </div>

          <!-- Card locked si el Plan no permite videos -->
          <div v-if="videoLocked" class="video-locked-card">
            <div class="vlc-icon">🔒</div>
            <div class="vlc-content">
              <strong>Tu plan Standard no incluye video en vivo</strong>
              <p>Sube a plan Pro para mostrar tu show en vivo a los clientes. Los DJs con video reciben hasta el doble de solicitudes.</p>
            </div>
            <router-link to="/tiers" class="btn btn-secondary btn-sm">Ver requisitos para Pro</router-link>
          </div>

          <template v-else>
            <div class="mix-add-row">
              <input v-model="newVideoTitle" type="text" class="input-field" placeholder="Título (ej: Boda Casco Antiguo 2026)" />
              <input v-model="newVideoUrl" type="url" class="input-field" placeholder="https://youtube.com/watch?v=..." @keyup.enter="addVideo" />
              <button class="btn btn-primary btn-sm" :disabled="!newVideoUrl || addingVideo" @click="addVideo">
                {{ addingVideo ? 'Agregando...' : 'Agregar' }}
              </button>
            </div>
            <div v-if="videoMedia.length" class="mix-list-dash">
              <div v-for="vid in videoMedia" :key="vid.id" class="mix-row">
                <div class="mix-row-icon">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
                </div>
                <div class="mix-row-info">
                  <strong>{{ vid.title || 'Sin título' }}</strong>
                  <a :href="vid.url" target="_blank" rel="noopener" class="mix-row-url">{{ vid.url }}</a>
                </div>
                <button class="mix-row-del" @click="deletePhoto(vid.id)" title="Eliminar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 01-2 2H9a2 2 0 01-2-2L5 6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
              </div>
            </div>
          </template>
        </section>

        <!-- ═══ Paquetes ═══ -->
        <section v-if="activeTab === 'packs'" class="tab-panel animate-fade-in">
          <div class="gallery-header">
            <div>
              <h3 class="gallery-h3">Mis Tarifas</h3>
              <p class="gallery-sub">Define cuánto cobras por evento. Estas son las tarifas que verá el cliente cuando te contrate.</p>
            </div>
            <button class="btn btn-primary btn-sm" @click="openPackForm()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Nueva tarifa
            </button>
          </div>

          <!-- Nota Partner: para DJs con equipo propio -->
          <div class="partner-hint">
            <div class="partner-hint-title">💡 Importante: estas son tarifas de tu performance</div>
            <p>
              Las tarifas que ves aquí son solo del DJ (tu show). El sonido, luces y demás producción se cotizan aparte.
            </p>
            <p>
              ¿Tienes equipo propio de sonido?
              <router-link to="/account" class="partner-link">Activa tu rol Aliado →</router-link>
              para ofrecer también paquetes de producción y ganar más por evento.
            </p>
          </div>

          <div v-if="packForm.open" class="pack-editor glass">
            <h4 class="pack-editor-title">{{ packForm.id ? 'Editar tarifa' : 'Nueva tarifa' }}</h4>
            <div class="form-grid">
              <div class="form-group full">
                <label class="label">Nombre</label>
                <input v-model="packForm.name" class="input-field" placeholder="Ej: Pack Boda Esencial" />
              </div>
              <div class="form-group">
                <label class="label">Precio ($)</label>
                <input v-model.number="packForm.price" type="number" class="input-field" placeholder="600" />
              </div>
              <div class="form-group">
                <label class="label">Duración (horas)</label>
                <input v-model.number="packForm.duration_hours" type="number" step="0.5" class="input-field" placeholder="4" />
              </div>
              <div class="form-group">
                <label class="label">Etiqueta si no hay precio</label>
                <input v-model="packForm.price_label" class="input-field" placeholder="Cotizar (opcional)" />
              </div>
              <div class="form-group">
                <label class="label">
                  <input v-model="packForm.is_featured" type="checkbox" style="margin-right: 6px" />
                  Marcar como "Popular"
                </label>
              </div>
              <div class="form-group full">
                <label class="label">Items incluidos</label>
                <div class="mood-input-wrap">
                  <div v-if="packForm.included_items.length" class="mood-tag-list">
                    <span v-for="(item, idx) in packForm.included_items" :key="idx" class="equip-chip equip-chip-yes">
                      ✓ {{ item }}
                      <button type="button" class="mood-tag-x" @click="packForm.included_items.splice(idx, 1)" aria-label="Quitar">×</button>
                    </span>
                  </div>
                  <input v-model="newPackItem" class="input-field" placeholder="Ej: DJ + sonido básico" @keydown.enter.prevent="addPackItem" />
                </div>
              </div>
            </div>
            <div class="form-actions">
              <button class="btn btn-primary btn-sm" :disabled="!packForm.name || savingPack" @click="savePack">
                {{ savingPack ? 'Guardando...' : (packForm.id ? 'Actualizar' : 'Crear') }}
              </button>
              <button class="btn btn-ghost btn-sm" @click="packForm.open = false">Cancelar</button>
            </div>
          </div>

          <div v-if="packs.length" class="packs-dash-grid">
            <div v-for="p in packs" :key="p.id" class="pack-dash-card" :class="{ featured: p.is_featured }">
              <div v-if="p.is_featured" class="pack-popular">POPULAR</div>
              <strong>{{ p.name }}</strong>
              <div class="pack-dash-price">
                <span v-if="p.price">${{ Number(p.price).toFixed(0) }}</span>
                <span v-else>{{ p.price_label || 'Cotizar' }}</span>
                <span v-if="p.duration_hours" class="pack-duration"> · {{ Number(p.duration_hours) }}h</span>
              </div>
              <ul v-if="p.included_items?.length" class="pack-includes">
                <li v-for="(item, idx) in p.included_items" :key="idx">{{ item }}</li>
              </ul>
              <div class="pack-dash-actions">
                <button class="btn btn-ghost btn-sm" @click="openPackForm(p)">Editar</button>
                <button class="btn btn-ghost btn-sm" style="color: #ef4444" @click="deletePack(p.id)">Eliminar</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-state" style="padding: var(--space-8)">
            <p style="opacity: 0.6">Aún no tienes tarifas configuradas. Crea una para que los clientes vean cuánto cobras.</p>
          </div>
        </section>

        <!-- ═══ FAQ ═══ -->
        <section v-if="activeTab === 'faqs'" class="tab-panel animate-fade-in">
          <!-- Locked preview (Plan Standard no incluye FAQ) -->
          <div v-if="faqLocked" class="locked-preview">
            <div class="locked-icon">🔒</div>
            <h3>FAQ está disponible en plan PRO</h3>
            <p class="locked-desc">
              Responde preguntas comunes de tus clientes ("¿Tomas requests?", "¿Cuánto tiempo de setup necesitas?")
              directamente en tu perfil público. Descarga preguntas repetidas a tu chat.
            </p>
            <div class="locked-requirements">
              <div class="locked-req-title">PARA DESBLOQUEAR FAQ</div>
              <div class="locked-req-list">
                <div>✓ Completa <strong>10 eventos</strong> (tienes {{ profile?.total_bookings || 0 }})</div>
                <div>✓ Mantén rating ≥ 4.5 ({{ profile?.total_reviews ? `tienes ${Number(profile.rating_avg).toFixed(1)}` : 'sin reseñas aún' }})</div>
                <div>✓ Cero cancelaciones en 6 meses</div>
              </div>
            </div>
            <router-link to="/tiers" class="btn btn-secondary btn-sm" style="margin-top: var(--space-4)">
              Ver requisitos del plan Pro
            </router-link>
          </div>

          <div v-else class="gallery-header">
            <div>
              <h3 class="gallery-h3">Preguntas frecuentes</h3>
              <p class="gallery-sub">Anticipa las dudas más comunes. Reduce mensajes repetidos y aumenta la conversión.</p>
            </div>
            <button class="btn btn-primary btn-sm" @click="openFaqForm()">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Nueva pregunta
            </button>
          </div>

          <template v-if="!faqLocked">
            <div v-if="faqForm.open" class="pack-editor glass">
              <h4 class="pack-editor-title">{{ faqForm.id ? 'Editar pregunta' : 'Nueva pregunta' }}</h4>
              <div class="form-grid">
                <div class="form-group full">
                  <label class="label">Pregunta</label>
                  <input v-model="faqForm.question" class="input-field" placeholder="Ej: ¿Puedo enviarte mi lista de canciones?" />
                </div>
                <div class="form-group full">
                  <label class="label">Respuesta</label>
                  <textarea v-model="faqForm.answer" class="input-field" rows="3" placeholder="Tu respuesta..."></textarea>
                </div>
              </div>
              <div class="form-actions">
                <button class="btn btn-primary btn-sm" :disabled="!faqForm.question || savingFaq" @click="saveFaq">
                  {{ savingFaq ? 'Guardando...' : (faqForm.id ? 'Actualizar' : 'Crear') }}
                </button>
                <button class="btn btn-ghost btn-sm" @click="faqForm.open = false">Cancelar</button>
              </div>
            </div>

            <div v-if="faqs.length" class="faq-dash-list">
              <div v-for="f in faqs" :key="f.id" class="faq-dash-item">
                <div class="faq-dash-q">{{ f.question }}</div>
                <p v-if="f.answer" class="faq-dash-a">{{ f.answer }}</p>
                <div class="faq-dash-actions">
                  <button class="btn btn-ghost btn-sm" @click="openFaqForm(f)">Editar</button>
                  <button class="btn btn-ghost btn-sm" style="color: #ef4444" @click="deleteFaq(f.id)">Eliminar</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state" style="padding: var(--space-8)">
              <p style="opacity: 0.6">Aún no tienes preguntas. Sugerencias: "¿Puedo enviarte mi lista?", "¿Tomas requests?", "¿Cuánto setup necesitas?"</p>
            </div>
          </template>
        </section>

        <!-- ═══ Editar Perfil ═══ -->
        <section v-if="activeTab === 'profile'" class="tab-panel animate-fade-in">
          <!-- Profile status overview (FIX #1) -->
          <div class="profile-status-header">
            <div>
              <h3 class="profile-status-title">Mi Perfil · {{ profileCompletionPct }}% completo</h3>
              <p class="profile-status-sub">Mientras más completo tu perfil, más alto apareces en búsquedas.</p>
            </div>
          </div>

          <div class="profile-status-grid">
            <div v-for="f in profileFields" :key="f.id" class="profile-status-card" :class="{ locked: f.locked }">
              <div class="psc-icon" :class="`psc-icon-${f.state}`">{{ f.iconChar }}</div>
              <div class="psc-info">
                <div class="psc-title">{{ f.title }}</div>
                <div class="psc-desc" :class="{ 'psc-desc-cyan': f.locked }">{{ f.desc }}</div>
              </div>
              <a v-if="f.actionLabel" class="psc-action" @click.prevent="f.action">{{ f.actionLabel }} →</a>
            </div>
          </div>

          <!-- Tip motivacional -->
          <div class="profile-tip">
            <span class="profile-tip-emoji">💡</span>
            <span>
              <strong>Tip:</strong> Los DJs con bio escrita y al menos 1 mix subido reciben
              <strong class="profile-tip-highlight">3× más solicitudes</strong>.
            </span>
          </div>

          <form @submit.prevent="saveProfile" class="profile-form">
            <!-- Cover Photo Upload -->
            <div class="cover-upload-section">
              <label class="label">Foto de Portada</label>
              <div class="cover-upload-area" @click="$refs.coverInput.click()" @dragover.prevent @drop.prevent="handleCoverDrop">
                <img v-if="coverPreview || profile?.cover_photo" :src="coverPreview || profile?.cover_photo" class="cover-preview" />
                <div v-else class="cover-placeholder">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  <p>Haz clic o arrastra una imagen aquí</p>
                  <span class="text-muted">JPG, PNG o WebP — máx 5MB</span>
                </div>
              </div>
              <input ref="coverInput" type="file" accept="image/jpeg,image/png,image/webp" hidden @change="handleCoverSelect" />
              <ImageCropper
                :file="pendingCover"
                :aspect-ratio="3"
                :max-output="1600"
                title="Ajusta tu foto de portada"
                @cropped="onCoverCropped"
                @cancel="pendingCover = null"
              />
              <button v-if="coverFile" type="button" class="btn btn-primary btn-sm" style="margin-top: var(--space-3)" @click="uploadCover" :disabled="uploadingCover">
                {{ uploadingCover ? 'Subiendo...' : '📷 Subir Foto de Portada' }}
              </button>
            </div>

            <div class="form-grid">
              <div class="form-group full">
                <label class="label">Nombre Artístico</label>
                <input v-model="profileForm.stage_name" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">Tipo de Talento</label>
                <select v-model="profileForm.talent_type" class="input-field">
                  <option value="dj">DJ</option>
                  <option value="musician">Músico</option>
                  <option value="band">Banda</option>
                </select>
              </div>
              <div class="form-group">
                <label class="label">Tarifa por Hora ($)</label>
                <input v-model.number="profileForm.hourly_rate" type="number" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">Ciudad</label>
                <input v-model="profileForm.city" class="input-field" />
              </div>
              <div class="form-group">
                <label class="label">País</label>
                <input v-model="profileForm.country" class="input-field" />
              </div>
              <div class="form-group full">
                <label class="label">Tagline</label>
                <input v-model="profileForm.tagline" class="input-field" placeholder="Frase corta que te describe" />
              </div>
              <div class="form-group full">
                <label class="label">Descripción / Biografía</label>
                <textarea v-model="profileForm.description" class="input-field" rows="4"></textarea>
              </div>
              <div class="form-group">
                <label class="label">Años de Experiencia</label>
                <input v-model.number="profileForm.experience_years" type="number" class="input-field" />
              </div>

              <div class="form-group full">
                <label class="label">Vibe / Mood</label>
                <div class="mood-input-wrap">
                  <div v-if="profileForm.mood_tags && profileForm.mood_tags.length" class="mood-tag-list">
                    <span v-for="(tag, idx) in profileForm.mood_tags" :key="idx" class="mood-tag-chip">
                      {{ tag }}
                      <button type="button" class="mood-tag-x" @click="removeMoodTag(idx)" aria-label="Quitar">×</button>
                    </span>
                  </div>
                  <input
                    v-model="newMoodTag"
                    type="text"
                    class="input-field"
                    placeholder="Escribe un vibe y presiona Enter (ej: Boda elegante)"
                    @keydown.enter.prevent="addMoodTag"
                  />
                </div>
                <small style="color: var(--color-text-muted); font-size: 0.78rem;">Ej: Boda elegante, After party, Cocktail formal, Cumpleaños hype</small>
              </div>

              <!-- Tipos de eventos -->
              <div class="form-group full">
                <label class="label">Tipos de eventos que cubres</label>
                <div class="event-type-grid">
                  <button
                    v-for="et in eventTypeOptions"
                    :key="et.value"
                    type="button"
                    class="event-type-tile"
                    :class="{ selected: profileForm.event_types.includes(et.value) }"
                    @click="toggleEventType(et.value)"
                  >
                    <span class="event-tile-icon" v-html="et.icon"></span>
                    <span>{{ et.label }}</span>
                  </button>
                </div>
              </div>

              <!-- Idiomas -->
              <div class="form-group full">
                <label class="label">Idiomas en MC</label>
                <div class="mood-input-wrap">
                  <div v-if="profileForm.languages && profileForm.languages.length" class="mood-tag-list">
                    <span v-for="(lang, idx) in profileForm.languages" :key="idx" class="lang-chip">
                      {{ lang }}
                      <button type="button" class="mood-tag-x" @click="removeLanguage(idx)" aria-label="Quitar">×</button>
                    </span>
                  </div>
                  <input v-model="newLanguage" type="text" class="input-field" placeholder="Ej: Español, Inglés, Portugués" @keydown.enter.prevent="addLanguage" />
                </div>
              </div>

              <!-- Equipamiento split -->
              <div class="form-group">
                <label class="label">Equipo que traes</label>
                <div class="mood-input-wrap">
                  <div v-if="profileForm.equipment_brings && profileForm.equipment_brings.length" class="mood-tag-list">
                    <span v-for="(item, idx) in profileForm.equipment_brings" :key="idx" class="equip-chip equip-chip-yes">
                      ✓ {{ item }}
                      <button type="button" class="mood-tag-x" @click="removeEquipBring(idx)" aria-label="Quitar">×</button>
                    </span>
                  </div>
                  <input v-model="newEquipBring" type="text" class="input-field" placeholder="Ej: 2x CDJ-3000" @keydown.enter.prevent="addEquipBring" />
                </div>
              </div>

              <div class="form-group">
                <label class="label">No incluido</label>
                <div class="mood-input-wrap">
                  <div v-if="profileForm.equipment_not_included && profileForm.equipment_not_included.length" class="mood-tag-list">
                    <span v-for="(item, idx) in profileForm.equipment_not_included" :key="idx" class="equip-chip equip-chip-no">
                      ✕ {{ item }}
                      <button type="button" class="mood-tag-x" @click="removeEquipNo(idx)" aria-label="Quitar">×</button>
                    </span>
                  </div>
                  <input v-model="newEquipNo" type="text" class="input-field" placeholder="Ej: Sonido +80 personas" @keydown.enter.prevent="addEquipNo" />
                </div>
              </div>

              <!-- Zonas de cobertura -->
              <div class="form-group full">
                <label class="label">Zonas específicas que cubres</label>
                <div class="mood-input-wrap">
                  <div v-if="profileForm.service_zones && profileForm.service_zones.length" class="mood-tag-list">
                    <span v-for="(zone, idx) in profileForm.service_zones" :key="idx" class="lang-chip">
                      📍 {{ zone }}
                      <button type="button" class="mood-tag-x" @click="removeZone(idx)" aria-label="Quitar">×</button>
                    </span>
                  </div>
                  <input v-model="newZone" type="text" class="input-field" placeholder="Ej: Casco Antiguo, Costa del Este, Coronado" @keydown.enter.prevent="addZone" />
                </div>
                <small style="color: var(--color-text-muted); font-size: 0.78rem;">Lista los barrios/ciudades específicos donde te presentas.</small>
              </div>

              <div class="form-group">
                <label class="label">Cargo fuera del área ($)</label>
                <input v-model.number="profileForm.travel_fee_extra" type="number" min="0" step="1" class="input-field" placeholder="50" />
                <small style="color: var(--color-text-muted); font-size: 0.78rem;">Si te llaman fuera de tu área, este es el extra por traslado.</small>
              </div>


            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="saving">
                {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
              <span v-if="saveSuccess" class="save-msg">✓ Perfil actualizado</span>
            </div>
          </form>
        </section>

      </div>
    </div>

    <!-- ═══ Profile Preview Modal ═══ -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showPreview" class="preview-backdrop" @click.self="showPreview = false">
          <div class="preview-modal animate-fade-in-up">
            <!-- Close -->
            <button class="preview-close" @click="showPreview = false" aria-label="Cerrar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>

            <!-- Cover -->
            <div class="preview-cover">
              <img :src="profile?.cover_photo || previewPlaceholderCover" alt="Cover" />
              <div class="preview-cover-overlay"></div>
              <span class="preview-label">👁 Vista previa — Así te ven los clientes</span>
            </div>

            <!-- Body -->
            <div class="preview-body">
              <div class="preview-avatar-section">
                <div class="preview-avatar-wrap">
                  <img :src="profile?.user?.avatar || previewPlaceholderAvatar" alt="Avatar" class="preview-avatar" />
                  <span v-if="profile?.is_available" class="preview-status-dot" title="Disponible"></span>
                </div>
                <div class="preview-identity">
                  <h2>{{ profile?.stage_name || auth.user?.first_name || 'Tu nombre' }}</h2>
                  <div class="preview-badges">
                    <span class="badge">{{ previewTypeLabel }}</span>
                    <span v-if="profile?.talent_level" class="badge" :class="profile.talent_level === 'premium' ? 'badge-accent' : ''">{{ profile.talent_level === 'premium' ? '⭐ Premium' : 'Standard' }}</span>
                  </div>
                </div>
              </div>

              <!-- Quick stats -->
              <div class="preview-stats">
                <div class="preview-stat">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                  <span>{{ profile?.city || '—' }}</span>
                </div>
                <div v-if="profile?.experience_years" class="preview-stat">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  <span>{{ profile.experience_years }} años exp.</span>
                </div>
                <div v-if="profile?.hourly_rate" class="preview-stat">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
                  <strong>${{ profile.hourly_rate }}</strong>/hora
                </div>
                <div v-if="profile?.rating_avg" class="preview-stat">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="#FBBF24" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                  <strong>{{ Number(profile.rating_avg).toFixed(1) }}</strong>
                  <span class="muted">({{ profile.total_reviews || 0 }})</span>
                </div>
              </div>

              <!-- Bio -->
              <div v-if="profile?.description" class="preview-section">
                <h4>Sobre mí</h4>
                <p>{{ profile.description }}</p>
              </div>

              <!-- Genres -->
              <div v-if="profile?.genres?.length" class="preview-section">
                <h4>Géneros</h4>
                <div class="preview-genres">
                  <span v-for="g in profile.genres" :key="g.id || g" class="badge">{{ g.name || g }}</span>
                </div>
              </div>



              <!-- Footer -->
              <div class="preview-footer">
                <router-link :to="`/talent/${profile?.id}`" class="btn btn-primary btn-sm" @click="showPreview = false">Ir a mi perfil público</router-link>
                <button class="btn btn-ghost btn-sm" @click="showPreview = false">Cerrar</button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import ImageCropper from '@/components/common/ImageCropper.vue'

const auth = useAuthStore()
const activeTab = ref('requests')
const bookings = ref([])
const profile = ref(null)
const availability = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const adjustingId = ref(null)
const adjustPrice = ref(null)
const adjustNotes = ref('')
const saving = ref(false)
const saveSuccess = ref(false)
const coverFile = ref(null)
const coverPreview = ref(null)
const uploadingCover = ref(false)
const showPreview = ref(false)

const previewPlaceholderCover = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400"%3E%3Cdefs%3E%3ClinearGradient id="g" x1="0" y1="0" x2="1" y2="1"%3E%3Cstop offset="0%25" stop-color="%23C1D82F" stop-opacity="0.15"/%3E%3Cstop offset="100%25" stop-color="%23E85D4A" stop-opacity="0.08"/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill="%230A0A0A" width="1200" height="400"/%3E%3Crect fill="url(%23g)" width="1200" height="400"/%3E%3C/svg%3E'
const previewPlaceholderAvatar = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120"%3E%3Crect fill="%230A0A0A" width="120" height="120" rx="60"/%3E%3Ccircle cx="60" cy="45" r="20" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3Cpath d="M30 95a30 30 0 0160 0" fill="none" stroke="%23C1D82F" stroke-width="2" opacity="0.5"/%3E%3C/svg%3E'

const previewTypeLabel = computed(() => {
  const map = { dj: 'DJ', musician: 'Músico', band: 'Banda' }
  return map[profile.value?.talent_type] || 'Talento'
})

const pendingCover = ref(null)

function handleCoverSelect(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (file) checkAndQueueCover(file)
}

function handleCoverDrop(e) {
  const file = e.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) checkAndQueueCover(file)
}

function checkAndQueueCover(file) {
  if (file.size > 5 * 1024 * 1024) {
    alert('La imagen no puede superar 5MB.')
    return
  }
  pendingCover.value = file
}

function onCoverCropped(croppedFile) {
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverFile.value = croppedFile
  coverPreview.value = URL.createObjectURL(croppedFile)
  pendingCover.value = null
}

async function uploadCover() {
  if (!coverFile.value) return
  uploadingCover.value = true
  try {
    // Si no existe perfil, crearlo primero con los datos actuales del formulario
    if (!profile.value) {
      const { data: created } = await api.post('/talents/create/', profileForm)
      profile.value = created
    }
    const formData = new FormData()
    formData.append('cover_photo', coverFile.value)
    const { data } = await api.post('/talents/me/cover-photo/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    profile.value.cover_photo = data.cover_photo
    coverFile.value = null
    saveSuccess.value = true
    setTimeout(() => saveSuccess.value = false, 3000)
  } catch (e) {
    alert('Error al subir la foto: ' + (e.response?.data?.error || e.response?.data?.stage_name?.[0] || 'Intenta de nuevo'))
  }
  uploadingCover.value = false
}

// ── Talent payout dashboard ──
const payout = ref(null)

async function fetchPayout() {
  try {
    const { data } = await api.get('/talents/me/payout/')
    payout.value = data
  } catch { /* silent */ }
}

function tierLabelText(tier) {
  if (tier === 'premium') return '★★ Premium'
  if (tier === 'pro') return '★ Pro'
  return 'Standard'
}

// ── Premium Invitation ──
const premiumInvitation = ref(null)
const invitationActing = ref(false)

async function fetchPremiumInvitation() {
  try {
    const { data } = await api.get('/premium/my-invitation/')
    premiumInvitation.value = data.invitation
  } catch { /* silent */ }
}

async function actInvitation(action) {
  if (!premiumInvitation.value) return
  invitationActing.value = true
  try {
    await api.post(`/premium/invitations/${premiumInvitation.value.id}/action/`, { action })
    premiumInvitation.value = null
    if (action === 'accept') {
      // Refresh profile to get new tier
      await fetchProfile()
    }
  } catch (err) {
    alert(err.response?.data?.error || 'No se pudo procesar.')
  }
  invitationActing.value = false
}

// ── Tier limits & warnings ──
const tierLimits = ref(null)

async function fetchTierLimits() {
  try {
    const { data } = await api.get('/talents/me/tier-limits/')
    tierLimits.value = data
  } catch { /* silent */ }
}

const FEATURE_BENEFITS = {
  video: {
    plural: 'videos',
    proBenefit: 'mostrar tu show en vivo y duplicar tus solicitudes',
    premiumBenefit: 'cargar hasta 4 videos + un video bio destacado',
  },
  pack: {
    plural: 'paquetes',
    proBenefit: 'ofrecer 1 paquete con precio fijo y vender sin cotizar caso por caso',
    premiumBenefit: 'crear paquetes ilimitados con pricing dinámico de alta temporada',
  },
  faq: {
    plural: 'FAQs',
    proBenefit: 'responder hasta 3 preguntas frecuentes y reducir mensajes repetidos',
    premiumBenefit: 'crear FAQs ilimitadas — Pulsar te ayuda a redactarlas',
  },
  photo: {
    plural: 'fotos',
    proBenefit: 'mostrar hasta 10 fotos de eventos pasados',
    premiumBenefit: 'galería ilimitada + sesión de fotos profesional gratis',
  },
  mix: {
    plural: 'mixes',
    proBenefit: 'subir hasta 4 mixes y ganar prioridad en búsqueda',
    premiumBenefit: 'mixes ilimitados + un mix destacado en tu perfil',
  },
}

const PLAN_LABELS = { standard: 'Standard', pro: 'Pro', premium: 'Premium' }

// Modal upsell: aparece solo cuando el DJ intenta hacer algo bloqueado
const pendingUpsell = ref(null)

// ── Welcome banner (DJs nuevos, dismiss persiste en localStorage) ──
const welcomeDismissed = ref(localStorage.getItem('pulsar-welcome-dismissed') === '1')
const showWelcomeBanner = computed(() => {
  if (welcomeDismissed.value) return false
  if (!profile.value) return false
  // Solo cuando aún no tiene reservas (recién publicado)
  return (profile.value.total_bookings || 0) === 0
})
function dismissWelcome() {
  welcomeDismissed.value = true
  localStorage.setItem('pulsar-welcome-dismissed', '1')
}

// ── FAQ locked para Plan Standard ──
const faqLocked = computed(() => {
  const info = tierLimits.value?.usage?.faq
  return info ? info.limit === 0 : false
})

// ── Video locked para Plan Standard ──
const videoLocked = computed(() => {
  const info = tierLimits.value?.usage?.video
  return info ? info.limit === 0 : false
})

// ── Tab indicators ──
const photoCountHint = computed(() => {
  const photos = (galleryMedia.value || []).filter(m => m.media_type === 'photo').length
  const limit = tierLimits.value?.usage?.photo?.limit
  if (limit == null) return photos > 0 ? String(photos) : null
  return `${photos}/${limit}`
})

const profileCompletionPct = computed(() => {
  if (!profile.value) return 0
  const p = profile.value
  const checks = [
    !!p.user?.avatar,
    Array.isArray(p.genres) && p.genres.length > 0,
    !!(p.hourly_rate || p.price_min),
    !!p.description && p.description.length >= 50,
    !!p.city,
    (galleryMedia.value || []).filter(m => m.media_type === 'photo').length >= 1,
    (galleryMedia.value || []).filter(m => m.media_type === 'audio').length >= 1,
    !!p.cover_photo,
  ]
  return Math.round((checks.filter(Boolean).length / checks.length) * 100)
})

const profileCompletionHint = computed(() => `${profileCompletionPct.value}%`)

// ── Profile status grid (FIX #1 + Mi Perfil rediseño) ──
const profileFields = computed(() => {
  const p = profile.value || {}
  const mixes = (galleryMedia.value || []).filter(m => m.media_type === 'audio').length

  const fields = [
    {
      id: 'avatar',
      title: 'Foto de perfil',
      done: !!p.user?.avatar,
      desc: p.user?.avatar ? 'Foto subida' : 'Sin foto · Súbela para destacar',
      actionLabel: !p.user?.avatar ? 'Subir' : null,
      action: () => { document.querySelector('.profile-form .cover-upload-area')?.scrollIntoView({ behavior: 'smooth' }) },
    },
    {
      id: 'genres',
      title: 'Géneros musicales',
      done: Array.isArray(p.genres) && p.genres.length > 0,
      desc: Array.isArray(p.genres) && p.genres.length > 0 ? `${p.genres.length} géneros configurados` : 'Sin géneros · Elige al menos 3',
      actionLabel: Array.isArray(p.genres) && p.genres.length > 0 ? null : 'Elegir',
      action: () => { document.querySelector('[name="genre_ids"], .profile-form')?.scrollIntoView({ behavior: 'smooth' }) },
    },
    {
      id: 'mixes',
      title: `Mixes (${mixes}/${tierLimits.value?.usage?.mix?.limit ?? '∞'})`,
      done: mixes >= 1,
      desc: mixes === 0 ? 'Sin mixes subidos' : `${mixes} ${mixes === 1 ? 'mix subido' : 'mixes subidos'}`,
      actionLabel: 'Subir',
      action: () => { activeTab.value = 'gallery' },
    },
    {
      id: 'video',
      title: 'Video en vivo',
      locked: videoLocked.value,
      done: !videoLocked.value && (galleryMedia.value || []).filter(m => m.media_type === 'video').length > 0,
      desc: videoLocked.value
        ? 'Disponible en plan Pro · Muestra tu show a clientes'
        : 'Sin videos subidos',
      actionLabel: videoLocked.value ? 'Ver Pro' : 'Subir',
      action: () => { if (videoLocked.value) { pendingUpsell.value = makeUpsell('video') } else { activeTab.value = 'gallery' } },
    },
    {
      id: 'bio',
      title: 'Bio profesional',
      done: !!p.description && p.description.length >= 50,
      desc: !p.description
        ? 'Vacía · Mín. 50 caracteres'
        : p.description.length < 50
          ? `${p.description.length}/50 caracteres · Necesitas más`
          : `${p.description.length} caracteres`,
      actionLabel: (!p.description || p.description.length < 50) ? 'Escribir' : null,
      action: () => { document.querySelector('textarea[v-model*="description"]')?.scrollIntoView({ behavior: 'smooth' }) },
    },
    {
      id: 'rate',
      title: 'Tarifa base',
      done: !!(p.hourly_rate || p.price_min),
      desc: p.hourly_rate
        ? `$${p.hourly_rate}/hora configurada`
        : p.price_min
          ? `Desde $${p.price_min}`
          : 'Sin tarifa configurada',
      actionLabel: !(p.hourly_rate || p.price_min) ? 'Configurar' : null,
      action: () => { activeTab.value = 'packs' },
    },
  ]

  // Asignar state visual a cada card
  return fields.map(f => ({
    ...f,
    state: f.locked ? 'locked' : f.done ? 'done' : 'pending',
    iconChar: f.locked ? '🔒' : f.done ? '✓' : '!',
  }))
})

// ── Primeros pasos (empty state Solicitudes, FIX #3) ──
const firstSteps = computed(() => {
  const p = profile.value || {}
  const photos = (galleryMedia.value || []).filter(m => m.media_type === 'photo').length
  const mixes = (galleryMedia.value || []).filter(m => m.media_type === 'audio').length
  const availabilityCount = (availability.value || []).length

  return [
    {
      id: 'avatar',
      text: 'Foto de perfil',
      done: !!p.user?.avatar,
      actionLabel: 'Subir',
      action: () => { activeTab.value = 'profile' },
    },
    {
      id: 'genres',
      text: 'Géneros musicales',
      note: Array.isArray(p.genres) && p.genres.length > 0 ? `(${p.genres.length} configurados)` : '',
      done: Array.isArray(p.genres) && p.genres.length > 0,
      actionLabel: 'Elegir',
      action: () => { activeTab.value = 'profile' },
    },
    {
      id: 'rate',
      text: 'Tarifa base configurada',
      done: !!(p.hourly_rate || p.price_min),
      actionLabel: 'Configurar',
      action: () => { activeTab.value = 'profile' },
    },
    {
      id: 'mix',
      text: 'Sube tu primer mix',
      note: `(${mixes}/2)`,
      done: mixes >= 1,
      actionLabel: 'Subir',
      action: () => { activeTab.value = 'gallery' },
    },
    {
      id: 'bio',
      text: 'Escribe tu bio',
      note: '(50 caracteres mínimo)',
      done: !!p.description && p.description.length >= 50,
      actionLabel: 'Escribir',
      action: () => { activeTab.value = 'profile' },
    },
    {
      id: 'photos',
      text: 'Sube 3 fotos a la galería',
      note: `(${photos}/3)`,
      done: photos >= 3,
      actionLabel: 'Subir',
      action: () => { activeTab.value = 'gallery' },
    },
    {
      id: 'availability',
      text: 'Configura disponibilidad del mes',
      done: availabilityCount > 0,
      actionLabel: 'Configurar',
      action: () => { activeTab.value = 'calendar' },
    },
  ]
})
const firstStepsDoneCount = computed(() => firstSteps.value.filter(s => s.done).length)

// ── Tu Plan: progreso hacia el siguiente plan (FIX #4) ──
// La comisión se lee del backend (payout endpoint) para mantener una sola fuente de verdad.
// Si el payout aún no cargó, se usa fallback (también en sintonía con backend defaults).
const PLAN_DATA = {
  standard: { letter: 'S', label: 'STANDARD', fallbackCommission: 20, next: 'pro', nextLabel: 'PRO' },
  pro:      { letter: 'P', label: '★ PRO',    fallbackCommission: 15, next: 'premium', nextLabel: 'PREMIUM' },
  premium:  { letter: 'P', label: '★★ PREMIUM', fallbackCommission: 12, next: null, nextLabel: null },
}

const planProgress = computed(() => {
  const tier = profile.value?.talent_level || 'standard'
  const data = PLAN_DATA[tier]
  if (!data || !data.next) return null

  // Comisión: si tenemos payout cargado, usar su valor (que viene del PlatformConfig real)
  const commissionPct = payout.value?.commission_pct
    ? Math.round(Number(payout.value.commission_pct))
    : data.fallbackCommission

  const eventsDone = profile.value?.total_bookings || 0
  const eventsNeeded = 10
  const ratingCurrent = Number(profile.value?.rating_avg || 0)
  const ratingNeeded = 4.5
  const cancelations = 0 // backend signal lo valida — asumimos 0 visible

  // Completitud del perfil — 7 campos clave
  const profileChecks = [
    !!profile.value?.user?.avatar,
    Array.isArray(profile.value?.genres) && profile.value.genres.length > 0,
    !!(profile.value?.hourly_rate || profile.value?.price_min),
    !!profile.value?.description && profile.value.description.length >= 50,
    !!profile.value?.city,
    (galleryMedia.value || []).filter(m => m.media_type === 'photo').length >= 1,
    (galleryMedia.value || []).filter(m => m.media_type === 'audio').length >= 1,
  ]
  const profileDoneCount = profileChecks.filter(Boolean).length
  const profilePct = Math.round((profileDoneCount / profileChecks.length) * 100)

  // Progreso global hacia el siguiente plan (pondera eventos + rating + perfil)
  const eventsPct = Math.min(100, (eventsDone / eventsNeeded) * 100)
  const ratingPct = ratingCurrent > 0 ? Math.min(100, (ratingCurrent / ratingNeeded) * 100) : 0
  const overallPct = Math.round((eventsPct + ratingPct + profilePct) / 3)

  const subText = data.next === 'pro'
    ? 'Con plan Pro tu comisión baja a 15%, recibes prioridad en búsquedas y desbloqueas video, FAQ y más fotos.'
    : 'Con plan Premium tu comisión baja a 12%, slot permanente en home, fotos pro gratis y un music supervisor.'

  return {
    currentTier: tier,
    currentLabel: data.label,
    commissionPct,
    nextLabel: data.nextLabel,
    iconLetter: data.letter,
    subText,
    progressPct: overallPct,
    criteria: [
      { label: `${eventsDone}/${eventsNeeded} eventos completados`, done: eventsDone >= eventsNeeded },
      { label: `Perfil ${profilePct}% completo`, done: profilePct >= 100 },
      { label: `Rating mínimo ${ratingNeeded}${ratingCurrent > 0 ? ` (tienes ${ratingCurrent.toFixed(1)})` : ' (sin reseñas)'}`, done: ratingCurrent >= ratingNeeded },
      { label: `${cancelations} cancelaciones en 6 meses`, done: cancelations === 0 && eventsDone > 0 },
    ],
  }
})

function makeUpsell(kind) {
  if (!tierLimits.value) return null
  const info = (tierLimits.value.usage || {})[kind]
  if (!info) return null
  if (info.can_add || info.limit === null) return null

  const currentTier = tierLimits.value.tier
  const upgradeTarget = currentTier === 'standard' ? 'pro' : currentTier === 'pro' ? 'premium' : null
  if (!upgradeTarget) return null

  const feat = FEATURE_BENEFITS[kind]
  if (!feat) return null

  const benefit = upgradeTarget === 'pro' ? feat.proBenefit : feat.premiumBenefit
  const planLabel = PLAN_LABELS[currentTier] || currentTier
  const upgradeLabel = PLAN_LABELS[upgradeTarget]

  const headline = info.limit === 0
    ? `Tu Plan ${planLabel} no incluye ${feat.plural}.`
    : `Llegaste al límite de ${feat.plural} (${info.current}/${info.limit}) en tu Plan ${planLabel}.`

  return {
    headline,
    action: `Haz upgrade al Plan ${upgradeLabel} para ${benefit}.`,
    ctaLabel: `Ver requisitos para ${upgradeLabel}`,
    upgradeTarget,
  }
}

/**
 * Helper que valida tier limits antes de ejecutar la acción.
 * Si el Plan no permite agregar más → muestra el modal upsell y retorna false.
 * Si sí permite → ejecuta el callback y retorna true.
 */
function tryAdd(kind, onAllowed) {
  const upsell = makeUpsell(kind)
  if (upsell) {
    pendingUpsell.value = upsell
    return false
  }
  if (typeof onAllowed === 'function') onAllowed()
  return true
}

// ── Gallery (event photos) ──
const galleryMedia = ref([])
const loadingMedia = ref(false)
const uploadingPhotos = ref(false)
const uploadProgress = ref('')
const galleryDragging = ref(false)
const photoMedia = computed(() => galleryMedia.value.filter(m => m.media_type === 'photo'))
const audioMedia = computed(() => galleryMedia.value.filter(m => m.media_type === 'audio'))

const newMixTitle = ref('')
const newMixUrl = ref('')
const addingMix = ref(false)

function mixProviderIcon(url) {
  if (!url) return ''
  const u = url.toLowerCase()
  if (u.includes('soundcloud')) return '<svg width="22" height="22" viewBox="0 0 24 24" fill="#FF5500"><path d="M1.18 16.84c.05-.04.07-.1.07-.16v-3.86c0-.06-.02-.12-.07-.16-.05-.04-.1-.06-.16-.04-.06.02-.1.07-.1.13v3.96c0 .06.04.11.1.13.06.02.11 0 .16-.04zm17.84-9.43c-.66 0-1.3.14-1.87.4-.38-4.32-4.01-7.7-8.42-7.7-1.08 0-2.12.21-3.07.58-.37.14-.46.29-.46.58v15.07c0 .31.24.55.55.55h13.27c2.61 0 4.73-2.12 4.73-4.74s-2.12-4.74-4.73-4.74z"/></svg>'
  if (u.includes('spotify')) return '<svg width="22" height="22" viewBox="0 0 24 24" fill="#1DB954"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.42 1.56-.299.421-1.02.599-1.559.3z"/></svg>'
  if (u.includes('mixcloud')) return '<svg width="22" height="22" viewBox="0 0 24 24" fill="#52ABFF"><path d="M16.59 13.27a.7.7 0 01-.7-.7c0-.7-.57-1.28-1.28-1.28-.7 0-1.28.57-1.28 1.28a.7.7 0 11-1.4 0c0-1.48 1.2-2.68 2.68-2.68s2.68 1.2 2.68 2.68a.7.7 0 01-.7.7zm-9.18 0a.7.7 0 01-.7-.7c0-.7-.57-1.28-1.28-1.28-.7 0-1.28.57-1.28 1.28a.7.7 0 11-1.4 0c0-1.48 1.2-2.68 2.68-2.68s2.68 1.2 2.68 2.68a.7.7 0 01-.7.7z"/></svg>'
  if (u.includes('youtube') || u.includes('youtu.be')) return '<svg width="22" height="22" viewBox="0 0 24 24" fill="#FF0000"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
  return '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>'
}

const videoMedia = computed(() => galleryMedia.value.filter(m => m.media_type === 'video'))
const newVideoTitle = ref('')
const newVideoUrl = ref('')
const addingVideo = ref(false)

async function addVideo() {
  if (!newVideoUrl.value || !profile.value) {
    if (!profile.value) alert('Primero completa tu perfil antes de añadir videos.')
    return
  }
  if (!tryAdd('video')) return
  addingVideo.value = true
  try {
    const { data } = await api.post(`/talents/${profile.value.id}/media/`, {
      media_type: 'video',
      url: newVideoUrl.value.trim(),
      title: newVideoTitle.value.trim(),
    })
    galleryMedia.value.unshift(data)
    newVideoTitle.value = ''
    newVideoUrl.value = ''
  } catch (err) {
    alert('No se pudo agregar el video. Verifica la URL.')
  }
  addingVideo.value = false
}

// ── Packs CRUD ──
const packs = ref([])
const packForm = reactive({
  open: false,
  id: null,
  name: '',
  price: null,
  price_label: '',
  duration_hours: null,
  is_featured: false,
  included_items: [],
})
const newPackItem = ref('')
const savingPack = ref(false)

function openPackForm(pack = null) {
  // Solo gateamos al crear NUEVO (editar uno existente siempre permitido)
  if (!pack && !tryAdd('pack')) return
  if (pack) {
    Object.assign(packForm, {
      open: true,
      id: pack.id,
      name: pack.name,
      price: pack.price,
      price_label: pack.price_label || '',
      duration_hours: pack.duration_hours,
      is_featured: pack.is_featured,
      included_items: Array.isArray(pack.included_items) ? [...pack.included_items] : [],
    })
  } else {
    Object.assign(packForm, {
      open: true, id: null, name: '', price: null, price_label: '',
      duration_hours: null, is_featured: false, included_items: [],
    })
  }
  newPackItem.value = ''
}

function addPackItem() {
  const v = newPackItem.value.trim()
  if (!v) return
  packForm.included_items.push(v)
  newPackItem.value = ''
}

async function savePack() {
  if (!profile.value) { alert('Primero completa tu perfil.'); return }
  savingPack.value = true
  const payload = {
    name: packForm.name,
    price: packForm.price || null,
    price_label: packForm.price_label,
    duration_hours: packForm.duration_hours || null,
    is_featured: packForm.is_featured,
    included_items: packForm.included_items,
  }
  try {
    if (packForm.id) {
      const { data } = await api.patch(`/talents/packs/${packForm.id}/`, payload)
      const idx = packs.value.findIndex(p => p.id === packForm.id)
      if (idx >= 0) packs.value[idx] = data
    } else {
      const { data } = await api.post(`/talents/${profile.value.id}/packs/`, payload)
      packs.value.push(data)
    }
    packForm.open = false
  } catch (err) {
    alert('No se pudo guardar el paquete.')
  }
  savingPack.value = false
}

async function deletePack(id) {
  if (!confirm('¿Eliminar esta tarifa?')) return
  try {
    await api.delete(`/talents/packs/${id}/`)
    packs.value = packs.value.filter(p => p.id !== id)
  } catch {
    alert('No se pudo eliminar.')
  }
}

async function fetchPacks() {
  if (!profile.value) return
  try {
    const { data } = await api.get(`/talents/${profile.value.id}/packs/`)
    packs.value = data.results || data
  } catch { /* silent */ }
}

// ── FAQs CRUD ──
const faqs = ref([])
const faqForm = reactive({
  open: false,
  id: null,
  question: '',
  answer: '',
})
const savingFaq = ref(false)

function openFaqForm(faq = null) {
  // Gating al crear nuevo (editar siempre permitido)
  if (!faq && !tryAdd('faq')) return
  if (faq) {
    Object.assign(faqForm, { open: true, id: faq.id, question: faq.question, answer: faq.answer || '' })
  } else {
    Object.assign(faqForm, { open: true, id: null, question: '', answer: '' })
  }
}

async function saveFaq() {
  if (!profile.value) { alert('Primero completa tu perfil.'); return }
  savingFaq.value = true
  const payload = { question: faqForm.question, answer: faqForm.answer }
  try {
    if (faqForm.id) {
      const { data } = await api.patch(`/talents/faqs/${faqForm.id}/`, payload)
      const idx = faqs.value.findIndex(f => f.id === faqForm.id)
      if (idx >= 0) faqs.value[idx] = data
    } else {
      const { data } = await api.post(`/talents/${profile.value.id}/faqs/`, payload)
      faqs.value.push(data)
    }
    faqForm.open = false
  } catch (err) {
    alert('No se pudo guardar la FAQ.')
  }
  savingFaq.value = false
}

async function deleteFaq(id) {
  if (!confirm('¿Eliminar esta pregunta?')) return
  try {
    await api.delete(`/talents/faqs/${id}/`)
    faqs.value = faqs.value.filter(f => f.id !== id)
  } catch {
    alert('No se pudo eliminar.')
  }
}

async function fetchFaqs() {
  if (!profile.value) return
  try {
    const { data } = await api.get(`/talents/${profile.value.id}/faqs/`)
    faqs.value = data.results || data
  } catch { /* silent */ }
}

async function toggleMixFeatured(mix) {
  if (!profile.value || profile.value.talent_level !== 'premium') return
  const newValue = !mix.is_cover
  try {
    await api.patch(`/talents/media/${mix.id}/`, { is_cover: newValue })
    // Si lo marcamos como destacado, desmarcar los otros audio en local
    if (newValue) {
      galleryMedia.value.forEach(m => {
        if (m.media_type === 'audio' && m.id !== mix.id) m.is_cover = false
      })
    }
    mix.is_cover = newValue
  } catch {
    alert('No se pudo actualizar.')
  }
}

async function addMix() {
  if (!newMixUrl.value || !profile.value) {
    if (!profile.value) alert('Primero completa tu perfil antes de añadir mixes.')
    return
  }
  if (!tryAdd('mix')) return
  addingMix.value = true
  try {
    const { data } = await api.post(`/talents/${profile.value.id}/media/`, {
      media_type: 'audio',
      url: newMixUrl.value.trim(),
      title: newMixTitle.value.trim(),
    })
    galleryMedia.value.unshift(data)
    newMixTitle.value = ''
    newMixUrl.value = ''
  } catch (err) {
    alert('No se pudo agregar el mix. Verifica que la URL sea válida.')
  }
  addingMix.value = false
}

async function fetchMedia() {
  if (!profile.value) return
  loadingMedia.value = true
  try {
    const { data } = await api.get(`/talents/${profile.value.id}/media/`)
    galleryMedia.value = data.results || data
  } catch { /* silent */ }
  loadingMedia.value = false
}

// Cola de fotos a recortar antes de subir
const galleryQueue = ref([])
const pendingGalleryPhoto = computed(() => galleryQueue.value[0] || null)

function onGalleryFilesSelected(e) {
  const files = Array.from(e.target.files || [])
  enqueueGalleryFiles(files)
  e.target.value = ''
}

function onGalleryDrop(e) {
  galleryDragging.value = false
  const files = Array.from(e.dataTransfer.files || []).filter(f => f.type.startsWith('image/'))
  enqueueGalleryFiles(files)
}

const galleryInput = ref(null)

function openGalleryPicker() {
  if (!profile.value) {
    alert('Primero completa tu perfil antes de subir fotos.')
    return
  }
  // Si llegó al límite de su Plan → mostrar upsell en vez de abrir el picker
  if (!tryAdd('photo')) return
  galleryInput.value?.click()
}

function enqueueGalleryFiles(files) {
  if (!profile.value) {
    alert('Primero completa tu perfil antes de subir fotos.')
    return
  }
  // Doble check para drag-and-drop
  if (!tryAdd('photo')) return
  const valid = files.filter(f => {
    if (f.size > 8 * 1024 * 1024) {
      alert(`"${f.name}" supera 8MB y se omitió.`)
      return false
    }
    return true
  })
  galleryQueue.value.push(...valid)
}

async function onGalleryPhotoCropped(croppedFile) {
  galleryQueue.value.shift()
  await uploadPhotos([croppedFile])
}

function skipCurrentGalleryPhoto() {
  galleryQueue.value.shift()
}

async function uploadPhotos(files) {
  if (!files.length || !profile.value) {
    if (!profile.value) alert('Primero completa tu perfil antes de subir fotos.')
    return
  }
  uploadingPhotos.value = true
  let done = 0
  for (const file of files) {
    if (file.size > 8 * 1024 * 1024) {
      alert(`"${file.name}" supera 8MB y se omitió.`)
      done++
      continue
    }
    uploadProgress.value = `${done + 1}/${files.length}`
    const fd = new FormData()
    fd.append('media_type', 'photo')
    fd.append('file', file)
    fd.append('title', '')
    try {
      const { data } = await api.post(`/talents/${profile.value.id}/media/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      galleryMedia.value.unshift(data)
    } catch (err) {
      console.error('Upload failed:', err)
    }
    done++
  }
  uploadingPhotos.value = false
  uploadProgress.value = ''
}

async function deletePhoto(id) {
  if (!confirm('¿Eliminar esta foto?')) return
  try {
    await api.delete(`/talents/media/${id}/`)
    galleryMedia.value = galleryMedia.value.filter(m => m.id !== id)
  } catch (err) {
    alert('No se pudo eliminar la foto.')
  }
}

async function updatePhotoTitle(photo, newTitle) {
  if (newTitle === photo.title) return
  try {
    await api.patch(`/talents/media/${photo.id}/`, { title: newTitle })
    photo.title = newTitle
  } catch { /* silent — no rompemos UX */ }
}

const calMonth = ref(new Date().getMonth())
const calYear = ref(new Date().getFullYear())
const monthNames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const profileForm = reactive({
  stage_name: '', talent_type: 'dj', hourly_rate: 0, city: '', country: 'Venezuela',
  tagline: '', description: '', experience_years: 0,
  instagram: '', tiktok: '', soundcloud: '', spotify: '',
  mood_tags: [],
  event_types: [],
  languages: [],
  equipment_brings: [],
  equipment_not_included: [],
  service_zones: [],
  travel_fee_extra: null,
})

const newZone = ref('')
function addZone() {
  const v = newZone.value.trim()
  if (!v) return
  if (!Array.isArray(profileForm.service_zones)) profileForm.service_zones = []
  if (!profileForm.service_zones.includes(v)) profileForm.service_zones.push(v)
  newZone.value = ''
}
function removeZone(idx) { profileForm.service_zones.splice(idx, 1) }

const SVG_OPEN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
const eventTypeOptions = [
  { value: 'wedding', label: 'Bodas', icon: `${SVG_OPEN}<circle cx="9" cy="15" r="5"/><circle cx="16" cy="15" r="5"/><path d="M7 9l2-5h6l2 5"/></svg>` },
  { value: 'corporate', label: 'Corporativo', icon: `${SVG_OPEN}<rect x="4" y="3" width="16" height="18" rx="1"/><line x1="9" y1="7" x2="9" y2="7.01"/><line x1="13" y1="7" x2="13" y2="7.01"/><line x1="9" y1="11" x2="9" y2="11.01"/><line x1="13" y1="11" x2="13" y2="11.01"/><line x1="9" y1="15" x2="9" y2="15.01"/><line x1="13" y1="15" x2="13" y2="15.01"/></svg>` },
  { value: 'birthday', label: 'Cumpleaños', icon: `${SVG_OPEN}<path d="M20 21v-8a2 2 0 00-2-2H6a2 2 0 00-2 2v8"/><path d="M4 16s1.5-2 4-2 3.5 2 4 2 1.5-2 4-2 4 2 4 2"/><line x1="2" y1="21" x2="22" y2="21"/><line x1="12" y1="4" x2="12" y2="11"/><path d="M10.5 4.5C10.5 3 12 2 12 2s1.5 1 1.5 2.5a1.5 1.5 0 01-3 0z"/></svg>` },
  { value: 'cocktail', label: 'Cocktail / Brunch', icon: `${SVG_OPEN}<path d="M5 3h14l-7 9z"/><path d="M12 12v9"/><path d="M8 21h8"/><circle cx="16" cy="6" r="0.8" fill="currentColor"/></svg>` },
  { value: 'club', label: 'Club / Residencia', icon: `${SVG_OPEN}<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><path d="M12 3v3"/><path d="M12 18v3"/><path d="M3 12h3"/><path d="M18 12h3"/><path d="M5.6 5.6l2.1 2.1"/><path d="M16.3 16.3l2.1 2.1"/><path d="M5.6 18.4l2.1-2.1"/><path d="M16.3 7.7l2.1-2.1"/></svg>` },
  { value: 'launch', label: 'Lanzamiento', icon: `${SVG_OPEN}<path d="M4.5 16.5L3 21l4.5-1.5"/><path d="M14 4l6 6-9 9-6-6z"/><circle cx="15.5" cy="8.5" r="1.5"/></svg>` },
  { value: 'graduation', label: 'Graduación', icon: `${SVG_OPEN}<path d="M22 10L12 5 2 10l10 5 10-5z"/><path d="M6 12v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/></svg>` },
  { value: 'festival', label: 'Festival', icon: `${SVG_OPEN}<path d="M2 20h20"/><path d="M12 3L4 20"/><path d="M12 3l8 17"/><path d="M12 3v17"/><path d="M9 20l3-6 3 6"/></svg>` },
  { value: 'private', label: 'Fiesta Privada', icon: `${SVG_OPEN}<path d="M5.8 11.3L2 22l10.7-3.79"/><path d="M4 3h.01"/><path d="M22 8h.01"/><path d="M15 2h.01"/><path d="M22 20h.01"/><path d="M22 2l-2.24.75a2.9 2.9 0 00-1.96 3.12c.1.86-.57 1.63-1.45 1.63h-.38c-.86 0-1.6.6-1.76 1.44L14 10"/><path d="M22 13l-.82-.33c-.86-.34-1.82.2-1.98 1.11c-.11.7-.72 1.22-1.43 1.22H17"/><path d="M11 2L11.33 2.82c.34.86-.2 1.82-1.11 1.98c-.7.11-1.22.72-1.22 1.43V7"/></svg>` },
  { value: 'anniversary', label: 'Aniversario', icon: `${SVG_OPEN}<path d="M12 21s-7-4.5-7-10a4 4 0 017-2.65A4 4 0 0119 11c0 5.5-7 10-7 10z"/></svg>` },
]

function toggleEventType(value) {
  if (!Array.isArray(profileForm.event_types)) profileForm.event_types = []
  const idx = profileForm.event_types.indexOf(value)
  if (idx >= 0) profileForm.event_types.splice(idx, 1)
  else profileForm.event_types.push(value)
}

const newLanguage = ref('')
function addLanguage() {
  const v = newLanguage.value.trim()
  if (!v) return
  if (!Array.isArray(profileForm.languages)) profileForm.languages = []
  if (!profileForm.languages.includes(v)) profileForm.languages.push(v)
  newLanguage.value = ''
}
function removeLanguage(idx) { profileForm.languages.splice(idx, 1) }

const newEquipBring = ref('')
function addEquipBring() {
  const v = newEquipBring.value.trim()
  if (!v) return
  if (!Array.isArray(profileForm.equipment_brings)) profileForm.equipment_brings = []
  profileForm.equipment_brings.push(v)
  newEquipBring.value = ''
}
function removeEquipBring(idx) { profileForm.equipment_brings.splice(idx, 1) }

const newEquipNo = ref('')
function addEquipNo() {
  const v = newEquipNo.value.trim()
  if (!v) return
  if (!Array.isArray(profileForm.equipment_not_included)) profileForm.equipment_not_included = []
  profileForm.equipment_not_included.push(v)
  newEquipNo.value = ''
}
function removeEquipNo(idx) { profileForm.equipment_not_included.splice(idx, 1) }

// ── Mood tags input ──
const newMoodTag = ref('')

function addMoodTag() {
  const value = newMoodTag.value.trim()
  if (!value) return
  if (!Array.isArray(profileForm.mood_tags)) profileForm.mood_tags = []
  if (profileForm.mood_tags.length >= 8) {
    alert('Máximo 8 vibes para no saturar el perfil.')
    return
  }
  if (profileForm.mood_tags.includes(value)) {
    newMoodTag.value = ''
    return
  }
  profileForm.mood_tags.push(value)
  newMoodTag.value = ''
}

function removeMoodTag(idx) {
  profileForm.mood_tags.splice(idx, 1)
}

// Computed
const pendingRequests = computed(() => bookings.value.filter(b => ['solicitud_enviada','pendiente_respuesta'].includes(b.status)))
const allBookings = computed(() => bookings.value)
const completedBookings = computed(() => bookings.value.filter(b => b.status === 'completada'))
const completedCount = computed(() => completedBookings.value.length)
const totalEarnings = computed(() => completedBookings.value.reduce((sum, b) => sum + parseFloat(b.quoted_price || b.precio_estimado || 0), 0) * 0.85)
const pendingEarnings = computed(() => bookings.value.filter(b => ['confirmada','pendiente_pago'].includes(b.status)).reduce((sum, b) => sum + parseFloat(b.quoted_price || b.precio_estimado || 0), 0) * 0.85)

const tabs = computed(() => [
  { key: 'requests', label: 'Solicitudes', badge: pendingRequests.value.length || null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>' },
  { key: 'bookings', label: 'Reservas', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>' },
  { key: 'earnings', label: 'Ingresos', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>' },
  { key: 'calendar', label: 'Calendario', badge: null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/></svg>' },
  { key: 'gallery', label: 'Galería', badge: photoMedia.value.length || null, hint: photoCountHint.value, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>' },
  { key: 'packs', label: 'Mis Tarifas', badge: packs.value.length || null, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>' },
  { key: 'faqs', label: 'FAQ', badge: faqs.value.length || null, locked: tierLimits.value?.usage?.faq?.limit === 0, lockedPlan: 'Pro', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' },
  { key: 'profile', label: 'Mi Perfil', badge: null, hint: profileCompletionHint.value, icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4-4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
])

const statsCards = computed(() => {
  const pending = pendingRequests.value.length
  const active = bookings.value.filter(b => ['confirmada','pendiente_pago','aceptada'].includes(b.status)).length
  const completed = completedCount.value
  const rating = Number(profile.value?.rating_avg || 0)
  const reviewsCount = profile.value?.total_reviews || 0

  return [
    {
      label: 'Solicitudes pendientes',
      value: pending,
      bg: 'var(--color-primary-ultra-light)',
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
      hint: pending === 0 ? 'Llegan cuando los clientes te encuentren' : pending === 1 ? '1 solicitud esperando respuesta' : `${pending} solicitudes esperando respuesta`,
      hintMuted: pending === 0,
    },
    {
      label: 'Reservas activas',
      value: active,
      bg: 'var(--color-accent-light)',
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>',
      hint: active === 0 ? 'Tu perfil acaba de salir al aire' : `${active} ${active === 1 ? 'evento confirmado' : 'eventos confirmados'}`,
      hintMuted: active === 0,
    },
    {
      label: 'Eventos completados',
      value: completed,
      bg: 'var(--color-success-light)',
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>',
      hint: completed === 0 ? 'Aplica al Founding DJ Program' : completed < 10 ? `${10 - completed} más para subir a plan Pro` : '¡Listo para plan Pro!',
      hintMuted: completed === 0,
    },
    {
      label: reviewsCount === 0 ? 'Rating · sin reseñas aún' : 'Rating promedio',
      value: rating > 0 ? rating.toFixed(1) + ' ★' : '—',
      bg: 'var(--color-warning-light)',
      icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
      hint: reviewsCount === 0 ? 'Tu primer cliente la genera' : `${reviewsCount} ${reviewsCount === 1 ? 'reseña' : 'reseñas'} verificadas`,
      hintMuted: reviewsCount === 0,
    },
  ]
})

// Calendar
const calendarDays = computed(() => {
  const firstDay = new Date(calYear.value, calMonth.value, 1)
  const lastDay = new Date(calYear.value, calMonth.value + 1, 0)
  let startWeekday = firstDay.getDay() || 7 // Monday = 1
  const days = []
  const prevMonth = new Date(calYear.value, calMonth.value, 0)
  for (let i = startWeekday - 1; i > 0; i--) {
    days.push({ day: prevMonth.getDate() - i + 1, current: false, status: null, isToday: false, dateStr: '' })
  }
  const today = new Date()
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${calYear.value}-${String(calMonth.value + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`
    const avail = availability.value.find(a => a.date === dateStr)
    const isToday = today.getFullYear() === calYear.value && today.getMonth() === calMonth.value && today.getDate() === d
    days.push({ day: d, current: true, status: avail?.status || null, isToday, dateStr })
  }
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    days.push({ day: i, current: false, status: null, isToday: false, dateStr: '' })
  }
  return days
})

function changeMonth(delta) {
  calMonth.value += delta
  if (calMonth.value > 11) { calMonth.value = 0; calYear.value++ }
  if (calMonth.value < 0) { calMonth.value = 11; calYear.value-- }
  fetchAvailability()
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-VE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function statusBadge(status) {
  const map = { solicitud_enviada: '', pendiente_respuesta: 'badge-warning', aceptada: 'badge-success', pendiente_pago: 'badge-warning', confirmada: 'badge-success', completada: 'badge-cyan', rechazada: 'badge-error', cancelada: 'badge-error' }
  return map[status] || ''
}

// Actions
async function handleRequest(bookingId, newStatus) {
  actionLoading.value = true
  try {
    const payload = { status: newStatus }
    if (adjustingId.value === bookingId && adjustPrice.value) {
      payload.quoted_price = adjustPrice.value
      payload.talent_notes = adjustNotes.value
    }
    await api.patch(`/bookings/${bookingId}/status/`, payload)
    await fetchBookings()
    adjustingId.value = null
    adjustPrice.value = null
    adjustNotes.value = ''
  } catch (e) {
    alert(e.response?.data?.error || 'Error al procesar la solicitud')
  }
  actionLoading.value = false
}

function toggleAdjust(booking) {
  if (adjustingId.value === booking.id) {
    handleRequest(booking.id, 'aceptada')
  } else {
    adjustingId.value = booking.id
    adjustPrice.value = parseFloat(booking.precio_estimado) || null
    adjustNotes.value = ''
  }
}

async function toggleAvailability(day) {
  if (!day.dateStr || !profile.value) return
  try {
    if (day.status === 'blocked') {
      await api.delete('/availability/manage/', { data: { date: day.dateStr } })
    } else if (!day.status || day.status === 'available') {
      await api.post('/availability/manage/', { date: day.dateStr, status: 'blocked' })
    }
    await fetchAvailability()
  } catch { /* silent */ }
}

async function saveProfile() {
  // Auto-flush: si hay texto pendiente en los inputs de chips, agrégalo antes de enviar
  if (newMoodTag.value && newMoodTag.value.trim()) addMoodTag()
  if (newLanguage.value && newLanguage.value.trim()) addLanguage()
  if (newZone.value && newZone.value.trim()) addZone()
  if (newEquipBring.value && newEquipBring.value.trim()) addEquipBring()
  if (newEquipNo.value && newEquipNo.value.trim()) addEquipNo()

  saving.value = true
  saveSuccess.value = false
  try {
    if (!profile.value) {
      const { data } = await api.post('/talents/create/', profileForm)
      profile.value = data
    } else {
      await api.patch('/talents/me/', profileForm)
    }
    saveSuccess.value = true
    setTimeout(() => saveSuccess.value = false, 3000)
  } catch (e) {
    alert('Error al guardar: ' + extractErrorMessage(e))
  }
  saving.value = false
}

function extractErrorMessage(err) {
  const data = err?.response?.data
  if (!data) return 'No se pudo conectar con el servidor.'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  if (data.error) return data.error
  // DRF field errors: { field: ['msg1', 'msg2'], ... }
  if (typeof data === 'object') {
    const parts = []
    for (const [field, msgs] of Object.entries(data)) {
      if (Array.isArray(msgs)) {
        parts.push(`${field}: ${msgs.join(' ')}`)
      } else if (typeof msgs === 'string') {
        parts.push(`${field}: ${msgs}`)
      }
    }
    if (parts.length) return parts.join(' | ')
  }
  return 'Intenta de nuevo.'
}

async function fetchBookings() {
  try {
    const { data } = await api.get('/bookings/')
    bookings.value = data.results || data
  } catch { /* silent */ }
}

async function fetchProfile() {
  try {
    const { data } = await api.get('/talents/me/')
    profile.value = data
    Object.keys(profileForm).forEach(k => {
      if (data[k] !== undefined && data[k] !== null) profileForm[k] = data[k]
    })
    // JSONField list fields pueden venir null en DB antigua → forzar array
    ;['mood_tags', 'event_types', 'languages', 'equipment_brings', 'equipment_not_included', 'service_zones'].forEach(k => {
      if (!Array.isArray(profileForm[k])) profileForm[k] = []
    })
  } catch { /* silent */ }
}

async function fetchAvailability() {
  if (!profile.value) return
  try {
    const { data } = await api.get(`/talents/${profile.value.id}/availability/`)
    availability.value = data.results || data
  } catch { /* silent */ }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchBookings(), fetchProfile()])
  await Promise.all([
    fetchAvailability(), fetchMedia(), fetchPacks(), fetchFaqs(),
    fetchPremiumInvitation(), fetchTierLimits(), fetchPayout(),
  ])
  loading.value = false
})
</script>

<style scoped>
.talent-dash { min-height: 100vh; padding-bottom: var(--space-16); }
.dash-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: var(--space-8); flex-wrap: wrap; gap: var(--space-4); }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-8); }
.stat-hint {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(193, 216, 47, 0.08);
  color: var(--color-primary);
  font-size: 0.68rem;
  line-height: 1.3;
  align-self: flex-start;
}
.stat-hint-muted {
  background: rgba(140, 140, 140, 0.08);
  color: var(--color-text-muted);
}
.stat-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-xl); transition: all var(--transition-base); }
.stat-card:hover { border-color: var(--color-border-hover); transform: translateY(-2px); }
.stat-icon { width: 48px; height: 48px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-family: var(--font-heading); font-size: var(--font-size-2xl); display: block; }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-muted); }

/* Tabs */
.dash-tabs { display: flex; gap: var(--space-1); background: var(--color-bg-card); border-radius: var(--radius-xl); padding: var(--space-1); margin-bottom: var(--space-6); overflow-x: auto; border: 1px solid var(--color-border); }
.tab-btn { display: inline-flex; align-items: center; gap: var(--space-2); padding: var(--space-3) var(--space-5); border-radius: var(--radius-lg); font-size: var(--font-size-sm); font-weight: 500; color: var(--color-text-muted); background: transparent; border: none; cursor: pointer; transition: all var(--transition-fast); white-space: nowrap; }
.tab-btn:hover { color: var(--color-text-primary); background: rgba(255,255,255,0.03); }
.tab-btn.active { background: var(--gradient-primary); color: #000; font-weight: 600; }
.tab-badge { background: var(--color-accent); color: white; font-size: 10px; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

/* Empty State */
.empty-state { text-align: center; padding: var(--space-16) var(--space-4); color: var(--color-text-muted); }

/* Profile status grid (Mi Perfil overview, FIX #1) */
.profile-status-header { margin-bottom: var(--space-4); }
.profile-status-title {
  font-size: 1.1rem;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}
.profile-status-sub {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0;
}
.profile-status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.profile-status-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 12px 14px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}
.profile-status-card.locked {
  border-color: rgba(193, 216, 47, 0.3);
}
.psc-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  font-weight: 800;
}
.psc-icon-done { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.psc-icon-pending { background: rgba(251, 146, 60, 0.15); color: #fb923c; }
.psc-icon-locked { background: rgba(193, 216, 47, 0.15); color: #C1D82F; }
.psc-info { flex: 1; min-width: 0; }
.psc-title {
  color: var(--color-text-primary);
  font-size: 0.85rem;
  font-weight: 600;
}
.psc-desc {
  color: var(--color-text-muted);
  font-size: 0.72rem;
  margin-top: 2px;
}
.psc-desc-cyan { color: #C1D82F; }
.psc-action {
  flex-shrink: 0;
  color: #C1D82F;
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
}
.psc-action:hover { color: var(--color-primary); }
@media (max-width: 640px) {
  .profile-status-grid { grid-template-columns: 1fr; }
}

/* Profile tip (final de Mi Perfil) */
.profile-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  margin-bottom: var(--space-5);
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: var(--radius-md);
  font-size: 0.82rem;
  color: var(--color-text-secondary);
}
.profile-tip-emoji { font-size: 1.1rem; }
.profile-tip strong { color: var(--color-text-primary); }
.profile-tip-highlight { color: var(--color-primary) !important; }

/* Inline lock badge (junto a títulos de sección bloqueada) */
.inline-lock-badge {
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(193, 216, 47, 0.15);
  color: #C1D82F;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.4px;
  vertical-align: middle;
}

/* Video locked card (FIX #1) */
.video-locked-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--color-bg-primary);
  border: 1px solid rgba(193, 216, 47, 0.3);
  border-radius: var(--radius-lg);
}
.vlc-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(193, 216, 47, 0.15);
  color: #C1D82F;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
}
.vlc-content { flex: 1; min-width: 0; }
.vlc-content strong {
  display: block;
  color: var(--color-text-primary);
  font-size: 0.95rem;
  margin-bottom: 2px;
}
.vlc-content p {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.45;
}
@media (max-width: 640px) {
  .video-locked-card { flex-direction: column; align-items: flex-start; text-align: left; }
}

/* Tab hint (count o porcentaje pequeño) */
.tab-hint {
  margin-left: 4px;
  font-size: 0.62rem;
  color: var(--color-text-dim, #555);
  font-weight: 500;
}
.tab-btn.active .tab-hint {
  color: rgba(193, 216, 47, 0.7);
}

/* Tab locked (FIX #5) — badge "PRO 🔒" en la tab */
.tab-btn.tab-locked { opacity: 0.85; }
.tab-lock-badge {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(193, 216, 47, 0.15);
  color: #C1D82F;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.4px;
}

/* Locked preview content (cuando se hace click en una tab gated) */
.locked-preview {
  text-align: center;
  padding: var(--space-8) var(--space-4);
  background: var(--color-bg-primary);
  border: 2px dashed rgba(193, 216, 47, 0.4);
  border-radius: var(--radius-xl);
}
.locked-icon {
  font-size: 2.4rem;
  color: #C1D82F;
  margin-bottom: var(--space-3);
}
.locked-preview h3 {
  color: var(--color-text-primary);
  font-size: 1.2rem;
  margin-bottom: var(--space-2);
}
.locked-desc {
  color: var(--color-text-muted);
  font-size: 0.88rem;
  max-width: 440px;
  margin: 0 auto var(--space-4);
  line-height: 1.5;
}
.locked-requirements {
  display: inline-block;
  padding: 14px 18px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  text-align: left;
  max-width: 440px;
}
.locked-req-title {
  color: #C1D82F;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
}
.locked-req-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}
.locked-req-list strong { color: var(--color-text-primary); }

/* Partner role hint en Mis Tarifas (FIX #2) */
.partner-hint {
  margin-bottom: var(--space-4);
  padding: 14px 16px;
  background: rgba(193, 216, 47, 0.05);
  border: 1px solid rgba(193, 216, 47, 0.25);
  border-radius: var(--radius-lg);
  font-size: 0.82rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.partner-hint-title {
  color: #C1D82F;
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 4px;
}
.partner-hint p {
  margin: 0 0 6px;
  color: var(--color-text-muted);
}
.partner-hint p:last-child { margin-bottom: 0; }
.partner-link {
  color: #C1D82F;
  font-weight: 600;
  text-decoration: none;
}
.partner-link:hover { color: var(--color-primary); }

/* Empty state rich (FIX #3) */
.empty-state-rich {
  text-align: center;
  padding: var(--space-8) var(--space-4);
}
.empty-celebration-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.2rem;
}
.empty-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.empty-desc {
  color: var(--color-text-muted);
  font-size: 0.92rem;
  max-width: 480px;
  margin: 0 auto var(--space-5);
  line-height: 1.6;
}
.empty-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
}

/* Checklist de primeros pasos */
.first-steps {
  max-width: 500px;
  margin: 0 auto;
  padding: var(--space-5);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: left;
}
.first-steps h4 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  color: var(--color-text-primary);
  margin-bottom: var(--space-3);
  font-weight: 600;
}
.first-steps-count {
  background: var(--color-primary);
  color: #0a0a0a;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}
.step-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px 0;
  border-bottom: 1px dashed var(--color-border);
  font-size: 0.88rem;
}
.step-item:last-child { border-bottom: none; }
.step-check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  font-weight: 700;
  flex-shrink: 0;
  border: 2px solid var(--color-border);
}
.step-check-done {
  background: #10b981;
  color: #0a0a0a;
  border-color: #10b981;
}
.step-check-todo { color: var(--color-text-muted); }
.step-text {
  flex: 1;
  color: var(--color-text-primary);
}
.step-note {
  color: var(--color-text-muted);
  font-size: 0.78rem;
  margin-left: 4px;
}
.step-item.done .step-text {
  color: var(--color-text-muted);
  text-decoration: line-through;
}
.step-action {
  background: transparent;
  border: none;
  color: #C1D82F;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  padding: 4px 8px;
  flex-shrink: 0;
}
.step-action:hover { color: var(--color-primary); }

.empty-tip {
  margin-top: var(--space-5);
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
.empty-tip strong { color: var(--color-primary); }
.empty-state svg { margin: 0 auto var(--space-4); opacity: 0.4; }

/* Request Cards */
.request-list { display: flex; flex-direction: column; gap: var(--space-4); }
.request-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.request-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); flex-wrap: wrap; gap: var(--space-3); }
.request-client { display: flex; align-items: center; gap: var(--space-3); }
.client-avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--gradient-cta); display: flex; align-items: center; justify-content: center; font-weight: 700; color: white; }
.request-date { font-size: var(--font-size-sm); color: var(--color-primary); font-weight: 600; }
.request-details { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-3); }
.detail-chip { display: inline-flex; align-items: center; gap: var(--space-1); padding: var(--space-1) var(--space-3); background: rgba(255,255,255,0.04); border-radius: var(--radius-full); font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.detail-chip.price { color: var(--color-primary); background: var(--color-primary-ultra-light); font-weight: 600; }
.request-desc { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-4); font-style: italic; border-left: 2px solid var(--color-border); padding-left: var(--space-3); }
.request-actions { display: flex; gap: var(--space-3); flex-wrap: wrap; }
.reject-btn { color: var(--color-accent) !important; }
.reject-btn:hover { background: var(--color-accent-light) !important; }

/* Adjust Section */
.adjust-section { padding: var(--space-4); background: rgba(193,216,47,0.05); border: 1px solid var(--color-border); border-radius: var(--radius-lg); margin-bottom: var(--space-4); }
.adjust-row { margin-bottom: var(--space-3); }

/* Bookings Table */
.bookings-table { border: 1px solid var(--color-border); border-radius: var(--radius-xl); overflow: hidden; }
.table-header { display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 1fr 1.5fr 40px; padding: var(--space-3) var(--space-5); font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--color-border); }
.table-row { display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 1fr 1.5fr 40px; padding: var(--space-4) var(--space-5); align-items: center; font-size: var(--font-size-sm); border-bottom: 1px solid rgba(255,255,255,0.03); cursor: pointer; transition: background var(--transition-fast); }
.table-row:hover { background: var(--color-bg-card-hover); }
.cell-client { font-weight: 600; }
.cell-price { color: var(--color-primary); font-weight: 600; }
.cell-arrow { color: var(--color-text-muted); font-size: var(--font-size-lg); }

/* Earnings */
.earnings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--space-4); }
.earnings-card { padding: var(--space-8); border-radius: var(--radius-xl); text-align: center; }
.earnings-card h3 { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-3); font-family: var(--font-family); }
.earnings-amount { font-family: var(--font-heading); font-size: var(--font-size-4xl); margin-bottom: var(--space-2); }
.earnings-sub { font-size: var(--font-size-xs); color: var(--color-text-muted); }

/* Calendar */
.calendar-container { padding: var(--space-6); border-radius: var(--radius-xl); }
.calendar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.calendar-header h3 { font-family: var(--font-heading); font-size: var(--font-size-xl); }
.calendar-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); text-align: center; font-size: var(--font-size-xs); color: var(--color-text-muted); font-weight: 600; margin-bottom: var(--space-2); }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; }
.cal-day { aspect-ratio: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: var(--radius-md); font-size: var(--font-size-sm); cursor: pointer; transition: all var(--transition-fast); border: 1px solid transparent; position: relative; }
.cal-day:hover { background: rgba(255,255,255,0.05); }
.cal-day.other-month { opacity: 0.2; pointer-events: none; }
.cal-day.today { border-color: var(--color-primary); }
.cal-day.booked { background: var(--color-accent-light); border-color: var(--color-accent); }
.cal-day.blocked { background: rgba(255,255,255,0.05); border-color: var(--color-text-muted); }
.cal-day.available { background: var(--color-primary-ultra-light); }
.day-num { font-weight: 500; }
.day-tag { font-size: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.calendar-legend { display: flex; gap: var(--space-6); justify-content: center; margin-top: var(--space-4); }
.legend-item { display: flex; align-items: center; gap: var(--space-2); font-size: var(--font-size-xs); color: var(--color-text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }

/* Profile Form */
.profile-form { max-width: 800px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin-bottom: var(--space-6); }
.form-group.full { grid-column: 1 / -1; }
.form-actions { display: flex; align-items: center; gap: var(--space-4); }
.save-msg { color: var(--color-success); font-size: var(--font-size-sm); font-weight: 500; }

/* Cover Photo Upload */
.cover-upload-section { margin-bottom: var(--space-6); }
.cover-upload-area {
  width: 100%; aspect-ratio: 3/1; border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl); cursor: pointer; overflow: hidden;
  transition: all var(--transition-base); position: relative;
  display: flex; align-items: center; justify-content: center;
}
.cover-upload-area:hover { border-color: var(--color-primary); background: rgba(193,216,47,0.03); }
.cover-preview { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { text-align: center; color: var(--color-text-muted); padding: var(--space-4); }
.cover-placeholder p { margin: var(--space-2) 0; font-size: var(--font-size-sm); }
.cover-placeholder .text-muted { font-size: var(--font-size-xs); opacity: 0.6; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .table-header { display: none; }
  .table-row { grid-template-columns: 1fr 1fr; gap: var(--space-2); }
  .form-grid { grid-template-columns: 1fr; }
  .dash-tabs { gap: 0; }
  .tab-btn { padding: var(--space-2) var(--space-3); font-size: var(--font-size-xs); }
  .photos-grid { grid-template-columns: 1fr 1fr; }
  .gallery-header { flex-direction: column; align-items: flex-start; }
}

/* Gallery tab */
.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
  flex-wrap: wrap;
}
.gallery-h3 { font-size: var(--font-size-xl); margin-bottom: var(--space-1); }
.gallery-sub { color: var(--color-text-muted); font-size: var(--font-size-sm); max-width: 520px; }

.gallery-dropzone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8) var(--space-4);
  text-align: center;
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
  transition: all var(--transition-base);
}
.gallery-dropzone svg { opacity: 0.5; margin-bottom: var(--space-2); }
.gallery-dropzone p { font-size: var(--font-size-sm); margin-bottom: var(--space-1); }
.dropzone-hint { font-size: var(--font-size-xs); opacity: 0.6; }
.gallery-dropzone.dragging {
  border-color: var(--color-primary);
  background: rgba(193,216,47,0.05);
  color: var(--color-primary);
}

.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-4);
}
.photo-tile {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
}
.photo-tile img { width: 100%; height: 100%; object-fit: cover; display: block; }
.photo-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-2);
  background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 30%, transparent 60%, rgba(0,0,0,0.75) 100%);
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.photo-tile:hover .photo-overlay { opacity: 1; }
.photo-delete {
  align-self: flex-end;
  width: 32px; height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(232,93,74,0.9);
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: transform var(--transition-fast);
}
.photo-delete:hover { transform: scale(1.1); background: rgb(232,93,74); }
.photo-caption-input {
  width: 100%;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 0.78rem;
  outline: none;
}
.photo-caption-input::placeholder { color: rgba(255,255,255,0.5); }
.photo-caption-input:focus { border-color: var(--color-primary); }

/* Payout summary + ladder */
.payout-summary {
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-6);
}
.payout-tier {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}
.payout-tier-label {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}
.tier-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 700;
}
.tier-badge.tier-standard { background: var(--color-bg-card); color: var(--color-text-muted); border: 1px solid var(--color-border); }
.tier-badge.tier-pro { background: rgba(193, 216, 47, 0.15); color: #C1D82F; border: 1px solid rgba(193, 216, 47, 0.4); }
.tier-badge.tier-premium { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.5); }
.payout-commission {
  margin-left: auto;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}
.payout-ladder {
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
}
.ladder-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 6px;
}
.ladder-row strong { color: var(--color-text-primary); }
.ladder-bar {
  height: 8px;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}
.ladder-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.4s ease;
}
.ladder-note {
  margin-top: var(--space-3);
  margin-bottom: 0;
  padding: 8px 12px;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  background: rgba(193,216,47,0.05);
  border-radius: var(--radius-md);
}
.ladder-note.premium-note {
  background: rgba(245,158,11,0.06);
  border-left: 3px solid #f59e0b;
}

.payout-items { margin-top: var(--space-6); }
.payout-items h4 { font-size: 1rem; margin-bottom: var(--space-3); }
.payout-table {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.payout-header, .payout-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr 1fr;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  font-size: 0.82rem;
  align-items: center;
}
.payout-header {
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.payout-row { border-top: 1px solid var(--color-border); }
.payout-code {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: var(--color-primary);
}
.payout-comm { color: #E85D4A; }
.payout-row strong { color: var(--color-text-primary); font-family: 'Poppins', sans-serif; }

@media (max-width: 768px) {
  .payout-header { display: none; }
  .payout-row { grid-template-columns: 1fr 1fr; }
}

/* Welcome banner (DJs nuevos) */
.welcome-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 12px 16px;
  margin-bottom: var(--space-4);
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-lg);
  font-size: 0.88rem;
  color: var(--color-text-secondary);
}
.welcome-banner-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #10b981;
  color: #000;
  font-weight: 800;
  font-size: 0.8rem;
  flex-shrink: 0;
}
.welcome-banner strong { color: var(--color-text-primary); margin-right: 4px; }
.welcome-dismiss {
  margin-left: auto;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
}
.welcome-dismiss:hover { background: rgba(255,255,255,0.05); color: var(--color-text-primary); }

/* "Tu Plan" progress card (FIX #4) */
.plan-progress-card {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--space-5);
  align-items: center;
  padding: var(--space-5) var(--space-6);
  margin-bottom: var(--space-5);
  background: linear-gradient(135deg, rgba(193,216,47,0.08), rgba(193,216,47,0.02));
  border: 1px solid rgba(193,216,47,0.3);
  border-radius: var(--radius-xl);
}
.plan-pp-badge-block { text-align: center; padding: 4px 8px; }
.plan-pp-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto var(--space-2);
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
}
.plan-pp-icon.plan-icon-pro { border-color: #C1D82F; color: #C1D82F; }
.plan-pp-icon.plan-icon-premium { border-color: #f59e0b; color: #f59e0b; }
.plan-pp-name {
  color: var(--color-text-primary);
  font-weight: 800;
  font-size: 0.72rem;
  letter-spacing: 2px;
}
.plan-pp-comm {
  color: var(--color-text-muted);
  font-size: 0.66rem;
  margin-top: 2px;
}

.plan-pp-body { min-width: 0; }
.plan-pp-headline {
  color: var(--color-text-primary);
  font-weight: 700;
  font-size: 0.95rem;
  margin-bottom: 4px;
}
.plan-pp-next { color: #C1D82F; }
.plan-pp-sub {
  color: var(--color-text-muted);
  font-size: 0.78rem;
  line-height: 1.45;
  margin-bottom: var(--space-3);
}
.plan-pp-bar {
  height: 8px;
  background: rgba(0,0,0,0.4);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: var(--space-3);
}
.plan-pp-bar-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.4s ease;
}
.plan-pp-criteria {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3) var(--space-4);
  font-size: 0.72rem;
  color: var(--color-text-muted);
}
.plan-pp-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.plan-pp-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  font-weight: 800;
}
.plan-pp-check.check-done { color: #10b981; }
.plan-pp-check.check-pending { color: var(--color-text-dim, #555); }

.plan-pp-cta { flex-shrink: 0; }
.plan-pp-link {
  color: #C1D82F;
  font-size: 0.78rem;
  text-decoration: none;
  white-space: nowrap;
  font-weight: 500;
}
.plan-pp-link:hover { color: var(--color-primary); }

@media (max-width: 768px) {
  .plan-progress-card { grid-template-columns: 1fr; gap: var(--space-3); text-align: center; }
  .plan-pp-criteria { justify-content: center; }
}

/* Premium invitation banner */
.premium-invite-banner {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  margin-bottom: var(--space-6);
  background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(245,158,11,0.04));
  border: 1px solid rgba(245,158,11,0.45);
  border-radius: var(--radius-xl);
  box-shadow: 0 8px 24px rgba(245,158,11,0.1);
}
.premium-invite-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(245,158,11,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.premium-invite-text { flex: 1; min-width: 0; }
.premium-invite-text strong {
  display: block;
  color: #f59e0b;
  font-size: 1rem;
  margin-bottom: 2px;
}
.premium-invite-text p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}
.premium-invite-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .premium-invite-banner { flex-direction: column; align-items: flex-start; }
}

/* Plan upsell modal — aparece solo cuando el DJ intenta algo bloqueado */
.plan-upsell-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}
.plan-upsell-modal {
  position: relative;
  width: 100%;
  max-width: 440px;
  padding: var(--space-6);
  text-align: center;
  background: var(--color-bg-card);
  border: 1px solid rgba(193, 216, 47, 0.4);
  border-radius: var(--radius-2xl);
  box-shadow: 0 24px 60px rgba(193, 216, 47, 0.18);
}
.plan-upsell-modal.plan-upsell-premium {
  border-color: rgba(245, 158, 11, 0.5);
  box-shadow: 0 24px 60px rgba(245, 158, 11, 0.2);
}
.plan-upsell-close {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.plan-upsell-close:hover {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}
.plan-upsell-icon-big {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--space-4);
  border-radius: 50%;
  background: rgba(193, 216, 47, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #C1D82F;
}
.plan-upsell-premium .plan-upsell-icon-big {
  background: rgba(245, 158, 11, 0.18);
  color: #f59e0b;
}
.plan-upsell-modal h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.plan-upsell-modal p {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  margin-bottom: var(--space-5);
}
.plan-upsell-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: center;
  flex-wrap: wrap;
}
.plan-upsell-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: var(--radius-lg);
  background: #C1D82F;
  color: #0a0a0a;
  font-size: 0.85rem;
  font-weight: 700;
  text-decoration: none;
  transition: all var(--transition-fast);
}
.plan-upsell-cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(193, 216, 47, 0.35);
}
.plan-upsell-premium .plan-upsell-cta {
  background: #f59e0b;
}
.plan-upsell-premium .plan-upsell-cta:hover {
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.35);
}

/* Mixes management */
.mix-add-row {
  display: grid;
  grid-template-columns: 1fr 1.5fr auto;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.mix-list-dash {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.mix-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast);
}
.mix-row:hover { border-color: var(--color-border-hover); }
.mix-row-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.mix-row-info { flex: 1; min-width: 0; }
.mix-row-info strong {
  display: block;
  font-size: 0.9rem;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}
.mix-row-url {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mix-row-url:hover { color: var(--color-primary); }
.mix-row-del {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.mix-row-del:hover { background: rgba(232,93,74,0.1); color: #E85D4A; }

.mix-row-feature {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.mix-row-feature:hover { background: rgba(245,158,11,0.1); }
.mix-row-feature.active { background: rgba(245,158,11,0.15); }
.mix-featured-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(245,158,11,0.15);
  color: #f59e0b;
  font-size: 0.65rem;
  font-weight: 700;
}

/* Mood tags input */
.mood-input-wrap { display: flex; flex-direction: column; gap: var(--space-2); }
.mood-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.mood-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px 5px 12px;
  background: rgba(236, 72, 153, 0.1);
  color: #ec4899;
  border: 1px solid rgba(236, 72, 153, 0.3);
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 500;
}
.mood-tag-x {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(236, 72, 153, 0.2);
  color: #ec4899;
  border: none;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.mood-tag-x:hover { background: #ec4899; color: #fff; }

/* Event type tiles */
.event-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-2);
}
.event-type-tile {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.event-type-tile:hover { border-color: var(--color-border-hover); }
.event-type-tile.selected {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}
.event-tile-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}
.event-type-tile:hover .event-tile-icon { color: var(--color-text-primary); }
.event-type-tile.selected .event-tile-icon { color: #f59e0b; }

/* Language + equipment chips */
.lang-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px 5px 12px;
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 0.8rem;
}
.equip-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px 5px 12px;
  border-radius: 999px;
  font-size: 0.8rem;
}
.equip-chip-yes {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.equip-chip-no {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Pack/FAQ editor */
.pack-editor {
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  margin-bottom: var(--space-6);
  border: 1px solid var(--color-primary);
}
.pack-editor-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: var(--space-4);
  color: var(--color-text-primary);
}

/* Pack dashboard grid */
.packs-dash-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-4);
}
.pack-dash-card {
  position: relative;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.pack-dash-card.featured {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(193,216,47,0.1);
}
.pack-dash-card strong {
  font-size: 0.95rem;
  color: var(--color-text-primary);
}
.pack-dash-price {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--color-primary);
}
.pack-dash-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: auto;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

/* FAQ dashboard list */
.faq-dash-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.faq-dash-item {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}
.faq-dash-q {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}
.faq-dash-a {
  font-size: 0.88rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  margin-bottom: var(--space-3);
}
.faq-dash-actions {
  display: flex;
  gap: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .mix-add-row { grid-template-columns: 1fr; }
}

/* ═══════════════════════════════════════
   Profile Preview Modal
   ═══════════════════════════════════════ */
.preview-backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  padding: var(--space-6);
}
.preview-modal {
  position: relative;
  width: 100%; max-width: 600px; max-height: 90vh;
  background: var(--color-bg-primary);
  border-radius: var(--radius-2xl);
  overflow-y: auto; overflow-x: hidden;
  border: none;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5);
}
.preview-close {
  position: absolute; top: var(--space-3); right: var(--space-3);
  z-index: 10; background: rgba(0,0,0,0.5); border: none;
  color: white; width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all var(--transition-fast);
}
.preview-close:hover { background: rgba(0,0,0,0.8); transform: scale(1.1); }

/* Cover */
.preview-cover {
  position: relative; height: 180px; overflow: hidden;
}
.preview-cover img { width: 100%; height: 100%; object-fit: cover; }
.preview-cover-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, transparent 40%, var(--color-bg-primary));
}
.preview-label {
  position: absolute; top: var(--space-3); left: var(--space-4);
  background: rgba(0,0,0,0.6); color: rgba(255,255,255,0.9);
  font-size: 11px; font-weight: 600; letter-spacing: 0.03em;
  padding: var(--space-1) var(--space-3); border-radius: var(--radius-full);
  backdrop-filter: blur(6px);
}

/* Body */
.preview-body { padding: var(--space-6); padding-top: 0; margin-top: -40px; position: relative; }

.preview-avatar-section { display: flex; align-items: flex-end; gap: var(--space-4); margin-bottom: var(--space-5); }
.preview-avatar-wrap { position: relative; flex-shrink: 0; }
.preview-avatar {
  width: 80px; height: 80px; border-radius: 50%; object-fit: cover;
  border: 3px solid var(--color-bg-primary);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}
.preview-status-dot {
  position: absolute; bottom: 4px; right: 4px;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--color-success);
  border: 2px solid var(--color-bg-primary);
}
.preview-identity h2 {
  font-family: var(--font-heading); font-size: var(--font-size-xl);
  margin-bottom: var(--space-1);
}
.preview-badges { display: flex; gap: var(--space-2); }

/* Stats row */
.preview-stats {
  display: flex; flex-wrap: wrap; gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-xl); margin-bottom: var(--space-5);
}
.preview-stat {
  display: flex; align-items: center; gap: var(--space-2);
  font-size: var(--font-size-sm); color: var(--color-text-secondary);
}
.preview-stat strong { color: var(--color-primary); }
.preview-stat .muted { color: var(--color-text-muted); font-size: var(--font-size-xs); }

/* Sections */
.preview-section { margin-bottom: var(--space-5); }
.preview-section h4 {
  font-family: var(--font-heading); font-size: var(--font-size-sm);
  color: var(--color-text-muted); text-transform: uppercase;
  letter-spacing: 0.06em; margin-bottom: var(--space-2);
}
.preview-section p { font-size: var(--font-size-sm); line-height: 1.6; color: var(--color-text-secondary); }
.preview-genres { display: flex; flex-wrap: wrap; gap: var(--space-2); }

/* Social */
.preview-social {
  display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-6);
}
.social-chip {
  display: inline-flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-full); font-size: var(--font-size-xs);
  color: var(--color-text-secondary); text-decoration: none;
  transition: all var(--transition-fast);
}
.social-chip:hover { border-color: var(--color-primary); color: var(--color-primary); }

/* Footer */
.preview-footer {
  display: flex; gap: var(--space-3); justify-content: center;
  padding-top: var(--space-4); border-top: 1px solid var(--color-border);
}

/* Transition */
.modal-enter-active { transition: all 0.25s ease-out; }
.modal-leave-active { transition: all 0.2s ease-in; }
.modal-enter-from { opacity: 0; }
.modal-enter-from .preview-modal { transform: translateY(20px) scale(0.95); }
.modal-leave-to { opacity: 0; }
.modal-leave-to .preview-modal { transform: translateY(10px) scale(0.98); }

@media (max-width: 768px) {
  .preview-backdrop { padding: var(--space-3); }
  .preview-modal { max-height: 95vh; }
  .preview-cover { height: 140px; }
  .preview-avatar { width: 64px; height: 64px; }
  .preview-stats { flex-direction: column; }
}
</style>
