# PULSAR by ShowRoots — Resumen Ejecutivo

> Resumen completo y organizado del documento `sistema.md`.  
> Última actualización: Abril 2026.

---

## 🎯 ¿Qué es Pulsar?

Pulsar (ShowRoots) es una **plataforma curada** para conectar clientes con **DJs, músicos y bandas**. No es un marketplace abierto — es un sistema controlado donde la calidad del talento es verificada por un administrador antes de ser visible al público.

**Modelo de negocio:** Comisión por reserva (10–20%) + fee de servicio al cliente.

---

## 👥 Roles del Sistema

El sistema tiene **4 roles principales**:

| Rol | Descripción | Dashboard |
|-----|-------------|-----------|
| **Cliente** | Persona que busca y contrata talento | `/dashboard` |
| **Talento** | DJ, músico o banda que ofrece servicios | `/talent-dashboard` |
| **Admin** | Equipo ShowRoots que supervisa todo | `/admin-dashboard` |
| **Partner** | Intermediario que trae clientes y gana comisión | `/partner` |

---

## 🟢 ROL: CLIENTE

### ¿Qué puede hacer?
- Explorar talentos **sin crear cuenta**
- Filtrar por ciudad, género musical, tipo y presupuesto
- Ver perfiles completos (fotos, videos, bio, reseñas, precio/hora)
- Enviar solicitud de cotización/reserva
- Ver precio estimado antes de reservar
- Recibir propuesta final ajustada por el talento
- Pagar un porcentaje (ej: 50%) o el total
- Chatear con el talento después de la reserva
- Dejar reseña después del evento
- Ver historial de reservas

### ¿Qué NO puede hacer?
- Editar perfiles de talentos
- Ver panel de admin
- Confirmar reserva sin pagar

### Flujo típico del cliente:
1. Entra a Pulsar
2. Selecciona: tipo de talento + ubicación + fecha
3. Ve los perfiles filtrados (premium primero, standard después)
4. Entra al perfil de un talento (fotos, videos, bio, precio, reseñas)
5. Solicita cotización → completa detalles del evento
6. El talento acepta/rechaza/ajusta
7. Cliente recibe propuesta final
8. **Crea cuenta** (obligatorio solo para pagar)
9. Paga → reserva confirmada
10. Se abre chat interno para coordinar
11. Después del evento → puede dejar reseña

---

## 🎵 ROL: TALENTO (DJ / Músico / Banda)

### ¿Qué puede hacer?
- Crear perfil profesional (nombre artístico, bio, fotos, videos)
- Definir géneros musicales
- Definir precio base por hora
- Configurar disponibilidad con calendario
- Recibir solicitudes de clientes
- Aceptar, rechazar o ajustar solicitudes
- Enviar mensajes al cliente dentro de la plataforma
- Ver historial de reservas
- Ver ingresos generados
- Cambiar su ubicación (si viaja)
- Subir fotos y videos al perfil

### ¿Qué NO puede hacer?
- Aprobarse a sí mismo (requiere aprobación del admin)
- Editar ajustes globales del sistema
- Modificar reservas ya pagadas sin intervención del admin

### Niveles de talento:
| Nivel | Descripción | Visibilidad |
|-------|-------------|-------------|
| **Premium** | Seleccionado por el admin, mayor calidad | Aparece primero, cards más grandes, badge especial |
| **Standard** | Registro abierto, por defecto | Aparece después de los premium, cards más simples |

> Todo talento nuevo entra como **Standard**. El Admin decide si lo sube a **Premium**.

### Diferencias de negocio (futuras):
- Standard paga más comisión
- Premium tiene beneficios y mayor visibilidad
- Se puede cobrar por subir de nivel

---

## 🛡️ ROL: ADMIN (ShowRoots)

### ¿Qué puede hacer?
- Aprobar o rechazar talentos (control de calidad)
- Ver todos los usuarios registrados
- Editar perfiles si es necesario
- Ver todas las reservas del sistema
- Intervenir en disputas entre cliente y talento
- Configurar comisión de la plataforma
- Ver ingresos totales
- Cambiar nivel de talento (Standard ↔ Premium)
- Gestionar contenido destacado (featured)
- Dashboard con métricas: reservas, ingresos, talentos activos

---

## 🤝 ROL: PARTNER ShowRoots

### ¿Qué es?
Personas o empresas que ya consiguen clientes (wedding planners, productores, promotores, dueños de locales, managers, DJs que no pueden cubrir fechas).

### ¿Qué puede hacer?
- Buscar talentos dentro de la plataforma
- Ver perfiles, precios y disponibilidad
- Crear reservas en nombre de un cliente
- Gestionar múltiples eventos
- Ganar comisión por cada reserva generada
- Dashboard con: eventos activos, ingresos, estado de bookings

### Modelo de comisión:
```
Evento: $500
Comisión ShowRoots (20%): $100
  → Partner recibe: $30
  → ShowRoots recibe: $70
```

**Modelo avanzado:** El Partner puede aumentar el precio al cliente final.
```
Precio DJ en plataforma: $400
Partner vende al cliente: $500
Ganancia del Partner: $100
```

### Ejemplos de Partners:
- DJs que no pueden cubrir fechas
- Productores de eventos
- Wedding planners
- Managers
- Promotores
- Dueños de locales

---

## 📋 Estados de una Reserva

Cada solicitud pasa por estos estados:

```
Solicitud enviada → Pendiente de respuesta → Aceptada → Pendiente de pago → Confirmada (pagada) → Completada
                                            → Rechazada
                                            → Cancelada
```

