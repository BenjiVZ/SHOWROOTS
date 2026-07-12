<template>
  <div class="partner-dashboard">
    <div class="container">
      <!-- Header -->
      <div class="dashboard-header animate-fade-in-up">
        <div class="header-left">
          <div class="partner-badge">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
          </div>
          <div>
            <h1>Dashboard de Aliado</h1>
            <p class="subtitle">Gestión de reservas y comisiones</p>
          </div>
        </div>
        <router-link to="/search" class="btn btn-cta">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Nueva Reserva
        </router-link>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Cargando dashboard...</p>
      </div>

      <!-- Stats Cards -->
      <div v-else class="animate-fade-in-up" style="animation-delay: 0.1s;">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon bookings-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_bookings }}</span>
              <span class="stat-label">Reservas Totales</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon active-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.active_bookings }}</span>
              <span class="stat-label">Activas</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon completed-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.completed_bookings }}</span>
              <span class="stat-label">Completadas</span>
            </div>
          </div>

          <div class="stat-card highlight">
            <div class="stat-icon commission-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">${{ formatMoney(stats.total_commission_earned) }}</span>
              <span class="stat-label">Comisiones Ganadas</span>
            </div>
          </div>
        </div>

        <!-- Pending Commission Banner -->
        <div v-if="parseFloat(stats.pending_commission) > 0" class="pending-banner">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          Tienes <strong>${{ formatMoney(stats.pending_commission) }}</strong> en comisiones pendientes de pago
        </div>

        <!-- ── Solicitudes abiertas (Uber para DJs / packs) ── -->
        <div v-if="productionProfile?.status === 'verified'" class="section-header" style="margin-top: var(--space-6)">
          <h2>
            <svg class="h2-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
            Solicitudes abiertas
          </h2>
          <span v-if="openGigs.length" class="badge">{{ openGigs.length }}</span>
        </div>
        <div v-if="productionProfile?.status === 'verified'" class="og-panel">
          <p v-if="!openGigs.length" class="og-empty">
            No hay solicitudes abiertas que matcheen tus categorías ahora mismo. Te avisamos por email cuando llegue una.
          </p>
          <div v-else class="og-list">
            <router-link v-for="g in openGigs" :key="g.id"
              :to="{ name: 'open-gig-detail', params: { id: g.id } }"
              class="og-card">
              <div class="og-card-head">
                <strong>{{ g.event_name || g.event_type_display }}</strong>
                <span v-if="g.my_offer_id" class="og-mine-badge">Ya ofertaste</span>
              </div>
              <div class="og-chips">
                <span v-for="it in (g.requested_items_display || [])" :key="it.key"
                  class="og-chip" :class="'need-' + it.key">{{ it.label }}</span>
              </div>
              <div class="og-meta">
                <span><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg> {{ g.event_date }}</span>
                <span><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> {{ g.event_time_start }} · {{ g.event_duration_hours }}h</span>
                <span><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg> {{ g.event_city || 'Panamá' }}</span>
                <span v-if="g.budget"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg> USD {{ g.budget }}</span>
              </div>
              <div class="og-footer">
                <span class="og-offers">{{ g.offers_count }} oferta{{ g.offers_count === 1 ? '' : 's' }}</span>
                <span class="og-cta">{{ g.my_offer_id ? 'Ver' : 'Ofertar' }} ›</span>
              </div>
            </router-link>
          </div>
        </div>

        <!-- ── Packs de Producción ── -->
        <div class="section-header" style="margin-top: var(--space-8)">
          <h2>
            <svg class="h2-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
            Mis Packs de Producción
          </h2>
          <button v-if="productionProfile?.status === 'verified'" class="btn btn-primary btn-sm" @click="openPackEditor()">
            + Crear Pack
          </button>
        </div>

        <!-- No production profile -->
        <div v-if="!productionProfile" class="empty-state">
          <p>Aún no activaste el módulo de producción.</p>
          <router-link to="/account" class="btn btn-outline">Activar en mi cuenta</router-link>
        </div>
        <!-- Draft: continuar onboarding -->
        <div v-else-if="productionProfile.status === 'draft'" class="empty-state">
          <p>Tu onboarding de producción está en progreso.</p>
          <router-link to="/partner/onboarding" class="btn btn-outline">Continuar onboarding</router-link>
        </div>
        <!-- Pending: esperando verificación -->
        <div v-else-if="productionProfile.status === 'pending'" class="pack-status-banner pending">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          Tu perfil está en verificación. Cuando un admin lo apruebe vas a poder publicar packs.
        </div>
        <!-- Rejected: motivo -->
        <div v-else-if="productionProfile.status === 'rejected'" class="pack-status-banner rejected">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          Tu solicitud fue rechazada. <router-link to="/partner/onboarding" class="banner-link">Revisar y reenviar →</router-link>
        </div>
        <!-- Verified: lista de packs -->
        <div v-else-if="productionProfile.status === 'verified'">
          <div v-if="packs.length === 0" class="empty-state">
            <p>Aún no publicaste packs. Crea el primero — sonido, luces, DJ booth, etc.</p>
            <button class="btn btn-primary" @click="openPackEditor()">+ Crear mi primer pack</button>
          </div>
          <div v-else class="packs-list">
            <div v-for="p in packs" :key="p.id" class="pack-row">
              <div class="pack-thumb" v-html="categoryIcon(p.category)"></div>
              <div class="pack-info">
                <div class="pack-name">
                  {{ p.name }}
                  <span class="pack-tag" :class="'tag-' + p.status">{{ packStatusLabel(p.status) }}</span>
                  <span v-if="p.includes_dj" class="pack-tag tag-dj">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px;margin-right:2px"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                    Con DJ
                  </span>
                </div>
                <div class="pack-meta">
                  <span>{{ p.category_display }}</span>
                  <span>{{ p.event_size_display }}</span>
                  <span class="pack-price">${{ formatMoney(p.price) }}</span>
                  <span v-if="p.rentals_count">· {{ p.rentals_count }} rentas</span>
                </div>
              </div>
              <div class="pack-actions">
                <button class="icon-btn" @click="togglePackStatus(p)" :title="p.status === 'published' ? 'Pausar' : 'Publicar'">
                  <svg v-if="p.status === 'published'" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                </button>
                <button class="icon-btn" @click="openPackEditor(p)" title="Editar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <button class="icon-btn icon-btn-danger" @click="deletePack(p)" title="Eliminar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 01-2 2H9a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a2 2 0 012-2h2a2 2 0 012 2v2"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Pack Editor Modal con live preview ── -->
        <Teleport to="body">
          <div v-if="packEditor.open" class="pack-modal-backdrop" @click.self="closePackEditor">
            <div class="pack-modal pack-modal-wide">
              <h3>{{ packEditor.form.id ? 'Editar Pack' : 'Nuevo Pack' }}</h3>
              <div class="pack-modal-split">
                <!-- Form side -->
                <div class="form-grid">
                  <div class="form-group full">
                    <label class="label">Nombre</label>
                    <input v-model="packEditor.form.name" type="text" class="input-field" placeholder="Ej: Pack Sonido Pro" />
                  </div>
                  <div class="form-group">
                    <label class="label">Categoría</label>
                    <select v-model="packEditor.form.category" class="input-field">
                      <option v-for="c in availableCategories" :key="c.value" :value="c.value">
                        {{ c.label }}
                      </option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="label">Tamaño del evento</label>
                    <select v-model="packEditor.form.event_size" class="input-field">
                      <option value="small">Pequeño (&lt;80 pers)</option>
                      <option value="medium">Mediano (80-300)</option>
                      <option value="large">Grande (300+)</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="label">Precio (USD)</label>
                    <input v-model.number="packEditor.form.price" type="number" min="0" step="1" class="input-field" />
                  </div>
                  <div class="form-group">
                    <label class="label">Setup (horas antes)</label>
                    <input v-model.number="packEditor.form.setup_hours_before" type="number" min="0" max="12" class="input-field" />
                  </div>
                  <div class="form-group full">
                    <label class="label">Descripción corta</label>
                    <input v-model="packEditor.form.short_description" type="text" class="input-field" placeholder="Ej: Sonido profesional para eventos medianos a grandes" />
                  </div>
                  <div class="form-group full">
                    <label class="label">Foto de portada</label>
                    <div class="cover-row">
                      <div class="cover-preview-img" v-if="packEditor.coverPreview || packEditor.form.cover_image">
                        <img :src="packEditor.coverPreview || packEditor.form.cover_image" alt="Cover" />
                      </div>
                      <input ref="packCoverInput" type="file" accept="image/*" hidden @change="onCoverSelected" />
                      <button type="button" class="btn btn-outline btn-sm" @click="$refs.packCoverInput.click()">
                        {{ packEditor.coverPreview || packEditor.form.cover_image ? 'Cambiar foto' : 'Subir foto' }}
                      </button>
                    </div>
                  </div>
                  <div class="form-group full">
                    <label class="label">Equipo incluido</label>
                    <div v-if="packEditor.form.equipment_items.length" class="chip-list">
                      <span v-for="(item, idx) in packEditor.form.equipment_items" :key="idx" class="chip">
                        {{ item }}
                        <button type="button" class="chip-x" @click="removeEquip(idx)">×</button>
                      </span>
                    </div>
                    <div class="add-equip">
                      <input v-model="newEquipItem" type="text" class="input-field" placeholder="Ej: 2x QSC KW153" @keydown.enter.prevent="addEquip" />
                      <button type="button" class="btn btn-outline btn-sm" @click="addEquip">Agregar</button>
                    </div>
                  </div>
                  <div class="form-group">
                    <label class="checkbox-label">
                      <input v-model="packEditor.form.includes_technician" type="checkbox" />
                      Incluye técnico in-situ
                    </label>
                  </div>
                  <div class="form-group">
                    <label class="checkbox-label">
                      <input v-model="packEditor.form.includes_setup" type="checkbox" />
                      Incluye montaje/desmontaje
                    </label>
                  </div>

                  <!-- ¿Incluye DJ? -->
                  <div class="form-group full dj-toggle-block">
                    <label class="checkbox-label dj-toggle">
                      <input v-model="packEditor.form.includes_dj" type="checkbox" />
                      <span class="dj-toggle-text">
                        <strong>Incluye DJ en este pack</strong>
                        <small>Actívalo si el pack es turnkey — el cliente reserva esto y no necesita buscar un DJ aparte.</small>
                      </span>
                    </label>
                    <div v-if="packEditor.form.includes_dj" class="dj-name-wrap">
                      <label class="label">Nombre del DJ <span class="optional">(opcional)</span></label>
                      <input
                        v-model="packEditor.form.dj_name"
                        type="text"
                        class="input-field"
                        placeholder="Ej: DJ ShowRoots — o deja vacío si eres vos"
                      />
                    </div>
                  </div>
                </div>

                <!-- Preview side -->
                <aside class="preview-side">
                  <div class="preview-label">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-2px;margin-right:4px"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                    Vista previa · como lo verá el cliente
                  </div>
                  <div class="preview-card">
                    <div class="preview-hero">
                      <img v-if="packEditor.coverPreview || packEditor.form.cover_image" :src="packEditor.coverPreview || packEditor.form.cover_image" alt="" />
                      <span v-else class="preview-emoji" v-html="categoryIcon(packEditor.form.category)"></span>
                    </div>
                    <div class="preview-body">
                      <div class="preview-name">{{ packEditor.form.name || 'Sin nombre' }}</div>
                      <div class="preview-meta">
                        {{ packEditor.form.category ? CATEGORY_INFO[packEditor.form.category]?.label : '—' }}
                        · {{ eventSizeLabel(packEditor.form.event_size) }}
                      </div>
                      <div class="preview-price">${{ Number(packEditor.form.price || 0).toFixed(0) }}</div>
                      <p v-if="packEditor.form.short_description" class="preview-desc">{{ packEditor.form.short_description }}</p>
                      <ul v-if="packEditor.form.equipment_items.length" class="preview-items">
                        <li v-for="(item, idx) in packEditor.form.equipment_items.slice(0, 6)" :key="idx">{{ item }}</li>
                        <li v-if="packEditor.form.equipment_items.length > 6" class="preview-more">
                          +{{ packEditor.form.equipment_items.length - 6 }} más
                        </li>
                      </ul>
                      <div class="preview-flags">
                        <span v-if="packEditor.form.includes_dj" class="preview-flag preview-flag-dj">
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                          DJ incluido<span v-if="packEditor.form.dj_name">: {{ packEditor.form.dj_name }}</span>
                        </span>
                        <span v-if="packEditor.form.includes_technician" class="preview-flag">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                          Técnico incl.
                        </span>
                        <span v-if="packEditor.form.includes_setup" class="preview-flag">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
                          Setup incl.
                        </span>
                      </div>
                    </div>
                  </div>
                </aside>
              </div>

              <p v-if="packEditor.error" class="form-error">{{ packEditor.error }}</p>

              <div class="modal-actions">
                <button class="btn btn-ghost" @click="closePackEditor">Cancelar</button>
                <button class="btn btn-outline" :disabled="packEditor.saving" @click="savePack('draft')">
                  Guardar borrador
                </button>
                <button class="btn btn-primary" :disabled="packEditor.saving" @click="savePack('published')">
                  {{ packEditor.saving ? 'Guardando…' : 'Publicar' }}
                </button>
              </div>
            </div>
          </div>
        </Teleport>

        <!-- ── Bundles (Fase 10) ── -->
        <div v-if="productionProfile?.status === 'verified' && packs.length >= 2" class="section-header" style="margin-top: var(--space-8)">
          <h2>★ Mis Bundles (combos con descuento)</h2>
          <button class="btn btn-primary btn-sm" @click="openBundleEditor()">+ Crear Bundle</button>
        </div>
        <div v-if="productionProfile?.status === 'verified' && packs.length >= 2">
          <div v-if="!bundles.length" class="empty-state" style="padding:var(--space-4)">
            <p>Combiná 2+ packs con un descuento (ej: "Sonido + Luces -15%"). Convierten 2x mejor.</p>
          </div>
          <div v-else class="bundles-list">
            <div v-for="b in bundles" :key="b.id" class="bundle-row">
              <div class="bundle-thumb">★</div>
              <div class="bundle-info">
                <div class="bundle-row-name">
                  {{ b.name }}
                  <span class="pack-tag" :class="'tag-' + b.status">{{ packStatusLabel(b.status) }}</span>
                </div>
                <div class="bundle-row-meta">
                  <span>{{ b.packs.length }} packs · -{{ Number(b.discount_percentage).toFixed(0) }}%</span>
                  <span class="bundle-row-price">${{ Number(b.discounted_price).toFixed(0) }} <s>${{ Number(b.base_price).toFixed(0) }}</s></span>
                </div>
              </div>
              <div class="pack-actions">
                <button class="icon-btn" @click="toggleBundleStatus(b)" :title="b.status === 'published' ? 'Pausar' : 'Publicar'">
                  {{ b.status === 'published' ? '⏸' : '▶' }}
                </button>
                <button class="icon-btn" @click="openBundleEditor(b)" title="Editar">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
                </button>
                <button class="icon-btn icon-btn-danger" @click="deleteBundle(b)" title="Eliminar">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 01-2 2H9a2 2 0 01-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a2 2 0 012-2h2a2 2 0 012 2v2"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Bundle Editor Modal -->
        <Teleport to="body">
          <div v-if="bundleEditor.open" class="pack-modal-backdrop" @click.self="closeBundleEditor">
            <div class="pack-modal">
              <h3>{{ bundleEditor.form.id ? 'Editar Bundle' : 'Nuevo Bundle' }}</h3>
              <div class="form-grid">
                <div class="form-group full">
                  <label class="label">Nombre</label>
                  <input v-model="bundleEditor.form.name" type="text" class="input-field" placeholder="Ej: Bundle Boda Completa" />
                </div>
                <div class="form-group full">
                  <label class="label">Descripción (opcional)</label>
                  <input v-model="bundleEditor.form.description" type="text" class="input-field" placeholder="Ej: Sonido + Luces + Pantalla. Todo lo necesario para una boda." />
                </div>
                <div class="form-group">
                  <label class="label">% de descuento</label>
                  <input v-model.number="bundleEditor.form.discount_percentage" type="number" min="0" max="50" step="1" class="input-field" />
                </div>
                <div class="form-group full">
                  <label class="label">Packs incluidos (mín 2)</label>
                  <div class="bundle-pack-picker">
                    <label v-for="p in packs.filter(x => x.status === 'published')" :key="p.id" class="bundle-pack-checkbox">
                      <input
                        type="checkbox"
                        :value="p.id"
                        :checked="bundleEditor.form.pack_ids.includes(p.id)"
                        @change="toggleBundlePack(p.id)"
                      />
                      <span class="bundle-pack-row"><span class="bundle-pack-icon" v-html="categoryIcon(p.category)"></span> <strong>{{ p.name }}</strong> · ${{ Number(p.price).toFixed(0) }}</span>
                    </label>
                  </div>
                </div>
                <div v-if="bundleEditor.form.pack_ids.length >= 2" class="form-group full bundle-summary">
                  <div>Base: <strong>${{ bundleEditorBasePrice.toFixed(0) }}</strong></div>
                  <div>Final: <strong style="color:var(--color-primary)">${{ bundleEditorDiscountedPrice.toFixed(0) }}</strong>
                  <small style="color:var(--color-text-muted)">(ahorro ${{ (bundleEditorBasePrice - bundleEditorDiscountedPrice).toFixed(0) }})</small></div>
                </div>
              </div>

              <p v-if="bundleEditor.error" class="form-error">{{ bundleEditor.error }}</p>

              <div class="modal-actions">
                <button class="btn btn-ghost" @click="closeBundleEditor">Cancelar</button>
                <button class="btn btn-outline" :disabled="bundleEditor.saving" @click="saveBundle('draft')">Borrador</button>
                <button class="btn btn-primary" :disabled="bundleEditor.saving || bundleEditor.form.pack_ids.length < 2" @click="saveBundle('published')">
                  {{ bundleEditor.saving ? 'Guardando…' : 'Publicar' }}
                </button>
              </div>
            </div>
          </div>
        </Teleport>

        <!-- Recent Bookings -->
        <div class="section-header" style="margin-top: var(--space-8)">
          <h2>Reservas Recientes</h2>
          <router-link to="/dashboard" class="link-muted">Ver todas</router-link>
        </div>

        <div v-if="recentBookings.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.4">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/>
            <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          <p>Aun no tienes reservas.</p>
          <router-link to="/search" class="btn btn-outline">Buscar Talentos</router-link>
        </div>

        <div v-else class="bookings-list">
          <div v-for="booking in recentBookings" :key="booking.id" class="booking-card glass" @click="goToBooking(booking.id)">
            <div class="booking-left">
              <div class="booking-avatar">
                <img v-if="booking.talent_avatar" :src="booking.talent_avatar" alt="">
                <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
                </svg>
              </div>
              <div class="booking-info">
                <h3>{{ booking.talent_name }}</h3>
                <p>{{ booking.event_type_display }} &middot; {{ formatDate(booking.event_date) }}</p>
                <p class="booking-location">{{ booking.event_city || booking.event_location }}</p>
              </div>
            </div>
            <div class="booking-right">
              <span class="status-badge" :class="'status-' + booking.status">
                {{ booking.status_display }}
              </span>
              <span class="booking-price" v-if="booking.quoted_price || booking.precio_estimado">
                ${{ formatMoney(booking.quoted_price || booking.precio_estimado) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(true)
const stats = ref({
  total_bookings: 0,
  active_bookings: 0,
  completed_bookings: 0,
  total_commission_earned: '0.00',
  pending_commission: '0.00',
})
const recentBookings = ref([])

// ── Production state ──
const productionProfile = ref(null) // null | {status, categories, ...}
const packs = ref([])
const newEquipItem = ref('')
const openGigs = ref([])

async function fetchOpenGigs() {
  try {
    const { data } = await api.get('/open-gigs/available-for-partner/')
    openGigs.value = Array.isArray(data) ? data : (data.results || [])
  } catch { openGigs.value = [] }
}

const SVG_O = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
const ICON_PACK = `${SVG_O}<path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`

const CATEGORY_INFO = {
  sound:    { icon: `${SVG_O}<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>`, label: 'Sonido' },
  lights:   { icon: `${SVG_O}<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`, label: 'Iluminación' },
  screens:  { icon: `${SVG_O}<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`, label: 'Pantallas' },
  mics:     { icon: `${SVG_O}<path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>`, label: 'Microfonía' },
  dj_booth: { icon: `${SVG_O}<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>`, label: 'DJ Booth' },
  fx:       { icon: `${SVG_O}<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/><path d="M12 3v3"/><path d="M12 18v3"/><path d="M3 12h3"/><path d="M18 12h3"/></svg>`, label: 'FX' },
}

const availableCategories = computed(() => {
  const cats = productionProfile.value?.categories || []
  return cats.map(c => ({ value: c, ...CATEGORY_INFO[c] }))
})

function categoryIcon(c) { return CATEGORY_INFO[c]?.icon || ICON_PACK }
function packStatusLabel(s) {
  return { draft: 'Borrador', published: 'Publicado', paused: 'Pausado' }[s] || s
}
function eventSizeLabel(s) {
  return { small: 'Pequeño (<80)', medium: 'Mediano (80-300)', large: 'Grande (300+)' }[s] || s
}

const packEditor = reactive({
  open: false,
  saving: false,
  error: '',
  coverFile: null,
  coverPreview: null,
  form: blankPack(),
})

function blankPack() {
  return {
    id: null,
    name: '',
    category: '',
    short_description: '',
    event_size: 'medium',
    equipment_items: [],
    price: 0,
    setup_hours_before: 2,
    includes_technician: true,
    includes_setup: true,
    includes_dj: false,
    dj_name: '',
    cover_image: '',
  }
}

function onCoverSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    packEditor.error = 'La imagen no puede superar 5MB.'
    return
  }
  if (packEditor.coverPreview) URL.revokeObjectURL(packEditor.coverPreview)
  packEditor.coverFile = file
  packEditor.coverPreview = URL.createObjectURL(file)
  packEditor.error = ''
}

