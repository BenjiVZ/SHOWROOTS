<template>
  <div class="booking-page">
    <div class="container">
      <!-- Back link -->
      <router-link :to="`/talent/${talentId}`" class="back-link animate-fade-in-up">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al perfil
      </router-link>

      <div class="booking-layout animate-fade-in-up" style="animation-delay:0.1s">
        <!-- Left: Multi-step Form -->
        <div class="booking-form-section">
          <h1 class="section-title">Solicitar Reserva</h1>

          <!-- Stepper -->
          <div class="stepper">
            <div v-for="(s, i) in steps" :key="i"
              class="step"
              :class="{ active: currentStep === i, completed: currentStep > i }"
            >
              <div class="step-circle">
                <svg v-if="currentStep > i" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                <span v-else>{{ i + 1 }}</span>
              </div>
              <span class="step-label">{{ s.label }}</span>
            </div>
          </div>

          <form @submit.prevent="handleSubmit" class="booking-form">
            <!-- ═══════ STEP 0: Información del Evento ═══════ -->
            <transition name="step-slide" mode="out-in">
              <div v-if="currentStep === 0" key="step0" class="step-content">
                <h2 class="step-title">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  Información Básica
                </h2>

                <div class="form-group">
                  <label class="form-label">Tipo de Evento</label>
                  <div class="event-tiles">
                    <button v-for="t in eventTypeTiles" :key="t.value" type="button"
                      class="event-tile"
                      :class="{ selected: form.event_type === t.value }"
                      @click="form.event_type = t.value">
                      <span class="event-tile-icon" v-html="t.icon"></span>
                      <span class="event-tile-label">{{ t.label }}</span>
                    </button>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Nombre del Evento <span class="optional">(opcional)</span></label>
                  <input v-model="form.event_name" type="text" class="form-input" placeholder="Ej: Boda de María y Pedro">
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">Fecha del Evento</label>
                    <input v-model="form.event_date" type="date" class="form-input" :min="minDate" required>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Hora de Inicio</label>
                    <select
                      v-model="form.event_time_start"
                      class="form-input"
                      required
                      @change="onTimeStartChange"
                    >
                      <option value="" disabled>Elegí una hora</option>
                      <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">Hora Final</label>
                    <select
                      v-model="form.event_time_end"
                      class="form-input"
                      :disabled="!form.event_time_start"
                      @change="onTimeEndChange"
                    >
                      <option value="" disabled>
                        {{ form.event_time_start ? 'Elegí la hora de fin' : 'Primero elegí la hora de inicio' }}
                      </option>
                      <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">Duración rápida</label>
                    <div class="duration-chips">
                      <button type="button" v-for="h in [2,3,4,5,6]" :key="h"
                        class="chip" :class="{ active: selectedDuration === h }"
                        :disabled="!form.event_time_start"
                        @click="selectDuration(h)"
                      >{{ h }} h</button>
                      <button type="button" class="chip" :class="{ active: selectedDuration === 0 && !!form.event_time_end }"
                        :disabled="!form.event_time_start"
                        @click="selectDuration(0)">Personalizado</button>
                    </div>
                    <p v-if="!form.event_time_start" class="duration-hint">Elegí la hora de inicio para habilitar la duración.</p>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Ciudad del Evento</label>
                  <select v-model="form.event_city" class="form-input">
                    <option value="" disabled>Elegí la ciudad</option>
                    <option v-for="c in panamaCities" :key="c" :value="c">{{ c }}</option>
                  </select>
                  <CoverageMap
                    v-if="form.event_city"
                    :city="form.event_city"
                    :show-circle="false"
                    :hint-text="`${form.event_city}, Panamá`"
                  />
                </div>

                <div class="form-row">
                  <div class="form-group" style="flex:2">
                    <label class="form-label">Ubicación específica</label>
                    <input v-model="form.event_location" type="text" class="form-input" placeholder="Ej: Hotel Riu, Salón Bella Vista, Calle 50" required>
                  </div>
                  <div class="form-group" style="flex:1">
                    <label class="form-label">País</label>
                    <input value="Panamá" type="text" class="form-input input-locked" readonly disabled aria-readonly="true">
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label class="form-label">Invitados Aprox.</label>
                    <input v-model.number="form.guest_count" type="number" class="form-input" placeholder="150" min="1">
                  </div>
                  <div class="form-group">
                    <label class="form-label">Tipo de Espacio</label>
                    <div class="toggle-row">
                      <button type="button" class="toggle-btn" :class="{ active: form.event_indoor }" @click="form.event_indoor = true">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/></svg>
                        Interior
                      </button>
                      <button type="button" class="toggle-btn" :class="{ active: !form.event_indoor }" @click="form.event_indoor = false">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/></svg>
                        Exterior
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- ═══════ STEP 1: Detalles del Servicio ═══════ -->
              <div v-else-if="currentStep === 1" key="step1" class="step-content">
                <h2 class="step-title">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                  Detalles del Servicio
                </h2>

                <div class="form-group">
                  <label class="form-label">Género Musical / Ambiente</label>
                  <div class="genre-chips">
                    <button type="button" v-for="g in genres" :key="g"
                      class="chip" :class="{ active: form.genre_preference === g }"
                      @click="form.genre_preference = g"
                    >{{ g }}</button>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Descripción del Evento</label>
                  <textarea v-model="form.description" class="form-input form-textarea" rows="4"
                    :class="{ 'form-input-warn': descViolations.length }"
                    placeholder="Describe qué tipo de ambiente buscas, requerimientos especiales, etc."></textarea>
                  <p v-if="descViolationMsg" class="anti-disinter-warn">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    {{ descViolationMsg }}
                  </p>
                </div>

                <div class="form-group">
                  <label class="form-label">Presupuesto Estimado <span class="optional">(opcional)</span></label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">$</span>
                    <input v-model.number="form.budget" type="number" class="form-input" placeholder="0.00" min="0" step="0.01">
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Mensaje al Talento <span class="optional">(opcional)</span></label>
                  <textarea v-model="form.client_notes" class="form-input form-textarea" rows="2"
                    placeholder="Algo más que quieras comunicar..."></textarea>
                </div>
              </div>

              <!-- ═══════ STEP 2: Servicios Adicionales ═══════ -->
              <div v-else-if="currentStep === 2" key="step2" class="step-content">
                <h2 class="step-title">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                  Producción Adicional
                </h2>
                <p class="step-subtitle">Selecciona los servicios extra que necesites para tu evento</p>

                <div class="services-grid">
                  <button type="button" v-for="svc in availableServices" :key="svc.id"
                    class="service-card"
                    :class="{ active: isServiceSelected(svc.id) }"
                    @click="toggleService(svc.id)"
                  >
                    <div class="svc-icon" v-html="svc.icon"></div>
                    <span class="svc-name">{{ svc.name }}</span>
                    <div class="svc-check">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                  </button>
                </div>

                <!-- Dynamic Questions per Service -->
                <div v-if="selectedServices.length > 0" class="dynamic-questions">
                  <!-- SOUND -->
                  <div v-if="isServiceSelected('sound')" class="svc-detail glass">
                    <h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>
                      Detalles de Sonido
                    </h4>
                    <div class="form-group">
                      <label class="form-label">¿Para cuántas personas?</label>
                      <select v-model="serviceDetails.sound.capacity" class="form-input">
                        <option value="">Seleccionar...</option>
                        <option value="small">Hasta 50 personas</option>
                        <option value="medium">50 - 150 personas</option>
                        <option value="large">150 - 500 personas</option>
                        <option value="xlarge">500+ personas</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label class="form-label">¿Necesita micrófono?</label>
                      <div class="toggle-row">
                        <button type="button" class="toggle-btn sm" :class="{ active: serviceDetails.sound.microphone }" @click="serviceDetails.sound.microphone = true">Sí</button>
                        <button type="button" class="toggle-btn sm" :class="{ active: !serviceDetails.sound.microphone }" @click="serviceDetails.sound.microphone = false">No</button>
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">Tipo de refuerzo</label>
                      <div class="toggle-row">
                        <button type="button" class="toggle-btn sm" :class="{ active: serviceDetails.sound.level === 'basic' }" @click="serviceDetails.sound.level = 'basic'">Básico</button>
                        <button type="button" class="toggle-btn sm" :class="{ active: serviceDetails.sound.level === 'pro' }" @click="serviceDetails.sound.level = 'pro'">Profesional</button>
                      </div>
                    </div>
                  </div>

                  <!-- LIGHTS -->
                  <div v-if="isServiceSelected('lights')" class="svc-detail glass">
                    <h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 00-4 12.7c.7.6 1 1.5 1 2.3v1h6v-1c0-.8.3-1.7 1-2.3A7 7 0 0012 2z"/></svg>
                      Detalles de Iluminación
                    </h4>
                    <div class="form-group">
                      <label class="form-label">Tipo de iluminación</label>
                      <div class="genre-chips">
                        <button type="button" v-for="t in ['Ambiental','Fiesta','Arquitectónica','Moving Heads']" :key="t"
                          class="chip sm" :class="{ active: serviceDetails.lights.type === t }"
                          @click="serviceDetails.lights.type = t"
                        >{{ t }}</button>
                      </div>
                    </div>
                    <div class="form-group">
                      <label class="form-label">¿Decorativa o de show?</label>
                      <div class="toggle-row">
                        <button type="button" class="toggle-btn sm" :class="{ active: serviceDetails.lights.purpose === 'decorative' }" @click="serviceDetails.lights.purpose = 'decorative'">Decorativa</button>
                        <button type="button" class="toggle-btn sm" :class="{ active: serviceDetails.lights.purpose === 'show' }" @click="serviceDetails.lights.purpose = 'show'">Show</button>
                      </div>
                    </div>
                  </div>

                  <!-- DJ BOOTH -->
                  <div v-if="isServiceSelected('booth')" class="svc-detail glass">
                    <h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/></svg>
                      Tipo de DJ Booth
                    </h4>
                    <div class="genre-chips">
                      <button type="button" v-for="t in ['Estándar','Blanco','Con Branding','Con Pantalla']" :key="t"
                        class="chip sm" :class="{ active: serviceDetails.booth.type === t }"
                        @click="serviceDetails.booth.type = t"
                      >{{ t }}</button>
                    </div>
                  </div>

                  <!-- SCREENS -->
                  <div v-if="isServiceSelected('screens')" class="svc-detail glass">
                    <h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                      Pantallas / Visuales
                    </h4>
                    <div class="form-group">
                      <label class="form-label">¿Tiene contenido propio?</label>
                      <div class="toggle-row">
                        <button type="button" class="toggle-btn sm" :class="{ active: serviceDetails.screens.hasContent }" @click="serviceDetails.screens.hasContent = true">Sí, tengo contenido</button>
                        <button type="button" class="toggle-btn sm" :class="{ active: !serviceDetails.screens.hasContent }" @click="serviceDetails.screens.hasContent = false">Necesito apoyo</button>
                      </div>
                    </div>
                  </div>

                  <!-- TECHNICIAN -->
                  <div v-if="isServiceSelected('technician')" class="svc-detail glass">
                    <h4>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
                      Soporte Técnico
                    </h4>
                    <div class="form-group">
                      <label class="form-label">¿Horario especial de montaje?</label>
                      <input v-model="serviceDetails.technician.schedule" type="text" class="form-input" placeholder="Ej: Montaje desde las 2pm">
                    </div>
                  </div>
                </div>

                <div class="form-group" style="margin-top: var(--space-4)">
                  <label class="form-label">Notas sobre producción <span class="optional">(opcional)</span></label>
                  <textarea v-model="form.additional_services_notes" class="form-input form-textarea" rows="2"
                    placeholder="Detalles adicionales sobre los servicios..."></textarea>
                </div>
              </div>

              <!-- ═══════ STEP 3: Datos Partner / Resumen ═══════ -->
              <div v-else-if="currentStep === 3" key="step3" class="step-content">
                <h2 class="step-title">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  Resumen de Solicitud
                </h2>

                <!-- Partner: Client Final Info -->
                <div v-if="auth.user?.role === 'partner'" class="partner-section">
                  <div class="partner-section-header">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2"/><circle cx="9" cy="7" r="4"/>
                      <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
                    </svg>
                    <span>Datos del Cliente Final</span>
                  </div>
                  <div class="form-row">
                    <div class="form-group" style="flex:2">
                      <label class="form-label">Nombre del Cliente</label>
                      <input v-model="form.client_final_name" type="text" class="form-input" placeholder="Nombre completo del cliente">
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label class="form-label">Email</label>
                      <input v-model="form.client_final_email" type="email" class="form-input" placeholder="email@ejemplo.com">
                    </div>
                    <div class="form-group">
                      <label class="form-label">Teléfono / WhatsApp</label>
                      <input v-model="form.client_final_phone" type="tel" class="form-input" placeholder="+58 412...">
                    </div>
                  </div>
                </div>

                <!-- Summary Cards -->
                <div class="summary-grid">
                  <div class="summary-item glass">
                    <span class="summary-label">Evento</span>
                    <span class="summary-value">{{ eventTypeLabels[form.event_type] || form.event_type }}</span>
                  </div>
                  <div class="summary-item glass">
                    <span class="summary-label">Fecha</span>
                    <span class="summary-value">{{ formatDate(form.event_date) }}</span>
                  </div>
                  <div class="summary-item glass">
                    <span class="summary-label">Hora</span>
                    <span class="summary-value">{{ form.event_time_start }} — {{ computedEndTime }}</span>
                  </div>
                  <div class="summary-item glass">
                    <span class="summary-label">Duración</span>
                    <span class="summary-value">{{ durationHours }}h</span>
                  </div>
                  <div class="summary-item glass">
                    <span class="summary-label">Ubicación</span>
                    <span class="summary-value">{{ form.event_location }}{{ form.event_city ? ', ' + form.event_city : '' }}</span>
                  </div>
                  <div class="summary-item glass">
                    <span class="summary-label">Espacio</span>
                    <span class="summary-value">{{ form.event_indoor ? 'Interior' : 'Exterior' }}</span>
                  </div>
                  <div v-if="form.genre_preference" class="summary-item glass">
                    <span class="summary-label">Género</span>
                    <span class="summary-value">{{ form.genre_preference }}</span>
                  </div>
                  <div v-if="form.guest_count" class="summary-item glass">
                    <span class="summary-label">Invitados</span>
                    <span class="summary-value">~{{ form.guest_count }}</span>
                  </div>
                </div>

                <!-- Services Summary -->
                <div v-if="selectedServices.length > 0" class="services-summary glass">
                  <h4>Servicios Adicionales</h4>
                  <div class="svc-tags">
                    <span v-for="svc in selectedServices" :key="svc" class="svc-tag">
                      {{ availableServices.find(s => s.id === svc)?.name }}
                    </span>
                  </div>
                </div>

                <div v-if="form.description" class="desc-summary glass">
                  <h4>Descripción</h4>
                  <p>{{ form.description }}</p>
                </div>
              </div>
            </transition>

            <!-- Error -->
            <div v-if="error" class="error-msg">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              {{ error }}
            </div>

            <!-- Navigation Buttons -->
            <div class="step-nav">
              <button v-if="currentStep > 0" type="button" class="btn btn-ghost" @click="prevStep">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
                Anterior
              </button>
              <div v-else></div>

              <button v-if="currentStep < steps.length - 1" type="button" class="btn btn-primary" @click="nextStep">
                Siguiente
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
              </button>
              <button v-else type="submit" class="btn btn-primary btn-lg" :disabled="submitting">
                <span v-if="submitting" class="spinner"></span>
                <span v-else>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
                  Enviar Solicitud
                </span>
              </button>
            </div>
          </form>
        </div>

        <!-- Right: Sticky Summary -->
        <div class="booking-summary">
          <div class="summary-card glass">
            <h3>Resumen</h3>
            <div v-if="talent" class="talent-summary">
              <img :src="talent.cover_photo || defaultAvatar" :alt="talent.stage_name" class="talent-thumb">
              <div>
                <h4>{{ talent.stage_name }}</h4>
                <span class="badge" :class="talent.talent_level === 'premium' ? 'badge-accent' : ''">
                  {{ talent.talent_level === 'premium' ? '⭐ Premium' : 'Standard' }}
                </span>
              </div>
            </div>

            <div class="summary-divider"></div>

            <div class="price-breakdown">
              <div class="price-row" v-if="talent?.hourly_rate">
                <span>Tarifa por hora</span>
                <span>${{ talent.hourly_rate }}</span>
              </div>
              <div class="price-row" v-if="durationHours > 0">
                <span>Duración</span>
                <span>{{ durationHours }} hrs</span>
              </div>
              <div v-if="selectedServices.length > 0" class="price-row">
                <span>Servicios extras</span>
                <span>{{ selectedServices.length }} seleccionados</span>
              </div>
              <div class="summary-divider" v-if="estimatedPrice > 0"></div>
              <div class="price-row price-total" v-if="estimatedPrice > 0">
                <span>Precio Estimado</span>
                <span>${{ estimatedPrice.toFixed(2) }}</span>
              </div>
              <p class="price-note" v-if="estimatedPrice > 0">
                * El precio final puede variar. Los servicios adicionales se cotizan aparte.
              </p>
            </div>

            <div class="summary-divider"></div>

            <div class="how-it-works">
              <h4>¿Cómo funciona?</h4>
              <div class="step-item" v-for="(st, i) in howItWorks" :key="i">
                <div class="step-num">{{ i + 1 }}</div>
                <p>{{ st }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Success / Confirmation Modal -->
      <div v-if="showSuccess" class="modal-overlay" @click.self="goToDashboard">
        <div class="modal-card success-card glass animate-fade-in-up">
          <div class="success-icon">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h2>¡Solicitud Enviada!</h2>
          <p class="success-sub">Tu solicitud llegó a <strong>{{ talent?.stage_name }}</strong>. Te notificaremos cuando responda.</p>

          <div v-if="createdBooking?.booking_code" class="booking-code-block">
            <span class="code-label">Código de tu reserva</span>
            <code class="booking-code">{{ createdBooking.booking_code }}</code>
          </div>

          <div class="next-steps-list">
            <h4>¿Qué pasa ahora?</h4>
            <div v-for="(step, i) in nextStepsTimeline" :key="i" class="next-step-item">
              <div class="next-num">{{ i + 1 }}</div>
              <div class="next-text">
                <strong>{{ step.title }}</strong>
                <span>{{ step.desc }}</span>
              </div>
            </div>
          </div>

          <div class="trust-pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Pago protegido por Pulsar · Reembolso 100% si el talento no se presenta
          </div>

          <div class="modal-actions">
            <button @click="goToDashboard" class="btn btn-primary">Ver mis reservas</button>
            <router-link to="/search" class="btn btn-ghost">Seguir explorando</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import CoverageMap from '@/components/common/CoverageMap.vue'
import { scan as antiScan, violationsMessage } from '@/utils/antiDisinter'

// Ciudades de Panamá (mismas del onboarding / CoverageMap)
const panamaCities = [
  'Ciudad de Panamá', 'San Miguelito', 'David', 'Colón', 'Santiago', 'Chitré',
  'Penonomé', 'Aguadulce', 'La Chorrera', 'Arraiján', 'Bocas del Toro', 'Las Tablas',
]

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const talentId = route.params.id
const talent = ref(null)
const error = ref('')
const submitting = ref(false)
const showSuccess = ref(false)
const createdBooking = ref(null)
const currentStep = ref(0)
const selectedDuration = ref(3)

const defaultAvatar = `data:image/svg+xml,${encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80"><rect fill="%23111" width="80" height="80"/><circle cx="40" cy="30" r="14" fill="%23C1D82F" opacity="0.3"/><ellipse cx="40" cy="62" rx="22" ry="14" fill="%23C1D82F" opacity="0.2"/></svg>')}`

const steps = [
  { label: 'Evento' },
  { label: 'Servicio' },
  { label: 'Producción' },
  { label: 'Resumen' },
]

const genres = ['House', 'Open Format', 'Reggaetón', 'Lounge', 'Afro House', 'Comercial', 'Latin', 'Tech House', 'Otro']

const availableServices = [
  { id: 'sound', name: 'Sonido', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 010 14.14"/><path d="M15.54 8.46a5 5 0 010 7.07"/></svg>' },
  { id: 'lights', name: 'Luces', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' },
  { id: 'booth', name: 'DJ Booth', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>' },
  { id: 'microphone', name: 'Micrófono', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>' },
  { id: 'screens', name: 'Pantallas', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>' },
  { id: 'ledfloor', name: 'Piso LED', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>' },
  { id: 'technician', name: 'Técnico', icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>' },
]

const eventTypeLabels = {
  wedding: 'Boda', corporate: 'Corporativo', birthday: 'Cumpleaños',
  rooftop: 'Rooftop', restaurant: 'Restaurante / Bar',
  private: 'Evento Privado', festival: 'Festival', other: 'Otro'
}

const howItWorks = [
  'Envías la solicitud',
  'El talento revisa y responde (48h)',
  'Recibes la propuesta final',
  'Pagas para confirmar',
]

const selectedServices = ref([])
const serviceDetails = reactive({
  sound: { capacity: '', microphone: false, level: 'basic' },
  lights: { type: '', purpose: 'decorative' },
  booth: { type: 'Estándar' },
  screens: { hasContent: false },
  technician: { schedule: '' },
})

const form = ref({
  event_type: '',
  event_name: '',
  event_date: '',
  event_time_start: '',
  event_time_end: '',
  event_location: '',
  event_city: 'Ciudad de Panamá',
  event_indoor: true,
  guest_count: null,
  genre_preference: '',
  description: '',
  budget: null,
  client_notes: '',
  additional_services: [],
  additional_services_notes: '',
  client_final_name: '',
  client_final_email: '',
  client_final_phone: '',
})

const minDate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
})

// Opciones de hora cada 30 min (valor 24h para la lógica, etiqueta 12h AM/PM)
const timeOptions = (() => {
  const opts = []
  for (let m = 0; m < 24 * 60; m += 30) {
    const h = Math.floor(m / 60)
    const mm = m % 60
    const value = `${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
    const h12 = h % 12 === 0 ? 12 : h % 12
    const ampm = h < 12 ? 'AM' : 'PM'
    const label = `${h12}:${String(mm).padStart(2, '0')} ${ampm}`
    opts.push({ value, label })
  }
  return opts
})()

function onTimeStartChange() {
  // Si había una duración preset activa, recalcular la hora final desde el nuevo inicio.
  if (form.value.event_time_start && selectedDuration.value > 0) {
    selectDuration(selectedDuration.value)
  }
}

function onTimeEndChange() {
  // El usuario eligió la hora final a mano → pasa a duración personalizada.
  selectedDuration.value = 0
}

function selectDuration(h) {
  selectedDuration.value = h
  if (h > 0 && form.value.event_time_start) {
    const [sh, sm] = form.value.event_time_start.split(':').map(Number)
    let endM = sh * 60 + sm + h * 60
    if (endM >= 24 * 60) endM -= 24 * 60
    const eh = Math.floor(endM / 60)
    const em = endM % 60
    form.value.event_time_end = `${String(eh).padStart(2,'0')}:${String(em).padStart(2,'0')}`
  }
}

const computedEndTime = computed(() => {
  if (selectedDuration.value > 0 && form.value.event_time_start) {
    const [sh, sm] = form.value.event_time_start.split(':').map(Number)
    let endM = sh * 60 + sm + selectedDuration.value * 60
    if (endM >= 24 * 60) endM -= 24 * 60
    const eh = Math.floor(endM / 60)
    const em = endM % 60
    return `${String(eh).padStart(2,'0')}:${String(em).padStart(2,'0')}`
  }
  return form.value.event_time_end || '--:--'
})

const durationHours = computed(() => {
  if (selectedDuration.value > 0) return selectedDuration.value
  if (!form.value.event_time_start || !form.value.event_time_end) return 0
  const [sh, sm] = form.value.event_time_start.split(':').map(Number)
  const [eh, em] = form.value.event_time_end.split(':').map(Number)
  let diff = (eh * 60 + em) - (sh * 60 + sm)
  if (diff <= 0) diff += 24 * 60
  return Math.round((diff / 60) * 100) / 100
})

const estimatedPrice = computed(() => {
  if (!talent.value?.hourly_rate || durationHours.value <= 0) return 0
  return parseFloat(talent.value.hourly_rate) * durationHours.value
})

function isServiceSelected(id) { return selectedServices.value.includes(id) }
function toggleService(id) {
  const i = selectedServices.value.indexOf(id)
  if (i >= 0) selectedServices.value.splice(i, 1)
  else selectedServices.value.push(id)
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d + 'T12:00:00').toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric' })
}

function validateStep(step) {
  if (step === 0) {
    if (!form.value.event_type) { error.value = 'Selecciona el tipo de evento.'; return false }
    if (!form.value.event_date) { error.value = 'Selecciona la fecha.'; return false }
    if (!form.value.event_time_start) {
      error.value = 'Selecciona la hora de inicio.'
      return false
    }
    if (!form.value.event_time_end) {
      error.value = 'Selecciona la hora final (o elegí una duración rápida).'
      return false
    }
    if (!form.value.event_location) { error.value = 'Ingresa la ubicación.'; return false }
  }
  return true
}

function nextStep() {
  error.value = ''
  if (!validateStep(currentStep.value)) return
  currentStep.value++
}
function prevStep() { currentStep.value--; error.value = '' }

// Helpers de draft persistence (sobreviven login/registro)
const DRAFT_KEY = 'booking_draft'

function snapshotDraft() {
  return {
    talentId: String(talentId),
    form: form.value,
    selectedServices: selectedServices.value,
    serviceDetails: { ...serviceDetails },
    selectedDuration: selectedDuration.value,
    currentStep: currentStep.value,
    savedAt: Date.now(),
  }
}

function persistDraft() {
  // No guardar si el usuario ya está logueado (el draft solo aplica al flujo "registrate para enviar").
  if (auth.isLoggedIn) return
  try {
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify(snapshotDraft()))
  } catch { /* quota / private mode — silent */ }
}

function restoreDraftIfMatches() {
  const raw = sessionStorage.getItem(DRAFT_KEY)
  if (!raw) return false
  try {
    const saved = JSON.parse(raw)
    if (String(saved.talentId) !== String(talentId)) return false  // Draft de otro talento — ignorar
    if (saved.form) Object.assign(form.value, saved.form)
    if (Array.isArray(saved.selectedServices)) selectedServices.value = saved.selectedServices
    if (saved.serviceDetails) Object.assign(serviceDetails, saved.serviceDetails)
    if (saved.selectedDuration) selectedDuration.value = saved.selectedDuration
    if (saved.currentStep != null) currentStep.value = saved.currentStep
    return true
  } catch {
    return false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/talents/${talentId}/`)
    talent.value = data
  } catch {
    error.value = 'No se pudo cargar la información del talento.'
  }

  // Restaurar borrador si pertenece a este talento
  const restored = restoreDraftIfMatches()
  if (restored && auth.isLoggedIn) {
    // Si el usuario llegó ya logueado con un draft restaurado, ya no hace falta — lo limpiamos.
    sessionStorage.removeItem(DRAFT_KEY)
  }
})

// Auto-guardar borrador (con debounce) mientras el usuario edita y no está logueado.
// Cubre el caso de navegar al navbar para registrarse sin haber hecho submit.
let saveTimer = null
function scheduleDraftSave() {
  if (auth.isLoggedIn) return
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(persistDraft, 400)
}
watch(
  () => [form.value, selectedServices.value, serviceDetails, selectedDuration.value, currentStep.value],
  scheduleDraftSave,
  { deep: true }
)

// Si el usuario se loguea durante esta sesión, limpiar el draft (ya no se necesita).
watch(() => auth.isLoggedIn, (loggedIn) => {
  if (loggedIn) {
    if (saveTimer) clearTimeout(saveTimer)
    sessionStorage.removeItem(DRAFT_KEY)
  }
})

async function handleSubmit() {
  if (descViolations.value.length) {
    error.value = descViolationMsg.value
    return
  }
  if (!auth.isLoggedIn) {
    // Guardar borrador (talent_id incluido) y redirigir al login con redirect explícito
    persistDraft()
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  error.value = ''
  submitting.value = true

  try {
    // Build services array
    const services = selectedServices.value.map(id => ({
      service: id,
      details: serviceDetails[id] || {}
    }))

    // Compute end time if using preset duration
    let endTime = form.value.event_time_end
    if (selectedDuration.value > 0 && form.value.event_time_start) {
      endTime = computedEndTime.value
    }

    const payload = {
      talent: parseInt(talentId),
      event_type: form.value.event_type,
      event_name: form.value.event_name,
      event_date: form.value.event_date,
      event_time_start: form.value.event_time_start,
      event_time_end: endTime,
      event_duration_hours: durationHours.value,
      event_location: form.value.event_location,
      event_city: form.value.event_city,
      event_indoor: form.value.event_indoor,
      guest_count: form.value.guest_count || 0,
      genre_preference: form.value.genre_preference,
      description: form.value.description,
      budget: form.value.budget || null,
      client_notes: form.value.client_notes,
      additional_services: services,
      additional_services_notes: form.value.additional_services_notes,
    }
    if (auth.user?.role === 'partner') {
      payload.client_final_name = form.value.client_final_name
      payload.client_final_email = form.value.client_final_email
      payload.client_final_phone = form.value.client_final_phone
    }
    const { data } = await api.post('/bookings/create/', payload)
    createdBooking.value = data
    showSuccess.value = true
  } catch (e) {
    const data = e.response?.data
    if (data) {
      const msgs = Object.values(data).flat()
      error.value = msgs.join(' ')
    } else {
      error.value = 'Error al enviar la solicitud. Intenta de nuevo.'
    }
  } finally {
    submitting.value = false
  }
}

const eventTypeTiles = [
  // Boda — anillos
  { value: 'wedding', label: 'Boda', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="15" r="5"/><circle cx="16" cy="15" r="5"/><path d="M7 9l2-5h6l2 5"/></svg>' },
  // Corporativo — edificio
  { value: 'corporate', label: 'Corporativo', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="1"/><line x1="9" y1="7" x2="9" y2="7.01"/><line x1="13" y1="7" x2="13" y2="7.01"/><line x1="9" y1="11" x2="9" y2="11.01"/><line x1="13" y1="11" x2="13" y2="11.01"/><line x1="9" y1="15" x2="9" y2="15.01"/><line x1="13" y1="15" x2="13" y2="15.01"/></svg>' },
  // Cumpleaños — torta con velita
  { value: 'birthday', label: 'Cumpleaños', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-8a2 2 0 00-2-2H6a2 2 0 00-2 2v8"/><path d="M4 16s1.5-2 4-2 3.5 2 4 2 1.5-2 4-2 4 2 4 2"/><line x1="2" y1="21" x2="22" y2="21"/><line x1="12" y1="4" x2="12" y2="11"/><path d="M10.5 4.5C10.5 3 12 2 12 2s1.5 1 1.5 2.5a1.5 1.5 0 01-3 0z"/></svg>' },
  // Privado — copas brindando
  { value: 'private', label: 'Privado', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M8 22h8"/><path d="M12 11v11"/><path d="M19 3l-7 8-7-8"/><path d="M5 3h14"/></svg>' },
  // Festival — carpa
  { value: 'festival', label: 'Festival', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20h20"/><path d="M12 3L4 20"/><path d="M12 3l8 17"/><path d="M12 3v17"/><path d="M9 20l3-6 3 6"/></svg>' },
  // Rooftop — skyline nocturno
  { value: 'rooftop', label: 'Rooftop', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21V11l4-2v12"/><path d="M7 21V7l5-2v16"/><path d="M12 21V9l5 2v10"/><path d="M17 21v-8l4 2v6"/><circle cx="18" cy="5" r="1"/></svg>' },
  // Restaurante — copa de cóctel
  { value: 'restaurant', label: 'Restaurante', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3h14l-7 9z"/><path d="M12 12v9"/><path d="M8 21h8"/><circle cx="16" cy="6" r="0.8" fill="currentColor"/></svg>' },
  // Otro — chispa / sparkles
  { value: 'other', label: 'Otro', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/><path d="M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z"/><path d="M5 14l.6 1.4L7 16l-1.4.6L5 18l-.6-1.4L3 16l1.4-.6z"/></svg>' },
]

const nextStepsTimeline = [
  { title: 'Pago confirmado', desc: 'Cuando el talento acepte, recibirás el link para pagar a Pulsar (no al talento).' },
  { title: 'El talento revisa', desc: 'Tiene hasta 48 horas para enviarte una propuesta personalizada.' },
  { title: 'Coordinación previa', desc: 'Chat in-app para confirmar setlist, setup y detalles del evento.' },
  { title: 'Día del evento', desc: 'El talento se presenta. Si no llega, te reembolsamos 100%.' },
  { title: 'Liberación del pago', desc: '24h después del evento, se libera el pago al talento y dejas tu reseña.' },
]

// Anti-desintermediación en descripción
const descViolations = ref([])
watch(() => form.value.description, (val) => {
  descViolations.value = antiScan(val || '')
})
const descViolationMsg = computed(() => violationsMessage(descViolations.value))

function goToDashboard() {
  router.push(auth.user?.role === 'partner' ? '/partner' : '/dashboard')
}
</script>

<style scoped>
.booking-page {
  padding-top: var(--space-4);
  min-height: 100vh;
  padding-bottom: var(--space-16);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-6);
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--color-primary); }

.booking-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: var(--space-10);
  align-items: start;
}

/* ── Stepper ── */
.stepper {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-8);
  position: relative;
}
.stepper::before {
  content: '';
  position: absolute;
  top: 16px;
  left: 32px;
  right: 32px;
  height: 2px;
  background: var(--color-border);
  z-index: 0;
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  position: relative;
  z-index: 1;
}
.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-bg-elevated);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--color-text-muted);
  transition: all var(--transition-normal);
}
.step.active .step-circle {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: var(--color-bg-primary);
}
.step.completed .step-circle {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: var(--color-bg-primary);
}
.step-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: 500;
}
.step.active .step-label { color: var(--color-primary); font-weight: 600; }
.step.completed .step-label { color: var(--color-text-secondary); }

/* ── Step Content Transitions ── */
.step-slide-enter-active,
.step-slide-leave-active {
  transition: all 0.3s ease;
}
.step-slide-enter-from { opacity: 0; transform: translateX(30px); }
.step-slide-leave-to { opacity: 0; transform: translateX(-30px); }

/* ── Step Content ── */
.step-content { display: flex; flex-direction: column; gap: var(--space-5); }
.step-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-xl);
  color: var(--color-primary);
  margin-bottom: var(--space-2);
}
.step-subtitle { color: var(--color-text-muted); font-size: var(--font-size-sm); margin-top: -var(--space-3); }

/* ── Form Elements ── */
.booking-form { display: flex; flex-direction: column; gap: var(--space-5); }
.form-group { display: flex; flex-direction: column; gap: var(--space-2); }
.form-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-secondary); }
.optional { font-weight: 400; color: var(--color-text-muted); }

.form-input {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
  font-family: var(--font-body);
}
.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-ultra-light);
}
.form-textarea { resize: vertical; min-height: 80px; }
select.form-input { cursor: pointer; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--space-4); }

