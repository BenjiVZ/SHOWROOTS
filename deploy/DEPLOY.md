# Pulsar – Guía de deploy en un Droplet de DigitalOcean

Esta guía asume:
- Droplet **Ubuntu 24.04 LTS · 2 GB RAM · NVMe**.
- Conexión por SSH como `root` con tu llave pública ya cargada.
- Dominios apuntando a la IP del droplet (registros A):
  - `pulsar.tudominio.com` → frontend
  - `api.pulsar.tudominio.com` → backend

> Reemplazá `IP_DEL_DROPLET` y los dominios por los reales en cada paso.

---

## 1. Primer acceso y hardening

```bash
ssh root@IP_DEL_DROPLET

# Actualizar todo
apt update && apt upgrade -y

# Crear usuario sin privilegios para correr la app
adduser deploy
usermod -aG sudo deploy

# Copiar tu llave SSH al usuario deploy para entrar directo
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy

# Firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

Salí y volvé a entrar como `deploy`:
```bash
exit
ssh deploy@IP_DEL_DROPLET
```

---

## 2. Instalar dependencias del sistema

```bash
sudo apt install -y python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx git curl ufw \
    build-essential libpq-dev \
    certbot python3-certbot-nginx
```

Node.js 20 (para buildear el frontend en el droplet):
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pnpm
```

---

## 3. Crear la base de datos Postgres

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE pulsar;
CREATE USER pulsar_user WITH PASSWORD 'CAMBIA_ESTA_PASSWORD';
ALTER ROLE pulsar_user SET client_encoding TO 'utf8';
ALTER ROLE pulsar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pulsar_user SET timezone TO 'America/Caracas';
GRANT ALL PRIVILEGES ON DATABASE pulsar TO pulsar_user;
\c pulsar
GRANT ALL ON SCHEMA public TO pulsar_user;
SQL
```

Anotá la password — va al `.env`.

---

## 4. Clonar el repo

```bash
mkdir -p ~/logs
cd ~
git clone https://github.com/TU_USUARIO/SHOWROOTS.git pulsar
cd pulsar
```

> Si el repo es privado: configurá una deploy key de GitHub para `deploy@droplet`.

---

## 5. Backend – venv, deps, .env

```bash
cd ~/pulsar/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copiar plantilla y editar
cp .env.example .env
nano .env
```

Completá en `.env`:
- `SECRET_KEY` — generala con: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `DEBUG=False`
- `ALLOWED_HOSTS=api.pulsar.tudominio.com`
- `DB_*` con la password del paso 3
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` (copiá del `.env` local)
- `EMAIL_HOST_PASSWORD` (app password de Gmail)
- `FRONTEND_URL=https://pulsar.tudominio.com`

Generar SECRET_KEY rápido:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## 6. Migrar la base + colectar static + superuser

```bash
cd ~/pulsar/backend
source venv/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

> Si querés llevar datos del SQLite local: en tu PC corré
> `python manage.py dumpdata --natural-foreign --natural-primary --indent 2 -e contenttypes -e auth.permission > dump.json`
> Subilo al droplet (`scp dump.json deploy@IP:~/pulsar/backend/`) y corré
> `python manage.py loaddata dump.json`.

---

## 7. Frontend – build de Vue

Ajustá la URL del backend en el `.env` del frontend (si tenés uno) o donde corresponda:

```bash
cd ~/pulsar/frontend
echo "VITE_API_URL=https://api.pulsar.tudominio.com" > .env.production
pnpm install
pnpm build
```

Esto deja el sitio listo en `~/pulsar/frontend/dist/`.

---

## 8. Gunicorn como servicio systemd

```bash
sudo cp ~/pulsar/deploy/pulsar.service /etc/systemd/system/pulsar.service
sudo systemctl daemon-reload
sudo systemctl enable pulsar
sudo systemctl start pulsar
sudo systemctl status pulsar
```

Si arrancó OK vas a ver `active (running)`. Los logs:
```bash
journalctl -u pulsar -f
tail -f ~/logs/gunicorn-error.log
```

---

## 9. Nginx + dominios

```bash
sudo cp ~/pulsar/deploy/nginx-pulsar.conf /etc/nginx/sites-available/pulsar

# Reemplazá los dominios en el archivo:
sudo sed -i 's/pulsar.tudominio.com/pulsar.tudominio.com/g; s/api.pulsar.tudominio.com/api.pulsar.tudominio.com/g' \
    /etc/nginx/sites-available/pulsar
# (cambiá los .tudominio.com reales)

sudo ln -s /etc/nginx/sites-available/pulsar /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Verificá que el frontend cargue en http://pulsar.tudominio.com y que la API responda en http://api.pulsar.tudominio.com/api/.

