@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Vida Marina VE - Demo local
chcp 65001 >nul

echo.
echo  ============================================
echo   Vida Marina VE - Catalogo de especies
echo  ============================================
echo.

rem --- Buscar Python ---------------------------------------------------------
set "PYTHON="
python --version >nul 2>nul && set "PYTHON=python"

if not defined PYTHON (
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)
if not defined PYTHON (
  if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if not defined PYTHON (
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)
if not defined PYTHON (
  if exist "C:\Python312\python.exe" set "PYTHON=C:\Python312\python.exe"
)
if not defined PYTHON (
  if exist "C:\Python311\python.exe" set "PYTHON=C:\Python311\python.exe"
)

if not defined PYTHON (
  echo  No se encontro Python 3 en este equipo.
  echo.
  echo  Instala Python 3.12 desde:
  echo    https://www.python.org/downloads/
  echo.
  echo  Importante: marca la casilla "Add python.exe to PATH".
  echo.
  pause
  exit /b 1
)

rem --- Crear el entorno virtual la primera vez ------------------------------
if not exist ".venv\Scripts\python.exe" (
  echo  Primera ejecucion: preparando el entorno...
  echo  Esto puede tardar 1-2 minutos y necesita Internet.
  echo.
  "%PYTHON%" -m venv .venv
  if errorlevel 1 goto error

  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto error

  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto error
)

rem --- Arrancar --------------------------------------------------------------
echo  Iniciando el servidor y abriendo el navegador...
echo.
".venv\Scripts\python.exe" iniciar.py
if errorlevel 1 goto error
exit /b 0

:error
echo.
echo  Ocurrio un error. Revisa el mensaje de arriba.
echo.
pause
exit /b 1
