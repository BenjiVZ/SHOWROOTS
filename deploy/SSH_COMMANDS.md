# 🤖 Pulsar — Deploy autónomo desde cero

> Este documento está escrito para que **un agente automatizado** ejecute el deploy completo en un droplet recién restaurado, sin necesidad de pedir contexto adicional.
>
> Si sos humano leyendo esto: seguí los pasos en orden y se logra el mismo resultado.

---

# 📌 Contexto fijo del proyecto

| Item | Valor |
|---|---|
| **IP del droplet** | `107.170.25.226` |
| **Acceso SSH** | `ssh root@107.170.25.226` (llave SSH ya configurada al crear el droplet) |
| **OS** | Ubuntu 24.04 LTS (Basic Premium Intel, 2 GB RAM / 70 GB NVMe / NYC2) |
| **Dominio frontend** | `im-pulsar.com` (+ `www.im-pulsar.com`) |
| **Dominio backend** | `api.im-pulsar.com` |
| **Repo** | `https://github.com/BenjiVZ/SHOWROOTS.git` (branch `main`) |
| **Path en droplet** | `/root/pulsar` |
| **Usuario en droplet** | `root` (no se crea usuario `deploy`) |
| **DB** | Postgres in-droplet (no Managed DB) |
| **Email humano para SSL/admin** | `desarrollodamasco@gmail.com` |

## Credenciales generadas (usar literales)

```
SECRET_KEY=SeUclkn_B_CU4l3_4qL3g1VAL4xlT0KGFUj1CUls0CsmtnzCrwH7fqb7aeHbnoIxKTLoetnU67LluspthSQJrw
DB_PASSWORD=iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg
GOOGLE_CLIENT_ID=320154314487-vjpmupb1ag0fh46f7r1inmn3cjbh16oa.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
EMAIL_HOST_USER=showrootspulse@gmail.com
EMAIL_HOST_PASSWORD=mwkdfntgxkookbkp
```

## Archivos locales en la PC del usuario (para scp)

| Archivo | Path en la PC |
|---|---|
| Dump de DB | `c:\Users\PC\Proyectos\SHOWROOTS\backend\pulsar_dump.json` (41 KB, 79 objetos) |
| Media uploads | `c:\Users\PC\Proyectos\SHOWROOTS\backend\media\` (25 MB, 38 archivos) |

## DNS — gestionado automáticamente por Cloudflare Tunnel

El dominio `im-pulsar.com` debe estar agregado en Cloudflare (nameservers apuntando a Cloudflare).
Los registros CNAME los crea automáticamente `cloudflared` en el paso B.13. No se necesitan registros A manuales.

---

# 🚦 Reglas para el agente

1. **Ejecutar los pasos en orden estricto**: B.1 → B.13.
2. **Verificar cada paso antes de avanzar**. Cada paso tiene una sección "Verificación".
3. **Si una verificación falla**, parar y reportar al usuario con el output exacto del error.
4. **No improvisar passwords ni cambiar paths**. Todos los literales están en la sección "Contexto fijo".
5. **Pausar y pedir intervención humana** solo en los pasos marcados con 🧑 (createsuperuser y Google OAuth).
6. **Tras cada `systemctl` start/restart**, verificar `is-active` antes de continuar.

---

# 🅰️ PRE-REQUISITO — Subir archivos desde la PC del usuario

> Estos 2 comandos los corre el USUARIO desde PowerShell **antes** de empezar la parte B (o el agente si tiene acceso a la PC). El agente debe verificar la existencia de estos archivos en el droplet antes de B.8.

```powershell
# DESDE LA PC DEL USUARIO
cd c:\Users\PC\Proyectos\SHOWROOTS\backend
scp pulsar_dump.json root@107.170.25.226:/root/
scp -r media root@107.170.25.226:/root/
```

(Se mueven dentro de `/root/pulsar/backend/` después de clonar el repo, en el paso B.6.)

---

# 🅱️ PARTE B — Comandos en el droplet (root)

## B.1 — Actualizar sistema + firewall

```bash
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade -y

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

**Verificación:**
```bash
ufw status | grep -E "(80/tcp|443/tcp|OpenSSH)" && echo "OK firewall"
```

