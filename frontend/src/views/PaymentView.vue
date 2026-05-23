<template>
  <div class="payment-page">
    <div class="container">
      <router-link :to="`/dashboard/bookings/${bookingId}`" class="back-link">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        Volver al booking
      </router-link>

      <div v-if="loading" class="loading-state">Cargando booking...</div>

      <div v-else-if="booking" class="payment-layout">
        <!-- Left: Payment flow -->
        <div class="payment-main">
          <!-- Trust hero -->
          <div class="trust-hero">
            <div class="trust-hero-icon">
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <div>
              <h1>Tu pago está protegido por Pulsar</h1>
              <p>El dinero queda en custodia. Solo lo liberamos 24h después de tu evento.</p>
            </div>
          </div>

          <!-- Escrow timeline 3 pasos -->
          <div class="escrow-timeline-card">
            <div class="escrow-stage">
              <div class="es-num">1</div>
              <div class="es-icon">💳</div>
              <strong>Hoy</strong>
              <span>Pagas a <strong>Pulsar</strong>, no al talento.</span>
            </div>
            <div class="es-line"></div>
            <div class="escrow-stage active">
              <div class="es-num active">2</div>
              <div class="es-icon">🛡</div>
              <strong>En custodia</strong>
              <span><strong>${{ totalToPay.toFixed(2) }}</strong> protegidos hasta el evento.</span>
            </div>
            <div class="es-line"></div>
            <div class="escrow-stage">
              <div class="es-num">3</div>
              <div class="es-icon">✓</div>
              <strong>24h post-evento</strong>
              <span>Liberación al talento. Si no se presenta: <strong>reembolso 100%</strong>.</span>
            </div>
          </div>

          <!-- Métodos de pago tiles -->
          <section class="payment-section">
            <h2 class="section-title">Método de pago</h2>
            <div class="payment-methods">
              <button
                v-for="m in paymentMethods" :key="m.key"
                type="button"
                class="payment-method-tile"
                :class="{ selected: selectedMethod === m.key }"
                @click="selectedMethod = m.key"
              >
                <div class="pm-icon" v-html="m.icon"></div>
                <div class="pm-text">
                  <strong>{{ m.label }}</strong>
                  <span>{{ m.desc }}</span>
                </div>
                <div class="pm-radio">
                  <span v-if="selectedMethod === m.key" class="pm-radio-dot"></span>
                </div>
              </button>
            </div>

            <!-- Card form (placeholder hasta Stripe) -->
            <div v-if="selectedMethod === 'card'" class="card-form">
              <p class="stripe-notice">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                Procesado por Stripe — PCI-DSS Level 1
              </p>
              <div class="form-group">
                <label>Número de tarjeta</label>
                <input type="text" placeholder="•••• •••• •••• ••••" class="input-field" disabled />
              </div>
              <div class="card-row">
                <div class="form-group">
                  <label>Expira</label>
                  <input type="text" placeholder="MM/AA" class="input-field" disabled />
                </div>
                <div class="form-group">
                  <label>CVC</label>
                  <input type="text" placeholder="•••" class="input-field" disabled />
                </div>
              </div>
              <p class="stripe-pending">⚠ Stripe Connect aún no configurado en este entorno. Usa "Marcar como pagado" para simular.</p>
            </div>

            <div v-else-if="selectedMethod === 'ach'" class="card-form">
              <p class="alt-method-notice">Recibirás instrucciones para transferencia ACH al confirmar.</p>
            </div>

            <div v-else-if="selectedMethod === 'yappy'" class="card-form">
              <p class="alt-method-notice">Te enviaremos solicitud de cobro Yappy a tu celular.</p>
            </div>
          </section>

          <!-- Cancellation policy -->
          <section class="payment-section">
            <h2 class="section-title">Política de cancelación</h2>
            <div class="cancel-policy-table">
              <div class="cp-row cp-good">
                <div class="cp-window">Más de 7 días antes</div>
                <div class="cp-refund"><strong>100%</strong> reembolso</div>
              </div>
              <div class="cp-row cp-warn">
                <div class="cp-window">Entre 2 y 7 días antes</div>
                <div class="cp-refund"><strong>50%</strong> reembolso</div>
              </div>
              <div class="cp-row cp-bad">
                <div class="cp-window">Menos de 48 horas</div>
                <div class="cp-refund"><strong>Sin reembolso</strong></div>
              </div>
            </div>
          </section>

          <!-- FAQs inline -->
          <section class="payment-section">
            <h2 class="section-title">Dudas frecuentes</h2>
            <div class="payment-faqs">
              <details v-for="f in faqs" :key="f.q" class="payment-faq">
                <summary>{{ f.q }}</summary>
                <p>{{ f.a }}</p>
              </details>
            </div>
          </section>
        </div>

        <!-- Right: Sticky summary -->
        <aside class="payment-summary">
          <div class="ps-card">
            <h3>Resumen</h3>

            <div class="ps-talent">
              <img :src="booking.talent?.avatar || placeholder" :alt="booking.talent?.stage_name" class="ps-avatar" />
              <div>
                <strong>{{ booking.talent?.stage_name }}</strong>
                <span class="ps-tier" :class="`tier-${booking.talent?.talent_level || 'standard'}`">
                  {{ tierLabel }}
                </span>
              </div>
            </div>

            <div class="ps-event">
              <div class="ps-row"><span>Tipo</span><strong>{{ booking.event_type_display }}</strong></div>
              <div class="ps-row"><span>Fecha</span><strong>{{ formatDate(booking.event_date) }}</strong></div>
              <div class="ps-row"><span>Duración</span><strong>{{ booking.event_duration_hours }} hrs</strong></div>
              <div class="ps-row"><span>Lugar</span><strong>{{ booking.event_city || booking.event_location }}</strong></div>
            </div>

            <!-- Breakdown del pago -->
            <div class="ps-breakdown">
              <div class="ps-row">
                <span>Performance del talento</span>
                <strong>${{ Number(performancePrice).toFixed(2) }}</strong>
              </div>
              <div v-if="booking.additional_services?.length" class="ps-row">
                <span>Servicios adicionales</span>
                <strong>${{ servicesPrice.toFixed(2) }}</strong>
              </div>
              <div class="ps-row ps-fee">
                <span>Tarifa Pulsar (gestión)</span>
                <strong>${{ Number(booking.service_fee || 0).toFixed(2) }}</strong>
              </div>
              <div class="ps-row ps-tax">
                <span>ITBMS 7%</span>
                <strong>${{ Number(booking.tax_amount || 0).toFixed(2) }}</strong>
              </div>
              <div class="ps-divider"></div>
              <div class="ps-row ps-total">
                <span>Total</span>
                <strong class="ps-total-amount">${{ totalToPay.toFixed(2) }}</strong>
              </div>
            </div>

            <button class="btn btn-cta btn-lg btn-pay" :disabled="!selectedMethod || paying" @click="processPayment">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              {{ paying ? 'Procesando...' : `Pagar $${totalToPay.toFixed(2)}` }}
            </button>

            <p class="ps-disclaimer">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              Tu dinero queda en custodia. El talento solo cobra después del evento.
            </p>

            <div v-if="payError" class="pay-error">{{ payError }}</div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const bookingId = route.params.id
