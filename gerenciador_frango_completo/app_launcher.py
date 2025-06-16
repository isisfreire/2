#!/usr/bin/env python3
"""
Launcher principal que inicia backend e frontend com tratamento robusto de erros
"""

import subprocess
import time
import webbrowser
import os
import sys
import signal
import threading
import socket
from pathlib import Path

# Configuração
FRONTEND_PORT = 3000
BACKEND_PORT = 8001
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

class AppLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        self.running = True
        
    def check_port(self, port):
        """Verificar se porta está livre"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            return result != 0  # True se porta está livre
    
    def kill_port(self, port):
        """Tentar liberar porta"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['netstat', '-ano'], capture_output=True)
                # No Windows é mais complexo, vamos apenas avisar
                print(f"⚠️  Porta {port} pode estar em uso")
            else:  # Linux/Mac
                subprocess.run(['pkill', '-f', f':{port}'], capture_output=True)
        except:
            pass
    
    def start_backend(self):
        """Iniciar servidor backend"""
        try:
            print("🔧 Verificando porta do backend...")
            if not self.check_port(BACKEND_PORT):
                print(f"⚠️  Porta {BACKEND_PORT} está em uso, tentando liberar...")
                self.kill_port(BACKEND_PORT)
                time.sleep(2)
            
            print("🚀 Iniciando servidor backend...")
            
            # Comando para iniciar uvicorn
            cmd = [
                sys.executable, '-m', 'uvicorn', 'server:app',
                '--host', '127.0.0.1',
                '--port', str(BACKEND_PORT),
                '--access-log'
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Aguardar inicialização
            print("⏳ Aguardando backend inicializar...")
            
            # Thread para ler output do backend
            def read_backend_output():
                if self.backend_process and self.backend_process.stdout:
                    for line in iter(self.backend_process.stdout.readline, ''):
                        if line and self.running:
                            if 'Application startup complete' in line:
                                print("✅ Backend totalmente inicializado!")
                            elif 'ERROR' in line.upper():
                                print(f"🔴 Backend: {line.strip()}")
                            elif 'INFO' in line:
                                print(f"🔵 Backend: {line.strip()}")
            
            threading.Thread(target=read_backend_output, daemon=True).start()
            
            # Esperar um pouco mais para garantir
            time.sleep(8)
            
            if self.backend_process.poll() is not None:
                print("❌ Backend falhou ao iniciar")
                return False
                
            # Testar conectividade
            import requests
            for attempt in range(5):
                try:
                    response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/', timeout=3)
                    if response.status_code == 200:
                        print("✅ Backend respondendo corretamente!")
                        data = response.json()
                        print(f"📡 API: {data.get('message', 'N/A')}")
                        return True
                    else:
                        print(f"⚠️  Backend respondeu com código: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"⏳ Tentativa {attempt + 1}/5: Aguardando backend...")
                    time.sleep(2)
            
            print("❌ Backend não respondeu após várias tentativas")
            return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
    
    def start_frontend(self):
        """Iniciar servidor frontend"""
        try:
            print("🌐 Verificando porta do frontend...")
            if not self.check_port(FRONTEND_PORT):
                print(f"⚠️  Porta {FRONTEND_PORT} está em uso, tentando liberar...")
                self.kill_port(FRONTEND_PORT)
                time.sleep(2)
            
            frontend_build_dir = self.base_dir / "frontend" / "build"
            if not frontend_build_dir.exists():
                print("❌ Frontend build não encontrado!")
                print("🔨 Execute 'npm run build' na pasta frontend primeiro")
                return False
            
            print("🌐 Iniciando servidor frontend...")
            
            self.frontend_process = subprocess.Popen([
                sys.executable, '-m', 'http.server', str(FRONTEND_PORT),
                '--bind', '127.0.0.1'
            ], cwd=str(frontend_build_dir),
               stdout=subprocess.DEVNULL, 
               stderr=subprocess.DEVNULL)
            
            time.sleep(3)
            
            if self.frontend_process.poll() is not None:
                print("❌ Frontend falhou ao iniciar")
                return False
                
            print("✅ Frontend iniciado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar frontend: {e}")
            return False
    
    def open_browser(self):
        """Abrir navegador"""
        try:
            print(f"🌐 Abrindo navegador: {FRONTEND_URL}")
            webbrowser.open(FRONTEND_URL)
            print("✅ Navegador aberto!")
        except Exception as e:
            print(f"❌ Erro ao abrir navegador: {e}")
            print(f"🔗 Abra manualmente: {FRONTEND_URL}")
    
    def stop_services(self):
        """Parar serviços"""
        self.running = False
        print("\n🛑 Parando serviços...")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend parado")
            except:
                self.frontend_process.kill()
                print("🔥 Frontend forçado a parar")
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ Backend parado")
            except:
                self.backend_process.kill()
                print("🔥 Backend forçado a parar")
    
    def signal_handler(self, signum, frame):
        """Handler para Ctrl+C"""
        print("\n⚠️ Ctrl+C detectado...")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Executar aplicação"""
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
        except:
            pass
        
        print("🐔 INICIANDO GERENCIADOR DE GRANJAS DE FRANGO...")
        print("=" * 50)
        
        try:
            # Verificar dependências críticas
            try:
                import fastapi, uvicorn, pydantic, reportlab
                print("✅ Dependências verificadas")
            except ImportError as e:
                print(f"❌ Dependência faltando: {e}")
                print("🔧 Execute novamente o INSTALAR_E_INICIAR.bat")
                return 1
            
            # Iniciar serviços
            if not self.start_backend():
                print("❌ Falha crítica no backend")
                return 1
            
            if not self.start_frontend():
                print("❌ Falha crítica no frontend")
                return 1
            
            # Abrir navegador
            self.open_browser()
            
            print("\n" + "=" * 50)
            print("🎉 APLICAÇÃO FUNCIONANDO!")
            print(f"🌐 URL: {FRONTEND_URL}")
            print("💾 Banco: broiler_data.db")
            print("📄 Relatórios: exports/")
            print("\n⚠️  MANTENHA esta janela aberta!")
            print("   Para parar: Pressione Ctrl+C")
            print("=" * 50)
            
            # Loop principal
            while self.running:
                time.sleep(1)
                
                # Verificar se processos ainda estão rodando
                if self.backend_process and self.backend_process.poll() is not None:
                    print("⚠️  Backend parou inesperadamente")
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️  Frontend parou inesperadamente")
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ Interrupção detectada...")
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            return 1
        finally:
            self.stop_services()
            print("\n👋 Aplicação encerrada!")
        
        return 0

if __name__ == "__main__":
    launcher = AppLauncher()
    sys.exit(launcher.run())