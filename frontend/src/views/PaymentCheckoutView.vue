<template>
  <div class="checkout-page">
    <div class="checkout-card">
      <h1>Pagar reserva</h1>

      <!-- Cargando métodos -->
      <div v-if="loadingMethods" class="state-loading">
        <div class="spinner"></div>
        <p>Cargando métodos de pago…</p>
      </div>

      <!-- Éxito pago automático (PagueloFacil) -->
      <div v-else-if="successOper" class="state-success">
        <div class="check-icon">✓</div>
        <h2>¡Pago aprobado!</h2>
        <p>Código de operación: <code>{{ successOper }}</code></p>
        <p>Te enviamos un email con el comprobante.</p>
        <button class="btn primary" @click="goToBooking">Ver mi reserva</button>
      </div>

      <!-- Pago manual enviado (en revisión) -->
      <div v-else-if="manualDone" class="state-success">
        <div class="check-icon clock">🕓</div>
        <h2>Pago en revisión</h2>
        <p>
          Recibimos tu comprobante. Nuestro equipo lo valida y te confirmamos la
          reserva por email y notificación en cuanto esté aprobado.
        </p>
        <button class="btn primary" @click="goToBooking">Ver mi reserva</button>
      </div>

      <!-- Formulario -->
      <div v-else class="state-form">
        <div class="summary">
          <div class="row">
            <span>Reserva</span>
            <strong>{{ bookingCode || `#${bookingId}` }}</strong>
          </div>
          <div class="row">
            <span>Monto</span>
            <strong>USD {{ amount.toFixed(2) }}</strong>
          </div>
        </div>

        <div v-if="error" class="inline-error">{{ error }}</div>

        <!-- 1) Selector de método -->
        <div v-if="!selectedMethod">
          <p class="pick-label">Elegí cómo querés pagar</p>
          <div v-if="!methods.length" class="empty-methods">
            No hay métodos de pago disponibles en este momento.
          </div>
          <button
            v-for="m in methods" :key="m.id"
            type="button" class="method-tile" @click="selectMethod(m)">
            <img v-if="m.logo" :src="m.logo" class="method-logo" alt="" />
            <span v-else class="method-logo placeholder">{{ m.kind === 'automatic' ? '💳' : '🏦' }}</span>
            <span class="method-body">
              <span class="method-name">{{ m.name }}</span>
              <span class="method-kind">
                {{ m.kind === 'automatic' ? 'Tarjeta · aprobación al instante' : 'Transferencia / comprobante' }}
              </span>
            </span>
            <span class="method-arrow">→</span>
          </button>
        </div>

        <!-- 2a) Método automático (PagueloFacil) -->
        <div v-else-if="isAutomatic">
          <button type="button" class="link-back" @click="backToMethods">← Cambiar método</button>
          <div class="row tiny sandbox-row">
            <span>Procesado por Paguelofacil · Pagos seguros</span>
            <span v-if="useSandbox" class="badge sandbox">MODO PRUEBA</span>
          </div>
          <div v-if="sdkLoading" class="state-loading small">
            <div class="spinner"></div>
            <p>Preparando el formulario…</p>
          </div>
          <div id="container-form" class="pf-container"></div>
          <p class="tiny-help">
            Tu tarjeta nunca pasa por nuestros servidores. Los datos van
            cifrados directamente a Paguelofacil.
          </p>
        </div>

        <!-- 2b) Método manual -->
        <div v-else-if="isManual">
          <button type="button" class="link-back" @click="backToMethods">← Cambiar método</button>

          <div class="manual-panel">
            <h3 class="manual-title">{{ selectedMethod.name }}</h3>
            <p v-if="selectedMethod.instructions" class="instructions">{{ selectedMethod.instructions }}</p>

            <div class="acct" v-if="hasAccountData">
              <div v-if="selectedMethod.account_holder" class="acct-row">
                <span>Titular</span><strong>{{ selectedMethod.account_holder }}</strong>
              </div>
              <div v-if="selectedMethod.bank_name" class="acct-row">
                <span>Banco</span><strong>{{ selectedMethod.bank_name }}</strong>
              </div>
              <div v-if="selectedMethod.account_number" class="acct-row">
                <span>Cuenta</span>
                <strong>{{ selectedMethod.account_number }}
                  <button type="button" class="copy" @click="copyText(selectedMethod.account_number)">copiar</button>
                </strong>
              </div>
              <div v-if="selectedMethod.account_type" class="acct-row">
                <span>Tipo</span><strong>{{ selectedMethod.account_type }}</strong>
              </div>
              <div v-if="selectedMethod.phone" class="acct-row">
                <span>Teléfono</span>
                <strong>{{ selectedMethod.phone }}
                  <button type="button" class="copy" @click="copyText(selectedMethod.phone)">copiar</button>
                </strong>
              </div>
              <div v-if="selectedMethod.extra_info" class="acct-row">
                <span>Dato</span><strong>{{ selectedMethod.extra_info }}</strong>
              </div>
            </div>

            <div class="acct-total">
              <span>Monto a pagar</span>
              <strong>USD {{ amount.toFixed(2) }}</strong>
            </div>

            <div class="manual-form">
              <label class="fl">N° de referencia / confirmación <span class="req">*</span></label>
              <input v-model="manualForm.reference" type="text" class="fi" placeholder="Ej: 0098123456" />

              <label class="fl">
                Comprobante
                <span v-if="selectedMethod.requires_proof" class="req">*</span>
                <span v-else class="opt">(opcional)</span>
              </label>
              <label class="file-drop">
                <input type="file" accept="image/*" @change="onFile" hidden />
                <span v-if="receiptName" class="file-has">📎 {{ receiptName }}</span>
                <span v-else class="file-empty">Tocá para subir una foto o captura del comprobante</span>
              </label>

              <label class="fl">Nota <span class="opt">(opcional)</span></label>
              <textarea v-model="manualForm.note" class="fi" rows="2"
                placeholder="Algo que debamos saber sobre el pago"></textarea>

              <button type="button" class="btn primary block" :disabled="submitting" @click="submitManual">
                <span v-if="submitting">Enviando…</span>
                <span v-else>Ya pagué — enviar comprobante</span>
              </button>
              <p class="tiny-help">
                Validamos el pago manualmente y te confirmamos la reserva por email.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()