.input-with-prefix { position: relative; }
.input-prefix {
  position: absolute; left: var(--space-4); top: 50%;
  transform: translateY(-50%); color: var(--color-text-muted); font-weight: 600;
}
.input-with-prefix .form-input { padding-left: var(--space-8); }

/* ── Duration Chips / Genre Chips ── */
.duration-chips, .genre-chips {
  display: flex; flex-wrap: wrap; gap: var(--space-2);
}
.chip {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-body);
}
.chip:hover { border-color: var(--color-primary); color: var(--color-primary); }
.chip.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-bg-primary);
  font-weight: 600;
}
.chip.sm { padding: var(--space-1) var(--space-3); font-size: var(--font-size-xs); }
.chip:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  border-color: var(--color-border);
  color: var(--color-text-muted);
}
.chip:disabled:hover { border-color: var(--color-border); color: var(--color-text-muted); }
.duration-hint { margin: var(--space-2) 0 0; font-size: var(--font-size-xs); color: var(--color-text-muted); }
select.form-input:disabled { opacity: 0.5; cursor: not-allowed; }
.input-locked { opacity: 0.7; cursor: not-allowed; border-style: dashed; }

/* ── Toggle Row ── */
.toggle-row { display: flex; gap: var(--space-2); }
.toggle-btn {
  flex: 1; padding: var(--space-3);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex; align-items: center; justify-content: center; gap: var(--space-2);
  font-family: var(--font-body);
}
.toggle-btn.active {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-ultra-light);
}
.toggle-btn.sm { padding: var(--space-2) var(--space-3); }

