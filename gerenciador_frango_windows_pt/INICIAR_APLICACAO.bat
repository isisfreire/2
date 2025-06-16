@echo off
chcp 65001 >nul
echo.
echo 🐔 GERENCIADOR DE GRANJAS DE FRANGO - VERSÃO WINDOWS
echo ================================================================
echo 🇧🇷 Sistema completo em português brasileiro
echo 💻 Compatível com Windows 10/11
echo ================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Por favor, instale Python 3.7+ do site oficial:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚙️  IMPORTANTE: Marque "Add Python to PATH" durante a instalação
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo.

REM Executar a aplicação
echo 🚀 Iniciando aplicação...
python iniciar_aplicacao.py

echo.
echo 👋 Aplicação encerrada.
pause