const bookingId = ref(Number(route.params.bookingId) || Number(route.query.booking) || 0)
const amount = ref(Number(route.query.amount || 0))
const paymentType = ref(route.query.type || 'full')
const bookingCode = ref(route.query.code || '')

const loadingMethods = ref(true)
const error = ref('')
const methods = ref([])
const selectedMethod = ref(null)

// Automático (PagueloFacil)
const sdkLoading = ref(false)
const successOper = ref('')
const internalRef = ref('')
const useSandbox = ref(false)
let sdkInstance = null

// Manual
const manualForm = ref({ reference: '', note: '' })
const receiptFile = ref(null)
const receiptName = ref('')
const submitting = ref(false)
const manualDone = ref(false)

const isAutomatic = computed(() => selectedMethod.value?.kind === 'automatic')
const isManual = computed(() => selectedMethod.value?.kind === 'manual')
const hasAccountData = computed(() => {
  const m = selectedMethod.value
  return !!(m && (m.account_holder || m.bank_name || m.account_number || m.account_type || m.phone || m.extra_info))
})

async function fetchMethods() {
  loadingMethods.value = true
  error.value = ''
  if (!bookingId.value || !amount.value) {
    error.value = 'Faltan datos del cobro (reserva o monto).'
    loadingMethods.value = false
    return
  }
  try {
    const { data } = await api.get('/payment-methods/')
    methods.value = Array.isArray(data) ? data : (data.results || [])
    if (!methods.value.length) {
      error.value = 'No hay métodos de pago configurados todavía. Contactá a soporte.'
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No pudimos cargar los métodos de pago.'
  } finally {
    loadingMethods.value = false
  }
}

async function selectMethod(m) {
  selectedMethod.value = m
  error.value = ''
  successOper.value = ''
  if (m.kind === 'automatic') {
    await nextTick()
    initAutomatic()
  }
}

function backToMethods() {
  selectedMethod.value = null
  error.value = ''
  sdkInstance = null
}

function goToBooking() {
  router.push({ name: 'booking-detail', params: { id: bookingId.value } })
}

function copyText(t) {
  try { navigator.clipboard.writeText(t) } catch (e) { /* noop */ }
}

// ───────────────────────── Automático (PagueloFacil) ─────────────────────────
function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve()
    const s = document.createElement('script')
    s.src = src
    s.async = true
    s.onload = () => resolve()
    s.onerror = () => reject(new Error('No se pudo cargar el SDK de Paguelofacil'))
    document.head.appendChild(s)
  })
}

