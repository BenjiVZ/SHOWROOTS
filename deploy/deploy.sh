#!/usr/bin/env bash
#
# Pulsar — script de deploy para el droplet.
# Uso:   bash /root/pulsar/deploy/deploy.sh
#
# Hace, en orden:
#   1. Trae los últimos cambios de GitHub (git pull).
#   2. Asegura que la app 'payments' quede APAGADA en prod (vulnerable).
#   3. Backend: instala deps, corre migraciones y reinicia gunicorn.
#   4. Frontend: asegura el .env, instala deps y recompila.
#   5. Muestra un resumen del estado.
#
# Es idempotente: podés correrlo las veces que quieras.

set -uo pipefail

# ── Configuración (ajustá si tu droplet usa otras rutas) ──────────────
REPO_DIR="/root/pulsar"
VENV="$REPO_DIR/backend/venv"
SERVICE="pulsar"
GOOGLE_CLIENT_ID="320154314487-vjpmupb1ag0fh46f7r1inmn3cjbh16oa.apps.googleusercontent.com"

# Colores para que se lea fácil
BOLD="\033[1m"; GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"
step() { echo -e "\n${BOLD}==> $1${RESET}"; }
ok()   { echo -e "${GREEN}✔ $1${RESET}"; }
warn() { echo -e "${YELLOW}! $1${RESET}"; }
die()  { echo -e "${RED}✗ $1${RESET}"; exit 1; }

cd "$REPO_DIR" || die "No existe $REPO_DIR"

# ── 1. Traer cambios de GitHub ────────────────────────────────────────
step "1/5  Trayendo cambios de GitHub (git pull)"
# Guardar cualquier cambio local a mano para que el pull no aborte
if ! git diff --quiet || ! git diff --cached --quiet; then
  warn "Hay cambios locales — los guardo con 'git stash' (quedan de respaldo)"
  git stash push -m "deploy-autostash-$(date +%s)" >/dev/null 2>&1 || true
fi
git pull origin main || die "Falló el git pull (¿token vencido? revisá 'git remote -v')"
ok "Código actualizado"

# ── 2. Apagar payments en producción ──────────────────────────────────
step "2/5  Asegurando payments APAGADO en producción"
ENV_BE="$REPO_DIR/backend/.env"
if grep -q '^PAYMENTS_ENABLED=' "$ENV_BE" 2>/dev/null; then
  sed -i 's/^PAYMENTS_ENABLED=.*/PAYMENTS_ENABLED=false/' "$ENV_BE"
else
  echo 'PAYMENTS_ENABLED=false' >> "$ENV_BE"
fi
ok "PAYMENTS_ENABLED=false"

# ── 3. Backend ────────────────────────────────────────────────────────
step "3/5  Backend: deps + migraciones + restart"
"$VENV/bin/pip" install -r "$REPO_DIR/backend/requirements.txt" -q || die "Falló pip install"
ok "Dependencias del backend al día"
( cd "$REPO_DIR/backend" && "$VENV/bin/python" manage.py migrate --noinput ) || warn "migrate reportó algo — revisa arriba"
# Recolectar estáticos (CSS/JS del admin de Django, etc.)
( cd "$REPO_DIR/backend" && "$VENV/bin/python" manage.py collectstatic --noinput ) || warn "collectstatic reportó algo — revisa arriba"
systemctl restart "$SERVICE" || die "No pude reiniciar $SERVICE"
sleep 2
if [ "$(systemctl is-active "$SERVICE")" = "active" ]; then
  ok "Backend activo (gunicorn corriendo)"
else
  die "El backend NO quedó activo — corré: journalctl -u $SERVICE -n 30 --no-pager"
fi

# ── 4. Frontend ───────────────────────────────────────────────────────
step "4/5  Frontend: .env + build"
ENV_FE="$REPO_DIR/frontend/.env"
if ! grep -q '^VITE_GOOGLE_CLIENT_ID=' "$ENV_FE" 2>/dev/null; then
  printf 'VITE_GOOGLE_CLIENT_ID=%s\nVITE_API_URL=/api\n' "$GOOGLE_CLIENT_ID" > "$ENV_FE"
  warn "Creé el frontend/.env (faltaba)"
fi
( cd "$REPO_DIR/frontend" && pnpm install --silent && pnpm build ) || die "Falló el build del frontend"
ok "Frontend recompilado"

# ── 5. Resumen ────────────────────────────────────────────────────────
step "5/5  Resumen"
echo -e "  Servicio      : $(systemctl is-active "$SERVICE")"
echo -e "  Commit actual : $(git rev-parse --short HEAD) — $(git log -1 --pretty=%s)"
echo -e "  payments      : $("$VENV/bin/python" -c "import os;os.environ['DJANGO_SETTINGS_MODULE']='config.settings';import django;os.chdir('$REPO_DIR/backend');django.setup();from django.conf import settings;print('CARGADO ⚠️' if 'payments' in settings.INSTALLED_APPS else 'apagado ✔')" 2>/dev/null || echo '¿?')"
echo -e "\n${GREEN}${BOLD}Deploy terminado.${RESET} Recargá im-pulsar.com con Ctrl+Shift+R.\n"
