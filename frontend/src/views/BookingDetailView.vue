<template>
  <div class="detail-page">
    <div class="container">
      <router-link to="/dashboard" class="back-link animate-fade-in-up">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al Dashboard
      </router-link>

      <div v-if="loading" class="loading-state">
        <div v-for="i in 4" :key="i" class="skeleton" style="height:60px;margin-bottom:var(--space-3);border-radius:var(--radius-lg);"></div>
      </div>

      <div v-else-if="booking" class="detail-layout animate-fade-in-up" style="animation-delay:0.1s">
        <!-- Left: Main Content -->
        <div class="detail-main">
          <!-- Header -->
          <div class="detail-header glass">
            <div class="header-top">
              <div>
                <code v-if="booking.booking_code" class="header-code">{{ booking.booking_code }}</code>
                <h1>{{ booking.event_name || booking.event_type_display }}</h1>
                <p class="event-date">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  {{ formatDate(booking.event_date) }} · {{ booking.event_time_start?.slice(0,5) }} - {{ booking.event_time_end?.slice(0,5) }}
                </p>
              </div>
              <span class="status-badge" :class="statusClass(booking.status)">{{ statusLabel(booking.status) }}</span>
            </div>

            <!-- Countdown banner (solo si confirmada y evento futuro) -->
            <div v-if="countdown" class="countdown-banner">
              <span class="cd-label">Faltan</span>
              <div class="cd-units">
                <div class="cd-unit"><strong>{{ countdown.days }}</strong><span>días</span></div>
                <div class="cd-unit"><strong>{{ countdown.hours }}</strong><span>horas</span></div>
                <div class="cd-unit"><strong>{{ countdown.minutes }}</strong><span>min</span></div>
              </div>
              <span class="cd-escrow">🛡 ${{ Number(booking.amount_paid || 0).toFixed(2) }} en custodia</span>
            </div>
          </div>

          <!-- Event Details -->
          <div class="info-card glass">
            <h3>Detalles del Evento</h3>
            <div class="info-grid">
              <div v-if="booking.event_type_display || booking.event_type" class="info-item">
                <span class="info-label">Tipo de evento</span>
                <span>{{ booking.event_type_display || booking.event_type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Ubicación</span>
                <span>{{ booking.event_location }}</span>
              </div>
              <div v-if="booking.event_city" class="info-item">
                <span class="info-label">Ciudad</span>
                <span>{{ booking.event_city }}</span>
              </div>
              <div v-if="booking.guest_count" class="info-item">
                <span class="info-label">Invitados</span>
                <span>{{ booking.guest_count }}</span>
              </div>
              <div v-if="booking.event_duration_hours" class="info-item">
                <span class="info-label">Duración</span>
                <span>{{ booking.event_duration_hours }} horas</span>
              </div>
              <div v-if="booking.event_indoor !== null && booking.event_indoor !== undefined" class="info-item">
                <span class="info-label">Espacio</span>
                <span>{{ booking.event_indoor ? '🏠 Interior' : '🌤 Exterior' }}</span>
              </div>
              <div v-if="booking.genre_preference" class="info-item">
                <span class="info-label">Género / ambiente</span>
                <span>{{ booking.genre_preference }}</span>
              </div>
              <div v-if="booking.budget" class="info-item">
                <span class="info-label">Presupuesto</span>
                <span>${{ booking.budget }}</span>
              </div>
            </div>
            <div v-if="booking.description" class="info-description">
              <span class="info-label">Descripción</span>
              <p>{{ booking.description }}</p>
            </div>
            <div v-if="booking.client_notes" class="info-description">
              <span class="info-label">Mensaje del cliente</span>
              <p>{{ booking.client_notes }}</p>
            </div>
            <div v-if="booking.talent_notes" class="info-description">
              <span class="info-label">Notas del talento</span>
              <p>{{ booking.talent_notes }}</p>
            </div>
          </div>

          <!-- Cliente final (sólo si reserva por Partner) -->
          <div v-if="booking.booking_type === 'partner' && (booking.client_final_name || booking.client_final_email || booking.client_final_phone)" class="info-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/></svg>
              Cliente Final
            </h3>
            <div class="info-grid">
              <div v-if="booking.client_final_name" class="info-item">
                <span class="info-label">Nombre</span>
                <span>{{ booking.client_final_name }}</span>
              </div>
              <div v-if="booking.client_final_email" class="info-item">
                <span class="info-label">Email</span>
                <span>{{ booking.client_final_email }}</span>
              </div>
              <div v-if="booking.client_final_phone" class="info-item">
                <span class="info-label">Teléfono</span>
                <span>{{ booking.client_final_phone }}</span>
              </div>
            </div>
          </div>

          <!-- Additional Services (from multi-step booking) -->
          <div v-if="normalizedServices.length" class="info-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
              Servicios de Producción
            </h3>
            <div class="services-grid">
              <div v-for="(item, idx) in normalizedServices" :key="idx" class="service-item">
                <div class="service-header">
                  <span class="service-icon" v-html="serviceIconsSvg[item.service] || '🎵'"></span>
                  <strong>{{ serviceLabels[item.service] || item.service }}</strong>
                </div>
                <div v-if="item.details && Object.keys(item.details).length" class="service-details">
                  <div v-for="(val, key) in item.details" :key="key" class="service-detail-row">
                    <template v-if="val !== '' && val !== null && val !== undefined">
                      <span class="info-label">{{ formatDetailKey(key) }}</span>
                      <span>{{ typeof val === 'boolean' ? (val ? 'Sí' : 'No') : val }}</span>
                    </template>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="booking.additional_services_notes" class="info-description" style="margin-top:var(--space-4)">
              <span class="info-label">Notas de producción</span>
              <p>{{ booking.additional_services_notes }}</p>
            </div>
          </div>

          <!-- ── Production Packs (Fase 7) ── -->
          <div class="info-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>
              Packs de Producción
              <button v-if="isClientView && canEditPacks" class="btn btn-outline btn-sm" style="margin-left:auto" @click="openPackPicker">+ Agregar pack</button>
            </h3>

            <div v-if="bookingPacks.length === 0" class="empty-mini">
              <span>Sin packs agregados.</span>
              <router-link to="/packs" class="link-muted">Ver catálogo →</router-link>
            </div>
            <div v-else class="bp-list">
              <div v-for="bp in bookingPacks" :key="bp.id" class="bp-row">
                <div class="bp-thumb">{{ prodCatIcon(bp.pack?.category) }}</div>
                <div class="bp-info">
                  <div class="bp-name">{{ bp.pack?.name }}</div>
                  <div class="bp-meta">{{ bp.pack?.vendor?.name }} · {{ bp.pack?.event_size_display }}</div>
                </div>
                <div class="bp-price">${{ Number(bp.line_total).toFixed(2) }}</div>
                <button v-if="isClientView && canEditPacks" class="bp-remove" @click="removeBookingPack(bp.id)" :disabled="removingPackId === bp.id" title="Quitar">×</button>
              </div>
              <div class="bp-total">
                Subtotal packs: <strong>${{ packsSubtotal.toFixed(2) }}</strong>
              </div>
            </div>

            <!-- Picker modal -->
            <Teleport to="body">
              <div v-if="packPicker.open" class="bp-picker-backdrop" @click.self="packPicker.open = false">
                <div class="bp-picker-modal">
                  <h3>Agregar pack al booking</h3>
                  <div v-if="packPicker.loading" class="empty-mini">Cargando…</div>
                  <div v-else-if="!packPicker.available.length" class="empty-mini">
                    No hay packs disponibles. <router-link to="/packs">Ir al catálogo →</router-link>
                  </div>
                  <div v-else class="bp-picker-list">
                    <button
                      v-for="pk in packPicker.available"
                      :key="pk.id"
                      class="bp-picker-row"
                      :class="{ 'bp-picker-recommended': pk.is_recommended }"
                      :disabled="isPackAlreadyAdded(pk.id) || packPicker.adding === pk.id"
                      @click="addBookingPack(pk.id)"
                    >
                      <span class="bp-thumb">{{ prodCatIcon(pk.category) }}</span>
                      <span class="bp-picker-info">
                        <strong>
                          <span v-if="pk.is_recommended" class="bp-rec-badge">★ RECOMENDADO POR {{ (booking.talent?.stage_name || 'TU DJ').toUpperCase() }}</span>
                          {{ pk.name }}
                        </strong>
                        <small>{{ pk.vendor?.name }} · {{ pk.event_size_display }}</small>
                      </span>
                      <span class="bp-picker-price">${{ Number(pk.price).toFixed(0) }}</span>
                      <span v-if="isPackAlreadyAdded(pk.id)" class="bp-picker-tag">Ya agregado</span>
                    </button>
                  </div>
                  <p v-if="packPicker.error" class="form-error">{{ packPicker.error }}</p>
                  <div class="bp-picker-actions">
                    <button class="btn btn-ghost btn-sm" @click="packPicker.open = false">Cerrar</button>
                  </div>
                </div>
              </div>
            </Teleport>
          </div>

          <!-- Talent Actions (accept/reject/adjust) -->
          <div v-if="isTalentView && canTalentAct" class="action-card glass">
            <h3>Responder Solicitud</h3>
            <div class="action-form">
              <div class="form-group">
                <label class="form-label">Precio Final ($)</label>
                <input v-model.number="quotedPrice" type="number" class="form-input" :placeholder="booking.precio_estimado || '0.00'" min="0" step="0.01">
              </div>
              <div class="form-group">
                <label class="form-label">Notas para el cliente</label>
                <textarea v-model="talentNotes" class="form-input" rows="3" placeholder="Detalles de tu propuesta..."></textarea>
              </div>
              <div class="action-buttons">
                <button @click="updateStatus('aceptada')" class="btn btn-primary" :disabled="actionLoading">
                  ✓ Aceptar
                </button>
                <button @click="updateStatus('rechazada')" class="btn btn-ghost btn-danger" :disabled="actionLoading">
                  ✕ Rechazar
                </button>
              </div>
            </div>
          </div>

          <!-- Client Actions (pay) -->
          <div v-if="isClientView && booking.status === 'pendiente_pago'" class="action-card glass action-pay-card">
            <div class="pay-cta-row">
              <div>
                <h3>¡Tu propuesta fue aceptada!</h3>
                <p class="action-desc">Completa el pago para confirmar tu reserva. Tu dinero queda en custodia hasta el evento.</p>
              </div>
              <div class="pay-price-block">
                <span>Total</span>
                <strong>${{ Number(booking.quoted_price || booking.precio_estimado || 0).toFixed(2) }}</strong>
              </div>
            </div>
            <div v-if="booking.talent_notes" class="talent-notes-box">
              <strong>Notas del talento:</strong>
              <p>{{ booking.talent_notes }}</p>
            </div>
            <router-link :to="`/dashboard/bookings/${booking.id}/pay`" class="btn btn-cta btn-lg btn-go-pay">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              Ir a pagar con Pulsar Escrow
            </router-link>
          </div>

          <!-- Review (if completed) - usa componente completo con 5 dimensiones + crédito -->
          <div v-if="isClientView && booking.status === 'completada' && !booking.review">
            <ReviewForm
              :booking-id="booking.id"
              :talent-name="booking.talent?.stage_name || 'el talento'"
              @submitted="onReviewSubmitted"
              @cancel="() => {}"
            />
          </div>

          <!-- Admin/Talent: Mark as completed -->
          <div v-if="canMarkComplete" class="action-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Marcar como Completado
            </h3>
            <p class="action-desc">El evento ya fue realizado. Marcar como completado habilita las reseñas y actualiza las estadísticas del talento.</p>
            <button @click="updateStatus('completada')" class="btn btn-primary" :disabled="actionLoading">
              ✓ Completar Evento
            </button>
          </div>

          <!-- Existing Review -->
          <div v-if="booking.review" class="info-card glass">
            <h3>Reseña</h3>
            <div class="review-display">
              <div class="stars">{{ '★'.repeat(booking.review.rating) }}{{ '☆'.repeat(5 - booking.review.rating) }}</div>
              <p>{{ booking.review.comment }}</p>
            </div>
          </div>

          <!-- Chat Section -->
          <div class="chat-card glass">
            <h3>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              Chat
            </h3>
            <div class="chat-disclaimer">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              Toda comunicación queda dentro de Pulsar. No compartas teléfonos, emails ni redes.
            </div>
            <div class="chat-messages" ref="chatContainer">
              <div v-if="!messages.length" class="chat-empty">
                <p>Aún no hay mensajes. Inicia la conversación.</p>
              </div>
              <div v-for="msg in messages" :key="msg.id" class="chat-msg" :class="{ mine: msg.sender === auth.user?.id, flagged: msg.flagged }">
                <div class="msg-bubble">
                  <span class="msg-sender">{{ msg.sender === auth.user?.id ? 'Tú' : msg.sender_name }}</span>
                  <p>{{ msg.content }}</p>
                  <span v-if="msg.flagged" class="msg-flagged-tag">⚠ Mensaje filtrado por anti-desintermediación</span>
                  <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
                </div>
              </div>
            </div>
            <div v-if="chatViolationMsg" class="anti-disinter-warn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ chatViolationMsg }}
            </div>
            <div class="chat-input-row">
              <input v-model="newMessage" @keyup.enter="sendMessage" type="text"
                class="form-input"
                :class="{ 'form-input-warn': chatViolations.length }"
                placeholder="Escribe un mensaje..."
              >
              <button @click="sendMessage" class="btn btn-primary btn-send" :disabled="!newMessage.trim() || chatViolations.length">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Right: Sidebar -->
        <div class="detail-sidebar">
          <!-- Counterpart Info -->
          <div class="sidebar-card glass">
            <h4>{{ isTalentView ? 'Cliente' : 'Talento' }}</h4>
            <div class="person-info">
              <div class="person-avatar">
                {{ (isTalentView ? booking.client?.first_name : booking.talent?.stage_name)?.[0] || '?' }}
              </div>
              <div>
                <strong>{{ isTalentView ? `${booking.client?.first_name} ${booking.client?.last_name}` : booking.talent?.stage_name }}</strong>
                <p v-if="!isTalentView && booking.talent?.talent_level" class="talent-level">
                  {{ booking.talent.talent_level === 'premium' ? '⭐ Premium' : 'Standard' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Pricing Info -->
          <div class="sidebar-card glass">
            <h4>Precios</h4>
            <div class="price-rows">
              <div v-if="booking.precio_estimado" class="price-row">
                <span>Estimado</span><span>${{ booking.precio_estimado }}</span>
              </div>
              <div v-if="booking.quoted_price" class="price-row">
                <span>Precio Final</span><span class="text-primary">${{ booking.quoted_price }}</span>
              </div>
              <div v-if="booking.budget" class="price-row">
                <span>Presupuesto</span><span>${{ booking.budget }}</span>
              </div>
              <div class="price-divider"></div>
              <div class="price-row">
                <span>Pagado</span><span class="text-success">${{ booking.amount_paid || '0.00' }}</span>
              </div>
              <div v-if="booking.remaining_balance > 0" class="price-row">
                <span>Pendiente</span><span class="text-warning">${{ booking.remaining_balance }}</span>
              </div>
            </div>
          </div>

          <!-- Payments History -->
          <div v-if="booking.payments?.length" class="sidebar-card glass">
            <h4>Pagos</h4>
            <div v-for="p in booking.payments" :key="p.id" class="payment-item">
              <div>
                <strong>${{ p.amount }}</strong>
                <span class="payment-type">{{ p.payment_type === 'deposit' ? 'Depósito' : 'Total' }}</span>
              </div>
              <span class="payment-status" :class="p.payment_status === 'completed' ? 'text-success' : 'text-warning'">
                {{ p.payment_status === 'completed' ? '✓' : '⏳' }}
              </span>
            </div>
          </div>

          <!-- Cancel / Modify / Report / Download contract -->
          <div v-if="canCancel || canModify || canReport || canDownloadContract" class="sidebar-card glass actions-sidebar-card">
            <button v-if="canDownloadContract" @click="downloadContract" class="btn btn-ghost btn-full btn-action">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 18 15 15"/></svg>
              Descargar contrato
            </button>
            <button v-if="canModify" @click="modifyModal.open = true" class="btn btn-ghost btn-full btn-action">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              Modificar fecha/hora
            </button>
            <button v-if="canReport" @click="reportModal.open = true" class="btn btn-ghost btn-full btn-action btn-report">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              Reportar problema
            </button>
            <button v-if="canCancel" @click="openCancelModal" class="btn btn-ghost btn-danger btn-full" :disabled="actionLoading">
              Cancelar Reserva
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancellation Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="cancelModal.open" class="cancel-modal-backdrop" @click.self="cancelModal.open = false">
          <div class="cancel-modal glass">
            <h3>Cancelar reserva</h3>
            <p class="cancel-policy-label">Política de cancelación de Pulsar</p>

            <div v-if="cancelModal.loading" class="cancel-loading">Calculando reembolso...</div>

            <div v-else-if="cancelModal.preview" class="cancel-preview">
              <div class="cancel-window-card">
                <strong>{{ cancelModal.preview.window_label }}</strong>
                <p class="cancel-days">Faltan {{ cancelModal.preview.days_to_event }} días al evento</p>
              </div>

              <div class="cancel-amounts">
                <div class="cancel-row">
                  <span>Pagado a la fecha</span>
                  <span>${{ Number(cancelModal.preview.paid).toFixed(2) }}</span>
                </div>
                <div class="cancel-row total">
                  <span>Te devolvemos</span>
                  <strong class="cancel-refund">${{ Number(cancelModal.preview.refund_amount).toFixed(2) }}</strong>
                </div>
                <p class="cancel-rate-note">Tasa de reembolso: {{ Math.round(Number(cancelModal.preview.refund_rate) * 100) }}%</p>
              </div>

              <p class="cancel-warning">
                ⚠ Esta acción no se puede deshacer. El talento será notificado y la fecha quedará disponible.
              </p>
            </div>

            <div v-if="cancelModal.error" class="cancel-error">{{ cancelModal.error }}</div>

            <div class="cancel-actions">
              <button class="btn btn-ghost btn-sm" @click="cancelModal.open = false">No cancelar</button>
              <button class="btn btn-danger btn-sm" :disabled="cancelModal.loading || actionLoading" @click="confirmCancel">
                Confirmar cancelación
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Modify Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="modifyModal.open" class="cancel-modal-backdrop" @click.self="modifyModal.open = false">
          <div class="cancel-modal glass">
            <h3>Modificar fecha del evento</h3>
            <p class="cancel-policy-label">Cambia fecha u hora · el talento debe re-confirmar</p>
            <div class="modify-grid">
              <div class="form-group">
                <label class="form-label">Nueva fecha</label>
                <input v-model="modifyModal.event_date" type="date" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Hora inicio</label>
                <input v-model="modifyModal.event_time_start" type="time" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Hora fin</label>
                <input v-model="modifyModal.event_time_end" type="time" class="form-input" />
              </div>
            </div>
            <p class="modify-note">⚠ Al modificar, el booking vuelve a "pendiente de respuesta" y el talento debe re-confirmar.</p>
            <p v-if="modifyModal.error" class="cancel-error">{{ modifyModal.error }}</p>
            <div class="cancel-actions">
              <button class="btn btn-ghost btn-sm" @click="modifyModal.open = false">Cancelar</button>
              <button class="btn btn-primary btn-sm" :disabled="modifyModal.loading || !canSubmitModify" @click="submitModify">
                {{ modifyModal.loading ? 'Enviando...' : 'Solicitar cambio' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Report Problem Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="reportModal.open" class="cancel-modal-backdrop" @click.self="reportModal.open = false">
          <div class="cancel-modal glass">
            <h3>Reportar problema</h3>
            <p class="cancel-policy-label">Pulsar revisará y retendrá el pago al talento</p>

            <div class="form-group">
              <label class="form-label">¿Qué pasó?</label>
              <select v-model="reportModal.reason" class="form-input">
                <option value="">Selecciona...</option>
                <option value="no_show">No se presentó</option>
                <option value="late">Llegó muy tarde</option>
                <option value="poor_service">Servicio deficiente</option>
                <option value="different_artist">Vino un artista distinto</option>
                <option value="equipment_failure">Fallas con el equipo</option>
                <option value="other">Otro</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Descripción detallada</label>
              <textarea v-model="reportModal.description" rows="4" class="form-input" placeholder="Cuéntanos qué sucedió. Mientras más detalle, más rápido resolvemos."></textarea>
            </div>

            <p class="modify-note">
              🛡 Al reportar, el pago queda retenido y nuestro equipo revisará en máximo 48h. Si tu reporte es válido, recibes reembolso 100%.
            </p>

            <p v-if="reportModal.error" class="cancel-error">{{ reportModal.error }}</p>

            <div class="cancel-actions">
              <button class="btn btn-ghost btn-sm" @click="reportModal.open = false">Cancelar</button>
              <button class="btn btn-danger btn-sm" :disabled="reportModal.loading || !canSubmitReport" @click="submitReport">
                {{ reportModal.loading ? 'Enviando...' : 'Reportar problema' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import ReviewForm from '@/components/booking/ReviewForm.vue'
import { scan as antiScan, violationsMessage } from '@/utils/antiDisinter'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const booking = ref(null)
const messages = ref([])
const loading = ref(true)
const actionLoading = ref(false)
const newMessage = ref('')
const quotedPrice = ref(null)
const talentNotes = ref('')
const reviewRating = ref(0)
const reviewComment = ref('')
const chatContainer = ref(null)

// ── Anti-desintermediación en chat ──
const chatViolations = ref([])
watch(newMessage, (val) => {
  chatViolations.value = antiScan(val)
})
const chatViolationMsg = computed(() => violationsMessage(chatViolations.value))

// ── Countdown banner ──
const now = ref(Date.now())
let countdownTimer = null
const countdown = computed(() => {
  if (!booking.value || booking.value.status !== 'confirmada') return null
  if (!booking.value.event_date || !booking.value.event_time_start) return null
  const target = new Date(`${booking.value.event_date}T${booking.value.event_time_start}`).getTime()
  const diff = target - now.value
  if (diff <= 0) return null
  return {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
  }
})
onMounted(() => { countdownTimer = setInterval(() => { now.value = Date.now() }, 30000) })
onUnmounted(() => { if (countdownTimer) clearInterval(countdownTimer) })

function onReviewSubmitted(review) {
  if (booking.value) booking.value.review = review
}

// ── Cancellation modal ──
const cancelModal = ref({
  open: false,
  loading: false,
  preview: null,
  error: '',
})

async function openCancelModal() {
  cancelModal.value = { open: true, loading: true, preview: null, error: '' }
  try {
    const { data } = await api.get(`/bookings/${booking.value.id}/cancel-preview/`)
    cancelModal.value.preview = data
  } catch (err) {
    cancelModal.value.error = err.response?.data?.error || 'No se pudo calcular el reembolso.'
  } finally {
    cancelModal.value.loading = false
  }
}

async function confirmCancel() {
  await updateStatus('cancelada')
  cancelModal.value.open = false
}

// ── Modify booking modal ──
const modifyModal = ref({
  open: false,
  event_date: '',
  event_time_start: '',
  event_time_end: '',
  loading: false,
  error: '',
})

const canModify = computed(() => {
  if (!booking.value) return false
  if (!isClientView.value) return false
  return ['aceptada', 'pendiente_pago', 'confirmada'].includes(booking.value.status)
})

const canSubmitModify = computed(() => {
  return modifyModal.value.event_date
    && modifyModal.value.event_time_start
    && modifyModal.value.event_time_end
})

watch(() => modifyModal.value.open, (open) => {
  if (open && booking.value) {
    modifyModal.value.event_date = booking.value.event_date || ''
    modifyModal.value.event_time_start = (booking.value.event_time_start || '').slice(0, 5)
    modifyModal.value.event_time_end = (booking.value.event_time_end || '').slice(0, 5)
    modifyModal.value.error = ''
  }
})

async function submitModify() {
  if (!canSubmitModify.value) return
  modifyModal.value.loading = true
  modifyModal.value.error = ''
  try {
    const { data } = await api.patch(`/bookings/${booking.value.id}/modify/`, {
      event_date: modifyModal.value.event_date,
      event_time_start: modifyModal.value.event_time_start,
      event_time_end: modifyModal.value.event_time_end,
    })
    booking.value = data
    modifyModal.value.open = false
  } catch (err) {
    modifyModal.value.error = err.response?.data?.error || 'No se pudo modificar.'
  } finally {
    modifyModal.value.loading = false
  }
}

// ── Report problem (dispute) modal ──
const reportModal = ref({
  open: false,
  reason: '',
  description: '',
  loading: false,
  error: '',
})

const canReport = computed(() => {
  if (!booking.value || !isClientView.value) return false
  if (['en_disputa', 'cancelada', 'rechazada'].includes(booking.value.status)) return false
  return ['confirmada', 'completada'].includes(booking.value.status)
})

const canSubmitReport = computed(() => {
  return reportModal.value.reason && reportModal.value.description.trim().length >= 20
})

// ── Descargar contrato ──
const canDownloadContract = computed(() => {
  if (!booking.value) return false
  return ['aceptada', 'pendiente_pago', 'confirmada', 'completada'].includes(booking.value.status)
})

function downloadContract() {
  const token = localStorage.getItem('access_token')
  fetch(`/api/bookings/${booking.value.id}/contract/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.blob()).then(blob => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `contrato-${booking.value.booking_code || booking.value.id}.html`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }).catch(() => alert('No se pudo descargar el contrato.'))
}

async function submitReport() {
  if (!canSubmitReport.value) return
  reportModal.value.loading = true
  reportModal.value.error = ''
  try {
    await api.post(`/bookings/${booking.value.id}/dispute/`, {
      reason: reportModal.value.reason,
      description: reportModal.value.description,
    })
    booking.value.status = 'en_disputa'
    reportModal.value.open = false
    reportModal.value.reason = ''
    reportModal.value.description = ''
  } catch (err) {
    reportModal.value.error = err.response?.data?.error || 'No se pudo enviar el reporte.'
  } finally {
    reportModal.value.loading = false
  }
}

const serviceLabels = {
  sound: 'Sonido',
  sonido: 'Sonido',
  lights: 'Luces',
  iluminacion: 'Iluminación',
  booth: 'DJ Booth',
  tarima: 'Tarima / Booth',
  microphone: 'Micrófono',
  screens: 'Pantallas LED',
  pantallas: 'Pantallas LED',
  ledfloor: 'Piso LED',
  technician: 'Técnico',
  efectos: 'Efectos Especiales',
}
const serviceIconsSvg = {
  sound: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>',
  sonido: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/></svg>',
  lights: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
  iluminacion: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
  booth: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>',
  microphone: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/></svg>',
  screens: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
  pantallas: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/></svg>',
  ledfloor: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
  technician: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>',
}

// Normalize additional_services to always be an array of {service, details}
// Handles both array format: [{service: "lights", details: {...}}]
// and legacy dict format: {"sonido": {...}, "iluminacion": {...}}
const normalizedServices = computed(() => {
  const raw = booking.value?.additional_services
  if (!raw) return []
  if (Array.isArray(raw)) {
    return raw.map(item => ({
      service: item.service || 'unknown',
      details: item.details || {}
    }))
  }
  // Legacy dict format
  return Object.entries(raw).map(([key, val]) => ({
    service: key,
    details: typeof val === 'object' ? val : {}
  }))
})

const detailKeyLabels = {
  capacity: 'Capacidad',
  microphone: 'Micrófono',
  level: 'Nivel',
  type: 'Tipo',
  purpose: 'Propósito',
  hasContent: 'Incluye Contenido',
  schedule: 'Horario',
}

function formatDetailKey(key) {
  return detailKeyLabels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const isTalentView = computed(() => auth.user?.role === 'talent')
const isClientView = computed(() => auth.user?.role === 'client' || auth.user?.role === 'partner')

const canTalentAct = computed(() =>
  ['solicitud_enviada', 'pendiente_respuesta'].includes(booking.value?.status)
)

const canCancel = computed(() =>
  ['solicitud_enviada', 'pendiente_respuesta', 'aceptada', 'pendiente_pago'].includes(booking.value?.status)
)

const isAdminView = computed(() => auth.user?.role === 'admin')

const canMarkComplete = computed(() => {
  if (!booking.value || booking.value.status !== 'confirmada') return false
  // Show for admin always, for talent only after event date
  if (isAdminView.value) return true
  if (isTalentView.value) {
    const eventDate = new Date(booking.value.event_date + 'T23:59:59')
    return new Date() > eventDate
  }
  return false
})

const statusMap = {
  solicitud_enviada: { label: 'Solicitud Enviada', class: 'status-info' },
  pendiente_respuesta: { label: 'Pendiente', class: 'status-warning' },
  aceptada: { label: 'Aceptada', class: 'status-success' },
  rechazada: { label: 'Rechazada', class: 'status-error' },
  pendiente_pago: { label: 'Pendiente de Pago', class: 'status-warning' },
  confirmada: { label: 'Confirmada', class: 'status-success' },
  completada: { label: 'Completada', class: 'status-completed' },
  cancelada: { label: 'Cancelada', class: 'status-error' },
}

function statusClass(s) { return statusMap[s]?.class || '' }
function statusLabel(s) { return statusMap[s]?.label || s }

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-VE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })
}

async function updateStatus(newStatus) {
  actionLoading.value = true
  try {
    const payload = { status: newStatus }
    if (quotedPrice.value) payload.quoted_price = quotedPrice.value
    if (talentNotes.value) payload.talent_notes = talentNotes.value

    const { data } = await api.patch(`/bookings/${booking.value.id}/status/`, payload)
    booking.value = data
  } catch (e) {
    alert(e.response?.data?.error || 'Error al actualizar el estado.')
  } finally {
    actionLoading.value = false
  }
}

async function processPayment(type) {
  actionLoading.value = true
  try {
    const finalPrice = parseFloat(booking.value.quoted_price || booking.value.precio_estimado || 0)
    const amount = type === 'deposit' ? finalPrice * 0.5 : finalPrice

    await api.post('/payments/create/', {
      booking: booking.value.id,
      amount: amount.toFixed(2),
      payment_type: type === 'deposit' ? 'deposit' : 'full',
      payment_method: 'card',
    })
    // Reload booking
    const { data } = await api.get(`/bookings/${booking.value.id}/`)
    booking.value = data
  } catch (e) {
    const msg = e.response?.data
    alert(typeof msg === 'object' ? Object.values(msg).flat().join(' ') : 'Error al procesar el pago.')
  } finally {
    actionLoading.value = false
  }
}

async function sendMessage() {
  if (!newMessage.value.trim()) return
  if (chatViolations.value.length) {
    // El backend también lo filtra, pero damos feedback inmediato
    return
  }
  try {
    const { data } = await api.post('/messages/send/', {
      booking: booking.value.id,
      content: newMessage.value.trim(),
    })
    messages.value.push(data)
    newMessage.value = ''
    await nextTick()
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  } catch (e) {
    console.error(e)
  }
}

async function submitReview() {
  actionLoading.value = true
  try {
    await api.post(`/bookings/${booking.value.id}/review/`, {
      rating: reviewRating.value,
      comment: reviewComment.value,
    })
    const { data } = await api.get(`/bookings/${booking.value.id}/`)
    booking.value = data
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al enviar la reseña.')
  } finally {
    actionLoading.value = false
  }
}

// ── Production packs ──
const PROD_CAT_ICONS = { sound: '🔊', lights: '💡', screens: '📺', mics: '🎤', dj_booth: '🎚', fx: '🪩' }
function prodCatIcon(c) { return PROD_CAT_ICONS[c] || '📦' }

const bookingPacks = ref([])
const removingPackId = ref(null)
const packPicker = ref({ open: false, loading: false, adding: null, available: [], error: '' })

const canEditPacks = computed(() => {
  if (!booking.value) return false
  return !['confirmada', 'completada', 'cancelada'].includes(booking.value.status)
})

const packsSubtotal = computed(() => {
  return bookingPacks.value.reduce((s, bp) => s + parseFloat(bp.line_total || 0), 0)
})

function isPackAlreadyAdded(packId) {
  return bookingPacks.value.some(bp => bp.pack?.id === packId)
}

async function fetchBookingPacks() {
  try {
    const { data } = await api.get(`/bookings/${route.params.id}/packs/`)
    bookingPacks.value = Array.isArray(data) ? data : []
  } catch {
    bookingPacks.value = []
  }
}

async function openPackPicker() {
  packPicker.value.open = true
  packPicker.value.loading = true
  packPicker.value.error = ''
  try {
    const params = {}
    if (booking.value?.talent?.id) {
      params.for_talent_id = booking.value.talent.id
    }
    const { data } = await api.get('/production-packs/', { params })
    packPicker.value.available = Array.isArray(data) ? data : []
  } catch {
    packPicker.value.available = []
  }
  packPicker.value.loading = false
}

async function addBookingPack(packId) {
  packPicker.value.adding = packId
  packPicker.value.error = ''
  try {
    await api.post(`/bookings/${route.params.id}/packs/`, { pack_id: packId, quantity: 1 })
    await fetchBookingPacks()
    packPicker.value.open = false
  } catch (e) {
    packPicker.value.error = e?.response?.data?.detail || 'No se pudo agregar.'
  }
  packPicker.value.adding = null
}

async function removeBookingPack(id) {
  if (!confirm('¿Quitar este pack del booking?')) return
  removingPackId.value = id
  try {
    await api.delete(`/bookings/${route.params.id}/packs/${id}/`)
    await fetchBookingPacks()
  } catch { /* silent */ }
  removingPackId.value = null
}

onMounted(async () => {
  try {
    const [bookRes, msgRes] = await Promise.all([
      api.get(`/bookings/${route.params.id}/`),
      api.get(`/bookings/${route.params.id}/messages/`),
    ])
    booking.value = bookRes.data
    messages.value = msgRes.data.results || msgRes.data
    await fetchBookingPacks()
    // Mark messages as read
    await api.post(`/bookings/${route.params.id}/messages/read/`)
    await nextTick()
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  padding-top: var(--space-4);
  min-height: 100vh;
  padding-bottom: var(--space-16);
}

.back-link {
  display: inline-flex; align-items: center; gap: var(--space-2);
  color: var(--color-text-muted); font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--color-primary); }

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: var(--space-8);
  align-items: start;
}

.detail-main { display: flex; flex-direction: column; gap: var(--space-6); }

/* Header */
.detail-header { padding: var(--space-6); border-radius: var(--radius-xl); }
.header-top { display: flex; justify-content: space-between; align-items: flex-start; }
.detail-header h1 { font-size: var(--font-size-2xl); margin-bottom: var(--space-2); }
.event-date { display: flex; align-items: center; gap: var(--space-2); color: var(--color-text-muted); font-size: var(--font-size-sm); }

/* Info Card */
.info-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.info-card h3 { font-size: var(--font-size-base); margin-bottom: var(--space-5); }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); }
.info-item { display: flex; flex-direction: column; gap: 2px; }
.info-label { font-size: var(--font-size-xs); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.info-description { margin-top: var(--space-4); }
.info-description p { margin-top: var(--space-2); color: var(--color-text-secondary); font-size: var(--font-size-sm); }

/* Action Card */
.action-card { padding: var(--space-6); border-radius: var(--radius-xl); border-color: var(--color-primary) !important; }
.action-card h3 { font-size: var(--font-size-base); margin-bottom: var(--space-4); }
.action-desc { color: var(--color-text-muted); font-size: var(--font-size-sm); margin-bottom: var(--space-4); }
.action-form { display: flex; flex-direction: column; gap: var(--space-4); }
.action-buttons { display: flex; gap: var(--space-3); }
.btn-danger { color: var(--color-accent) !important; border-color: var(--color-accent) !important; }
.btn-danger:hover { background: rgba(232,93,74,0.1) !important; }
.btn-full { width: 100%; }

.form-group { display: flex; flex-direction: column; gap: var(--space-2); }
.form-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-secondary); }
.form-input {
  background: var(--color-bg-elevated); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-sm); color: var(--color-text-primary);
  font-family: var(--font-body);
  transition: border-color var(--transition-fast);
}
.form-input:focus { outline: none; border-color: var(--color-primary); }

.price-final { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.price-big { font-size: var(--font-size-3xl); font-weight: 800; color: var(--color-primary); }

.action-pay-card {
  background: linear-gradient(135deg, rgba(16,185,129,0.05), rgba(193,216,47,0.02));
  border: 1px solid rgba(16,185,129,0.35) !important;
}
.pay-cta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}
.pay-price-block { text-align: right; }
.pay-price-block span {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}
.pay-price-block strong {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  color: var(--color-primary);
}
.btn-go-pay {
  width: 100%;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: var(--space-3);
}

.talent-notes-box { background: var(--color-bg-elevated); border-radius: var(--radius-lg); padding: var(--space-4); margin-bottom: var(--space-4); font-size: var(--font-size-sm); }
.talent-notes-box p { color: var(--color-text-secondary); margin-top: var(--space-1); }

/* Review */
.review-form { display: flex; flex-direction: column; gap: var(--space-4); }
.star-rating { display: flex; gap: var(--space-1); }
.star-btn {
  background: none; border: none; font-size: 28px;
  color: var(--color-border); cursor: pointer;
  transition: color var(--transition-fast);
}
.star-btn.active, .star-btn:hover { color: #FFD700; }
.review-display .stars { font-size: 20px; color: #FFD700; margin-bottom: var(--space-2); }
.review-display p { color: var(--color-text-secondary); font-size: var(--font-size-sm); }

/* Chat */
.chat-card { padding: var(--space-6); border-radius: var(--radius-xl); }
.chat-card h3 { display: flex; align-items: center; gap: var(--space-2); font-size: var(--font-size-base); margin-bottom: var(--space-4); }
.chat-messages { max-height: 400px; overflow-y: auto; margin-bottom: var(--space-4); display: flex; flex-direction: column; gap: var(--space-3); padding: var(--space-2); }
.chat-empty { text-align: center; padding: var(--space-8); color: var(--color-text-muted); font-size: var(--font-size-sm); }
.chat-msg { display: flex; }
.chat-msg.mine { justify-content: flex-end; }
.msg-bubble {
  max-width: 75%; padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
/* Other person's messages: subtle distinct background */
.chat-msg:not(.mine) .msg-bubble {
  border-radius: 4px var(--radius-lg) var(--radius-lg) var(--radius-lg);
}
/* Own messages: solid primary-tinted background with strong contrast */
.chat-msg.mine .msg-bubble {
  background: var(--color-primary);
  border-color: var(--color-primary);
  border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg);
}
.chat-msg.mine .msg-sender { color: rgba(0,0,0,0.65); }
.chat-msg.mine .msg-bubble p { color: #000; }
.chat-msg.mine .msg-time { color: rgba(0,0,0,0.5); }

.msg-sender { font-size: var(--font-size-xs); font-weight: 600; color: var(--color-primary); display: block; margin-bottom: 2px; }
.msg-bubble p { font-size: var(--font-size-sm); margin: 0; }
.msg-time { font-size: 10px; color: var(--color-text-muted); margin-top: 2px; display: block; text-align: right; }

.chat-input-row { display: flex; gap: var(--space-2); }
.chat-input-row .form-input { flex: 1; }
.btn-send { padding: var(--space-3); flex-shrink: 0; }

/* Chat anti-disinter */
.chat-disclaimer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  margin-bottom: var(--space-3);
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #10b981;
  border-radius: var(--radius-md);
  font-size: 0.72rem;
}
.anti-disinter-warn {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: var(--space-2);
  padding: 8px 12px;
  background: rgba(232, 93, 74, 0.08);
  border: 1px solid rgba(232, 93, 74, 0.3);
  border-radius: 8px;
  color: #E85D4A;
  font-size: 0.78rem;
}
.form-input-warn { border-color: #E85D4A !important; }
.chat-msg.flagged .msg-bubble {
  border: 1px solid rgba(232, 93, 74, 0.3);
  background: rgba(232, 93, 74, 0.05);
}
.msg-flagged-tag {
  display: block;
  font-size: 10px;
  color: #E85D4A;
  margin-top: 4px;
  font-style: italic;
}

/* Header booking code */
.header-code {
  display: inline-block;
  font-family: 'Courier New', monospace;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 8px;
  margin-bottom: 6px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-primary);
  letter-spacing: 0.5px;
}

/* Countdown banner */
.countdown-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(193, 216, 47, 0.05));
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: var(--radius-lg);
}
.cd-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}
.cd-units { display: flex; gap: var(--space-4); }
.cd-unit { text-align: center; }
.cd-unit strong {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
}
.cd-unit span {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
}
.cd-escrow {
  font-size: 0.8rem;
  font-weight: 600;
  color: #10b981;
}
@media (max-width: 768px) {
  .countdown-banner { flex-direction: column; align-items: flex-start; gap: var(--space-2); }
}

/* Cancellation Modal */
.cancel-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-4);
}
.cancel-modal {
  width: 100%;
  max-width: 480px;
  padding: var(--space-6);
  border-radius: var(--radius-2xl);
}
.cancel-modal h3 {
  font-size: 1.25rem;
  margin-bottom: var(--space-2);
}
.cancel-policy-label {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-4);
}
.cancel-loading { padding: var(--space-6); text-align: center; color: var(--color-text-muted); }

.cancel-window-card {
  padding: var(--space-3) var(--space-4);
  background: rgba(232, 93, 74, 0.06);
  border: 1px solid rgba(232, 93, 74, 0.25);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}
.cancel-window-card strong {
  display: block;
  color: var(--color-text-primary);
  font-size: 0.95rem;
  margin-bottom: 2px;
}
.cancel-days {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin: 0;
}
.cancel-amounts {
  padding: var(--space-4);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}
.cancel-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  padding: 6px 0;
}
.cancel-row.total {
  padding-top: var(--space-3);
  margin-top: var(--space-2);
  border-top: 1px solid var(--color-border);
}
.cancel-refund {
  font-family: 'Poppins', sans-serif;
  font-size: 1.4rem;
  color: var(--color-primary);
}
.cancel-rate-note {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  margin-top: 6px;
  text-align: right;
}
.cancel-warning {
  font-size: 0.78rem;
  color: #E85D4A;
  padding: 8px 12px;
  background: rgba(232, 93, 74, 0.06);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}
.cancel-error {
  font-size: 0.85rem;
  color: #E85D4A;
  margin-bottom: var(--space-3);
}
.cancel-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Sidebar actions */
.actions-sidebar-card { display: flex; flex-direction: column; gap: var(--space-2); }
.btn-action {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-report { color: #f59e0b; }
.btn-report:hover { background: rgba(245,158,11,0.08); }

/* Modify modal */
.modify-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.modify-grid .form-group:first-child { grid-column: 1 / -1; }
.modify-note {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  padding: 8px 12px;
  background: rgba(245,158,11,0.06);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
  margin-top: var(--space-2);
}

/* Sidebar */
.detail-sidebar { display: flex; flex-direction: column; gap: var(--space-4); position: sticky; top: 100px; }
.sidebar-card { padding: var(--space-5); border-radius: var(--radius-xl); }
.sidebar-card h4 { font-size: var(--font-size-sm); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: var(--space-4); }

.person-info { display: flex; align-items: center; gap: var(--space-3); }
.person-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: var(--color-primary-ultra-light); color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: var(--font-size-lg);
}
.talent-level { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: 2px; }

.price-rows { display: flex; flex-direction: column; gap: var(--space-3); }
.price-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); }
.price-divider { height: 1px; background: var(--color-border); }
.text-primary { color: var(--color-primary); font-weight: 700; }
.text-success { color: var(--color-success); font-weight: 600; }
.text-warning { color: var(--color-warning); font-weight: 600; }

.payment-item { display: flex; justify-content: space-between; align-items: center; padding: var(--space-2) 0; border-bottom: 1px solid var(--color-border); }
.payment-item:last-child { border: none; }
.payment-type { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-left: var(--space-2); }

/* Status badges */
.status-badge { padding: 4px 12px; border-radius: 20px; font-size: var(--font-size-xs); font-weight: 600; white-space: nowrap; }
.status-info { background: rgba(100,149,237,0.15); color: #6495ed; }
.status-warning { background: var(--color-warning-light); color: var(--color-warning); }
.status-success { background: var(--color-success-light); color: var(--color-success); }
.status-error { background: rgba(232,93,74,0.15); color: var(--color-accent); }
.status-completed { background: rgba(193,216,47,0.15); color: var(--color-primary); }

/* Services Grid */
.services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-4); }
.service-item {
  background: var(--color-bg-elevated); border-radius: var(--radius-lg);
  padding: var(--space-4); border: 1px solid var(--color-border);
}
.service-header { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }
.service-icon { font-size: 20px; }
.service-details { display: flex; flex-direction: column; gap: var(--space-2); }
.service-detail-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); }
.info-card h3 { display: flex; align-items: center; gap: var(--space-2); }

.loading-state { padding: var(--space-8); }

@media (max-width: 900px) {
  .detail-layout { grid-template-columns: 1fr; }
  .detail-sidebar { position: static; }
  .info-grid { grid-template-columns: 1fr; }
}

/* ── Production Packs in booking detail ── */
.empty-mini { color: var(--color-text-muted); font-size: 0.9rem; display: flex; gap: 8px; align-items: center; }
.bp-list { display: flex; flex-direction: column; gap: 8px; }
.bp-row {
  display: grid;
  grid-template-columns: 40px 1fr auto auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}
.bp-thumb { width: 40px; height: 40px; border-radius: 8px; background: rgba(245,158,11,0.12); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; }
.bp-name { color: var(--color-text-primary); font-weight: 600; }
.bp-meta { color: var(--color-text-muted); font-size: 0.78rem; margin-top: 2px; }
.bp-price { color: var(--color-primary); font-weight: 700; }
.bp-remove {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
}
.bp-remove:hover { border-color: #ef4444; color: #ef4444; }
.bp-total {
  text-align: right;
  color: var(--color-text-muted);
  font-size: 0.9rem;
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-border);
}
.bp-total strong { color: var(--color-primary); font-size: 1.1rem; margin-left: 6px; }

.bp-picker-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.75);
  z-index: 1000;
  display: flex; align-items: flex-start; justify-content: center;
  padding: var(--space-6) var(--space-4);
  overflow-y: auto;
}
.bp-picker-modal {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  max-width: 560px;
  width: 100%;
}
.bp-picker-modal h3 { margin-bottom: var(--space-3); font-size: 1.15rem; }
.bp-picker-list { display: flex; flex-direction: column; gap: 6px; }
.bp-picker-row {
  display: grid;
  grid-template-columns: 40px 1fr auto auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  color: inherit;
  text-align: left;
}
.bp-picker-row:hover:not(:disabled) { border-color: var(--color-primary); background: rgba(193,216,47,0.04); }
.bp-picker-row:disabled { opacity: 0.5; cursor: not-allowed; }
.bp-picker-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bp-picker-info small { color: var(--color-text-muted); font-size: 0.78rem; }
.bp-picker-price { color: var(--color-primary); font-weight: 700; }
.bp-picker-tag { background: rgba(140,140,140,0.15); color: var(--color-text-muted); padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }
.bp-picker-recommended { border-color: #f59e0b; background: rgba(245,158,11,0.04); }
.bp-rec-badge {
  display: block;
  color: #f59e0b;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 2px;
}
.bp-picker-actions { display: flex; justify-content: flex-end; margin-top: var(--space-3); }
</style>