function openPackEditor(pack = null) {
  packEditor.error = ''
  packEditor.coverFile = null
  if (packEditor.coverPreview) {
    URL.revokeObjectURL(packEditor.coverPreview)
    packEditor.coverPreview = null
  }
  if (pack) {
    packEditor.form = {
      id: pack.id,
      name: pack.name,
      category: pack.category,
      short_description: pack.short_description || '',
      event_size: pack.event_size,
      equipment_items: [...(pack.equipment_items || [])],
      price: pack.price,
      setup_hours_before: pack.setup_hours_before,
      includes_technician: pack.includes_technician,
      includes_setup: pack.includes_setup,
      includes_dj: !!pack.includes_dj,
      dj_name: pack.dj_name || '',
      cover_image: pack.cover_image || '',
    }
  } else {
    packEditor.form = blankPack()
    if (availableCategories.value.length) {
      packEditor.form.category = availableCategories.value[0].value
    }
  }
  packEditor.open = true
}

function closePackEditor() {
  packEditor.open = false
  newEquipItem.value = ''
  if (packEditor.coverPreview) {
    URL.revokeObjectURL(packEditor.coverPreview)
    packEditor.coverPreview = null
  }
  packEditor.coverFile = null
}

function addEquip() {
  const v = newEquipItem.value.trim()
  if (!v) return
  packEditor.form.equipment_items.push(v)
  newEquipItem.value = ''
}
function removeEquip(idx) { packEditor.form.equipment_items.splice(idx, 1) }

