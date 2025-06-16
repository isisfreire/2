@echo off
title Gerenciador de Granjas de Frango - Instalacao

echo.
echo ================================================================
echo  GERENCIADOR DE GRANJAS DE FRANGO - VERSAO WINDOWS
echo  Sistema profissional em portugues brasileiro  
echo  Instalacao automatica para Windows
echo ================================================================
echo.

set "ERRO=0"

echo [PASSO 1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao esta instalado ou nao esta no PATH
    echo.
    echo SOLUCAO:
    echo    1. Baixe Python em: https://python.org/downloads/
    echo    2. Durante a instalacao, MARQUE "Add Python to PATH"
    echo    3. Reinicie o computador apos instalar
    echo    4. Execute este arquivo novamente
    echo.
    set "ERRO=1"
    goto :erro
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python %PYTHON_VERSION% encontrado!

echo.
echo [PASSO 2/5] Verificando e instalando dependencias...
echo Instalando FastAPI, Uvicorn, Pydantic e ReportLab...
echo (Esta etapa pode demorar alguns minutos na primeira vez)
echo.

python -m pip install --quiet --upgrade pip
if %errorlevel% neq 0 (
    echo Aviso: Nao foi possivel atualizar pip, mas continuando...
)

echo    Instalando FastAPI...
python -m pip install --quiet fastapi
if %errorlevel% neq 0 (
    echo Falha ao instalar FastAPI
    set "ERRO=1"
    goto :erro
)

echo    Instalando Uvicorn...
python -m pip install --quiet uvicorn
if %errorlevel% neq 0 (
    echo Falha ao instalar Uvicorn
    set "ERRO=1"
    goto :erro
)

echo    Instalando Pydantic...
python -m pip install --quiet pydantic
if %errorlevel% neq 0 (
    echo Falha ao instalar Pydantic
    set "ERRO=1"
    goto :erro
)

echo    Instalando ReportLab...
python -m pip install --quiet reportlab
if %errorlevel% neq 0 (
    echo Falha ao instalar ReportLab
    set "ERRO=1"
    goto :erro
)

echo OK: Todas as dependencias instaladas com sucesso!

echo.
echo [PASSO 3/5] Testando banco de dados...
python test_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo Problema com o banco de dados
    echo Tentando recriar banco...
    del /q broiler_data.db >nul 2>&1
    python test_database.py >nul 2>&1
    if %errorlevel% neq 0 (
        echo Falha critica no banco de dados
        set "ERRO=1"
        goto :erro
    )
)
echo OK: Banco de dados SQLite funcionando!

echo.
echo [PASSO 4/5] Verificando frontend...
if not exist "frontend\build" (
    echo Primeira execucao: construindo interface...
    echo (Esta etapa pode demorar alguns minutos)
    cd frontend
    call npm install --silent
    call npm run build --silent
    cd ..
    echo OK: Interface construida!
) else (
    echo OK: Interface ja construida!
)

echo.
echo [PASSO 5/5] Iniciando aplicacao...
echo Startando servidores...
echo.
echo ================================================================
echo  APLICACAO INICIANDO...
echo  O navegador abriara automaticamente em alguns segundos
echo  URL: http://127.0.0.1:3000
echo  Dados salvos em: broiler_data.db
echo  Relatorios em: exports\
echo.
echo  IMPORTANTE: NAO FECHE esta janela!
echo  Para parar a aplicacao: Pressione Ctrl+C
echo ================================================================
echo.

REM Iniciar a aplicacao principal
python app_launcher.py
goto :fim

:erro
echo.
echo ================================================================
echo  ERRO NA INSTALACAO
echo ================================================================
echo.
if "%ERRO%"=="1" (
    echo DIAGNOSTICO:
    echo    Verifique sua conexao com a internet
    echo    Execute como Administrador se necessario
    echo    Certifique-se que o antivirus nao esta bloqueando
    echo.
    echo SOLUCOES:
    echo    1. Clique com botao direito neste arquivo
    echo    2. Selecione "Executar como administrador"  
    echo    3. Tente novamente
    echo.
)

:fim
echo.
echo Pressione qualquer tecla para sair...
pause >nul