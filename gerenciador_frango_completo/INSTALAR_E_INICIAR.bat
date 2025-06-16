@echo off
chcp 65001 >nul
color 0A
title Gerenciador de Granjas de Frango - Instalação e Inicialização

echo.
echo  ████████╗██████╗   █████╗  ███╗   ██╗ ██████╗   █████╗ ███████╗
echo  ██╔═════╝██╔══██╗ ██╔══██╗ ████╗  ██║██╔════╝  ██╔══██╗██╔════╝
echo  ██║  ███╗██████╔╝ ███████║ ██╔██╗ ██║██║  ███╗ ███████║███████╗
echo  ██║   ██║██╔══██╗ ██╔══██║ ██║╚██╗██║██║   ██║ ██╔══██║╚════██║
echo  ╚██████╔╝██║  ██║ ██║  ██║ ██║ ╚████║╚██████╔╝ ██║  ██║███████║
echo   ╚═════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═══╝ ╚═════╝  ╚═╝  ╚═╝╚══════╝
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🐔 GERENCIADOR DE GRANJAS DE FRANGO - VERSÃO COMPLETA
echo  🇧🇷 Sistema profissional em português brasileiro  
echo  💻 Instalação automática para Windows
echo ═══════════════════════════════════════════════════════════════════
echo.

set "ERRO=0"

echo [PASSO 1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Python não está instalado ou não está no PATH
    echo.
    echo 📥 SOLUÇÃO:
    echo    1. Baixe Python em: https://python.org/downloads/
    echo    2. Durante a instalação, MARQUE "Add Python to PATH"
    echo    3. Reinicie o computador após instalar
    echo    4. Execute este arquivo novamente
    echo.
    set "ERRO=1"
    goto :erro
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado!

echo.
echo [PASSO 2/5] Verificando e instalando dependências...
echo 📦 Instalando FastAPI, Uvicorn, Pydantic e ReportLab...
echo    (Esta etapa pode demorar alguns minutos na primeira vez)
echo.

python -m pip install --quiet --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  Aviso: Não foi possível atualizar pip, mas continuando...
)

echo    • Instalando FastAPI...
python -m pip install --quiet fastapi
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar FastAPI
    set "ERRO=1"
    goto :erro
)

echo    • Instalando Uvicorn...
python -m pip install --quiet uvicorn
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar Uvicorn
    set "ERRO=1"
    goto :erro
)

echo    • Instalando Pydantic...
python -m pip install --quiet pydantic
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar Pydantic
    set "ERRO=1"
    goto :erro
)

echo    • Instalando ReportLab...
python -m pip install --quiet reportlab
if %errorlevel% neq 0 (
    echo ❌ Falha ao instalar ReportLab
    set "ERRO=1"
    goto :erro
)

echo ✅ Todas as dependências instaladas com sucesso!

echo.
echo [PASSO 3/5] Testando banco de dados...
python test_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Problema com o banco de dados
    echo 🔧 Tentando recriar banco...
    del /q broiler_data.db >nul 2>&1
    python test_database.py >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Falha crítica no banco de dados
        set "ERRO=1"
        goto :erro
    )
)
echo ✅ Banco de dados SQLite funcionando!

echo.
echo [PASSO 4/5] Construindo frontend...
if not exist "frontend\build" (
    echo 🔨 Primeira execução: construindo interface...
    echo    (Esta etapa pode demorar alguns minutos)
    cd frontend
    call npm install --silent
    call npm run build --silent
    cd ..
    echo ✅ Interface construída!
) else (
    echo ✅ Interface já construída!
)

echo.
echo [PASSO 5/5] Iniciando aplicação...
echo 🚀 Startando servidores...
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  🎉 APLICAÇÃO INICIANDO...
echo  🌐 O navegador abrirá automaticamente em alguns segundos
echo  📱 URL: http://127.0.0.1:3000
echo  💾 Dados salvos em: broiler_data.db
echo  📄 Relatórios em: exports\
echo.
echo  ⚠️  IMPORTANTE: NÃO FECHE esta janela!
echo      Para parar a aplicação: Pressione Ctrl+C
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Iniciar a aplicação principal
python app_launcher.py
goto :fim

:erro
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  ❌ ERRO NA INSTALAÇÃO
echo ═══════════════════════════════════════════════════════════════════
echo.
if "%ERRO%"=="1" (
    echo 🔍 DIAGNÓSTICO:
    echo    • Verifique sua conexão com a internet
    echo    • Execute como Administrador se necessário
    echo    • Certifique-se que o antivírus não está bloqueando
    echo.
    echo 🛠️  SOLUÇÕES:
    echo    1. Clique com botão direito neste arquivo
    echo    2. Selecione "Executar como administrador"  
    echo    3. Tente novamente
    echo.
)

:fim
echo.
echo Pressione qualquer tecla para sair...
pause >nul