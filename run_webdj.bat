@echo off
title ShowRoots - Launcher
color 0A

echo ============================================
echo     SHOW ROOTS - Iniciando Servicios
echo ============================================
echo.

:: ---- Backend: Django (puerto 3000) ----
echo [1/3] Iniciando Backend Django en puerto 3000...
start "ShowRoots-Backend" cmd /c "cd /d %~dp0backend && python manage.py runserver 0.0.0.0:3000"

:: Esperar 3 segundos para que el backend arranque primero
timeout /t 3 /nobreak > nul

:: ---- Frontend: Vue + Vite (puerto 3001) ----
echo [2/3] Iniciando Frontend Vue+Vite en puerto 3001...
start "ShowRoots-Frontend" cmd /c "cd /d %~dp0frontend && npm run dev -- --port 3001"

:: Esperar 2 segundos
timeout /t 2 /nobreak > nul

:: ---- Scheduler: Tareas periodicas ----
:: DESACTIVADO en local — solo corre en produccion (droplet).
:: Si querés reactivarlo en tu PC, descomenta las 2 lineas de abajo.
:: echo [3/3] Iniciando Scheduler de tareas periodicas...
:: start "ShowRoots-Scheduler" cmd /c "cd /d %~dp0backend && python manage.py run_scheduler"

echo.
echo ============================================
echo   Backend:   http://localhost:3000
echo   Frontend:  http://localhost:3001
echo   Dominios:
echo     backend.aplicacionesdamasco.com -> :3000
echo     frontend.aplicacionesdamasco.com -> :3001
echo   Scheduler: DESACTIVADO en local (solo prod)
echo ============================================
echo.
echo Tres servicios iniciados en ventanas separadas.
echo Cierra las ventanas para detenerlos.
echo.
pause