## B.2 — Instalar paquetes del sistema

```bash
apt-get install -y \
    python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx git curl \
    build-essential libpq-dev \
    dnsutils
```

**Verificación:**
```bash
python3 --version && psql --version && nginx -v && certbot --version
```

## B.3 — Instalar Node.js 20 + pnpm

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g pnpm
```

**Verificación:**
```bash
node --version  # debe imprimir v20.x.x
pnpm --version  # debe imprimir 9.x o 10.x
```

## B.4 — Crear DB Postgres + usuario (con verificación robusta)

```bash
sudo -u postgres psql <<'SQL'
DROP DATABASE IF EXISTS pulsar;
DROP USER IF EXISTS pulsar_user;
CREATE USER pulsar_user WITH PASSWORD 'iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg';
CREATE DATABASE pulsar OWNER pulsar_user;
ALTER ROLE pulsar_user SET client_encoding TO 'utf8';
ALTER ROLE pulsar_user SET timezone TO 'America/Caracas';
GRANT ALL PRIVILEGES ON DATABASE pulsar TO pulsar_user;
\c pulsar
GRANT ALL ON SCHEMA public TO pulsar_user;
ALTER SCHEMA public OWNER TO pulsar_user;
SQL

# Re-aplicar password explícitamente (workaround por bug observado en intento anterior)
sudo -u postgres psql -c "ALTER USER pulsar_user WITH PASSWORD 'iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg';"
```

**Verificación (OBLIGATORIA antes de avanzar):**
```bash
PGPASSWORD='iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg' psql -h localhost -U pulsar_user -d pulsar -c "SELECT current_user;" 2>&1
```

Debe imprimir una fila con `pulsar_user`. **Si falla, parar y reportar al usuario** — no avanzar.

## B.5 — Clonar el repo

```bash
mkdir -p /root/logs
cd /root
git clone https://github.com/BenjiVZ/SHOWROOTS.git pulsar
cd pulsar
```

> Si el repo es privado y pide credenciales, **parar y reportar al usuario** — necesita generar un Personal Access Token en https://github.com/settings/tokens (scope `repo`) y configurarlo.

**Verificación:**
```bash
test -f /root/pulsar/backend/manage.py && test -f /root/pulsar/frontend/package.json && echo "OK repo"
```

## B.6 — Mover dump y media a su lugar dentro del proyecto

> Estos archivos deben existir en `/root/` por el paso 🅰️ pre-requisito. Si no existen, **parar y avisar al usuario** que corra los `scp`.

```bash
mkdir -p /root/pulsar/backend/media

# Verificar que los archivos están en /root/
test -f /root/pulsar_dump.json || { echo "FALTA pulsar_dump.json — pedir al usuario que haga scp"; exit 1; }
test -d /root/media || { echo "FALTA carpeta media — pedir al usuario que haga scp"; exit 1; }

