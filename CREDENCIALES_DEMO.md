# 🔐 Credenciales de Usuarios Demo — ShowRoots (Pulsar)

> Archivo de referencia para validación y testing de perfiles.
> Última actualización: 2026-04-30

---

## 🔑 Contraseña Única

| Todos los usuarios (excepto Admin) | **`Show2026!`** |
|-------------------------------------|-----------------|

---

## 🔴 ADMIN

| Usuario | Contraseña | Email | Rol | Notas |
|---------|-----------|-------|-----|-------|
| `admin` | `admin123` | admin@webdj.com | Admin (superuser) | Acceso total + Django Admin |

---

## 🎵 TALENTOS

### ⭐ Premium

| # | Usuario | Nombre | Stage Name | Tipo | Ciudad | Email | Instagram |
|---|---------|--------|------------|------|--------|-------|-----------|
| 1 | `djvoltex` | Carlos Mendoza | DJ Voltex | DJ | Caracas | carlos@showroots.com | @djvoltex |
| 2 | `mariafuego` | María Fuentes | María Fuego | Músico | Valencia | maria@showroots.com | @mariafuego |
| 3 | `losvientos` | Roberto Herrera | Los Vientos del Caribe | Banda | Maracaibo | roberto@showroots.com | @losvientosdelcaribe |

### ○ Estándar

| # | Usuario | Nombre | Stage Name | Tipo | Ciudad | Email | Instagram |
|---|---------|--------|------------|------|--------|-------|-----------|
| 4 | `djnova` | Andrea Suárez | DJ Nova | DJ | Caracas | andrea@showroots.com | @djnova_ve |
| 5 | `elmaestro` | Fernando Castillo | El Maestro Castillo | Músico | Barquisimeto | fernando@showroots.com | @maestrocastillo |
| 6 | `rockforce` | Luis Ramírez | Rock Force | Banda | Mérida | luis@showroots.com | @rockforce_ve |

---

## 👤 CLIENTES

| # | Usuario | Nombre | Ciudad | Email |
|---|---------|--------|--------|-------|
| 1 | `cliente_ana` | Ana Martínez | Caracas | ana@cliente.com |
| 2 | `cliente_jose` | José Rodríguez | Valencia | jose@cliente.com |
| 3 | `cliente_laura` | Laura Pérez | Maracaibo | laura@cliente.com |

---

## 🤝 PARTNER

| # | Usuario | Nombre | Ciudad | Email |
|---|---------|--------|--------|-------|
| 1 | `partner_ricardo` | Ricardo Gómez | Caracas | ricardo@showroots.com |

---

## 📋 Resumen Rápido

| Rol | Cantidad | Contraseña |
|-----|----------|-----------|
| **Admin** | 1 | `admin123` |
| **Talentos Premium** | 3 | `Show2026!` |
| **Talentos Estándar** | 3 | `Show2026!` |
| **Clientes** | 3 | `Show2026!` |
| **Partner** | 1 | `Show2026!` |
| **Total** | **11** | — |

---

## ⚠️ Notas

- Todos los usuarios (excepto admin) usan la contraseña **`Show2026!`**
- El admin conserva su contraseña original `admin123`.
- Los usuarios fueron regenerados con `reset_users.py` el 30/04/2026.
- Para resetear una contraseña: `python manage.py changepassword <username>`
