# 📊 Pulsar by ShowRoots — Estado del Proyecto

> Checklist maestro alineado **línea por línea** con los 3 mockups HTML. Última actualización: **2026-05-12**

**Estado global**: ✅ **100% del scope visual completo**. Lo único pendiente es integración con servicios externos (Stripe form real, Yappy, hosting, Sentry) que no se hace sin cuentas.

---

## 🎯 Resumen ejecutivo

| Mockup | Cobertura | Comentario |
|---|---|---|
| **#1 — Perfil DJ** (14 secciones + sidebar + hero) | ✅ **100%** | Todos los detalles del HTML: share en hero, tooltip Premium, stats sidebar, pricing format, mix meta, header links, cobertura textual, review meta verificada, TikTok |
| **#2 — Booking Flow** (7 pantallas) | ✅ **100%** visual | Stripe form real es lo único pendiente (necesita cuenta) |
| **#3 — Tiers** (13 secciones comparadas + escalera) | ✅ **100%** | Tabla side-by-side completa + escalera de progresión + auto-promoción + gating |
| **Anti-desintermediación + Escrow trust** | ✅ 100% | |
| **Disputas + reembolsos + audit trail** | ✅ 100% | |
| **Admin tools** | ✅ 100% | |

---

## ✅ COMPLETADO

### 🎨 Mockup #1 — Perfil del DJ (alineado 1:1 al HTML)

#### Hero
- [x] Cover image 320px con gradiente
- [x] Badge "🛡 Pago protegido por Pulsar" (esquina superior)
- [x] **Botón "Compartir" en hero** (top-right, no en sidebar)

#### Sidebar
- [x] Avatar grande con borde primario + status dot
- [x] Nombre
- [x] **Badges DJ + tier con tooltip explicativo** (hover muestra "Talento verificado · 20+ eventos · Top performer · Curado por Pulsar")
- [x] Rating ★★★★★ + número + count
- [x] **Stats row (3 columnas) dentro del sidebar**: Eventos / Responde en (h) / Miembro desde (año)
- [x] Info row 📍 ubicación + idiomas en MC
- [x] **Pricing block destacado** formato "$X desde / 4 hrs" + "$Y/hr adicional · Add-ons cotizan aparte" + pill alta temporada
- [x] Availability line "⚡ Disponible: 15, 22, 29 may"
- [x] Botón "📅 Reservar Ahora"
- [x] **Botón "💬 Enviar consulta"** (abre modal con anti-disinter scan + crea notificación al talento)
- [x] Trust card escrow

#### Secciones del perfil
1. [x] **🎵 Mixes / Audio** — embed real SoundCloud/Spotify/Mixcloud/YouTube + **link "Ver todos →"** al SoundCloud profile + mix metadata
2. [x] **🎬 Video en vivo** — embed YouTube/Vimeo grid 2 columnas
3. [x] **👤 Bio**
4. [x] **🎶 Géneros & Mood** — labels "GÉNEROS" + "VIBE / MOOD" con tags color
5. [x] **📅 Tipos de eventos** — tags ámbar con emoji
6. [x] **📦 Paquetes** — grid 2x2 con badge "POPULAR" + **link "Personalizar →"** (a booking flow)
7. [x] **📸 Galería** con lightbox + **link "Ver todas (N) →"** abre primer item
8. [x] **🎛 Equipamiento split** (Yo traigo / No incluido)
9. [x] **📍 Cobertura + Idiomas** — **sección textual** con zonas listadas + "Fuera del área: +$X traslado" + mapa
10. [x] **⭐ Reseñas** — score grande + breakdown 5 dimensiones + **selector "Filtrar ↓"** (recientes/mejor/peor/verificadas) + cards con **avatar circular + meta "Boda · 350 invitados · abril 2026" + tag "✓ Verificada"** + respuesta DJ (Premium)
11. [x] **📅 Disponibilidad** — calendario navegable semafórico
12. [x] **❓ FAQ** — acordeón
13. [x] **🛡 Cómo funciona** — 5 pasos escrow
14. [x] **🌐 Redes sociales** — Instagram, **TikTok**, SoundCloud, Spotify, Mixcloud, YouTube, Web (sin link directo)

#### Backend fields que alimentan el perfil
- [x] `response_time_hours` (computed: promedio entre booking creado y primer mensaje del talento)
- [x] `repeat_rate` (computed: % clientes que repitieron)
- [x] `service_zones` (JSONField list de zonas)
- [x] `travel_fee_extra` (Decimal, cargo fuera del área)
- [x] `tiktok` (CharField)
- [x] Review meta: `event_type_display`, `event_guest_count`, `event_date`, `is_verified`

---

### 🎨 Mockup #2 — Client Booking Flow (alineado 1:1)

