# 💳 Integración Paguelofacil — Pulsar

> Arquitectura híbrida: **SDK JavaScript** en el frontend (cero PCI) + **API Server-to-Server**
> en el backend (verificación, reembolsos, webhooks).

---

## 🔑 Credenciales (PFL panel → Llaves)

Tu cliente debe darte:
- **CCLW** (Código Web) — 128 chars hex
- **Access token API** — formato `PUBLIC_KEY|PRIVATE_KEY` separados por `|`

**Importante**: PFL tiene credenciales DIFERENTES para sandbox y producción. No se pueden mezclar.

---

## 🧪 Cómo saber si son sandbox o producción

En el droplet, después del primer deploy:

```bash
cd /root/pulsar/backend && source venv/bin/activate

# Probar contra sandbox
python manage.py pfl_check --target sandbox

# Probar contra producción
python manage.py pfl_check --target production
```

El comando hace una **pre-autorización** (no captura) de USD 1.00 con tarjeta de prueba. Resultados posibles:

| Resultado | Significado |
|---|---|
| ✅ `success` en `--target sandbox` | Credenciales SON de sandbox. Podés testear libre. |
| ❌ `code 600 MERCHANT NOT VALID` en sandbox | Las credenciales son de PRODUCCIÓN. Cambiar `PAGUELOFACIL_ENV=production` en `.env`. |
| ✅ `success` en `--target production` | Credenciales SON de producción. Cuidado, todos los tests cobran plata real. |

---

## 📝 Variables en el `.env` del droplet

```env
PAGUELOFACIL_ENV=sandbox                                  # o "production"
PAGUELOFACIL_CCLW=<128-char-hex>
PAGUELOFACIL_ACCESS_TOKEN=<PUBLIC_KEY>|<PRIVATE_KEY>
PAGUELOFACIL_RETURN_URL=https://im-pulsar.com/payment/return
PAGUELOFACIL_WEBHOOK_URL=https://im-pulsar.com/api/payments/paguelofacil/webhook/
```

Después de editar `.env`:
```bash
systemctl restart pulsar
```

---

## 🪝 Activar webhooks (vía SOPORTE de PFL, no desde el panel)

**Importante**: Según los docs oficiales, los webhooks NO se activan desde el panel — hay que solicitarlos a soporte de PFL.

**Solicitud a soporte:**

```
Asunto: Activación de Webhook — Pulsar (CCLW: A521BB98…)

Hola,

Solicito activar el webhook server-to-server para mi comercio en PagueloFacil.

URL del webhook:  https://im-pulsar.com/api/payments/paguelofacil/webhook/
Método:           POST
Eventos:          Aprobaciones, rechazos, reembolsos (todos los estados de transacción)
Comercio:         Pulsar (CCLW empieza con A521BB98…)

Por favor confírmenme cuando esté activo y, si existe, indíquenme el mecanismo
de firma/autenticación (HMAC, header de validación, IPs de origen) para
verificar la autenticidad de las notificaciones del lado nuestro.

Gracias.
```

**No es bloqueante:** mientras los webhooks no estén activos, el flujo igual funciona porque
el endpoint `/confirm/` ya valida server-side llamando a la API de consulta. El webhook es
solo redundancia para el caso raro en que el browser del usuario se cierre justo después
del pago pero antes de que dispare `/confirm/`.

---

## 🚀 Deploy de la app `payments`

En el droplet, después de `git pull`:

```bash
cd /root/pulsar/backend && source venv/bin/activate

# Instalar nueva dep (requests, ya viene con Django pero por las dudas)
pip install -r requirements.txt

# Crear migración + aplicar
python manage.py makemigrations payments
python manage.py migrate payments

# Reiniciar gunicorn
systemctl restart pulsar
```

Frontend:
```bash
cd /root/pulsar/frontend
pnpm install
pnpm build
```

---

## 🧪 Test end-to-end (sandbox)

1. En el frontend, andá a tu reserva en estado `confirmed`/`aceptada`.
2. Hacé click en **"Ir a pagar con Pulsar Escrow"**.
3. Te lleva a `/dashboard/bookings/<id>/pay`.
4. El form de PFL se renderiza embedido (badge "MODO PRUEBA" si `PAGUELOFACIL_ENV=sandbox`).
5. Llená con tarjeta de prueba:

   **Aprobada:**
   - Número: `5038460000000019`
   - CVV: `475`
   - Fecha: `04/29` (cualquier futura)

   **Declinada:**
   - Número: `6013770095374264`

6. Confirmá. Deberías ver "¡Pago aprobado!" con el código de operación.
7. En la DB:
   - `payments_paguelofaciltransaction`: una fila con `status='approved'`
   - `payments`: un Payment con `payment_status='completed'`
   - `payouts`: un Payout pendiente al DJ con `amount = talent_payout`

---

## 🛠️ Endpoints expuestos

| Método | Path | Quién | Para qué |
|---|---|---|---|
| POST | `/api/payments/paguelofacil/init/` | Cliente autenticado | Crea tx y devuelve config SDK |
| POST | `/api/payments/paguelofacil/confirm/` | Cliente autenticado | Verifica server-side tras onTxSuccess |
| GET | `/api/payments/paguelofacil/status/<ref>/` | Cliente autenticado | Polling de estado |
| POST | `/api/payments/paguelofacil/webhook/` | PFL (público) | Notificación async |
| GET | `/api/payments/admin/payouts/?status=pending` | Admin | Lista de payouts a pagar |
| POST | `/api/payments/admin/payouts/<id>/pay/` | Admin | Marcar payout como pagado |

---

## 💰 Flujo del dinero

```
Cliente → tarjeta → SDK PFL → PFL captura → Pulsar recibe USD 200
                                                      │
                                                      ↓
                      Pulsar genera Payout pendiente: DJ recibe USD 156
                                                      │
                                                      ↓
                           Admin manualmente transfiere desde
                           cuenta Pulsar → cuenta del DJ
                                                      │
                                                      ↓
                            Admin marca Payout como "paid"
                            con referencia bancaria
```

**Cálculo de comisiones** (sobre los USD 200 cobrados):
- Pulsar (tier Standard 22%): USD 44
- DJ recibe: USD 156
- Si hay Partner referente: el 30% del 22% va al partner = USD 13.20

Todo eso lo calcula automáticamente `Payment.calculate_commissions()` cuando se aprueba la transacción.

---

## 🔒 Pendientes de seguridad antes de producción seria

1. **Validar firma del webhook**: implementar `verify_webhook_signature` con HMAC (esperando docs de PFL).
2. **Rate limit** específico en el endpoint `/init/` (3 intentos por minuto por user).
3. **Logs de auditoría** separados para todos los eventos de pago.
4. **3DS**: ya está manejado por el SDK, pero verificar con PFL si necesitamos exponer `returnUrlString` adicional.
5. **Reembolsos**: agregar endpoint admin para reembolsar (`POST /api/payments/admin/refund/<tx_id>/`).
