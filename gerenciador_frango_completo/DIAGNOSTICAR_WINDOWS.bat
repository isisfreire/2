@echo off
title Diagnostico do Sistema

echo.
echo DIAGNOSTICO COMPLETO DO SISTEMA
echo ================================================================
echo.

set "PROBLEMAS=0"

REM Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado
    set /a PROBLEMAS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo OK: Python %%i encontrado
)

REM Verificar pip
echo.
echo [2/6] Verificando pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: pip nao funcional
    set /a PROBLEMAS+=1
) else (
    echo OK: pip funcionando
)

REM Verificar dependencias
echo.
echo [3/6] Verificando dependencias...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: FastAPI nao instalado
    set /a PROBLEMAS+=1
) else (
    echo OK: FastAPI instalado
)

python -c "import uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Uvicorn nao instalado
    set /a PROBLEMAS+=1
) else (
    echo OK: Uvicorn instalado
)

python -c "import pydantic" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Pydantic nao instalado
    set /a PROBLEMAS+=1
) else (
    echo OK: Pydantic instalado
)

python -c "import reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: ReportLab nao instalado
    set /a PROBLEMAS+=1
) else (
    echo OK: ReportLab instalado
)

REM Verificar banco
echo.
echo [4/6] Verificando banco de dados...
python test_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Problema no banco SQLite
    set /a PROBLEMAS+=1
) else (
    echo OK: Banco SQLite funcionando
)

REM Verificar frontend
echo.
echo [5/6] Verificando frontend...
if exist "frontend\build\index.html" (
    echo OK: Frontend construido
) else (
    echo ERRO: Frontend nao construido
    set /a PROBLEMAS+=1
)

REM Verificar portas
echo.
echo [6/6] Verificando portas...
netstat -an | find ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo AVISO: Porta 3000 em uso
) else (
    echo OK: Porta 3000 livre
)

netstat -an | find ":8001" >nul 2>&1
if %errorlevel% equ 0 (
    echo AVISO: Porta 8001 em uso
) else (
    echo OK: Porta 8001 livre
)

echo.
echo ================================================================
if %PROBLEMAS% equ 0 (
    echo SISTEMA OK - PRONTO PARA USO!
    echo Execute: INICIAR_WINDOWS.bat
) else (
    echo PROBLEMAS ENCONTRADOS: %PROBLEMAS%
    echo.
    echo SOLUCOES AUTOMATICAS:
    echo    1. Execute: REPARAR_WINDOWS.bat
    echo    2. Ou execute: INICIAR_WINDOWS.bat (instala automaticamente)
)
echo ================================================================

pause