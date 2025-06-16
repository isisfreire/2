#!/usr/bin/env python3
"""
Gerenciador de Granjas de Frango - Lançador da Aplicação Principal
Este script inicia tanto o servidor backend quanto abre o frontend no navegador padrão.
"""

import subprocess
import time
import webbrowser
import os
import sys
import signal
from pathlib import Path

# Configuração
BACKEND_EXE = "./BroilerBackend64"
FRONTEND_PORT = 3000
BACKEND_PORT = 8001
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

class GerenciadorGranjaFrango:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        
    def iniciar_backend(self):
        """Iniciar o servidor backend"""
        try:
            backend_path = self.base_dir / "BroilerBackend64"
            if not backend_path.exists():
                raise FileNotFoundError(f"Executável do backend não encontrado: {backend_path}")
            
            # Tornar executável
            os.chmod(backend_path, 0o755)
            
            print("Iniciando servidor backend...")
            self.backend_process = subprocess.Popen(
                [str(backend_path)],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar o backend iniciar
            time.sleep(3)
            
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                raise RuntimeError(f"Backend falhou ao iniciar: {stderr.decode()}")
                
            print(f"✅ Servidor backend iniciado (PID: {self.backend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Falha ao iniciar backend: {e}")
            return False
    
    def iniciar_frontend(self):
        """Iniciar o servidor frontend"""
        try:
            frontend_build_dir = self.base_dir / "frontend" / "build"
            if not frontend_build_dir.exists():
                raise FileNotFoundError(f"Diretório build do frontend não encontrado: {frontend_build_dir}")
            
            print("Iniciando servidor frontend...")
            
            # Iniciar servidor HTTP Python para frontend
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "http.server", str(FRONTEND_PORT),
                "--bind", "127.0.0.1"
            ], cwd=str(frontend_build_dir),
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Aguardar o frontend iniciar
            time.sleep(2)
            
            if self.frontend_process.poll() is not None:
                raise RuntimeError("Servidor frontend falhou ao iniciar")
                
            print(f"✅ Servidor frontend iniciado (PID: {self.frontend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Falha ao iniciar frontend: {e}")
            return False
    
    def abrir_navegador(self):
        """Abrir a aplicação no navegador padrão"""
        try:
            print(f"Abrindo navegador em {FRONTEND_URL}...")
            webbrowser.open(FRONTEND_URL)
            print("✅ Navegador aberto com sucesso")
        except Exception as e:
            print(f"❌ Falha ao abrir navegador: {e}")
            print(f"Por favor, abra manualmente: {FRONTEND_URL}")
    
    def parar_servicos(self):
        """Parar todos os serviços"""
        print("\nParando serviços...")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Servidor frontend parado")
            except:
                self.frontend_process.kill()
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ Servidor backend parado")
            except:
                self.backend_process.kill()
    
    def manipulador_sinal(self, signum, frame):
        """Manipular Ctrl+C e outros sinais de terminação"""
        print("\nSinal de terminação recebido...")
        self.parar_servicos()
        sys.exit(0)
    
    def executar(self):
        """Ponto de entrada principal da aplicação"""
        # Configurar manipuladores de sinal
        signal.signal(signal.SIGINT, self.manipulador_sinal)
        signal.signal(signal.SIGTERM, self.manipulador_sinal)
        
        print("🐔 Gerenciador de Granjas de Frango Iniciando...")
        print("=" * 50)
        
        try:
            # Iniciar backend
            if not self.iniciar_backend():
                return 1
            
            # Iniciar frontend  
            if not self.iniciar_frontend():
                return 1
            
            # Abrir navegador
            self.abrir_navegador()
            
            print("\n" + "=" * 50)
            print("🎉 Gerenciador de Granjas de Frango está executando!")
            print(f"📱 Acesse a aplicação em: {FRONTEND_URL}")
            print("💾 Dados são armazenados localmente em: broiler_data.db")
            print("📄 Relatórios são salvos em: exports/")
            print("\nPressione Ctrl+C para parar a aplicação")
            print("=" * 50)
            
            # Manter a aplicação executando
            try:
                while True:
                    time.sleep(1)
                    # Verificar se processos ainda estão executando
                    if (self.backend_process and self.backend_process.poll() is not None or
                        self.frontend_process and self.frontend_process.poll() is not None):
                        print("⚠️  Um serviço parou inesperadamente")
                        break
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            print(f"❌ Erro na aplicação: {e}")
            return 1
        finally:
            self.parar_servicos()
        
        return 0

if __name__ == "__main__":
    app = GerenciadorGranjaFrango()
    sys.exit(app.executar())
