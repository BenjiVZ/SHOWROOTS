<template>
  <div class="return-page">
    <div class="return-card">
      <div v-if="loading" class="state">
        <div class="spinner"></div>
        <h2>Verificando tu pago...</h2>
        <p class="muted">Esto toma unos segundos.</p>
      </div>

      <div v-else-if="status === 'approved'" class="state success">
        <div class="icon">✓</div>
        <h2>¡Pago aprobado!</h2>
        <p>Código: <code>{{ codOper }}</code></p>
        <p class="muted">Te enviamos el recibo por email.</p>
        <button v-if="bookingId" class="btn primary" @click="$router.push(`/dashboard/bookings/${bookingId}`)">
          Ver mi reserva
        </button>
        <button v-else class="btn" @click="$router.push('/dashboard')">
          Ir al dashboard
        </button>
      </div>

      <div v-else-if="status === 'declined'" class="state error">
        <div class="icon error">✕</div>
        <h2>Pago rechazado</h2>
        <p class="muted">{{ errorMessage || 'El banco rechazó la transacción. Prueba con otra tarjeta.' }}</p>
        <button v-if="bookingId" class="btn primary" @click="$router.push(`/dashboard/bookings/${bookingId}/pay`)">
          Reintentar
        </button>
      </div>

      <div v-else-if="status === 'processing'" class="state">
        <div class="spinner"></div>
        <h2>Pago en proceso</h2>
        <p class="muted">PFL todavía está procesando. Te avisaremos por email cuando se confirme.</p>
        <button class="btn" @click="$router.push('/dashboard')">Ir al dashboard</button>
      </div>

      <div v-else class="state error">
        <div class="icon error">!</div>
        <h2>No pudimos verificar el pago</h2>
        <p class="muted">{{ errorMessage || 'Contactá soporte con este link.' }}</p>
        <button class="btn" @click="$router.push('/dashboard')">Ir al dashboard</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()

const loading = ref(true)
const status = ref('')
const codOper = ref('')
const errorMessage = ref('')
const bookingId = ref(null)

async function verify() {
  // PFL puede mandar varios nombres de parámetro tras 3DS — buscamos todos
  const internalRef =
    route.query.ref ||
    route.query.internal_reference ||
    route.query.PARM_1 ||
    ''
  codOper.value =
    route.query.codOper ||
    route.query.cod_oper ||
    route.query.Oper ||
    route.query.operationCode ||
    ''

  if (!internalRef && !codOper.value) {
    errorMessage.value = 'No recibimos identificadores de la pasarela.'
    status.value = 'error'
    loading.value = false
    return
  }

  try {
    if (internalRef) {
      const { data } = await api.get(`/payments/paguelofacil/status/${internalRef}/`)
      status.value = data.status === 'approved' ? 'approved'
                   : data.status === 'declined' ? 'declined'
                   : data.status === 'processing' || data.status === 'initiated' ? 'processing'
                   : 'error'
      bookingId.value = data.booking
      codOper.value = data.paguelofacil_id || codOper.value
    } else if (codOper.value) {
      // Solo tenemos codOper — confirmar contra la API
      const { data } = await api.post('/payments/paguelofacil/confirm/', {
        internal_reference: internalRef,
        cod_oper: codOper.value,
      })
      status.value = data.status
      bookingId.value = data.booking
    }
  } catch (e) {
    console.error('Verify error', e)
    errorMessage.value = e?.response?.data?.detail || 'Error consultando el estado.'
    status.value = 'error'
  } finally {
    loading.value = false
  }
}

onMounted(verify)
</script>

<style scoped>
.return-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  background: var(--color-bg, #0a0a0a);
}
.return-card {
  width: 100%;
  max-width: 480px;
  background: var(--color-surface, #141414);
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
.state h2 { margin: .5rem 0; color: var(--color-text, #fff); }
.muted { color: var(--color-text-muted, #aaa); font-size: .9rem; }
.icon {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: #1aaa44;
  color: #fff;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-weight: 700;
}
.icon.error { background: #e74c3c; }
.spinner {
  width: 48px; height: 48px;
  border: 3px solid rgba(255,255,255,.1);
  border-top-color: var(--color-accent, #c8ff00);
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.btn {
  margin-top: 1.5rem;
  padding: .8rem 1.6rem;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,.2);
  background: transparent;
  color: var(--color-text, #fff);
  cursor: pointer;
  font-weight: 600;
}
.btn.primary {
  background: var(--color-accent, #c8ff00);
  color: #000;
  border-color: var(--color-accent, #c8ff00);
}
code {
  background: rgba(255,255,255,.08);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: ui-monospace, monospace;
}
</style>