const booking = ref(null)
const loading = ref(true)
const paying = ref(false)
const payError = ref('')
const selectedMethod = ref('card')

const placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60"%3E%3Crect fill="%230A0A0A" width="60" height="60" rx="30"/%3E%3C/svg%3E'

const paymentMethods = [
  {
    key: 'card',
    label: 'Tarjeta de crédito/débito',
    desc: 'Visa, Mastercard, Amex · Procesado por Stripe',
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>',
  },
  {
    key: 'ach',
    label: 'Transferencia ACH',
    desc: 'Confirmación en 1-2 días hábiles',
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M5 18V9M19 18V9M9 18v-9M15 18v-9M3 9l9-6 9 6"/></svg>',
  },
  {
    key: 'yappy',
    label: 'Yappy',
    desc: 'Pago directo desde tu celular · Panamá',
    icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="#a020f0" stroke="none"><rect width="24" height="24" rx="6"/><text x="12" y="16" font-family="sans-serif" font-weight="700" font-size="10" text-anchor="middle" fill="white">Y</text></svg>',
  },
]

const faqs = [
  { q: '¿Cuándo se cobra el talento?', a: '24 horas después de que el evento se realice, una vez confirmamos que todo salió bien.' },
  { q: '¿Qué pasa si el talento no se presenta?', a: 'Reembolso 100% del monto pagado. El proceso toma 24-72h hábiles.' },
  { q: '¿Puedo cancelar después de pagar?', a: 'Sí. La política de cancelación arriba determina el porcentaje a reembolsar según los días al evento.' },
  { q: '¿El precio incluye impuestos?', a: 'Sí. El total mostrado incluye ITBMS 7% y la tarifa de gestión Pulsar.' },
  { q: '¿Dónde queda mi dinero mientras tanto?', a: 'En una cuenta de custodia separada, regulada. No se mezcla con operaciones de Pulsar ni del talento.' },
]