#### Pantalla 1 — Detalles del evento
- [x] **Stepper de 4 pasos**: Evento → Servicio → Producción → Resumen
- [x] **Tiles visuales** con iconos grandes (8 tipos: 💍🏢🎂🎉🎪🌃🍸✨)
- [x] Campos completos + sticky summary lateral
- [x] Anti-desintermediación en descripción

#### Pantalla 2 — Confirmar talento + mensaje
- [x] Card del DJ + selector géneros + textarea con anti-disinter

#### Pantalla 3 — Pago con Escrow ⭐ (vista dedicada `/dashboard/bookings/:id/pay`)
- [x] Hero verde "Tu pago está protegido por Pulsar"
- [x] **Escrow Timeline 3 pasos** (Hoy → En custodia → Liberación)
- [x] **Tiles métodos de pago** (Tarjeta / ACH / Yappy)
- [x] Form de tarjeta placeholder (Stripe pending)
- [x] **Breakdown completo** del pago (Performance + Tarifa Pulsar + ITBMS 7%)
- [x] **Cancellation policy** escalonada (100% / 50% / 0%)
- [x] **5 FAQs inline expandibles**
- [x] Sticky summary con tier badge

#### Pantalla 4 — Confirmación
- [x] Modal hero con check + `booking_code` único + timeline 5 pasos + píldora escrow

#### Pantalla 5 — Dashboard Mis Reservas
- [x] **KPIs**: Próximos / En custodia / Completados / Crédito Pulsar
- [x] **Cards de countdown** (días/hrs/min vivo) + badge custodia
- [x] Tabs Activas / Completadas / Todas

#### Pantalla 6 — Booking activo
- [x] `booking_code` chip + **countdown banner** + **chat anti-disinter**
- [x] **Botón "Descargar contrato"** (genera HTML imprimible)
- [x] Modales: Modificar fecha · Reportar problema · Cancelar (con preview reembolso)

#### Pantalla 7 — Reseña post-evento
- [x] `ReviewForm.vue` con 5 dimensiones + anti-disinter + $50 crédito automático

---

### 🎨 Mockup #3 — Tiers Standard / Pro / Premium (alineado 1:1)

#### Lógica
- [x] Comisiones reales 22% / 15% / 12% configurables
- [x] **Auto-promoción Standard→Pro** vía signal (10+ eventos, rating ≥4.5, 0 cancel 6 meses)
- [x] **Premium por invitación** (modelo PremiumInvitation + admin endpoint + accept/decline)
- [x] **Feature gating real** aplicado en serializers/views:
  - Standard: 5 fotos / 2 mixes / 0 videos / 0 packs / 0 FAQs / bio 200 ✓ enforce
  - Pro: 10 / 4 / 1 / 1 / 3 / 500
  - Premium: ilimitado
- [x] **Pricing dinámico** Premium (+15% alta temporada)
- [x] **Respuesta DJ a reseñas** (solo Premium)
- [x] **Mix destacado** (solo Premium)

#### Visual
- [x] Badge Pro cyan + Premium gold con glow + "CURADO POR PULSAR"
- [x] Border + shadow por tier en cards de search y perfil

#### Páginas públicas
- [x] **`/tiers`** con:
  - 3 cards sticky comparativas
  - **Tabla side-by-side de 16 filas** (todas las features del mockup)
  - Escalera de progresión visual
  - Protecciones universales
  - CTA
- [x] **`/como-funciona`** con timeline escrow + 6 FAQs

#### Dashboard del talento
- [x] Tab Ingresos: tier + comisión real + **escalera con barras** (eventos/rating) + payouts tabla
- [x] Banner Premium invitation
- [x] Tier warning si se alcanza límite
- [x] Editor de mix destacado (Premium)

---

### 🛡 Anti-desintermediación
- [x] Backend `bookings/anti_disinter.py` + espejo JS `utils/antiDisinter.js`
- [x] `Message.save()` sanitize automático
- [x] Scanner live en: descripción booking, chat, review comment, **inquiry modal**
- [x] Admin tab "Mensajes filtrados" con stats + top users + lista

### 🔍 Búsqueda
- [x] Filtros: tier (chips), experience_level, languages, event_types, moods, genres
- [x] TalentCard con badges tier + glow Premium

### 💼 Admin
- [x] Tabs: Talentos, Reservas, Usuarios, Pagos, Mensajes filtrados, **Disputas**
- [x] Modal Refund + CSV export + Audit trail

### 🛠 Backend foundations
- [x] Booking codes `PUL-YYYY-MM-XXXX` + ITBMS + cancellation refund calc
- [x] ClientCredit ($50 auto al reseñar)
- [x] **Endpoint inquiry** `/talents/<id>/inquire/`
- [x] **Endpoint payout** `/talents/me/payout/`
- [x] **Endpoint contrato** `/bookings/<id>/contract/` (HTML descargable)
- [x] Rate limiting + AuditLog + CSV export