async function initAutomatic() {
  sdkLoading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/payments/paguelofacil/init/', {
      booking_id: bookingId.value,
      amount: amount.value,
      payment_type: paymentType.value,
    })
    const cfg = data.sdk_config
    internalRef.value = data.internal_reference
    useSandbox.value = cfg.use_sandbox

    await loadScript(cfg.script_url)
    if (!window.pfWallet) {
      throw new Error('El SDK de Paguelofacil no se inicializó (revisá AdBlock / Network).')
    }
    window.pfWallet.useAsSandbox(cfg.use_sandbox)

    const merchantSetup = await window.pfWallet.openService({
      apiKey: cfg.api_key,
      cclw: cfg.cclw,
    })

    const paymentInfo = {
      amount: cfg.amount,
      discount: 0.0,
      taxAmount: 0.0,
      description: cfg.description,
    }

    const setup = {
      lang: 'es',
      embedded: true,
      container: 'container-form',
      onError: (errData) => {
        error.value = errData?.message || errData?.description || 'Hubo un problema con el formulario de pago.'
      },
      onTxSuccess: async (txData) => {
        const codOper = txData?.Oper || txData?.operationCode || txData?.codOper
        if (!codOper) {
          error.value = 'Pago confirmado pero sin código de operación. Contactá soporte.'
          return
        }
        try {
          await api.post('/payments/paguelofacil/confirm/', {
            internal_reference: internalRef.value,
            cod_oper: codOper,
          })
          successOper.value = codOper
        } catch (e) {
          error.value =
            'El pago fue aprobado pero no pudimos confirmarlo. No vuelvas a pagar — ' +
            'contactá soporte con el código: ' + codOper
        }
      },
      onTxError: (txErr) => {
        error.value = txErr?.message || txErr?.description || 'Pago rechazado.'
      },
      onClose: () => {},
    }

    sdkInstance = merchantSetup.init(merchantSetup.dataMerchant, paymentInfo, setup)
    sdkLoading.value = false
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Error inicializando el pago.'
    sdkLoading.value = false
  }
}

// ───────────────────────────────── Manual ────────────────────────────────────
function onFile(e) {
  const f = e.target.files && e.target.files[0]
  if (!f) { receiptFile.value = null; receiptName.value = ''; return }
  receiptFile.value = f
  receiptName.value = f.name
}

async function submitManual() {
  error.value = ''
  if (!manualForm.value.reference.trim()) {
    error.value = 'Ingresá el número de referencia del pago.'
    return
  }
  if (selectedMethod.value.requires_proof && !receiptFile.value) {
    error.value = 'Este método requiere que subas el comprobante.'
    return
  }
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('booking', bookingId.value)
    fd.append('method', selectedMethod.value.id)
    fd.append('amount', amount.value)
    fd.append('payment_type', paymentType.value)
    fd.append('reference', manualForm.value.reference.trim())
    if (manualForm.value.note.trim()) fd.append('client_note', manualForm.value.note.trim())
    if (receiptFile.value) fd.append('receipt', receiptFile.value)
    await api.post('/manual-payments/', fd)
    manualDone.value = true
  } catch (e) {
    const d = e?.response?.data || {}
    error.value =
      d.detail || d.reference?.[0] || d.receipt?.[0] || d.amount?.[0] ||
      d.booking?.[0] || d.method?.[0] || d.non_field_errors?.[0] ||
      'No pudimos registrar tu pago. Revisá los datos e intentá de nuevo.'
  } finally {
    submitting.value = false
  }
}

onMounted(fetchMethods)
onBeforeUnmount(() => { sdkInstance = null })
</script>

