#!/usr/bin/env python3
"""
Teste de banco de dados para verificar se está funcionando
"""

import sys
import os
import sqlite3
from pathlib import Path

def test_database():
    """Testar se o banco SQLite está funcionando"""
    try:
        # Importar database
        from database import db
        import asyncio
        
        async def run_tests():
            print("🔍 Testando banco de dados...")
            
            # Testar criação de handler
            handler_data = {
                'name': 'Teste Sistema',
                'email': 'teste@sistema.com'
            }
            
            handler_id = await db.insert_handler(handler_data)
            print(f"✅ Handler criado: {handler_id}")
            
            # Testar busca
            handler = await db.find_handler_by_name('Teste Sistema')
            if handler:
                print("✅ Busca funcionando")
            
            # Testar tabelas de cálculos
            calculations = await db.get_all_calculations()
            print(f"✅ Tabela calculations: {len(calculations)} registros")
            
            return True
        
        result = asyncio.run(run_tests())
        return result
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print("✅ Banco de dados OK")
        sys.exit(0)
    else:
        print("❌ Banco de dados com problemas")
        sys.exit(1)