---

## ❌ PENDIENTE — Solo infraestructura externa

| Item | Por qué | Naturaleza |
|---|---|---|
| **Stripe Connect** form de tarjeta real + payouts | Sin esto el escrow es decorativo | Cuenta Stripe + KYC talentos |
| **Yappy / ACH** | Métodos Panamá | Partnership bancaria |
| **Email transaccional** | Sin notif emails se pierden bookings | SendGrid / Postmark |
| **Postgres + hosting** | SQLite no aguanta producción | Railway / RDS / Supabase |
| **KYC talentos** automatizado | "Premium curado" más sólido | Persona / Onfido |
| **Sentry + backups** | Operacional | Cuentas externas |
| **WebSocket realtime** | Chat/notif en vivo | Channels + Redis + ASGI |
| **Push notifications mobile** | UX | Firebase Cloud Messaging |
| **Google/Apple Calendar sync** Premium | Mockup tier 3 | OAuth externo |
| **Phone verification SMS OTP** | KYC ligero | Twilio |
| **2FA admin** | Security | TOTP |
| **CDN media** | Performance | CloudFront / Bunny |

---

## 🚧 PENDIENTE — Se podría hacer en código (opcional)

- [ ] **Partner Module** (`Pulsar_Partner_Module.html` separado, nunca implementado)
- [ ] **Onboarding wizard para Partners**
- [ ] **Map view** de talentos en search
- [ ] **Favoritos / saved searches** cliente
- [ ] **Notification preferences** (push/email/in-app por tipo)
- [ ] **Bloqueo calendario por tipo de evento** (Pro tier)
- [ ] **Tests** (backend + frontend) — 0 actualmente
- [ ] **CI/CD** GitHub Actions
- [ ] **Account deletion / data export** GDPR
- [ ] **Logging estructurado**
- [ ] Landing mejorada + **Términos / Privacidad** + Meta SEO

---

## 📂 Archivos clave

### Backend
```
backend/
  talents/
    models.py            TalentProfile (+ service_zones, travel_fee_extra, tiktok)
                         Pack, TalentFAQ
    tier_limits.py       Source of truth gating
    filters.py           TalentFilter expandido (tier/lang/events/mood)
    serializers.py       Con response_time_hours + repeat_rate + review meta
    views.py             + TalentInquiryView + TalentPayoutView
  bookings/
    models.py            Booking, ClientCredit, PremiumInvitation, Dispute, AuditLog
    signals.py           Auto-promoción Standard→Pro
    anti_disinter.py     Scanner regex
    views.py             + DisputeCreate + BookingModify + ProcessRefund + BookingContract + BookingsExportCSV
  config/settings.py     DRF throttle + CORS
```

### Frontend
```
frontend/src/
  views/
    TalentProfileView.vue       14 secciones perfil + inquiry modal + share hero + mix featured + review filter/meta + cobertura textual
    BookingRequestView.vue      Wizard + tiles tipo evento
    PaymentView.vue             ⭐ Pantalla 3 Escrow completa
    BookingDetailView.vue       Countdown + chat + modals + download contract
    DashboardView.vue           KPIs + cards countdown
    TalentDashboardView.vue     Payout + escalera tier + mix destacado mgmt + service_zones + tiktok
    TalentOnboardingView.vue    Wizard 10 pasos
    AdminDashboardView.vue      Disputas + flagged + CSV
    TiersView.vue               Cards + tabla 16 filas comparativa + escalera
    HowItWorksView.vue          /como-funciona
    SearchView.vue              Filtros expandidos
  components/
    booking/ReviewForm.vue      5 dimensiones + crédito
    common/NavBar.vue
    talent/TalentCard.vue       Tier badges + CURADO
  utils/antiDisinter.js
  stores/{auth,theme}.js
```

---

## 🔌 Endpoints REST (completos)

### Auth (`/api/auth/`)
- POST `/register/`, `/login/`, `/refresh/`, `/google/`
- GET/PATCH `/me/`, POST `/me/avatar/`
- POST `/password-reset/`, `/password-reset/confirm/`

### Talents (`/api/`)
- GET `/genres/`, `/talents/`, `/talents/<id>/`, `/featured/`, `/stats/`
- POST `/talents/create/`, PATCH `/talents/me/`, POST `/talents/me/cover-photo/`
- GET/POST `/talents/<id>/media/`, GET/PATCH/DELETE `/talents/media/<pk>/`
- GET/POST `/talents/<id>/experiences/`
- GET `/talents/<id>/availability/`, POST `/availability/manage/`
- GET/POST `/talents/<id>/packs/`, GET/PATCH/DELETE `/talents/packs/<pk>/`
- GET/POST `/talents/<id>/faqs/`, GET/PATCH/DELETE `/talents/faqs/<pk>/`
- GET `/talents/me/tier-limits/`
- GET `/talents/me/payout/`
- **POST `/talents/<id>/inquire/`** (Enviar consulta)