const tierLabel = computed(() => {
  const l = booking.value?.talent?.talent_level
  if (l === 'premium') return '★★ Premium'
  if (l === 'pro') return '★ Pro'
  return 'Standard'
})

const performancePrice = computed(() => {
  return Number(booking.value?.quoted_price || booking.value?.precio_estimado || 0)
})

const servicesPrice = computed(() => {
  // Si los servicios adicionales tienen precio, sumarlos. Por ahora 0.
  return 0
})

const totalToPay = computed(() => {
  return performancePrice.value + servicesPrice.value
    + Number(booking.value?.service_fee || 0)
    + Number(booking.value?.tax_amount || 0)
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T00:00:00').toLocaleDateString('es-PA', { day: 'numeric', month: 'long', year: 'numeric' })
}

async function processPayment() {
  if (!selectedMethod.value) return
  paying.value = true
  payError.value = ''
  try {
    // Sin Stripe real → marcar pago como completado (placeholder backend)
    await api.post('/payments/create/', {
      booking: booking.value.id,
      amount: totalToPay.value,
      payment_type: 'full',
      payment_method: selectedMethod.value,
    })
    router.push(`/dashboard/bookings/${booking.value.id}?paid=1`)
  } catch (err) {
    payError.value = err.response?.data?.detail || err.response?.data?.error || 'Error al procesar el pago.'
  } finally {
    paying.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/bookings/${bookingId}/`)
    booking.value = data
  } catch (err) {
    payError.value = 'No se pudo cargar el booking.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.payment-page { padding-top: 100px; padding-bottom: var(--space-12); min-height: 100vh; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  margin-bottom: var(--space-4);
}
.back-link:hover { color: var(--color-primary); }

.loading-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
}

.payment-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: var(--space-6);
  align-items: flex-start;
}
.payment-main { display: flex; flex-direction: column; gap: var(--space-5); }

/* Trust hero */
.trust-hero {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.02));
  border: 1px solid rgba(16,185,129,0.3);
  border-radius: var(--radius-2xl);
}
.trust-hero-icon {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(16,185,129,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}
.trust-hero h1 {
  font-size: 1.5rem;
  margin: 0 0 4px;
  color: var(--color-text-primary);
}
.trust-hero p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

/* Escrow timeline */
.escrow-timeline-card {
  display: flex;
  align-items: stretch;
  padding: var(--space-5);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}
.escrow-stage {
  flex: 1;
  text-align: center;
  padding: 0 var(--space-2);
}
.escrow-stage.active strong { color: #10b981; }
.es-num {
  width: 32px;
  height: 32px;
  margin: 0 auto var(--space-2);
  border-radius: 50%;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
}
.es-num.active {
  background: #10b981;
  border-color: #10b981;
  color: #fff;
}
.es-icon { font-size: 1.6rem; margin-bottom: var(--space-2); }
.escrow-stage strong { display: block; font-size: 0.92rem; margin-bottom: 4px; }
.escrow-stage span { display: block; font-size: 0.78rem; color: var(--color-text-muted); line-height: 1.4; }
.es-line {
  flex: 0 0 24px;
  align-self: center;
  height: 2px;
  background: var(--color-border);
}

/* Sections */
.payment-section {
  padding: var(--space-5);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}
.section-title { font-size: 1.1rem; margin-bottom: var(--space-4); }

/* Payment methods */
.payment-methods { display: flex; flex-direction: column; gap: var(--space-2); }
.payment-method-tile {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-primary);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}
.payment-method-tile:hover { border-color: var(--color-border-hover); }
.payment-method-tile.selected {
  border-color: var(--color-primary);
  background: rgba(193,216,47,0.04);
}
.pm-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}
.payment-method-tile.selected .pm-icon { color: var(--color-primary); }
.pm-text { flex: 1; min-width: 0; }
.pm-text strong { display: block; font-size: 0.92rem; }
.pm-text span { font-size: 0.78rem; color: var(--color-text-muted); }
.pm-radio {
  width: 18px; height: 18px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.payment-method-tile.selected .pm-radio { border-color: var(--color-primary); }
.pm-radio-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
}

.card-form {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
}
.stripe-notice {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(99,91,255,0.1);
  color: #635bff;
  font-size: 0.72rem;
  margin-bottom: var(--space-3);
}
.card-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-3); }
.form-group { display: flex; flex-direction: column; gap: 4px; margin-bottom: var(--space-3); }
.form-group label { font-size: 0.78rem; color: var(--color-text-muted); }
.input-field {
  padding: 10px 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  outline: none;
}
.input-field:disabled { opacity: 0.5; cursor: not-allowed; }
.stripe-pending {
  margin-top: var(--space-2);
  padding: 8px 12px;
  background: rgba(245,158,11,0.08);
  border-left: 3px solid #f59e0b;
  color: #f59e0b;
  font-size: 0.78rem;
}
.alt-method-notice {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  margin: 0;
}

/* Cancellation policy */
.cancel-policy-table {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.cp-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
}
.cp-good { background: rgba(16,185,129,0.06); border-left: 3px solid #10b981; }
.cp-warn { background: rgba(245,158,11,0.06); border-left: 3px solid #f59e0b; }
.cp-bad { background: rgba(239,68,68,0.06); border-left: 3px solid #ef4444; }
.cp-window { font-size: 0.88rem; color: var(--color-text-secondary); }
.cp-refund { font-size: 0.92rem; }
.cp-good .cp-refund strong { color: #10b981; }
.cp-warn .cp-refund strong { color: #f59e0b; }
.cp-bad .cp-refund strong { color: #ef4444; }

/* Payment FAQs */
.payment-faqs { display: flex; flex-direction: column; gap: var(--space-2); }
.payment-faq {
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}
.payment-faq[open] { border-color: var(--color-primary); }
.payment-faq summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--color-text-primary);
  list-style: none;
}
.payment-faq summary::-webkit-details-marker { display: none; }
.payment-faq summary::after {
  content: '+';
  float: right;
  color: var(--color-primary);
}
.payment-faq[open] summary::after { content: '−'; }
.payment-faq p {
  margin: var(--space-2) 0 0;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}

/* Sticky summary */
.payment-summary { position: sticky; top: 100px; }
.ps-card {
  padding: var(--space-5);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}
.ps-card h3 { font-size: 1rem; margin-bottom: var(--space-4); }

.ps-talent {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-4);
}
.ps-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-primary);
}
.ps-talent strong { display: block; font-size: 0.95rem; }
.ps-tier {
  display: inline-block;
  margin-top: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
}
.ps-tier.tier-standard { background: var(--color-bg-primary); color: var(--color-text-muted); }
.ps-tier.tier-pro { background: rgba(193, 216, 47, 0.12); color: #C1D82F; }
.ps-tier.tier-premium { background: rgba(245,158,11,0.12); color: #f59e0b; }

.ps-event {
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-4);
}
.ps-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  padding: 4px 0;
}
.ps-row span { color: var(--color-text-muted); }
.ps-row strong { color: var(--color-text-primary); }

.ps-breakdown { margin-bottom: var(--space-4); }
.ps-fee, .ps-tax { color: var(--color-text-muted); }
.ps-divider {
  height: 1px;
  background: var(--color-border);
  margin: var(--space-3) 0;
}
.ps-total { font-size: 1rem; }
.ps-total-amount {
  font-family: 'Poppins', sans-serif;
  font-size: 1.4rem;
  color: var(--color-primary);
}

.btn-pay {
  width: 100%;
  margin-bottom: var(--space-3);
}
.ps-disclaimer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  padding: 8px 10px;
  background: rgba(16,185,129,0.06);
  border-radius: var(--radius-md);
  color: #10b981;
  font-size: 0.72rem;
}
.pay-error {
  margin-top: var(--space-3);
  padding: 8px 12px;
  background: rgba(232,93,74,0.08);
  border-radius: var(--radius-md);
  color: #E85D4A;
  font-size: 0.82rem;
}

@media (max-width: 900px) {
  .payment-layout { grid-template-columns: 1fr; }
  .payment-summary { position: static; }
  .escrow-timeline-card { flex-direction: column; gap: var(--space-3); }
  .es-line { width: 2px; height: 24px; flex: 0 0 24px; }
}
</style>
