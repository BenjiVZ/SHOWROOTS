# 🚀 Deploy a DigitalOcean — Comandos SSH en orden

> Copiá y pegá bloque por bloque. Si algo da error, parate ahí y avisame antes de seguir.

---

## 🔑 Datos generados para vos

```
SECRET_KEY (Django):
SeUclkn_B_CU4l3_4qL3g1VAL4xlT0KGFUj1CUls0CsmtnzCrwH7fqb7aeHbnoIxKTLoetnU67LluspthSQJrw

DB_PASSWORD (Postgres):
iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg
```

Guardalas — las vas a usar en el paso 7.

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PARTE A — EN TU PC (Windows / PowerShell)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 0. Pushear los cambios al repo

Antes de tocar el droplet, subí los cambios nuevos a GitHub:

```powershell
cd c:\Users\PC\Proyectos\SHOWROOTS
git add backend/config/settings.py backend/requirements.txt backend/.env.example deploy/
git commit -m "Preparar backend para deploy: env vars, requirements, configs"
git push origin main
```

> El `pulsar_dump.json` lo subimos a parte por scp (paso 6) — no va al repo.

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PARTE B — EN EL DROPLET (Ubuntu 24.04)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> IP del droplet: **`107.170.25.226`** (ya está reemplazada en todos los comandos).

## 1. Primer login como root + crear usuario `deploy`

```bash
ssh root@107.170.25.226
```

Una vez dentro:
```bash
apt update && apt upgrade -y

# Crear usuario sin privilegios root
adduser deploy
# (cuando pida password, ponele una fuerte y anotala)

usermod -aG sudo deploy

# Copiar tu llave SSH al usuario deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy

# Firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

exit
```

## 2. Reconectarte como `deploy`

```bash
ssh deploy@107.170.25.226
```

A partir de acá todo corre como `deploy`.

## 3. Instalar paquetes del sistema

```bash
sudo apt install -y python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx git curl \
    build-essential libpq-dev \
    certbot python3-certbot-nginx

# Node.js 20 + pnpm (para buildear el frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pnpm
```

## 4. Crear la base de datos Postgres

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE pulsar;
CREATE USER pulsar_user WITH PASSWORD 'iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg';
ALTER ROLE pulsar_user SET client_encoding TO 'utf8';
ALTER ROLE pulsar_user SET timezone TO 'America/Caracas';
GRANT ALL PRIVILEGES ON DATABASE pulsar TO pulsar_user;
\c pulsar
GRANT ALL ON SCHEMA public TO pulsar_user;
SQL
```

> Verificá conexión:
> ```bash
> PGPASSWORD='iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg' psql -h localhost -U pulsar_user -d pulsar -c "SELECT version();"
> ```

## 5. Clonar el repo

```bash
mkdir -p ~/logs
cd ~
git clone https://github.com/BenjiVZ/SHOWROOTS.git pulsar
cd pulsar
```

> Si el repo es privado y te pide credenciales: usá un **Personal Access Token** de GitHub (https://github.com/settings/tokens) en lugar de la password.

## 6. Subir el dump de datos (DESDE TU PC)

**Abrí otra terminal en tu PC** y corré:

```powershell
cd c:\Users\PC\Proyectos\SHOWROOTS\backend
scp pulsar_dump.json deploy@107.170.25.226:/home/deploy/pulsar/backend/
```

(Sigue después en el droplet con el paso 7.)

## 7. Configurar `.env` del backend

De vuelta en el droplet:

```bash
cd ~/pulsar/backend
cp .env.example .env
nano .env
```

Pegá exactamente esto (reemplazá los dominios reales en `ALLOWED_HOSTS` y `FRONTEND_URL`):

```
SECRET_KEY=SeUclkn_B_CU4l3_4qL3g1VAL4xlT0KGFUj1CUls0CsmtnzCrwH7fqb7aeHbnoIxKTLoetnU67LluspthSQJrw
DEBUG=False
ALLOWED_HOSTS=api.tudominio.com,tudominio.com

DB_ENGINE=postgres
DB_NAME=pulsar
DB_USER=pulsar_user
DB_PASSWORD=iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg
DB_HOST=localhost
DB_PORT=5432

GOOGLE_CLIENT_ID=320154314487-vjpmupb1ag0fh46f7r1inmn3cjbh16oa.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=showrootspulse@gmail.com
EMAIL_HOST_PASSWORD=mwkdfntgxkookbkp
DEFAULT_FROM_EMAIL=Pulsar <showrootspulse@gmail.com>

FRONTEND_URL=https://tudominio.com
SECURE_SSL_REDIRECT=True

