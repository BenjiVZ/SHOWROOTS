# Pulsar / SHOWROOTS — Project Conventions

## Package manager

**Siempre usar `pnpm`** para instalar, actualizar o ejecutar dependencias en el frontend.

- Instalar paquetes: `pnpm add <paquete>` (no `npm install` ni `yarn add`).
- Instalar dev deps: `pnpm add -D <paquete>`.
- Correr scripts: `pnpm dev`, `pnpm build`, `pnpm preview`.
- Sync de lockfile: `pnpm install` (en CI o tras `git pull`).
- **No** crear `package-lock.json` ni `yarn.lock`. Sólo `pnpm-lock.yaml` debe vivir en el repo.

Si encuentras un `package-lock.json` o `yarn.lock` en el frontend, bórralo y regenera con `pnpm install`.