| Estado | Descripción |
|--------|-------------|
| `solicitud_enviada` | El cliente envió la solicitud |
| `pendiente_respuesta` | Esperando que el talento responda |
| `aceptada` | El talento aceptó |
| `rechazada` | El talento rechazó |
| `pendiente_pago` | Aceptada pero falta el pago |
| `confirmada` | Pagada, reserva activa |
| `completada` | El evento ya ocurrió |
| `cancelada` | Cancelada por cualquier parte |

---

## 💰 Lógica de Pagos

- El cliente puede pagar un **porcentaje** (ej: 50%) o el **total**
- El pago inicial **bloquea la fecha**
- El monto restante debe pagarse antes del evento
- El sistema divide automáticamente:
  - **Comisión ShowRoots** (10–20%)
  - **Pago al talento** (neto)
  - **Comisión partner** (si aplica)
- El talento puede visualizar el monto neto que recibirá
- El admin puede ver todos los movimientos

---

## 💬 Mensajería Interna

- Se activa cuando el cliente envía una solicitud
- Chat completo se habilita cuando el talento acepta
- El sistema puede limitar intercambio de contacto (teléfono, redes) antes del pago
- Cada chat está vinculado a una reserva específica

---

## 📅 Disponibilidad

- El talento configura su calendario
- El sistema evita doble reserva en la misma fecha
- Fechas se bloquean automáticamente al confirmar una reserva
- El talento puede editar disponibilidad manualmente

---

## 📝 Formulario de Cotización/Reserva (9 pasos)

| Paso | Contenido |
|------|-----------|
| **1. Evento** | Tipo talento, fecha, hora, duración, ubicación, tipo evento, # personas, interior/exterior |
| **2. Búsqueda** | Sistema muestra talentos filtrados (premium primero) |
| **3. Detalles** | Género musical, descripción, presupuesto estimado, mensaje adicional |
| **4. Producción** | Servicios adicionales: sonido, luces, DJ booth, micrófono, pantalla, piso LED, técnico |
| **5. Preguntas dinámicas** | Preguntas específicas según los servicios seleccionados |
| **6. Resumen** | Vista previa con todo lo seleccionado + precio estimado |
| **7. Datos cliente** | Nombre, email, teléfono (si no tiene cuenta) |
| **8. Envío** | Solicitud llega al talento y admin |
| **9. Pago** | Propuesta final → pago (abono o total) → confirmación |

---

## 🔔 Notificaciones

El sistema envía notificaciones por **email** y dentro de la plataforma:

- Nueva solicitud recibida (al talento)
- Solicitud aceptada/rechazada (al cliente)
- Pago realizado (ambos)
- Reserva confirmada (ambos)
- Recordatorio previo al evento
- Nueva reseña recibida

---

## ⚖️ Reglas de Negocio

1. Un talento **no puede recibir pagos** sin haber aceptado la solicitud
2. Una reserva **no se confirma** hasta que exista un pago
3. Una fecha **no puede ser doble reservada** para el mismo talento
4. El sistema **bloquea fechas** automáticamente al confirmar
5. Solo se puede dejar reseña si la reserva está **"completada"**
6. El talento **no puede modificar** una reserva pagada sin el admin
7. La **comisión se calcula automáticamente** en cada pago
8. Solicitudes sin respuesta en 24h pueden **expirar automáticamente**

---

## 📊 Base de Datos — Tablas Principales

| Tabla | Propósito |
|-------|-----------|
| **Usuarios** | Info general de todos (id, nombre, email, rol, estado) |
| **Talentos** | Perfil profesional (nombre artístico, tipo, bio, tarifa, nivel, rating) |
| **Géneros** | Catálogo de géneros musicales |
| **Talento_Géneros** | Relación muchos-a-muchos entre talento y géneros |
| **Media** | Fotos y videos del perfil del talento |
| **Disponibilidad** | Calendario del talento (fecha, hora, estado) |
| **Reservas** | Tabla principal: cliente + talento + evento + estado + precio |
| **Pagos** | Montos, método, comisiones, estado del pago |
| **Mensajes** | Chat interno vinculado a cada reserva |
| **Reviews** | Puntuación y comentario del cliente al talento |
| **Notificaciones** | Alertas del sistema para cada usuario |

---

## 🚀 Fases de Desarrollo

### Fase 1 (MVP)
- Perfiles de talento
- Búsqueda y filtros
- Solicitudes y reservas
- Pagos básicos
- Panel admin
- Notificaciones por email
- Calendario básico

### Fase 2
- Chat en tiempo real
- Reseñas
- Calendario mejorado

### Fase 3 (Futuro)
- Recomendación automática de talentos (IA)
- Sistema de ranking
- Publicación de eventos
- Venta de tickets
- Dashboard financiero completo
- Integración con WhatsApp
- Cupones y promociones
- Paquetes por evento
- Multiciudad / multipaís
- Facturación automática

---

## 🎨 Visión del Producto

> ShowRoots no será solo una plataforma de DJs. Será una **red de distribución de talento**, donde múltiples actores (clientes, talentos, partners) pueden generar negocio dentro del sistema.

La clave está en:
- **Calidad controlada** (sistema curado, no marketplace abierto)
- **Dos niveles de talento** (premium vs standard)
- **Red de ventas escalable** (rol Partner)
- **Monetización múltiple** (comisión por reserva + fee de servicio + posicionamiento destacado + upgrade de nivel)