/* ── Services Grid ── */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-3);
}
.service-card {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-2); padding: var(--space-4);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  font-family: var(--font-body);
}
.service-card:hover { border-color: var(--color-primary); transform: translateY(-2px); }
.service-card.active {
  border-color: var(--color-primary);
  background: var(--color-primary-ultra-light);
}
.svc-icon { color: var(--color-text-muted); }
.service-card.active .svc-icon { color: var(--color-primary); }
.svc-name { font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-secondary); }
.service-card.active .svc-name { color: var(--color-primary); }
.svc-check {
  position: absolute; top: 6px; right: 6px;
  width: 20px; height: 20px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-bg-primary);
  display: none; align-items: center; justify-content: center;
}
.service-card.active .svc-check { display: flex; }

/* ── Dynamic Service Questions ── */
.dynamic-questions { display: flex; flex-direction: column; gap: var(--space-4); margin-top: var(--space-4); }
.svc-detail {
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  display: flex; flex-direction: column; gap: var(--space-4);
}
.svc-detail h4 { font-size: var(--font-size-base); margin-bottom: var(--space-1); }

/* ── Summary Grid ── */
.summary-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}
.summary-item {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  display: flex; flex-direction: column; gap: 2px;
}
.summary-label { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.summary-value { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-primary); }

