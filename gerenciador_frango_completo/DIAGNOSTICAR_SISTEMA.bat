@echo off
chcp 65001 >nul
title Diagnóstico do Sistema

echo.
echo 🔍 DIAGNÓSTICO COMPLETO DO SISTEMA
echo ════════════════════════════════════════════════════════════════
echo.

set "PROBLEMAS=0"

REM Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado
    set /a PROBLEMAS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i encontrado
)

REM Verificar pip
echo.
echo [2/6] Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip não funcional
    set /a PROBLEMAS+=1
) else (
    echo ✅ pip funcionando
)

REM Verificar dependências
echo.
echo [3/6] Verificando dependências...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FastAPI não instalado
    set /a PROBLEMAS+=1
) else (
    echo ✅ FastAPI OK
)

python -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Uvicorn não instalado
    set /a PROBLEMAS+=1
) else (
    echo ✅ Uvicorn OK
)

python -c "import pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pydantic não instalado
    set /a PROBLEMAS+=1
) else (
    echo ✅ Pydantic OK
)

python -c "import reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ReportLab não instalado
    set /a PROBLEMAS+=1
) else (
    echo ✅ ReportLab OK
)

REM Verificar banco
echo.
echo [4/6] Verificando banco de dados...
python test_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Problema no banco SQLite
    set /a PROBLEMAS+=1
) else (
    echo ✅ Banco SQLite funcionando
)

REM Verificar frontend
echo.
echo [5/6] Verificando frontend...
if exist "frontend\build\index.html" (
    echo ✅ Frontend construído
) else (
    echo ❌ Frontend não construído
    set /a PROBLEMAS+=1
)

REM Verificar portas
echo.
echo [6/6] Verificando portas...
netstat -an | find ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Porta 3000 em uso
) else (
    echo ✅ Porta 3000 livre
)

netstat -an | find ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Porta 8001 em uso
) else (
    echo ✅ Porta 8001 livre
)

echo.
echo ════════════════════════════════════════════════════════════════
if %PROBLEMAS% equ 0 (
    echo ✅ SISTEMA OK - PRONTO PARA USO!
    echo    Execute: INSTALAR_E_INICIAR.bat
) else (
    echo ❌ PROBLEMAS ENCONTRADOS: %PROBLEMAS%
    echo.
    echo 🔧 SOLUÇÕES AUTOMÁTICAS:
    echo    1. Execute: REPARAR_SISTEMA.bat
    echo    2. Ou execute: INSTALAR_E_INICIAR.bat (instala automaticamente)
)
echo ════════════════════════════════════════════════════════════════

pause