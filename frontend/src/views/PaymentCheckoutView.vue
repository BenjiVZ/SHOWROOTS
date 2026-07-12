<template>
  <div class="checkout-page">
    <div class="checkout-card">
      <h1>Pagar reserva</h1>

      <div v-if="loading" class="state-loading">
        <div class="spinner"></div>
        <p>Preparando el formulario de pago...</p>
      </div>

      <div v-else-if="error" class="state-error">
        <h2>No pudimos abrir el pago</h2>
        <p>{{ error }}</p>
        <button class="btn" @click="$router.back()">Volver</button>
      </div>

      <div v-else-if="successOper" class="state-success">
        <div class="check-icon">✓</div>
        <h2>¡Pago aprobado!</h2>
        <p>Código de operación: <code>{{ successOper }}</code></p>
        <p>Te enviamos un email con el comprobante.</p>
        <button class="btn primary" @click="$router.push(`/bookings/${bookingId}`)">
          Ver mi reserva
        </button>
      </div>

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
          <div class="row tiny">
            <span>Procesado por Paguelofacil · Pagos seguros</span>
            <span v-if="useSandbox" class="badge sandbox">MODO PRUEBA</span>
          </div>
        </div>

        <!-- El SDK renderiza el formulario aquí -->
        <div id="container-form" class="pf-container"></div>

        <p class="tiny-help">
          Tu tarjeta nunca pasa por nuestros servidores. Los datos van
          directamente cifrados a Paguelofacil.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()

const bookingId = ref(Number(route.params.bookingId) || Number(route.query.booking) || 0)
const amount = ref(Number(route.query.amount || 0))
const paymentType = ref(route.query.type || 'full')
const bookingCode = ref(route.query.code || '')

const loading = ref(true)
const error = ref('')
const successOper = ref('')

const internalRef = ref('')
const useSandbox = ref(false)
let sdkInstance = null
let scriptEl = null

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve()
    const s = document.createElement('script')
    s.src = src
    s.async = true
    s.onload = () => resolve()
    s.onerror = () => reject(new Error('No se pudo cargar el SDK de Paguelofacil'))
    document.head.appendChild(s)
    scriptEl = s
  })
}

async function initCheckout() {
  if (!bookingId.value || !amount.value) {
    error.value = 'Faltan datos del cobro (booking_id o monto).'
    loading.value = false
    return
  }

  try {
    console.log('[PFL] 1. Llamando a /init/...')
    const { data } = await api.post('/payments/paguelofacil/init/', {
      booking_id: bookingId.value,
      amount: amount.value,
      payment_type: paymentType.value,
    })
    console.log('[PFL] 2. Init OK', data)

    const cfg = data.sdk_config
    internalRef.value = data.internal_reference
    useSandbox.value = cfg.use_sandbox

    console.log('[PFL] 3. Cargando script', cfg.script_url)
    await loadScript(cfg.script_url)
    console.log('[PFL] 4. Script cargado. window.pfWallet =', !!window.pfWallet)

    if (!window.pfWallet) {
      throw new Error(
        'El SDK de Paguelofacil no se inicializó correctamente. ' +
        'Probablemente el script bloqueó (revisa Network tab + AdBlock).'
      )
    }

    console.log('[PFL] 5. useAsSandbox(' + cfg.use_sandbox + ')')
    window.pfWallet.useAsSandbox(cfg.use_sandbox)

    console.log('[PFL] 6. openService con apiKey/cclw...')
    const merchantSetup = await window.pfWallet.openService({
      apiKey: cfg.api_key,
      cclw: cfg.cclw,
    })
    console.log('[PFL] 7. openService OK', merchantSetup)

    const paymentInfo = {
      amount: cfg.amount,
      discount: 0.0,
      taxAmount: 0.0,
      description: cfg.description,
    }
    console.log('[PFL] 8. paymentInfo', paymentInfo)

    const setup = {
      lang: 'es',
      embedded: true,
      container: 'container-form',
      onError: (errData) => {
        console.error('[PFL] onError', errData)
        error.value =
          (errData?.message || errData?.description || 'Hubo un problema con el formulario de pago.') +
          ' (revisa la console)'
      },
      onTxSuccess: async (txData) => {
        console.log('[PFL] onTxSuccess', txData)
        const codOper = txData?.Oper || txData?.operationCode || txData?.codOper
        if (!codOper) {
          error.value = 'Pago confirmado pero sin código de operación. Contactá soporte.'
          return
        }
        try {
          console.log('[PFL] Confirmando server-side con codOper=', codOper)
          await api.post('/payments/paguelofacil/confirm/', {
            internal_reference: internalRef.value,
            cod_oper: codOper,
          })
          successOper.value = codOper
        } catch (e) {
          console.error('[PFL] confirm/ falló', e)
          error.value =
            'El pago fue aprobado pero no pudimos confirmarlo. ' +
            'No vuelvas a pagar — contactá soporte con el código: ' + codOper
        }
      },
      onTxError: (txErr) => {
        console.error('[PFL] onTxError', txErr)
        const msg = txErr?.message || txErr?.description || JSON.stringify(txErr) || 'Pago rechazado.'
        error.value = msg
      },
      onClose: () => {
        console.log('[PFL] onClose')
      },
    }
    console.log('[PFL] 9. Inicializando form embebido...', setup)

    sdkInstance = merchantSetup.init(merchantSetup.dataMerchant, paymentInfo, setup)
    console.log('[PFL] 10. SDK instance creado', sdkInstance)
    loading.value = false
  } catch (e) {
    console.error('[PFL] FATAL en initCheckout', e)
    error.value = e?.response?.data?.detail || e.message || 'Error inicializando el pago.'
    loading.value = false
  }
}

onMounted(() => {
  initCheckout()
})

onBeforeUnmount(() => {
  // No removemos el script para que quede cacheado, solo limpiamos la instancia
  if (sdkInstance) sdkInstance = null
})
</script>

<style scoped>
.checkout-page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
  background: var(--color-bg, #0a0a0a);
}
.checkout-card {
  width: 100%;
  max-width: 560px;
  background: var(--color-surface, #141414);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
h1 {
  margin: 0 0 1.5rem;
  font-size: 1.5rem;
  color: var(--color-text, #fff);
}
h2 {
  margin: 0 0 .5rem;
  color: var(--color-text, #fff);
}
.summary {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}
.summary .row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .35rem 0;
  color: var(--color-text-muted, #aaa);
}
.summary .row strong {
  color: var(--color-text, #fff);
}
.summary .row.tiny {
  font-size: .78rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  margin-top: .5rem;
  padding-top: .6rem;
}
.badge.sandbox {
  background: #ffb800;
  color: #000;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: .65rem;
}
.pf-container {
  min-height: 420px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
}
.tiny-help {
  margin-top: 1rem;
  font-size: .78rem;
  color: var(--color-text-muted, #888);
  text-align: center;
}
.state-loading,
.state-error,
.state-success {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--color-text, #fff);
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-accent, #c8ff00);
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.check-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #1aaa44;
  color: #fff;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}
.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: .7rem 1.4rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: var(--color-text, #fff);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}
.btn.primary {
  background: var(--color-accent, #c8ff00);
  border-color: var(--color-accent, #c8ff00);
  color: #000;
}
code {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
  font-size: .85em;
}
</style>