async function savePack(status) {
  packEditor.saving = true
  packEditor.error = ''
  // Auto-flush input pendiente
  if (newEquipItem.value.trim()) addEquip()
  try {
    const id = packEditor.form.id

    // Si hay archivo de cover → multipart; si no → JSON normal
    let response
    if (packEditor.coverFile) {
      const fd = new FormData()
      fd.append('name', packEditor.form.name)
      fd.append('category', packEditor.form.category)
      fd.append('short_description', packEditor.form.short_description || '')
      fd.append('event_size', packEditor.form.event_size)
      fd.append('price', String(packEditor.form.price))
      fd.append('setup_hours_before', String(packEditor.form.setup_hours_before))
      fd.append('includes_technician', String(packEditor.form.includes_technician))
      fd.append('includes_setup', String(packEditor.form.includes_setup))
      fd.append('includes_dj', String(!!packEditor.form.includes_dj))
      if (packEditor.form.dj_name) fd.append('dj_name', packEditor.form.dj_name)
      fd.append('status', status)
      // JSONField vía FormData: mandar el array completo como string JSON.
      // Si mandamos múltiples `fd.append('equipment_items', 'X')`, DRF intenta parsear "X"
      // como JSON y falla con "El valor debe ser JSON válido".
      fd.append('equipment_items', JSON.stringify(packEditor.form.equipment_items || []))
      fd.append('cover_image', packEditor.coverFile)
      response = id
        ? await api.patch(`/partner/production/packs/${id}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
        : await api.post('/partner/production/packs/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    } else {
      const payload = { ...packEditor.form, status }
      delete payload.id
      delete payload.cover_image // no enviar si no cambió
      response = id
        ? await api.patch(`/partner/production/packs/${id}/`, payload)
        : await api.post('/partner/production/packs/', payload)
    }
    void response
    await fetchPacks()
    closePackEditor()
  } catch (e) {
    packEditor.error = e?.response?.data?.detail
      || Object.values(e?.response?.data || {}).flat().join(' ')
      || 'No se pudo guardar.'
  }
  packEditor.saving = false
}

async function togglePackStatus(pack) {
  const newStatus = pack.status === 'published' ? 'paused' : 'published'
  try {
    await api.patch(`/partner/production/packs/${pack.id}/`, { status: newStatus })
    await fetchPacks()
  } catch { /* silent */ }
}

async function deletePack(pack) {
  if (!confirm(`¿Eliminar "${pack.name}"?`)) return
  try {
    await api.delete(`/partner/production/packs/${pack.id}/`)
    await fetchPacks()
  } catch { /* silent */ }
}

async function fetchProductionProfile() {
  try {
    const { data } = await api.get('/partner/production/')
    productionProfile.value = data
  } catch {
    productionProfile.value = null
  }
}

async function fetchPacks() {
  try {
    const { data } = await api.get('/partner/production/packs/')
    packs.value = Array.isArray(data) ? data : []
  } catch {
    packs.value = []
  }
}

// ── Bundles ──
const bundles = ref([])
const bundleEditor = reactive({
  open: false,
  saving: false,
  error: '',
  form: blankBundle(),
})

function blankBundle() {
  return {
    id: null,
    name: '',
    description: '',
    discount_percentage: 15,
    pack_ids: [],
  }
}

const bundleEditorBasePrice = computed(() => {
  return bundleEditor.form.pack_ids.reduce((s, id) => {
    const p = packs.value.find(x => x.id === id)
    return s + (p ? parseFloat(p.price || 0) : 0)
  }, 0)
})
const bundleEditorDiscountedPrice = computed(() => {
  const factor = (100 - (bundleEditor.form.discount_percentage || 0)) / 100
  return bundleEditorBasePrice.value * factor
})

function openBundleEditor(bundle = null) {
  bundleEditor.error = ''
  if (bundle) {
    bundleEditor.form = {
      id: bundle.id,
      name: bundle.name,
      description: bundle.description || '',
      discount_percentage: parseFloat(bundle.discount_percentage),
      pack_ids: bundle.packs.map(p => p.id),
    }
  } else {
    bundleEditor.form = blankBundle()
  }
  bundleEditor.open = true
}
function closeBundleEditor() { bundleEditor.open = false }

function toggleBundlePack(id) {
  const idx = bundleEditor.form.pack_ids.indexOf(id)
  if (idx >= 0) bundleEditor.form.pack_ids.splice(idx, 1)
  else bundleEditor.form.pack_ids.push(id)
}

async function saveBundle(status) {
  bundleEditor.saving = true
  bundleEditor.error = ''
  try {
    const payload = {
      name: bundleEditor.form.name,
      description: bundleEditor.form.description,
      discount_percentage: bundleEditor.form.discount_percentage,
      pack_ids: bundleEditor.form.pack_ids,
      status,
    }
    if (bundleEditor.form.id) {
      await api.patch(`/partner/production/bundles/${bundleEditor.form.id}/`, payload)
    } else {
      await api.post('/partner/production/bundles/', payload)
    }
    await fetchBundles()
    closeBundleEditor()
  } catch (e) {
    bundleEditor.error = e?.response?.data?.detail
      || Object.values(e?.response?.data || {}).flat().join(' ')
      || 'No se pudo guardar.'
  }
  bundleEditor.saving = false
}

async function toggleBundleStatus(bundle) {
  const newStatus = bundle.status === 'published' ? 'paused' : 'published'
  try {
    await api.patch(`/partner/production/bundles/${bundle.id}/`, { status: newStatus })
    await fetchBundles()
  } catch { /* silent */ }
}

async function deleteBundle(bundle) {
  if (!confirm(`¿Eliminar bundle "${bundle.name}"?`)) return
  try {
    await api.delete(`/partner/production/bundles/${bundle.id}/`)
    await fetchBundles()
  } catch { /* silent */ }
}

async function fetchBundles() {
  try {
    const { data } = await api.get('/partner/production/bundles/')
    bundles.value = Array.isArray(data) ? data : []
  } catch {
    bundles.value = []
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/partner/dashboard/')
    stats.value = data.stats
    recentBookings.value = data.recent_bookings
  } catch (err) {
    console.error('Error loading partner dashboard:', err)
  }
  await fetchProductionProfile()
  if (productionProfile.value?.status === 'verified') {
    await Promise.all([fetchPacks(), fetchBundles(), fetchOpenGigs()])
  }
  loading.value = false
})

function formatMoney(val) {
  return parseFloat(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('es-VE', { day: 'numeric', month: 'short', year: 'numeric' })
}

function goToBooking(id) {
  router.push(`/dashboard/bookings/${id}`)
}
</script>

<style scoped>
.partner-dashboard {
  min-height: 100vh;
  padding: var(--space-8) var(--space-6);
  background: var(--color-bg-primary);
}

.container { max-width: 1100px; margin: 0 auto; }

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.partner-badge {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-bg-primary);
}

.dashboard-header h1 {
  font-size: var(--font-size-2xl);
  font-family: var(--font-heading);
  margin: 0;
}

.subtitle {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin: 0;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
}

.stat-card.highlight {
  background: linear-gradient(135deg, rgba(var(--color-primary-rgb, 163,190,140), 0.1), rgba(var(--color-primary-rgb, 163,190,140), 0.05));
  border-color: var(--color-primary);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bookings-icon { background: rgba(136, 192, 208, 0.15); color: #88c0d0; }
.active-icon { background: rgba(235, 203, 139, 0.15); color: #ebcb8b; }
.completed-icon { background: rgba(163, 190, 140, 0.15); color: #a3be8c; }
.commission-icon { background: rgba(163, 190, 140, 0.2); color: #a3be8c; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text-primary); }
.stat-label { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: 2px; }

/* Pending banner */
.pending-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: rgba(235, 203, 139, 0.1);
  border: 1px solid rgba(235, 203, 139, 0.3);
  border-radius: var(--radius-lg);
  color: #ebcb8b;
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
}

/* Section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.section-header h2 {
  font-size: var(--font-size-lg);
  font-family: var(--font-heading);
}

.link-muted {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.link-muted:hover { color: var(--color-primary-light); }

/* Bookings list */
.bookings-list { display: flex; flex-direction: column; gap: var(--space-3); }

.booking-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.booking-card:hover {
  transform: translateX(4px);
  border-color: var(--color-border-hover);
}

.booking-left { display: flex; align-items: center; gap: var(--space-4); }

.booking-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-input);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.booking-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.booking-info h3 {
  font-size: var(--font-size-base);
  margin: 0 0 2px;
}

.booking-info p {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.booking-location {
  font-size: var(--font-size-xs) !important;
  color: var(--color-text-muted) !important;
}

.booking-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--space-2);
}

.booking-price {
  font-weight: 600;
  color: var(--color-primary-light);
  font-size: var(--font-size-base);
}

/* Status badges */
.status-badge {
  font-size: var(--font-size-xs);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.status-solicitud_enviada { background: rgba(136,192,208,0.15); color: #88c0d0; }
.status-pendiente_respuesta { background: rgba(235,203,139,0.15); color: #ebcb8b; }
.status-aceptada { background: rgba(163,190,140,0.15); color: #a3be8c; }
.status-pendiente_pago { background: rgba(208,135,112,0.15); color: #d08770; }
.status-confirmada { background: rgba(163,190,140,0.2); color: #a3be8c; }
.status-completada { background: rgba(163,190,140,0.3); color: #a3be8c; }
.status-rechazada { background: rgba(191,97,106,0.15); color: #bf616a; }
.status-cancelada { background: rgba(191,97,106,0.1); color: #bf616a; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: var(--space-12) var(--space-6);
  color: var(--color-text-muted);
}

.empty-state p { margin: var(--space-4) 0; }

/* Loading */
.loading-state {
  text-align: center;
  padding: var(--space-16) 0;
  color: var(--color-text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary-light);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto var(--space-4);
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .booking-card { flex-direction: column; align-items: flex-start; gap: var(--space-3); }
  .booking-right { align-items: flex-start; flex-direction: row; gap: var(--space-3); }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
  .og-list { grid-template-columns: 1fr !important; }
  .dashboard-header { flex-direction: column; align-items: flex-start; }
}

/* ── Packs section ── */
.pack-status-banner {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}
.pack-status-banner.pending { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); color: #f59e0b; }
.pack-status-banner.rejected { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }
.banner-link { color: inherit; font-weight: 700; text-decoration: underline; }

.packs-list { display: flex; flex-direction: column; gap: var(--space-2); }
.pack-row {
  display: grid;
  grid-template-columns: 56px 1fr auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}
.pack-thumb {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: rgba(245,158,11,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
}
.pack-thumb svg { width: 26px; height: 26px; }
.h2-icon { color: var(--color-primary); vertical-align: -4px; margin-right: 6px; }
.bundle-pack-row { display: inline-flex; align-items: center; gap: 6px; }
.bundle-pack-icon { display: inline-flex; color: var(--color-text-muted); }
.bundle-pack-icon svg { width: 16px; height: 16px; }
.pack-name { color: var(--color-text-primary); font-weight: 700; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pack-meta { color: var(--color-text-muted); font-size: 0.85rem; margin-top: 4px; display: flex; flex-wrap: wrap; gap: 10px; }
.pack-meta .pack-price { color: var(--color-primary); font-weight: 700; }
.pack-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.pack-tag.tag-draft { background: rgba(140,140,140,0.15); color: var(--color-text-muted); }
.pack-tag.tag-published { background: rgba(16,185,129,0.15); color: #10b981; }
.pack-tag.tag-dj {
  background: rgba(245,158,11,0.12);
  color: #f59e0b;
  display: inline-flex;
  align-items: center;
}
.pack-tag.tag-paused { background: rgba(245,158,11,0.15); color: #f59e0b; }

.pack-actions { display: flex; gap: 6px; }
.icon-btn {
  width: 32px;
  height: 32px;
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}
.icon-btn:hover { border-color: var(--color-primary); }
.icon-btn-danger:hover { border-color: #ef4444; color: #ef4444; }

/* Modal */
.pack-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-6) var(--space-4);
  overflow-y: auto;
}
.pack-modal {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  max-width: 720px;
  width: 100%;
}
.pack-modal-wide { max-width: 1080px; }
.pack-modal-split { display: grid; grid-template-columns: 1.3fr 1fr; gap: var(--space-5); }
.pack-modal h3 { margin-bottom: var(--space-4); font-size: 1.25rem; }

.cover-row { display: flex; align-items: center; gap: var(--space-3); }
.cover-preview-img { width: 80px; height: 60px; border-radius: 8px; overflow: hidden; background: var(--color-bg-soft, rgba(255,255,255,0.02)); border: 1px solid var(--color-border); }
.cover-preview-img img { width: 100%; height: 100%; object-fit: cover; display: block; }

/* Preview side */
.preview-side {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid rgba(245,158,11,0.3);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  align-self: start;
  position: sticky;
  top: 0;
}
.preview-label {
  color: #f59e0b;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
  margin-bottom: var(--space-3);
}
.preview-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}
.preview-hero {
  aspect-ratio: 16/10;
  background: linear-gradient(135deg, #2a1a3e, #1a3a2e);
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-hero img { width: 100%; height: 100%; object-fit: cover; }
.preview-emoji {
  opacity: 0.5;
  color: var(--color-text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.preview-emoji svg { width: 56px; height: 56px; }
.preview-body { padding: var(--space-3); }
.preview-name { color: var(--color-text-primary); font-weight: 700; font-size: 1.05rem; margin-bottom: 4px; }
.preview-meta { color: var(--color-text-muted); font-size: 0.8rem; margin-bottom: 6px; }
.preview-price { color: var(--color-primary); font-weight: 800; font-size: 1.4rem; margin-bottom: 6px; }
.preview-desc { color: var(--color-text-muted); font-size: 0.85rem; margin-bottom: var(--space-2); }
.preview-items { list-style: none; padding: 0; margin: var(--space-2) 0; font-size: 0.8rem; color: var(--color-text-muted); }
.preview-items li { padding: 3px 0 3px 14px; position: relative; }
.preview-items li::before { content: '✓'; position: absolute; left: 0; color: #10b981; }
.preview-items .preview-more::before { content: '+'; color: var(--color-text-muted); }
.preview-flags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: var(--space-2); }
.preview-flag { background: rgba(16,185,129,0.08); color: #10b981; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; display: inline-flex; align-items: center; gap: 4px; }
.preview-flag-dj { background: rgba(245,158,11,0.12); color: #f59e0b; }

/* Toggle "Incluye DJ" en el editor de pack */
.dj-toggle-block {
  padding: var(--space-3);
  background: rgba(245,158,11,0.06);
  border: 1px solid rgba(245,158,11,0.25);
  border-radius: var(--radius-md);
}
.dj-toggle { align-items: flex-start; gap: 10px; padding-top: 0; }
.dj-toggle input[type="checkbox"] { margin-top: 4px; flex-shrink: 0; }
.dj-toggle-text { display: flex; flex-direction: column; }
.dj-toggle-text strong { color: #f59e0b; font-size: 0.92rem; }
.dj-toggle-text small { color: var(--color-text-muted); font-size: 0.78rem; line-height: 1.45; margin-top: 2px; }
.dj-name-wrap { margin-top: var(--space-3); padding-top: var(--space-3); border-top: 1px dashed rgba(245,158,11,0.25); }
.dj-name-wrap .label { display: block; font-size: 0.8rem; color: var(--color-text-muted); margin-bottom: 4px; }
.dj-name-wrap .optional { color: var(--color-text-muted); font-weight: 400; }

/* Bundles */
.bundles-list { display: flex; flex-direction: column; gap: var(--space-2); }
.bundle-row {
  display: grid;
  grid-template-columns: 56px 1fr auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3);
  background: var(--color-bg-card);
  border: 1px solid #f59e0b;
  border-radius: var(--radius-md);
}
.bundle-thumb {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #fb923c);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: #0d0d0d;
  font-weight: 800;
}
.bundle-row-name { color: var(--color-text-primary); font-weight: 700; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.bundle-row-meta { color: var(--color-text-muted); font-size: 0.85rem; margin-top: 4px; display: flex; gap: 12px; flex-wrap: wrap; }
.bundle-row-price { color: var(--color-primary); font-weight: 700; }
.bundle-row-price s { color: var(--color-text-muted); font-weight: 400; margin-left: 4px; }

.bundle-pack-picker {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 240px;
  overflow-y: auto;
  padding: var(--space-2);
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: 8px;
}
.bundle-pack-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  padding: 4px;
  cursor: pointer;
}
.bundle-pack-checkbox input { accent-color: var(--color-primary); }
.bundle-summary {
  background: rgba(245,158,11,0.06);
  border: 1px solid rgba(245,158,11,0.3);
  border-radius: 8px;
  padding: var(--space-3);
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}

@media (max-width: 920px) {
  .pack-modal-split { grid-template-columns: 1fr; }
  .preview-side { position: static; }
}

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.form-group.full { grid-column: 1 / -1; }
.form-group { display: flex; flex-direction: column; }
.label { color: var(--color-text-muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.input-field {
  background: var(--color-bg-soft, rgba(255,255,255,0.02));
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 12px;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  font-family: inherit;
}
.input-field:focus { border-color: var(--color-primary); outline: none; }
.checkbox-label { display: flex; align-items: center; gap: 8px; color: var(--color-text-primary); font-size: 0.9rem; cursor: pointer; padding-top: 24px; }

.chip-list { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.chip { background: rgba(193,216,47,0.1); color: var(--color-primary); padding: 4px 10px; border-radius: 999px; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 6px; }
.chip-x { background: none; border: none; color: inherit; cursor: pointer; font-size: 1.1rem; line-height: 1; padding: 0; }
.add-equip { display: flex; gap: 6px; }
.add-equip .input-field { flex: 1; }

.modal-actions { display: flex; gap: var(--space-3); justify-content: flex-end; margin-top: var(--space-5); }
.form-error { color: #ef4444; font-size: 0.85rem; margin-top: var(--space-3); }

/* ── Solicitudes abiertas (partner) ── */
.og-panel { margin-bottom: var(--space-6); }
.og-empty { color: var(--color-text-muted); font-size: 0.9rem; padding: 14px 18px; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-lg); }
.og-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.og-card {
  display: block; text-decoration: none; color: inherit;
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: 14px 16px;
  transition: transform 0.15s, border-color 0.15s;
}
.og-card:hover { transform: translateY(-1px); border-color: var(--color-border-hover); }
.og-card-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 8px; }
.og-card-head strong { color: var(--color-text-primary); font-size: 0.95rem; }
.og-mine-badge {
  font-size: 0.7rem; font-weight: 700; padding: 2px 9px;
  border-radius: 999px; background: rgba(193, 216, 47, 0.16); color: #C1D82F;
}
.og-chips { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.og-chip {
  display: inline-flex; padding: 2px 9px; border-radius: 999px;
  font-size: 0.7rem; font-weight: 600;
  background: rgba(193, 216, 47, 0.13); color: #C1D82F;
  border: 1px solid rgba(193, 216, 47, 0.3);
}
.og-chip.need-sound   { background: rgba(90, 160, 255, 0.13); color: #a5c6ff; border-color: rgba(165, 198, 255, 0.28); }
.og-chip.need-lights  { background: rgba(255, 180, 60, 0.15); color: #f5c85c; border-color: rgba(245, 200, 92, 0.28); }
.og-chip.need-booth   { background: rgba(200, 100, 220, 0.15); color: #d4a5ff; border-color: rgba(212, 165, 255, 0.28); }
.og-chip.need-screens { background: rgba(90, 220, 190, 0.13); color: #7fddc0; border-color: rgba(127, 221, 192, 0.28); }
.og-chip.need-other   { background: rgba(180, 180, 180, 0.13); color: #cfcfcf; border-color: rgba(200, 200, 200, 0.2); }

.og-meta {
  display: flex; flex-wrap: wrap; gap: 10px;
  color: var(--color-text-muted); font-size: 0.82rem; margin-bottom: 10px;
}
.og-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 8px; border-top: 1px solid var(--color-border);
  font-size: 0.82rem;
}
.og-offers { color: var(--color-text-muted); }
.og-cta { color: #C1D82F; font-weight: 600; }

@media (max-width: 720px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