.services-summary, .desc-summary {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-top: var(--space-3);
}
.services-summary h4, .desc-summary h4 {
  font-size: var(--font-size-sm); color: var(--color-text-muted); margin-bottom: var(--space-3);
}
.svc-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.svc-tag {
  padding: var(--space-1) var(--space-3);
  background: var(--color-primary-ultra-light);
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: 600;
}
.desc-summary p { font-size: var(--font-size-sm); color: var(--color-text-secondary); }

/* ── Navigation ── */
.step-nav {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}

/* ── Error Message ── */
.error-msg {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: rgba(232,93,74,0.1);
  border: 1px solid rgba(232,93,74,0.3);
  border-radius: var(--radius-lg);
  color: var(--color-accent);
  font-size: var(--font-size-sm);
}

.spinner {
  width: 20px; height: 20px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Right Sidebar ── */
.booking-summary { position: sticky; top: 100px; }
.summary-card {
  padding: var(--space-6);
  border-radius: var(--radius-xl);
}
.summary-card h3 { font-size: var(--font-size-lg); margin-bottom: var(--space-5); }

.talent-summary { display: flex; align-items: center; gap: var(--space-4); }
.talent-thumb {
  width: 56px; height: 56px;
  border-radius: var(--radius-lg);
  object-fit: cover;
  background: var(--color-bg-elevated);
}
.talent-summary h4 { font-size: var(--font-size-base); margin-bottom: var(--space-1); }

.summary-divider { height: 1px; background: var(--color-border); margin: var(--space-4) 0; }

.price-breakdown { display: flex; flex-direction: column; gap: var(--space-3); }
.price-row {
  display: flex; justify-content: space-between;
  font-size: var(--font-size-sm); color: var(--color-text-secondary);
}
.price-total {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-primary);
}
.price-note { font-size: var(--font-size-xs); color: var(--color-text-muted); font-style: italic; }