# Mover
mv /root/pulsar_dump.json /root/pulsar/backend/pulsar_dump.json
cp -r /root/media/* /root/pulsar/backend/media/ 2>/dev/null || true
rm -rf /root/media
```

**Verificación:**
```bash
ls -la /root/pulsar/backend/pulsar_dump.json && \
echo "Archivos en media: $(find /root/pulsar/backend/media -type f | wc -l)"
```

## B.7 — Configurar `.env` del backend

```bash
cat > /root/pulsar/backend/.env <<'EOF'
SECRET_KEY=SeUclkn_B_CU4l3_4qL3g1VAL4xlT0KGFUj1CUls0CsmtnzCrwH7fqb7aeHbnoIxKTLoetnU67LluspthSQJrw
DEBUG=False
ALLOWED_HOSTS=im-pulsar.com,www.im-pulsar.com,api.im-pulsar.com,107.170.25.226

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

FRONTEND_URL=https://im-pulsar.com
SECURE_SSL_REDIRECT=False

USE_SPACES=False
EOF

chmod 600 /root/pulsar/backend/.env
```

> `SECURE_SSL_REDIRECT=False` se mantiene hasta tener SSL (paso B.13). Después se cambia a `True`.

**Verificación:**
```bash
grep -E "^(SECRET_KEY|DB_PASSWORD|ALLOWED_HOSTS|FRONTEND_URL)=" /root/pulsar/backend/.env
```

## B.8 — venv + deps + migrate + loaddata + collectstatic

```bash
cd /root/pulsar/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata pulsar_dump.json
python manage.py collectstatic --noinput
rm pulsar_dump.json
```

**Verificación:**
```bash
source /root/pulsar/backend/venv/bin/activate
cd /root/pulsar/backend
python manage.py shell -c "
from accounts.models import User
from talents.models import TalentProfile
from bookings.models import Booking
print(f'Users: {User.objects.count()}')
print(f'Talents: {TalentProfile.objects.count()}')
print(f'Bookings: {Booking.objects.count()}')
"
```

Debe imprimir `Users: 12`, `Talents: 5`, `Bookings: 2` (o números > 0 — confirman que el dump cargó).

## B.9 — Build del frontend

```bash
cd /root/pulsar/frontend
echo "VITE_API_URL=https://api.im-pulsar.com" > .env.production
pnpm install
pnpm build
```

**Verificación:**
```bash
test -f /root/pulsar/frontend/dist/index.html && \
echo "Build OK — $(ls /root/pulsar/frontend/dist/assets | wc -l) assets generados"
```

## B.10 — Gunicorn como servicio systemd

```bash
cat > /etc/systemd/system/pulsar.service <<'EOF'
[Unit]
Description=Pulsar Django (gunicorn)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=root
Group=root
WorkingDirectory=/root/pulsar/backend
EnvironmentFile=/root/pulsar/backend/.env
ExecStart=/root/pulsar/backend/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/pulsar.sock \
    --access-logfile /root/logs/gunicorn-access.log \
    --error-logfile /root/logs/gunicorn-error.log \
    --timeout 60 \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
KillMode=mixed
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pulsar
systemctl start pulsar
sleep 3
```

**Verificación:**
```bash
systemctl is-active pulsar && \
test -S /run/pulsar.sock && \
echo "OK gunicorn"
```

Si falla:
```bash
journalctl -u pulsar -n 50 --no-pager
tail /root/logs/gunicorn-error.log
```

## B.11 — Nginx (HTTP, dominios reales)

```bash
cat > /etc/nginx/sites-available/pulsar <<'EOF'
# ─── Backend API: api.im-pulsar.com ───
server {
    listen 80;
    listen [::]:80;
    server_name api.im-pulsar.com;

    client_max_body_size 25M;

    location /static/ {
        alias /root/pulsar/backend/staticfiles/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /root/pulsar/backend/media/;
        expires 7d;
        access_log off;
    }

    location / {
        proxy_pass http://unix:/run/pulsar.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 60s;
    }
}

# ─── Frontend Vue: im-pulsar.com (+ www) ───
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name im-pulsar.com www.im-pulsar.com;

    root /root/pulsar/frontend/dist;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;
    gzip_min_length 1024;

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Permisos para que nginx (user www-data) lea bajo /root
chmod o+x /root /root/pulsar /root/pulsar/frontend /root/pulsar/frontend/dist
chmod o+x /root/pulsar/backend /root/pulsar/backend/staticfiles /root/pulsar/backend/media

ln -sf /etc/nginx/sites-available/pulsar /etc/nginx/sites-enabled/pulsar
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
sleep 2
```

**Verificación:**
```bash
systemctl is-active nginx && \
curl -sI -o /dev/null -w "Front: %{http_code}\n" -H "Host: im-pulsar.com" http://localhost/ && \
curl -sI -o /dev/null -w "API:   %{http_code}\n" -H "Host: api.im-pulsar.com" http://localhost/api/
```

Códigos esperados: front `200`, API `200` o `404` (Django responde con 404 para `/api/` plano — eso significa que el proxy funciona).

## B.12 — Swap (importante con 2 GB RAM)

```bash
if ! swapon --show | grep -q /swapfile; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
fi
```

**Verificación:**
```bash
free -h | grep Swap
```

## B.13 — SSL con Cloudflare Tunnel

> Cloudflare Tunnel elimina la necesidad de certbot, registros A manuales y esperar propagación DNS. SSL es automático vía Cloudflare.

**Requisito:** el dominio `im-pulsar.com` debe estar agregado en la cuenta de Cloudflare del usuario (nameservers apuntando a Cloudflare).

### B.13.1 — Instalar cloudflared

```bash
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared.deb
rm cloudflared.deb
```

**Verificación:**
```bash
cloudflared --version
```

### B.13.2 — Autenticar (🧑 requiere navegador del usuario)

```bash
cloudflared tunnel login
```

Esto imprime un URL. El usuario debe abrirlo en su navegador, seleccionar el dominio `im-pulsar.com` y autorizar. Después el certificado se guarda en `/root/.cloudflared/cert.pem`.

**Verificación:**
```bash
test -f /root/.cloudflared/cert.pem && echo "OK auth"
```

### B.13.3 — Crear el túnel

```bash
cloudflared tunnel create pulsar
```

Anotar el **Tunnel ID** que imprime (UUID). Se usa en los siguientes pasos.

### B.13.4 — Configurar rutas del túnel

```bash
# Reemplazar <TUNNEL_ID> con el UUID del paso anterior
TUNNEL_ID=$(cloudflared tunnel list | grep pulsar | awk '{print $1}')

cat > /root/.cloudflared/config.yml <<EOF
tunnel: $TUNNEL_ID
credentials-file: /root/.cloudflared/${TUNNEL_ID}.json

ingress:
  - hostname: api.im-pulsar.com
    service: http://localhost:80
  - hostname: im-pulsar.com
    service: http://localhost:80
  - hostname: www.im-pulsar.com
    service: http://localhost:80
  - service: http_status:404
EOF
```

**Verificación:**
```bash
cat /root/.cloudflared/config.yml
```

### B.13.5 — Crear registros DNS en Cloudflare

```bash
cloudflared tunnel route dns pulsar im-pulsar.com
cloudflared tunnel route dns pulsar www.im-pulsar.com
cloudflared tunnel route dns pulsar api.im-pulsar.com
```

### B.13.6 — Instalar como servicio systemd

```bash
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
sleep 3
```

**Verificación:**
```bash
systemctl is-active cloudflared && echo "OK tunnel"
```

### B.13.7 — Verificar HTTPS funcional

Esperar ~30 segundos y probar:

```bash
curl -sI -o /dev/null -w "https front: %{http_code}\n" https://im-pulsar.com/
curl -sI -o /dev/null -w "https API:   %{http_code}\n" https://api.im-pulsar.com/api/
```

Esperar `200` (o `301`/`404` que confirman que el túnel funciona).

> **Nota:** `SECURE_SSL_REDIRECT` se deja en `False` con Cloudflare Tunnel porque Cloudflare maneja SSL. El tráfico entre Cloudflare y el droplet va por el túnel encriptado.

---

## 🧑 B.14 — Crear superuser de Django (INTERACTIVO — requiere humano)

Esto el agente NO puede automatizar. Pedirle al usuario que corra:

```bash
cd /root/pulsar/backend
source venv/bin/activate
python manage.py createsuperuser
```

## 🧑 B.15 — Configurar Google OAuth (acción del usuario en navegador)

El usuario debe ir a https://console.cloud.google.com/apis/credentials, abrir el OAuth 2.0 Client ID `320154314487-vjpmupb1ag0fh46f7r1inmn3cjbh16oa` y agregar:

**Authorized JavaScript origins:**
- `https://im-pulsar.com`
- `https://www.im-pulsar.com`

**Authorized redirect URIs:**
- `https://im-pulsar.com`
- `https://www.im-pulsar.com`

Sin esto, el login con Google fallará en producción.

---

# ✅ Reporte final del agente al usuario

Al terminar B.13 correctamente, ejecutar este bloque y pasarle el output al usuario:

```bash
echo "═══════════════════════════════════════════"
echo "REPORTE DE DEPLOY"
echo "═══════════════════════════════════════════"
echo ""
echo "Servicios:"
for s in postgresql pulsar nginx; do
    printf "  %-12s %s\n" "$s:" "$(systemctl is-active $s)"
done
echo ""
echo "Endpoints (esperado 200 o 301):"
echo "  Frontend HTTP:  $(curl -sI -o /dev/null -w "%{http_code}" -H "Host: im-pulsar.com" http://localhost/)"
echo "  API HTTP:       $(curl -sI -o /dev/null -w "%{http_code}" -H "Host: api.im-pulsar.com" http://localhost/api/)"
if [ -f /etc/letsencrypt/live/im-pulsar.com/fullchain.pem ]; then
    echo "  Frontend HTTPS: $(curl -sI -o /dev/null -w "%{http_code}" https://im-pulsar.com/)"
    echo "  API HTTPS:      $(curl -sI -o /dev/null -w "%{http_code}" https://api.im-pulsar.com/api/)"
    echo "  SSL:            ✅ activo"
else
    echo "  SSL:            ⚠️ pendiente (DNS no propagado o paso B.13 omitido)"
fi
echo ""
echo "Memoria:"
free -h | head -2
echo ""
echo "Datos cargados en DB:"
cd /root/pulsar/backend && source venv/bin/activate && python manage.py shell -c "
from accounts.models import User
from talents.models import TalentProfile
from bookings.models import Booking
print(f'  Users:    {User.objects.count()}')
print(f'  Talents:  {TalentProfile.objects.count()}')
print(f'  Bookings: {Booking.objects.count()}')
" 2>/dev/null
echo ""
echo "Pendientes manuales:"
echo "  🧑 Crear superuser (paso B.14)"
echo "  🧑 Agregar im-pulsar.com a Google OAuth (paso B.15)"
echo "═══════════════════════════════════════════"
```

---

# 🆘 Troubleshooting — errores conocidos

### `password authentication failed for user "pulsar_user"`

El `CREATE USER WITH PASSWORD` falló silenciosamente o el `.env` tiene un carácter raro:

```bash
sudo -u postgres psql -c "ALTER USER pulsar_user WITH PASSWORD 'iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg';"
PGPASSWORD='iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg' psql -h localhost -U pulsar_user -d pulsar -c "SELECT 1;"
grep DB_PASSWORD /root/pulsar/backend/.env  # debe ser exactamente "DB_PASSWORD=iT86R7hT8cCynTMCrbOoTPjZ4dF824Jg" sin espacios ni comillas
```

### `502 Bad Gateway`

```bash
systemctl status pulsar
journalctl -u pulsar -n 50 --no-pager
tail /root/logs/gunicorn-error.log
ls -la /run/pulsar.sock  # debe existir
```

### `403 Forbidden` en frontend

```bash
chmod o+x /root /root/pulsar /root/pulsar/frontend /root/pulsar/frontend/dist
tail /var/log/nginx/error.log
```

### `nginx: [emerg] could not build server_names_hash`

```bash
echo "server_names_hash_bucket_size 64;" >> /etc/nginx/conf.d/server_names.conf
nginx -t && systemctl reload nginx
```

### `cloudflared` no conecta

```bash
systemctl status cloudflared
journalctl -u cloudflared -n 50 --no-pager
cat /root/.cloudflared/config.yml
```

Verificar que el Tunnel ID y credentials-file son correctos.

### Túnel funciona pero dominio no carga

Verificar que el dominio está en Cloudflare y los CNAME fueron creados:
```bash
cloudflared tunnel route dns pulsar im-pulsar.com
cloudflared tunnel route dns pulsar www.im-pulsar.com
cloudflared tunnel route dns pulsar api.im-pulsar.com
```

---

# 🔄 Workflow para futuros updates (no parte del deploy inicial)

```bash
ssh root@107.170.25.226
cd /root/pulsar && git pull

cd backend && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart pulsar

cd ../frontend
pnpm install
pnpm build
```

---

# 📋 Decisiones fijas (no consultar al usuario)

- Postgres in-droplet (no Managed DB).
- Usuario `root` (no `deploy`).
- Path `/root/pulsar`.
- `USE_SPACES=False` (media en disco local — el droplet tiene 70 GB).
- 3 workers gunicorn.
- 2 GB swap.
- Logs en `/root/logs/gunicorn-{access,error}.log`.
- Backups del droplet ya habilitados (Weekly, $3.20/mes) — no configurar nada adicional acá.
