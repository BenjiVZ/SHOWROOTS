# Migración SQLite → Postgres (Pulsar)

Guía mínima para mover los datos del `db.sqlite3` local al Postgres del droplet.

---

## EN TU PC (Windows)

### 1. Exportar todos los datos de SQLite a JSON

```powershell
cd c:\Users\PC\Proyectos\SHOWROOTS\backend
.\venv\Scripts\activate

python manage.py dumpdata `
    --natural-foreign `
    --natural-primary `
    --indent 2 `
    -e contenttypes `
    -e auth.permission `
    -e admin.logentry `
    -e sessions `
    -o pulsar_dump.json
```

Esto crea `backend/pulsar_dump.json` con todos los usuarios, talentos, bookings, packs, etc.

> Si el archivo pesa mucho (>50 MB), comprimílo:
> ```powershell
> Compress-Archive pulsar_dump.json pulsar_dump.zip
> ```

### 2. Subir el dump al droplet

```powershell
scp pulsar_dump.json deploy@IP_DEL_DROPLET:/home/deploy/pulsar/backend/
```

---

## EN EL DROPLET

### 3. Crear DB Postgres (si todavía no existe)

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE pulsar;
CREATE USER pulsar_user WITH PASSWORD 'CAMBIA_ESTA_PASSWORD';
ALTER ROLE pulsar_user SET client_encoding TO 'utf8';
ALTER ROLE pulsar_user SET timezone TO 'America/Caracas';
GRANT ALL PRIVILEGES ON DATABASE pulsar TO pulsar_user;
\c pulsar
GRANT ALL ON SCHEMA public TO pulsar_user;
SQL
```

### 4. Configurar `.env` apuntando a Postgres

```bash
cd ~/pulsar/backend
cp .env.example .env
nano .env
```

Como mínimo, completá:
```
DB_ENGINE=postgres
DB_NAME=pulsar
DB_USER=pulsar_user
DB_PASSWORD=la-password-del-paso-3
DB_HOST=localhost
DB_PORT=5432
```

### 5. Aplicar migraciones (estructura vacía)

```bash
cd ~/pulsar/backend
source venv/bin/activate

python manage.py migrate
```

> Esto crea todas las tablas, pero **vacías**. Acá Django también inserta sus content types y permissions — por eso los excluimos en el dump.

### 6. Cargar los datos del JSON

```bash
python manage.py loaddata pulsar_dump.json
```

Si todo sale bien vas a ver `Installed N object(s) from 1 fixture(s)`.

### 7. Verificar

```bash
python manage.py shell -c "
from accounts.models import User
from talents.models import TalentProfile
from bookings.models import Booking
print(f'Users: {User.objects.count()}')
print(f'Talents: {TalentProfile.objects.count()}')
print(f'Bookings: {Booking.objects.count()}')
"
```

Compará contra los números del SQLite local.

### 8. Borrar el dump del servidor

```bash
rm ~/pulsar/backend/pulsar_dump.json
```

(Tiene passwords hasheadas y datos personales — no lo dejes ahí.)

---

## Errores comunes

| Error | Solución |
|---|---|
| `IntegrityError: duplicate key value` al cargar | La DB no estaba vacía. `python manage.py flush` y volvé a migrar/cargar. |
| `UnicodeDecodeError` al cargar | Subí el archivo con `scp` (binario), no copy-paste por SSH. |
| `relation "X" does not exist` | Te falta `python manage.py migrate` antes del loaddata. |
| Usuarios no pueden entrar | Las passwords están hasheadas, OK. Si usaban Google OAuth verificá que el `google_id` se haya migrado. |
| `psycopg2.OperationalError: password authentication failed` | La password del `.env` no coincide con la del `CREATE USER`. |

---

## Migrar también las fotos (`backend/media/`)

Los uploads NO van en el JSON. Hay 2 opciones:

### Opción A — Copiarlos al droplet

```powershell
# Desde tu PC
scp -r c:\Users\PC\Proyectos\SHOWROOTS\backend\media\* `
    deploy@IP_DEL_DROPLET:/home/deploy/pulsar/backend/media/
```

### Opción B — Mandarlos a Spaces (recomendado)

Después de configurar `USE_SPACES=True` en el `.env`, desde tu PC:

```powershell
pip install s3cmd
s3cmd --configure   # te pide SPACES_KEY/SECRET y el endpoint nyc3.digitaloceanspaces.com
s3cmd sync c:\Users\PC\Proyectos\SHOWROOTS\backend\media\ s3://pulsar-media/ --acl-public
```

Listo. Las URLs de las fotos en la DB ya apuntan a rutas relativas (`media/avatars/...`), y Django va a resolver contra Spaces automáticamente.