.how-it-works h4 { font-size: var(--font-size-sm); margin-bottom: var(--space-4); color: var(--color-text-muted); }
.step-item { display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-3); }
.step-num {
  width: 28px; height: 28px;
  background: var(--color-primary-ultra-light);
  color: var(--color-primary);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--font-size-xs); font-weight: 700; flex-shrink: 0;
}
.step-item p { font-size: var(--font-size-sm); color: var(--color-text-secondary); }

/* ── Success Modal ── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: var(--space-6);
}
.modal-card {
  max-width: 440px; width: 100%;
  padding: var(--space-10);
  border-radius: var(--radius-2xl);
  text-align: center;
}
.success-icon { color: var(--color-primary); margin-bottom: var(--space-4); }
.modal-card h2 { margin-bottom: var(--space-3); }
.modal-card p { color: var(--color-text-secondary); margin-bottom: var(--space-4); }
.expire-note { font-size: var(--font-size-sm); color: var(--color-primary); font-weight: 600; margin-bottom: var(--space-6); }
.modal-actions { display: flex; flex-direction: column; gap: var(--space-3); }

/* Success card (confirmación con booking_code + timeline) */
.success-card {
  max-width: 520px;
  padding: var(--space-8) var(--space-6);
  text-align: left;
}
.success-card .success-icon { display: flex; justify-content: center; }
.success-card h2 { text-align: center; }
.success-sub { text-align: center; }
.booking-code-block {
  text-align: center;
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
  margin: var(--space-4) 0 var(--space-6);
}
.code-label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  margin-bottom: 6px;
}
.booking-code {
  font-family: 'Courier New', monospace;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 1px;
}
.next-steps-list { margin-bottom: var(--space-5); }
.next-steps-list h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: var(--space-3);
  color: var(--color-text-primary);
}
.next-step-item {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  margin-bottom: var(--space-3);
}
.next-num {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: rgba(193,216,47,0.15);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.78rem;
}
.next-text strong {
  display: block;
  font-size: 0.85rem;
  color: var(--color-text-primary);
}
.next-text span {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}
.trust-pill {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: var(--space-5);
}