USE_SPACES=False
```

Guardá con `Ctrl+O`, Enter, `Ctrl+X`.

## 8. Crear venv + instalar deps + migrar + cargar dump

```bash
cd ~/pulsar/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Migraciones (crea tablas vacías)
python manage.py migrate

# Cargar datos desde el SQLite local
python manage.py loaddata pulsar_dump.json

# Static files
python manage.py collectstatic --noinput

# Borrar el dump (tiene datos personales)
rm pulsar_dump.json
```

## 9. Verificar que arranca

```bash
python manage.py runserver 0.0.0.0:8000
```

Desde otra terminal probá: `curl http://localhost:8000/api/` debería responder algo (no 500).

Apretá `Ctrl+C` para parar. (No vamos a usar runserver en prod — para eso está gunicorn.)

## 10. Buildear el frontend

```bash
cd ~/pulsar/frontend
echo "VITE_API_URL=https://api.tudominio.com" > .env.production
pnpm install
pnpm build
```

> Si te falta algún `.env` específico que use el frontend para Google OAuth o Mapbox, copialo a este paso.

## 11. Instalar gunicorn como servicio

```bash
sudo cp ~/pulsar/deploy/pulsar.service /etc/systemd/system/pulsar.service
sudo systemctl daemon-reload
sudo systemctl enable pulsar
sudo systemctl start pulsar
sudo systemctl status pulsar --no-pager
```

Deberías ver **active (running)** en verde. Si dice `failed`:
```bash
journalctl -u pulsar -n 50 --no-pager
```

## 12. Configurar Nginx

```bash
# Copiar el template
sudo cp ~/pulsar/deploy/nginx-pulsar.conf /etc/nginx/sites-available/pulsar

# Reemplazá los dominios (cambiá tudominio.com por el real)
sudo nano /etc/nginx/sites-available/pulsar
# Buscá pulsar.tudominio.com y api.pulsar.tudominio.com → poné tus dominios

# Activar el site
sudo ln -s /etc/nginx/sites-available/pulsar /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test de config + reload
sudo nginx -t
sudo systemctl restart nginx
```

Probá en el navegador: `http://tudominio.com` debería cargar el frontend.

## 13. SSL gratis con Let's Encrypt

```bash
sudo certbot --nginx \
    -d tudominio.com \
    -d api.tudominio.com \
    --redirect --agree-tos \
    -m desarrollodamasco@gmail.com
```

(Reemplazá los dominios.) Certbot reescribe nginx para forzar HTTPS y renueva solo cada 90 días.

## 14. Swap (recomendado con 2 GB de RAM)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
free -h
```

## 15. Subir las fotos al droplet (DESDE TU PC)

Son 25 MB / 38 archivos. En tu PC:

```powershell
cd c:\Users\PC\Proyectos\SHOWROOTS\backend
scp -r media/* deploy@107.170.25.226:/home/deploy/pulsar/backend/media/
```

> O usá WinSCP si preferís interfaz gráfica.

## 16. Crear superuser para Django Admin

```bash
cd ~/pulsar/backend
source venv/bin/activate
python manage.py createsuperuser
```

Te crea un admin en `https://api.tudominio.com/admin/`.

---

# ✅ Checklist final

Probá uno por uno desde el navegador:

- [ ] `https://tudominio.com` → carga el frontend
- [ ] `https://api.tudominio.com/api/` → responde (no 502, no 500)
- [ ] `https://api.tudominio.com/admin/` → login de admin funciona
- [ ] Login en la app con email funciona
- [ ] Una foto subida antes (avatar) se ve correctamente
- [ ] Email de recuperación llega

# 🆘 Si algo se rompe

| Síntoma | Comando |
|---|---|
| **502 Bad Gateway** | `sudo systemctl status pulsar` + `tail ~/logs/gunicorn-error.log` |
| **500 en API** | `tail ~/logs/gunicorn-error.log` |
| **Frontend no carga** | `sudo nginx -t && sudo tail /var/log/nginx/error.log` |
| **CORS bloquea login** | Editá `backend/config/settings.py` — agregá tu dominio en `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS`, después `sudo systemctl restart pulsar` |
| **Google OAuth falla** | En Google Cloud Console → OAuth credentials → agregá `https://tudominio.com` a Authorized JavaScript origins y `https://tudominio.com` a Authorized redirect URIs |

---

# 🔄 Para futuros updates (cuando cambies código)

```bash
ssh deploy@107.170.25.226
cd ~/pulsar
git pull

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart pulsar

# Frontend (si cambió)
cd ../frontend
pnpm install
pnpm build
```

Eso es todo. Nginx sirve los archivos nuevos del `dist/` automáticamente.