### Bookings (`/api/`)
- GET/POST `/bookings/`, GET `/bookings/<id>/`, PATCH `/bookings/<id>/status/`
- POST `/payments/create/`, GET `/bookings/<id>/payments/`
- GET/POST `/bookings/<id>/messages/`, POST `/messages/send/`, POST `/bookings/<id>/messages/read/`
- GET `/notifications/`, POST `/notifications/read/`, GET `/notifications/unread-count/`
- POST `/bookings/<id>/review/`, GET `/talents/<id>/reviews/`
- PATCH `/reviews/<id>/response/` (Premium)
- GET `/credits/`
- GET `/bookings/<id>/cancel-preview/`
- POST `/bookings/<id>/dispute/`
- PATCH `/bookings/<id>/modify/`
- GET `/bookings/<id>/contract/` (HTML download)
- Premium invitations CRUD

### Admin (`/api/admin/`)
- Flagged messages + stats
- Disputes list + refund
- Bookings export CSV
- Platform config

---

## 📋 Migraciones aplicadas (10 total)

```
accounts/   0001, 0002_discovery_source
talents/    0001..0006 (mood, equipment, Pack, FAQ, service_zones+travel_fee, tiktok)
bookings/   0001..0009 (review dimensiones, booking_code, ITBMS, ClientCredit,
                       PremiumInvitation, Pro tier, Dispute, AuditLog)
```

---

## 🧪 Testing manual end-to-end

```bash
cd backend && python manage.py migrate && python manage.py runserver
cd ../frontend && npm install && npm run dev
```

### Flujo completo (15 min)
1. Cliente registra en `/register`
2. `/search` → filtra por tier=Pro, lang=Inglés, event=Boda, mood=Cocktail formal
3. Abre perfil DJ → ve:
   - Botón Compartir en hero ✓
   - Tooltip al hover sobre badge Premium ✓
   - Stats row "Eventos / Responde en / Miembro desde" ✓
   - Pricing "$X desde / 4 hrs · $Y/hr adicional" ✓
   - Sección Mixes con embeds + "Ver todos →" si hay >3 ✓
   - Sección Cobertura textual con zonas + "+$50 traslado" ✓
   - Reseñas con filtro "Filtrar ↓" + meta "Boda · 350 invitados · abril 2026" + tag "✓ Verificada" ✓
   - TikTok en redes ✓
4. Click **"Enviar consulta"** → modal con anti-disinter → talento recibe notificación
5. Click **"Reservar Ahora"** → wizard con **tiles visuales** de tipo de evento
6. Submit → modal con `booking_code` + timeline
7. Cuando booking pase a `pendiente_pago` → `/dashboard/bookings/:id/pay` muestra:
   - Hero escrow verde ✓
   - Timeline 3 pasos ✓
   - Tiles Tarjeta/ACH/Yappy ✓
   - Breakdown ITBMS ✓
   - Política cancelación ✓
   - 5 FAQs ✓
8. Cliente Dashboard → **cards countdown** + KPIs
9. BookingDetail → countdown banner + chat + download contract + 3 botones
10. `/tiers` → cards sticky + **tabla 16 filas comparativa** + escalera
11. `/como-funciona` → timeline escrow + 6 FAQs
12. Admin → tab Disputas + emite refund + CSV export

---

## 🎯 Roadmap soft launch

### Sprint 1 (1-2 semanas)
- [ ] Postgres + Railway/Supabase
- [ ] Stripe Connect + KYC mínimo
- [ ] SendGrid templates email
- [ ] Sentry + backups cron
- [ ] Tests críticos booking flow
- [ ] Términos + Privacidad legal

### Sprint 2
- [ ] Yappy/ACH Panamá
- [ ] WebSocket realtime
- [ ] Map view + favoritos
- [ ] Partner Module si hay demanda

### Sprint 3
- [ ] Mobile app + FCM
- [ ] Calendar sync Premium
- [ ] Music supervisor tooling

---

## ✅ Notas finales

- **100% del scope visual** de los 3 mockups MVP completo
- **Tema dual** claro/oscuro funcionando
- **Mobile responsive** todas las vistas
- **Stack**: Vue 3 + Vite + Pinia + Django 5 + DRF + SQLite (dev)
- **Lo único que falta para producción es infra externa** (cuentas de pago, hosting, email)

> Single source of truth: este documento + mockups en root (`Pulsar_*.html`) + `Pulsar_Mockups_Overview.md`.