/* Anti-desintermediación warning */
.anti-disinter-warn {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 8px 12px;
  background: rgba(232, 93, 74, 0.08);
  border: 1px solid rgba(232, 93, 74, 0.3);
  border-radius: 8px;
  color: #E85D4A;
  font-size: 0.78rem;
}
.form-input-warn { border-color: #E85D4A !important; }

/* Event type tiles (Pantalla 1 del mockup) */
.event-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: var(--space-2);
}
.event-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: var(--space-4) var(--space-2);
  background: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
}
.event-tile:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
}
.event-tile.selected {
  border-color: var(--color-primary);
  background: rgba(193,216,47,0.06);
  color: var(--color-primary);
}
.event-tile-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: var(--color-text-secondary);
  transition: color var(--transition-fast);
}
.event-tile:hover .event-tile-icon { color: var(--color-text-primary); }
.event-tile.selected .event-tile-icon { color: var(--color-primary); }
.event-tile-label {
  font-size: 0.82rem;
  font-weight: 500;
}

/* ── Partner Section ── */
.partner-section {
  display: flex; flex-direction: column; gap: var(--space-4);
  padding: var(--space-5);
  border: 1px solid rgba(163, 190, 140, 0.3);
  border-radius: var(--radius-xl);
  background: rgba(163, 190, 140, 0.05);
  margin-bottom: var(--space-4);
}
.partner-section-header {
  display: flex; align-items: center; gap: var(--space-3);
  font-weight: 600; font-size: var(--font-size-sm); color: var(--color-primary-light);
}

@media (max-width: 900px) {
  .booking-layout { grid-template-columns: 1fr; }
  .booking-summary { position: static; order: -1; }
  .summary-grid { grid-template-columns: 1fr; }
  .services-grid { grid-template-columns: repeat(3, 1fr); }
  .stepper { gap: 0; }
  .step-label { font-size: 10px; }
}

@media (max-width: 500px) {
  .services-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