---

## 10. SSL gratis con Let's Encrypt

```bash
sudo certbot --nginx \
    -d pulsar.tudominio.com \
    -d api.pulsar.tudominio.com \
    --redirect --agree-tos -m desarrollodamasco@gmail.com
```

Certbot reescribe el nginx para forzar HTTPS. Renueva solo cada 90 días.

---

## 11. (Opcional pero recomendado) Spaces para media

1. En el panel de DigitalOcean: **Spaces Object Storage** → Create a Space.
   - Region: NYC3 (cerca del droplet)
   - Name: `pulsar-media`
   - File listing: Restricted
   - Activá **CDN** (gratis).
2. **API** → **Spaces Keys** → Generate New Key → guardá Access Key + Secret.
3. En `~/pulsar/backend/.env`:
   ```
   USE_SPACES=True
   SPACES_KEY=DOXXXXXXXXXX
   SPACES_SECRET=xxxxxxxx
   SPACES_BUCKET=pulsar-media
   SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
   SPACES_REGION=nyc3
   SPACES_CDN=pulsar-media.nyc3.cdn.digitaloceanspaces.com
   ```
4. Reiniciá:
   ```bash
   sudo systemctl restart pulsar
   ```
5. Comentá el bloque `location /media/` en el nginx (ya no lo necesitás).
6. Los uploads nuevos van a Spaces. Para migrar los existentes:
   ```bash
   # subir todo lo que hay en backend/media/ al bucket
   pip install s3cmd
   # configurar con SPACES_KEY/SECRET y luego:
   s3cmd sync media/ s3://pulsar-media/ --acl-public
   ```

---

## 12. Swap (importante con 2 GB de RAM)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

---

## 13. Actualizar el código (workflow diario)

```bash
ssh deploy@IP_DEL_DROPLET

cd ~/pulsar
git pull

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart pulsar

# Frontend
cd ../frontend
pnpm install
pnpm build
# nginx sirve los archivos nuevos automáticamente
```

---

## 14. Backups (además del semanal del droplet)

Backup nocturno de la DB a `/home/deploy/backups`:

```bash
mkdir -p ~/backups

cat > ~/backup_db.sh <<'BASH'
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M)
pg_dump -U pulsar_user -h localhost pulsar | gzip > ~/backups/pulsar-$DATE.sql.gz
# Mantener sólo los últimos 14 dumps
ls -1t ~/backups/pulsar-*.sql.gz | tail -n +15 | xargs -r rm
BASH

chmod +x ~/backup_db.sh

# Pedirle a Postgres que confíe en localhost para deploy
# (editar /etc/postgresql/16/main/pg_hba.conf si pide password — opcional)

# Cron diario a las 3am
(crontab -l 2>/dev/null; echo "0 3 * * * /home/deploy/backup_db.sh") | crontab -
```

---

## Checklist final

- [ ] `https://pulsar.tudominio.com` carga el frontend
- [ ] `https://api.pulsar.tudominio.com/api/` responde
- [ ] Login con email funciona
- [ ] Login con Google funciona (agregá el nuevo dominio en Google Cloud Console → OAuth credentials)
- [ ] Email de recuperación llega
- [ ] Subir foto de perfil funciona (verificá que se ve después de recargar)
- [ ] Reservar un talento funciona end-to-end
- [ ] `sudo systemctl status pulsar` → active (running)
- [ ] `sudo systemctl status nginx` → active (running)
- [ ] `sudo systemctl status postgresql` → active (running)
- [ ] Swap activo: `free -h` muestra Swap > 0
- [ ] Backups: hay archivo en `~/backups/` al día siguiente

---

## Troubleshooting rápido

| Síntoma | Mirar |
|---|---|
| 502 Bad Gateway | `sudo systemctl status pulsar` + `tail ~/logs/gunicorn-error.log` |
| 500 en la API | `tail ~/logs/gunicorn-error.log` (probable falta de env var) |
| Estáticos no cargan | `python manage.py collectstatic` + reiniciar pulsar |
| CORS bloquea el frontend | Agregar el dominio frontend en `CORS_ALLOWED_ORIGINS` (settings.py) |
| Google OAuth da error | En Google Cloud Console agregar `https://pulsar.tudominio.com` a los Authorized JavaScript origins |
| `psycopg2.OperationalError: password authentication` | Verificá `DB_PASSWORD` en `.env` vs lo que pusiste en el `CREATE USER` |
| Fotos subidas no se ven | Si usás Spaces: verificá `USE_SPACES=True` y que el bucket sea público |
