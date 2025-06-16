@echo off
title Reparacao Automatica do Sistema

echo.
echo REPARACAO AUTOMATICA DO SISTEMA
echo ================================================================
echo Esta ferramenta vai tentar resolver problemas automaticamente
echo ================================================================
echo.

echo [1/5] Atualizando pip...
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo Aviso: Nao foi possivel atualizar pip
) else (
    echo OK: pip atualizado
)

echo.
echo [2/5] Reinstalando dependencias principais...
python -m pip uninstall -y fastapi uvicorn pydantic reportlab >nul 2>&1
python -m pip install fastapi uvicorn pydantic reportlab --quiet
if %errorlevel% neq 0 (
    echo ERRO: Falha na reinstalacao
    goto :erro
) else (
    echo OK: Dependencias reinstaladas
)

echo.
echo [3/5] Verificando banco de dados...
if exist "broiler_data.db" (
    echo Removendo banco corrompido...
    del /q "broiler_data.db" >nul 2>&1
)

python test_database.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Problema persistente no banco
    goto :erro
) else (
    echo OK: Banco recriado com sucesso
)

echo.
echo [4/5] Verificando frontend...
if not exist "frontend\build" (
    echo Reconstruindo frontend...
    cd frontend
    call npm install --silent
    call npm run build --silent
    cd ..
    echo OK: Frontend reconstruido
) else (
    echo OK: Frontend ja existe
)

echo.
echo [5/5] Limpando processos antigos...
taskkill /f /im python.exe >nul 2>&1
echo OK: Processos limpos

echo.
echo ================================================================
echo REPARACAO CONCLUIDA COM SUCESSO!
echo.
echo Agora execute: INICIAR_WINDOWS.bat
echo ================================================================
goto :fim

:erro
echo.
echo ================================================================
echo REPARACAO FALHOU
echo.
echo SOLUCOES MANUAIS:
echo    1. Reinstalar Python do site python.org
echo    2. Executar como Administrador
echo    3. Verificar conexao com internet
echo    4. Desativar antivirus temporariamente
echo ================================================================

:fim
pause