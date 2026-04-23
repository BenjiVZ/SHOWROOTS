### MODELO DEL SISTEMA
### ShowRoots funcionará como una plataforma curada, no
### completamente automática.
### El flujo de reservas será el siguiente:
### 1. El cliente solicita disponibilidad o cotización.
### 2. El talento revisa la solicitud.
### 3. El talento puede aceptar, rechazar o ajustar la propuesta.
### 4. Una vez aceptada, el cliente puede proceder con el
### pago.
### 5. El pago confirma la reserva.
- El cliente deberá definir:
- fecha del evento
- hora de inicio
- duración del servicio (horas)
- El sistema calculará el precio estimado en base a:
- tarifa por hora del talento
- duración del evento
### Esto permite garantizar calidad, disponibilidad real y
### control de la experiencia.
### FUNCIONES DEL SISTEMA

### ROLES DEL SISTEMA
#### 1. Cliente (el que contrata)
#### 2. Talento (DJ, músico, banda)
#### 3. Admin (ShowRoots)
#### FUNCIONES POR ROL
### CLIENTE
#### Funciones:
●​ Crear cuenta (El cliente SÍ puede cotizar sin crear cuenta,pero debe crear cuenta
para reservar/pagar)
●​ Buscar talentos (por ciudad, género musical, presupuesto)
●​ Ver perfiles (videos, fotos, bio, reviews)
●​ Solicitar cotización del talento que desee, el talento previamente tiene una tarifa que
el coloco por hora pero hay dos opciones una donde el cliente pueda enviar un
mensaje al talento solicitando la reserva
●​ Reservar con un porcentaje o la totalidad del monto
●​ Se envía notificación a talento y al que contrata y se abre un portal donde se puedan
enviar mensajes y coordinar el evento
●​ Dejar review después del evento
#### Ejemplo real:
1.​ Entra a ShowRoots
2.​ Lo primero que coloca es: tipo de talento, ubicación del evento y la fecha.

