@echo off
chcp 65001 >nul
echo.
echo 🧪 TESTE RÁPIDO DO SISTEMA
echo ================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado
    goto :end
)
echo ✅ Python encontrado

REM Testar banco
echo 🔍 Testando banco de dados...
python -c "
from database import db
import asyncio

async def test():
    try:
        await db.insert_handler({'name': 'Teste Rápido'})
        print('✅ Banco funcionando')
        return True
    except Exception as e:
        print(f'❌ Erro no banco: {e}')
        return False

asyncio.run(test())
" 2>nul

if %errorlevel% neq 0 (
    echo ❌ Problema no banco
) else (
    echo ✅ Banco funcionando
)

REM Testar importações
echo 🔍 Testando dependências...
python -c "
try:
    import fastapi, uvicorn, pydantic, reportlab
    print('✅ Todas as dependências OK')
except ImportError as e:
    print(f'❌ Dependência faltando: {e}')
" 2>nul

echo.
echo ✅ SISTEMA PRONTO PARA USO!
echo.
echo Para iniciar: Duplo clique em INICIAR_APLICACAO.bat
echo.

:end
pause