<style scoped>
.checkout-page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
  background: var(--color-bg-primary, #0a0a0a);
}
.checkout-card {
  width: 100%;
  max-width: 560px;
  background: var(--color-bg-card, #141414);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
h1 { margin: 0 0 1.5rem; font-size: 1.5rem; color: var(--color-text-primary); }
h2 { margin: 0 0 .5rem; color: var(--color-text-primary); }

.summary {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}
.summary .row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .35rem 0; color: var(--color-text-muted, #aaa);
}
.summary .row strong { color: var(--color-text-primary); }
.row.tiny { font-size: .78rem; }
.sandbox-row {
  display: flex; justify-content: space-between; align-items: center;
  color: var(--color-text-muted, #aaa); margin: .25rem 0 1rem;
}
.badge.sandbox {
  background: #ffb800; color: #000; padding: 2px 8px;
  border-radius: 4px; font-weight: 700; font-size: .65rem;
}

.inline-error {
  background: var(--color-accent-light, rgba(232,93,74,.12));
  border: 1px solid var(--color-accent, #e85d4a);
  color: var(--color-accent, #e85d4a);
  padding: .7rem .9rem; border-radius: 8px; font-size: .88rem; margin-bottom: 1rem;
}

/* Selector de método */
.pick-label { color: var(--color-text-secondary, #ccc); font-weight: 600; margin: 0 0 .75rem; }
.empty-methods { color: var(--color-text-muted, #888); font-size: .9rem; padding: 1rem 0; }
.method-tile {
  width: 100%; display: flex; align-items: center; gap: 14px;
  background: var(--color-bg-elevated, rgba(255,255,255,0.03));
  border: 1.5px solid var(--color-border, rgba(255,255,255,0.1));
  border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
  cursor: pointer; text-align: left; transition: all .15s;
}
.method-tile:hover {
  border-color: var(--color-primary, #c1d82f);
  transform: translateY(-1px);
}
.method-logo {
  width: 42px; height: 42px; border-radius: 8px; object-fit: cover;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; flex-shrink: 0;
}
.method-logo.placeholder { background: rgba(255,255,255,0.06); }
.method-body { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.method-name { font-weight: 700; color: var(--color-text-primary); }
.method-kind { font-size: .78rem; color: var(--color-text-muted, #999); }
.method-arrow { color: var(--color-primary, #c1d82f); font-size: 1.1rem; }

.link-back {
  background: none; border: none; color: var(--color-primary, #c1d82f);
  cursor: pointer; font-weight: 600; padding: 0; margin-bottom: 1rem; font-size: .9rem;
}

/* Automático */
.pf-container { min-height: 420px; border-radius: 12px; background: rgba(255,255,255,0.02); }

/* Manual */
.manual-panel {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 12px; padding: 1.1rem 1.25rem;
}
.manual-title { margin: 0 0 .5rem; color: var(--color-text-primary); font-size: 1.15rem; }
.instructions { color: var(--color-text-secondary, #bbb); font-size: .88rem; line-height: 1.5; margin: 0 0 1rem; }
.acct { border-top: 1px solid rgba(255,255,255,0.06); padding-top: .5rem; margin-bottom: .5rem; }
.acct-row {
  display: flex; justify-content: space-between; align-items: center;
  gap: 10px; padding: .4rem 0; font-size: .9rem; color: var(--color-text-muted, #aaa);
}
.acct-row strong { color: var(--color-text-primary); text-align: right; }
.copy {
  background: rgba(255,255,255,0.08); border: none; color: var(--color-primary, #c1d82f);
  border-radius: 5px; padding: 2px 8px; margin-left: 6px; cursor: pointer; font-size: .7rem;
}
.acct-total {
  display: flex; justify-content: space-between; align-items: center;
  padding: .7rem 0; border-top: 1px dashed rgba(255,255,255,0.12);
  margin-top: .3rem; color: var(--color-text-secondary);
}
.acct-total strong { color: var(--color-primary, #c1d82f); font-size: 1.1rem; }

.manual-form { margin-top: 1rem; }
.fl { display: block; font-size: .82rem; font-weight: 600; color: var(--color-text-secondary, #ccc); margin: .8rem 0 .35rem; }
.req { color: var(--color-accent, #e85d4a); }
.opt { color: var(--color-text-muted, #888); font-weight: 400; }
.fi {
  width: 100%; box-sizing: border-box;
  background: var(--color-bg-input, rgba(255,255,255,0.04));
  border: 1px solid var(--color-border, rgba(255,255,255,0.12));
  color: var(--color-text-primary); border-radius: 8px;
  padding: 10px 12px; font-size: .92rem; font-family: inherit;
}
.fi:focus { outline: none; border-color: var(--color-primary, #c1d82f); }
textarea.fi { resize: vertical; }
.file-drop {
  display: flex; align-items: center; justify-content: center; text-align: center;
  border: 1.5px dashed var(--color-border, rgba(255,255,255,0.18));
  border-radius: 8px; padding: 16px; cursor: pointer; font-size: .85rem;
  color: var(--color-text-muted, #999); transition: border-color .15s;
}
.file-drop:hover { border-color: var(--color-primary, #c1d82f); }
.file-has { color: var(--color-primary, #c1d82f); font-weight: 600; }

.tiny-help { margin-top: 1rem; font-size: .78rem; color: var(--color-text-muted, #888); text-align: center; }

.state-loading, .state-error, .state-success { text-align: center; padding: 2rem 1rem; color: var(--color-text-primary); }
.state-loading.small { padding: 1.2rem; }
.spinner {
  width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--color-primary, #c1d82f); border-radius: 50%;
  margin: 0 auto 1rem; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.check-icon {
  width: 60px; height: 60px; border-radius: 50%; background: #1aaa44; color: #fff;
  font-size: 2rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem;
}
.check-icon.clock { background: #ffb800; color: #000; }
.btn {
  display: inline-block; margin-top: 1rem; padding: .7rem 1.4rem;
  border: 1px solid var(--color-border, rgba(255,255,255,0.2)); background: transparent;
  color: var(--color-text-primary); border-radius: 8px; cursor: pointer; font-weight: 600; font-family: inherit;
}
.btn.primary { background: var(--color-primary, #c1d82f); border-color: var(--color-primary, #c1d82f); color: #0d0d0d; }
.btn.primary:disabled { opacity: .5; cursor: not-allowed; }
.btn.block { width: 100%; margin-top: 1.2rem; }
code {
  background: rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 4px;
  font-family: ui-monospace, monospace; font-size: .85em;
}
</style>
