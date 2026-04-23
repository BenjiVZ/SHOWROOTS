@echo off
title ShowRoots - Launcher
color 0A

echo ============================================
echo     SHOW ROOTS - Iniciando Servicios
echo ============================================
echo.

:: ---- Backend: Django (puerto 5000) ----
echo [1/3] Iniciando Backend Django en puerto 5000...
start "ShowRoots-Backend" cmd /c "cd /d %~dp0backend && python manage.py runserver 0.0.0.0:5000"

:: Esperar 3 segundos para que el backend arranque primero
timeout /t 3 /nobreak > nul

:: ---- Frontend: Vue + Vite (puerto 5001) ----
echo [2/3] Iniciando Frontend Vue+Vite en puerto 5001...
start "ShowRoots-Frontend" cmd /c "cd /d %~dp0frontend && npm run dev -- --port 5001"

:: Esperar 2 segundos
timeout /t 2 /nobreak > nul

:: ---- Scheduler: Tareas periodicas ----
echo [3/3] Iniciando Scheduler de tareas periodicas...
start "ShowRoots-Scheduler" cmd /c "cd /d %~dp0backend && python manage.py run_scheduler"

echo.
echo ============================================
echo   Backend:   http://localhost:5000
echo   Frontend:  http://localhost:5001
echo   Scheduler: Activo (expiracion + recordatorios)
echo ============================================
echo.
echo Tres servicios iniciados en ventanas separadas.
echo Cierra las ventanas para detenerlos.
echo.
pause
