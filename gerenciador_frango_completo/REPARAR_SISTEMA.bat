@echo off
chcp 65001 >nul
title Reparação Automática do Sistema

echo.
echo 🔧 REPARAÇÃO AUTOMÁTICA DO SISTEMA
echo ════════════════════════════════════════════════════════════════
echo  Esta ferramenta vai tentar resolver problemas automaticamente
echo ════════════════════════════════════════════════════════════════
echo.

echo [1/5] Atualizando pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo ⚠️  Aviso: Não foi possível atualizar pip
) else (
    echo ✅ pip atualizado
)

echo.
echo [2/5] Reinstalando dependências principais...
python -m pip uninstall -y fastapi uvicorn pydantic reportlab >nul 2>&1
python -m pip install fastapi uvicorn pydantic reportlab --quiet
if %errorlevel% neq 0 (
    echo ❌ Falha na reinstalação
    goto :erro
) else (
    echo ✅ Dependências reinstaladas
)

echo.
echo [3/5] Verificando banco de dados...
if exist "broiler_data.db" (
    echo 🗑️  Removendo banco corrompido...
    del /q "broiler_data.db" >nul 2>&1
)

python test_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Problema persistente no banco
    goto :erro
) else (
    echo ✅ Banco recriado com sucesso
)

echo.
echo [4/5] Verificando frontend...
if not exist "frontend\build" (
    echo 🔨 Reconstruindo frontend...
    cd frontend
    call npm install --silent
    call npm run build --silent
    cd ..
    echo ✅ Frontend reconstruído
) else (
    echo ✅ Frontend OK
)

echo.
echo [5/5] Limpando processos antigos...
taskkill /f /im python.exe >nul 2>&1
echo ✅ Processos limpos

echo.
echo ════════════════════════════════════════════════════════════════
echo ✅ REPARAÇÃO CONCLUÍDA COM SUCESSO!
echo.
echo 🚀 Agora execute: INSTALAR_E_INICIAR.bat
echo ════════════════════════════════════════════════════════════════
goto :fim

:erro
echo.
echo ════════════════════════════════════════════════════════════════
echo ❌ REPARAÇÃO FALHOU
echo.
echo 🆘 SOLUÇÕES MANUAIS:
echo    1. Reinstalar Python do site python.org
echo    2. Executar como Administrador
echo    3. Verificar conexão com internet
echo    4. Desativar antivírus temporariamente
echo ════════════════════════════════════════════════════════════════

:fim
pause