3.​ Lo lleva a la pagina de perfiles (dependiendo del talento que haya escogido se filtran
los talentos, si es musico, banda o DJ)
4.​ Hace clic en el talento que quiere y entra al perfil (ya ahi dentro puede ver toda la
información inclusive el precio por hora de ese DJ, Fotos, videos, biografia, resenas,
videos, fotos ​
Aqui dejo Link de ejemplo: https://cueup.io/es/user/meliee
5.​ Solicita cotización y asi podria ser la pagina de reserva donde el cliente puede ver un
detalle previo en base a la tarifa por hora y tener un estimado y agregar otros

detalles que capaz no haya agregado antes.
6.​ Aqui el cliente puede ver un estimado en base a horas pero eso puede variar
dependiendo de varios factores que lo establece el dj en el chat luego → cliente
recibe propuesta final (puede cambiar precio)
7.​ → cliente acepta propuesta
8.​ → cliente paga
9.​
10.​Una vez ya cancelado se le manda confirmación a ambos tanto al cliente como al
artista

#### CLIENTE
- El cliente podrá ver un precio estimado antes de enviar la solicitud.
- El cliente podrá recibir una propuesta final ajustada por el talento antes de pagar.
- El cliente deberá crear una cuenta únicamente en el momento de reservar o pagar.
- El sistema podrá crear automáticamente una cuenta con el email ingresado durante la
cotización.
**El sistema debe permitir que el cliente cotice sin crear cuenta.**
**El registro será obligatorio solo en el momento de reservar o pagar.**
**Idealmente, el sistema puede crear una cuenta automática con el email ingresado**
#### durante la cotización para facilitar el proceso.
#### ESTADOS DE UNA RESERVA
#### Cada solicitud o reserva tendrá los siguientes estados:
- Solicitud enviada
- Pendiente de respuesta del talento
- Aceptada
- Rechazada
- Pendiente de pago
- Confirmada (pagada)
- Completada
- Cancelada
**Estos estados permitirán organizar el flujo interno del sistema y dar visibilidad tanto**
#### al cliente como al talento.
#### MONETIZACIÓN DE LA PLATAFORMA
#### ShowRoots generará ingresos mediante:

- Comisión por cada reserva confirmada (ej: 10%–20%)
- Fee de servicio al cliente (opcional)
- Opciones de posicionamiento destacado para talentos (featured)
**El sistema deberá calcular automáticamente la comisión en cada transacción.**
### TALENTO (DJ, MÚSICO, BANDA) (si quieres aqui te puedo
### dar acceso a mi cue up o puedes crearte un perfil y asi ves
### la parte interna del perfil de talento)
#### Funciones:
- Crear perfil profesional
- Subir fotos, videos y biografía
- Definir géneros musicales
- Definir precio base (por hora o paquete)
- Configurar disponibilidad (calendario)
- Recibir solicitudes de clientes
- Aceptar, rechazar o ajustar solicitudes
- Enviar mensajes al cliente dentro de la plataforma
- Ver historial de reservas
- Ver ingresos generados
- Recibir notificaciones de nuevas solicitudes y pagos
#### IMPORTANTE:
El talento debe aceptar la solicitud antes de que el cliente pueda realizar el pago final.
Ellos tienen algo muy cool y que monetizan bien y es que si el talento viaja puede cambiar
su locacion.

#### ADMIN (SHOWROOTS)
#### Funciones:
- Aprobar o rechazar talentos (control de calidad)
- Ver todos los usuarios registrados
- Editar perfiles si es necesario
- Ver todas las reservas del sistema
- Intervenir en disputas entre cliente y talento
- Configurar comisión de la plataforma
- Ver ingresos totales de la plataforma
- Acceder a dashboard con métricas:
- número de reservas
- ingresos
- talentos activos
- Gestionar contenido destacado (featured talentos)
#### MENSAJERÍA INTERNA
El sistema contará con un chat interno entre cliente y talento.
Condiciones:
- El chat se activará una vez que el cliente envíe una solicitud.

- El chat completo se habilita cuando el talento acepta la solicitud.
- El sistema puede limitar el intercambio de información de contacto (teléfono, redes) antes
del pago para evitar que los usuarios salgan de la plataforma.
- El chat estará vinculado a cada reserva específica.
Esto permite mantener la comunicación dentro de la plataforma.
#### DISPONIBILIDAD
El talento podrá configurar su disponibilidad mediante un calendario.
El sistema deberá:
- Evitar doble reserva en una misma fecha
- Bloquear fechas automáticamente cuando haya una reserva confirmada
- Permitir editar disponibilidad manualmente
#### FUNCIONES FUTURAS
El sistema podrá escalar para incluir:
- Recomendación automática de talentos (IA)
- Sistema de ranking de talentos
- Publicación de eventos
- Venta de tickets
- Dashboard financiero para talentos
- Integración con WhatsApp
​
### FLUJO GENERAL DEL SISTEMA
#### Flujo del cliente

1.​ El cliente entra a la plataforma.
2.​ Selecciona:
○​ tipo de talento
○​ ubicación del evento
○​ fecha
3.​ El sistema muestra los talentos disponibles según los filtros.
4.​ El cliente entra al perfil del talento.
5.​ Ve información del perfil:
○​ fotos
○​ videos
○​ biografía
○​ géneros musicales
○​ tarifa base
○​ reseñas
6.​ El cliente llena los detalles del evento.
7.​ El sistema muestra un precio estimado.
8.​ El cliente envía una solicitud de reserva o cotización.
9.​ El talento recibe la solicitud.
10.​El talento puede:
●​ aceptar
●​ rechazar
●​ ajustar la propuesta
11.​Si el talento acepta o ajusta, el cliente recibe la propuesta final.
12.​El cliente crea cuenta o inicia sesión para continuar.
13.​El cliente paga un porcentaje o el total.
14.​El sistema confirma la reserva.
15.​Se habilita el chat interno para coordinar detalles.
16.​Después del evento, el cliente puede dejar una reseña.
#### Flujo del talento
1.​ El talento crea su cuenta.
2.​ Completa su perfil profesional.
3.​ Configura:
○​ géneros
○​ ubicación
○​ tarifa
○​ disponibilidad
4.​ Recibe solicitudes de clientes.
5.​ Revisa detalles del evento.
6.​ Decide si acepta, rechaza o ajusta.
7.​ Si el cliente paga, recibe confirmación.
8.​ Gestiona la comunicación desde el chat interno.
9.​ Visualiza historial de reservas e ingresos.

#### Flujo del admin
1.​ Admin accede al panel interno.
2.​ Revisa nuevos talentos registrados.
3.​ Aprueba o rechaza perfiles.
4.​ Supervisa reservas activas.
5.​ Monitorea pagos y comisiones.
6.​ Gestiona incidencias o disputas.
7.​ Ve métricas generales de la plataforma.
### Estructura de base de datos básica
### TABLAS PRINCIPALES DEL SISTEMA
#### 1. Usuarios
### Guarda la información general de todos los usuarios.
### Campos:
### ●​ id
### ●​ nombre
### ●​ apellido
### ●​ email
### ●​ teléfono
### ●​ contraseña
### ●​ rol (cliente, talento, admin)
### ●​ fecha de creación
### ●​ estado de cuenta
#### 2. Talentos
### Información específica del talento.
### Campos:
### ●​ id
### ●​ user_id

### ●​ nombre artístico
### ●​ tipo de talento (DJ, músico, banda)
### ●​ biografía
### ●​ ciudad
### ●​ país
### ●​ tarifa base por hora
### ●​ foto de perfil
### ●​ portada
### ●​ estado de aprobación
### ●​ destacado (sí/no)
### ●​ rating promedio
#### 3. Géneros musicales
### Campos:
### ●​ id
### ●​ nombre
#### 4. Talento_Géneros
### Relaciona cada talento con varios géneros.
### Campos:
### ●​ id
### ●​ talento_id
### ●​ genero_id
#### 5. Media del talento
### Para fotos y videos del perfil.
### Campos:

### ●​ id
### ●​ talento_id
### ●​ tipo_archivo (foto/video)
### ●​ url
### ●​ orden
#### 6. Disponibilidad
### Calendario del talento.
### Campos:
### ●​ id
### ●​ talento_id
### ●​ fecha
### ●​ hora_inicio
### ●​ hora_fin
### ●​ estado (disponible, bloqueado, reservado)
#### 7. Solicitudes / Reservas
### Esta es la tabla más importante.
### Campos:
### ●​ id
### ●​ cliente_id
### ●​ talento_id
### ●​ fecha_evento
### ●​ hora_inicio
### ●​ hora_fin
### ●​ ubicación_evento
### ●​ ciudad_evento
### ●​ tipo_evento
### ●​ descripción

### ●​ precio_estimado
### ●​ precio_final
### ●​ porcentaje_reserva
### ●​ monto_pagado
### ●​ estado
### Estados recomendados:
### ●​ solicitud_enviada
### ●​ pendiente_respuesta
### ●​ aceptada
### ●​ rechazada
### ●​ pendiente_pago
### ●​ confirmada
### ●​ completada
### ●​ cancelada
#### 8. Pagos
### Campos:
### ●​ id
### ●​ reserva_id
### ●​ cliente_id
### ●​ monto
### ●​ tipo_pago (abono / total)
### ●​ estado_pago
### ●​ método_pago
### ●​ fecha_pago
### ●​ comisión_showroots
#### 9. Mensajes / Chat
### Campos:

### ●​ id
### ●​ reserva_id
### ●​ remitente_id
### ●​ mensaje
### ●​ archivo_url
### ●​ fecha_envío
### ●​ leído
#### 10. Reviews / Reseñas
### Campos:
### ●​ id
### ●​ reserva_id
### ●​ cliente_id
### ●​ talento_id
### ●​ puntuación
### ●​ comentario
### ●​ fecha
#### 11. Notificaciones
### Campos:
### ●​ id
### ●​ user_id
### ●​ tipo
### ●​ título
### ●​ mensaje
### ●​ leído
### ●​ fecha
### NOTIFICACIONES

### El sistema deberá enviar notificaciones en los siguientes
### casos:
### ● Nueva solicitud recibida (talento)
### ● Solicitud aceptada o rechazada (cliente)
### ● Pago realizado (ambos)
### ● Reserva confirmada (ambos)
### ● Recordatorio previo al evento
### ● Nueva reseña recibida
### Las notificaciones pueden ser por:
### - email
### - dentro de la plataforma
### MVP vs versión avanzada
#### Cliente
### ●​ buscar talentos
### ●​ ver perfil
### ●​ enviar solicitud
### ●​ registrarse/iniciar sesión
### ●​ pagar reserva
### ●​ recibir confirmación

#### Talento
### ●​ crear perfil
### ●​ subir fotos/videos
### ●​ configurar tarifa base
### ●​ aceptar/rechazar solicitudes
### ●​ ver reservas
#### Admin
### ●​ aprobar talentos
### ●​ ver reservas
### ●​ ver pagos
### ●​ gestionar usuarios
#### Sistema
### ●​ notificaciones por email
### ●​ estados de reserva
### ●​ calendario básico
### ●​ reseñas simples
### Versión avanzada
### Esto puede venir después:
### ●​ chat en tiempo real
### ●​ integración con WhatsApp
### ●​ IA para recomendar talentos
### ●​ dashboard financiero más completo
### ●​ sistema de talentos destacados pagados
### ●​ cupones o promociones
### ●​ paquetes por evento
### ●​ multiciudad / multipaís
### ●​ facturación automática

# Qué debe hacer cada rol, bien claro
### CLIENTE
### Puede:
### ●​ explorar talentos
### ●​ filtrar búsqueda
### ●​ ver precios estimados
### ●​ enviar solicitud
### ●​ pagar
### ●​ chatear después de reservar
### ●​ dejar reseña
### ●​ ver historial de reservas
### No puede:
### ●​ editar perfiles de talentos
### ●​ ver panel de admin
### ●​ saltarse el pago para confirmar
### TALENTO
### Puede:
### ●​ editar perfil
### ●​ definir precios
### ●​ subir contenido
### ●​ ver solicitudes
### ●​ aceptar / rechazar / ajustar
### ●​ bloquear fechas
### ●​ ver reservas
### ●​ ver ingresos
### No puede:

### ●​ aprobarse a sí mismo si la plataforma es curada
### ●​ editar sistema global
### ●​ modificar reservas ya pagadas sin control
### ADMIN
### Puede:
### ●​ aprobar talentos
### ●​ editar usuarios
### ●​ supervisar reservas
### ●​ cambiar estados si hace falta
### ●​ ver pagos y comisiones
### ●​ resolver disputas
### ●​ destacar perfiles
### ●​ ver métricas generales
### Módulo 1: autenticación
### ●​ registro
### ●​ login
### ●​ recuperación de contraseña
### Módulo 2: perfiles de talento
### ●​ info pública
### ●​ media
### ●​ géneros
### ●​ tarifas
### Módulo 3: búsqueda y filtros

### ●​ ciudad
### ●​ tipo
### ●​ género
### ●​ precio
### Módulo 4: solicitudes y reservas
### ●​ formulario de solicitud
### ●​ estados
### ●​ aceptación del talento
### Módulo 5: pagos
### ●​ porcentaje o total
### ●​ confirmación de reserva
### Módulo 6: mensajería
### ●​ coordinación entre cliente y talento
### Módulo 7: admin
### ●​ aprobar talentos
### ●​ ver bookings
### ●​ monitorear ingresos
### ESTRUCTURA FUNCIONAL DEL SISTEMA
### ShowRoots será una plataforma curada para conectar clientes
### con DJs, músicos y bandas.
### La lógica principal del sistema será:
### 1.​El cliente podrá explorar talentos sin necesidad de crear
### cuenta.
### 2.​El cliente podrá ver perfiles, contenido y precio estimado.
### 3.​El cliente enviará una solicitud de reserva o cotización.

### 4.​El talento recibirá la solicitud y podrá aceptarla,
### rechazarla o ajustarla.
### 5.​Una vez aprobada la solicitud, el cliente deberá
### registrarse o iniciar sesión para pagar.
### 6.​El pago confirmará la reserva.
### 7.​Luego de la confirmación, ambas partes podrán
### comunicarse dentro de la plataforma.
### 8.​Al finalizar el evento, el cliente podrá dejar una reseña.
### El sistema contará con tres roles principales:
### ●​ Cliente
### ●​ Talento
### ●​ Admin
### El sistema deberá incluir como módulos mínimos:
### ●​ autenticación de usuarios
### ●​ perfiles de talento
### ●​ búsqueda y filtros
### ●​ solicitudes y reservas
### ●​ pagos
### ●​ mensajería interna
### ●​ panel administrativo
#### Fase 1
### ●​ perfiles
### ●​ búsqueda
### ●​ solicitud
### ●​ aceptación
### ●​ pago
### ●​ admin
#### Fase 2
### ●​ chat
### ●​ reviews

### ●​ calendario mejorado
#### Fase 3
### ●​ automatizaciones
### ●​ IA
### ●​ escalabilidad internacional
### REGLAS DE NEGOCIO
### ● Un talento no puede recibir pagos sin haber aceptado la solicitud
### previamente.
### ● Una reserva no se considera confirmada hasta que exista un
### pago registrado.
### ● Una fecha no puede ser reservada por más de un cliente para el
### mismo talento.
### ● El sistema bloqueará automáticamente fechas cuando una
### reserva esté confirmada.
### ● El cliente solo podrá dejar una reseña si la reserva está en
### estado "completada".
### ● El talento no podrá modificar una reserva una vez esté pagada,
### sin intervención del admin.
### ● El sistema debe calcular automáticamente la comisión de
### ShowRoots en cada pago.
### ● Si una solicitud no es respondida por el talento en X tiempo (ej:
### 24h), puede expirar automáticamente.
### LÓGICA DE PAGOS

### ● El cliente podrá pagar:
### - Un porcentaje (ej: 50%)
### - El total del evento
### ● El pago inicial bloquea la fecha.
### ● El monto restante (si aplica) deberá pagarse antes del evento o
### según condiciones definidas.
### ● El sistema debe dividir automáticamente:
### - Comisión de ShowRoots
### - Pago al talento
### ● El talento podrá visualizar el monto neto a recibir.
### ● El admin podrá ver todos los movimientos de pagos.
### SEGURIDAD Y CONTROL
### ● El sistema deberá proteger la información de los usuarios.
### ● Los pagos deberán procesarse mediante plataformas seguras.
### ● El admin tendrá control total para intervenir en reservas en caso
### de disputa.
### ● El sistema registrará historial de acciones importantes (logs).


###otros datos:

###Primo sabes que me gustaria 

La plataforma no será solo un marketplace abierto.

Tendrá dos niveles de talento dentro del mismo sistema:

Talentos seleccionados (premium)
Talentos estándar (open)

La idea es que el cliente vea primero los talentos premium, pero que también existan opciones más económicas en segundo plano.

Esto nos permite mantener calidad alta sin perder volumen de clientes.

en la tabla de talentos 
Podrias agregar: 
nivel_talento:
- premium
- standard
- ⁠
Cuando el cliente busque talentos:

Primero deben mostrarse los talentos con nivel "premium"
Luego los talentos "standard"

Dentro de cada grupo se pueden ordenar por:

rating
precio
relevancia

Los talentos premium deben tener:
más visibilidad en la plataforma
aparecer primero en resultados
posibilidad de destacarse visualmente (badge o etiqueta)

DIFERENCIA EN UX
Que visualmente se note:

Premium:
más grande
mejor diseño
badge
más fotos visibles

Standard:
más simple
menos protagonismo

DIFERENCIA EN LÓGICA DE NEGOCIO
Más adelante:

Talentos standard pagan más comisión
Talentos premium tienen beneficios
Se puede cobrar por subir de nivel


FLUJO COMPLETO
Talento se registra
Queda como standard por defecto
Admin (tú) decide si lo sube a premium
En la plataforma:
premium arriba
standard abajo

No es un filtro visual solamente, es una lógica de negocio donde el orden de los resultados depende del nivel del talento.

Esto es importante porque queremos evitar que la plataforma se vuelva como un marketplace lleno de opciones malas.

Queremos controlar la calidad y al mismo tiempo no perder oportunidades de negocio.

Necesitamos que los talentos tengan un nivel (premium o standard).

En los resultados:

premium siempre aparece primero
standard después

El admin puede cambiar ese nivel manualmente.


###otro:

Nuevo rol: Partner ShowRoots

Función:
Personas que consiguen clientes y usan la plataforma para encontrar DJs.

Pueden:
- buscar talentos
- crear reservas
- gestionar eventos
- ganar comisión

Lógica:
- cada reserva puede tener un partner
- el sistema calcula comisión automáticamente

Objetivo:
convertir la plataforma en una red de ventas escalable

# DOCUMENTO FUNCIONAL – ROL PARTNER SHOWROOTS

---

## 1. NUEVO ROL DEL SISTEMA

### Nombre del rol:
Partner ShowRoots

---

## 2. DEFINICIÓN DEL ROL

El Partner ShowRoots representa a personas o empresas que ya trabajan consiguiendo clientes o gestionando eventos (DJs, productores, planners, etc).

El Partner puede utilizar la plataforma para:

- Buscar talentos cuando no pueda cubrir un evento  
- Referir clientes a talentos dentro de la plataforma  
- Gestionar reservas en nombre de sus clientes  

El Partner actúa como intermediario entre el cliente final y el talento.

---

## 3. FUNCIONES DEL PARTNER

- Crear cuenta como Partner  
- Buscar talentos dentro de la plataforma  
- Ver perfiles, precios y disponibilidad  

- Crear una solicitud de reserva en nombre de un cliente  
- Gestionar múltiples eventos  

- Recibir comisión por cada reserva generada  
- Ver historial de reservas realizadas  

- Acceder a un dashboard con:
  - eventos activos  
  - ingresos generados  
  - estado de sus bookings  

---

## 4. FLUJO DEL PARTNER

1. El Partner recibe un cliente (ej: alguien le pide un DJ)  
2. El Partner entra a ShowRoots  
3. Busca talento disponible según:
   - fecha  
   - ubicación  
   - tipo de evento  

4. Selecciona un DJ de la plataforma  
5. Envía solicitud de reserva  

6. El talento acepta o ajusta  
7. El Partner confirma con su cliente  
8. Se realiza el pago a través de la plataforma  
9. Reserva confirmada  

10. El Partner recibe una comisión por ese booking  

---

## 5. MONETIZACIÓN DEL PARTNER

El Partner generará ingresos por cada reserva que gestione.

### Modelo base:

- La plataforma cobra comisión (ej: 20%)  
- De esa comisión, el Partner recibe un porcentaje  

### Ejemplo:

Evento: $500  
Comisión ShowRoots: 20% = $100  

Distribución:
- Partner: $30  
- ShowRoots: $70  

---

## 6. MODELO AVANZADO (RECOMENDADO)

El Partner puede aumentar el precio al cliente final.

### Ejemplo:

Precio DJ en plataforma: $400  
Partner vende al cliente en: $500  

Ganancia del Partner: $100  

Esto incentiva el uso de la plataforma y genera mayor volumen de ventas.

---

## 7. LÓGICA DEL SISTEMA

- El Partner actúa como un tipo especial de cliente  
- Puede crear reservas, pero marcadas como:
  “reserva gestionada por partner”  

Cada reserva debe guardar:
- partner_id  
- cliente_final (opcional)  
- talento_id  

El sistema debe calcular automáticamente:
- comisión de ShowRoots  
- comisión del Partner  

---

## 8. CAMBIOS EN BASE DE DATOS

### Tabla Usuarios:
Agregar nuevo rol:
- cliente  
- talento  
- admin  
- partner  

---

### Tabla Reservas:
Agregar:
- partner_id (opcional)  
- tipo_reserva (directa / partner)  

---

### Tabla Pagos:
Agregar:
- comisión_partner  

---

## 9. DASHBOARD DEL PARTNER

El Partner podrá ver:

- Total de reservas generadas  
- Ingresos generados  
- Reservas activas  
- Historial de eventos  
- Estado de cada booking  

---

## 10. IMPORTANCIA DEL ROL

Este rol permite convertir la plataforma en una red de ventas.

En lugar de depender solo de clientes directos, otras personas pueden traer clientes y usar la plataforma como herramienta.

Esto permite escalar el negocio más rápido.

---

## 11. EJEMPLOS DE PARTNERS

- DJs que no pueden cubrir fechas  
- Productores de eventos  
- Wedding planners  
- Managers  
- Promotores  
- Dueños de locales  

---

## 12. RESUMEN GENERAL

Nuevo rol: Partner ShowRoots  

Función:
Personas que consiguen clientes y usan la plataforma para encontrar DJs.  

Pueden:
- buscar talentos  
- crear reservas  
- gestionar eventos  
- ganar comisión  

Lógica:
- cada reserva puede tener un partner  
- el sistema calcula comisión automáticamente  

Objetivo:
Convertir la plataforma en una red de ventas escalable  

---

## 13. VISIÓN

ShowRoots no será solo una plataforma de DJs.

Será una red de distribución de talento, donde múltiples actores pueden generar negocio dentro del sistema.

#### otro:

ESTRUCTURA DEL FORMULARIO DE COTIZACIÓN / RESERVA

Objetivo:
Permitir que el cliente solicite un DJ o talento musical y, al mismo tiempo, agregar servicios de producción adicional como sonido, luces, DJ booth y otros elementos del evento.

La idea es que el formulario sea simple al inicio, pero que se vuelva más detallado según lo que el cliente seleccione.

--------------------------------------------------
1. PASO 1: INFORMACIÓN BÁSICA DEL EVENTO
--------------------------------------------------

Campos:
- Tipo de talento que busca
  Opciones:
  - DJ
  - Músico
  - Banda

- Fecha del evento

- Hora de inicio

- Duración del servicio
  Ejemplo:
  - 2 horas
  - 3 horas
  - 4 horas
  - 5+ horas

- Ubicación del evento
  - Dirección o zona
  - Ciudad

- Tipo de evento
  Opciones:
  - Boda
  - Cumpleaños
  - Corporativo
  - Rooftop
  - Restaurante / bar
  - Evento privado
  - Otro

- Cantidad aproximada de personas

- Evento interior o exterior
  Opciones:
  - Interior
  - Exterior

--------------------------------------------------
2. PASO 2: BÚSQUEDA Y SELECCIÓN DE TALENTO
--------------------------------------------------

Después de completar lo anterior, el sistema debe mostrar talentos sugeridos según:
- tipo de talento
- fecha
- ubicación
- estilo / género
- presupuesto si aplica

Cada perfil debe mostrar:
- nombre artístico
- foto
- géneros musicales
- tarifa base
- reviews
- videos / contenido

El cliente podrá:
- entrar al perfil
- ver detalles
- hacer clic en “Reservar” o “Solicitar cotización”

--------------------------------------------------
3. PASO 3: DETALLES DEL TALENTO / EVENTO
--------------------------------------------------

Una vez el cliente selecciona el talento, debe completar:

- Género musical o ambiente deseado
  Ejemplo:
  - House
  - Open format
  - Reggaetón
  - Lounge
  - Afro house
  - Comercial
  - Otro

- Descripción del evento
  Campo abierto para explicar mejor lo que necesita

- Presupuesto estimado (opcional)

- ¿Desea enviar un mensaje adicional al talento?
  Campo abierto

--------------------------------------------------
4. PASO 4: SERVICIOS ADICIONALES / PRODUCCIÓN
--------------------------------------------------

Sección:
“Producción adicional para tu evento”

Opciones seleccionables:
- Sonido
- Luces
- DJ Booth
- Micrófono
- Pantalla / visuales
- Piso LED
- Técnico / montaje
- Otro

El cliente puede marcar uno o varios.

--------------------------------------------------
5. PASO 5: PREGUNTAS DINÁMICAS SEGÚN SERVICIO
--------------------------------------------------

A. SI ELIGE SONIDO
Campos:
- ¿Para cuántas personas necesita el sonido?
- ¿El evento es interior o exterior?
- ¿Necesita micrófono?
- ¿Habrá discursos o animación?
- ¿Habrá músicos en vivo o solo DJ?
- ¿Desea sonido básico o mayor refuerzo?

B. SI ELIGE LUCES
Campos:
- Tipo de luces deseadas:
  - Ambientales
  - Fiesta
  - Arquitectónicas
  - Moving heads
- ¿Desea iluminación decorativa o de show?

C. SI ELIGE DJ BOOTH
Campos:
- Tipo de booth:
  - Estándar
  - Blanco
  - Con branding
  - Con pantalla / visuales

D. SI ELIGE PANTALLAS / VISUALES
Campos:
- ¿Desea mostrar branding, logos o visuales?
- ¿Tiene contenido propio o necesita apoyo creativo?

E. SI ELIGE PISO LED
Campos:
- Tamaño aproximado requerido
- ¿El área es plana?
- ¿Es interior o exterior?

F. SI ELIGE TÉCNICO / MONTAJE
Campos:
- ¿Requiere soporte técnico durante el evento?
- ¿Hay horario especial de montaje o desmontaje?

--------------------------------------------------
6. PASO 6: RESUMEN Y ESTIMADO
--------------------------------------------------

Antes de enviar la solicitud, el sistema debe mostrar un resumen con:

- talento seleccionado
- fecha
- horario
- duración
- ubicación
- tipo de evento
- servicios adicionales seleccionados

El sistema puede mostrar:
- un precio estimado base
o
- un mensaje de “cotización personalizada”

Recomendación:
En fase 1, mostrar precio estimado del talento y dejar los extras para validación manual del admin.

--------------------------------------------------
7. PASO 7: DATOS DEL CLIENTE
--------------------------------------------------

Si el cliente todavía no tiene cuenta, aquí debe colocar:

- nombre
- apellido
- email
- teléfono / WhatsApp

Y luego:
- continuar sin cuenta para enviar solicitud
o
- crear cuenta al momento de reservar / pagar

Ideal:
el sistema puede generar una cuenta automáticamente con el email.

--------------------------------------------------
8. PASO 8: ENVÍO DE SOLICITUD
--------------------------------------------------

Cuando el cliente envía la solicitud:

- el talento recibe la solicitud
- admin también puede verla
- la solicitud queda con estado:
  “pendiente de respuesta”

Luego el talento puede:
- aceptar
- rechazar
- ajustar propuesta

--------------------------------------------------
9. PASO 9: PROPUESTA FINAL Y PAGO
--------------------------------------------------

Si el talento o admin aprueban la solicitud:

El cliente recibe:
- propuesta final
- precio ajustado
- monto de reserva (porcentaje o total)

Luego puede:
- pagar abono
- pagar total

Una vez pagado:
- reserva confirmada
- se bloquea fecha
- se habilita comunicación interna

--------------------------------------------------
10. RECOMENDACIONES DE UX
--------------------------------------------------

- El formulario debe estar dividido por pasos, no en una sola pantalla.
- Debe ser visual, simple y progresivo.
- Solo mostrar preguntas adicionales si el cliente selecciona servicios extra.
- En móvil debe sentirse rápido y limpio.
- Debe existir opción de “guardar y continuar” en fases futuras.

--------------------------------------------------
11. LÓGICA DE NEGOCIO
--------------------------------------------------

- El cliente puede cotizar sin crear cuenta
- El registro será obligatorio para pagar o confirmar
- El talento debe aceptar antes del pago final
- Los servicios adicionales pueden ser aprobados manualmente por admin en fase 1
- En una fase más avanzada, el sistema podrá calcular automáticamente servicios y precios sugeridos

--------------------------------------------------
12. ESTRUCTURA INTERNA RECOMENDADA
--------------------------------------------------

El formulario debe guardar:
- datos del evento
- talento seleccionado
- servicios adicionales
- respuestas dinámicas
- datos del cliente
- estado de la solicitud

Esto permitirá crear una reserva completa y posteriormente convertirla en booking confirmado.

--------------------------------------------------
13. OBJETIVO DEL FORMULARIO
--------------------------------------------------

No debe ser solo un formulario de contacto.

Debe funcionar como:
- captador de leads
- sistema de cotización
- inicio del proceso de reserva
- herramienta de upsell de producción adicional