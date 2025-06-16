#!/usr/bin/env python3
"""
Launcher simples e robusto para Windows - sem caracteres especiais
"""

import subprocess
import time
import webbrowser
import os
import sys
import signal
from pathlib import Path

# Configuracao
FRONTEND_PORT = 3000
BACKEND_PORT = 8001
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

class AppLauncherSimple:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        self.running = True
        
    def start_backend(self):
        """Iniciar servidor backend"""
        try:
            print("Iniciando servidor backend...")
            
            # Comando para iniciar uvicorn
            cmd = [
                sys.executable, '-m', 'uvicorn', 'server:app',
                '--host', '127.0.0.1',
                '--port', str(BACKEND_PORT)
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=str(self.base_dir)
            )
            
            # Aguardar inicializacao
            print("Aguardando backend inicializar...")
            time.sleep(8)
            
            if self.backend_process.poll() is not None:
                print("ERRO: Backend falhou ao iniciar")
                return False
                
            # Testar conectividade
            try:
                import requests
                for attempt in range(5):
                    try:
                        response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/', timeout=3)
                        if response.status_code == 200:
                            print("OK: Backend respondendo corretamente!")
                            return True
                    except:
                        print(f"Tentativa {attempt + 1}/5: Aguardando backend...")
                        time.sleep(2)
                
                print("ERRO: Backend nao respondeu apos varias tentativas")
                return False
                
            except ImportError:
                # Se requests nao estiver disponivel, assumir que funcionou
                print("OK: Backend iniciado")
                return True
                
        except Exception as e:
            print(f"ERRO ao iniciar backend: {e}")
            return False
    
    def start_frontend(self):
        """Iniciar servidor frontend"""
        try:
            frontend_build_dir = self.base_dir / "frontend" / "build"
            if not frontend_build_dir.exists():
                print("ERRO: Frontend build nao encontrado!")
                return False
            
            print("Iniciando servidor frontend...")
            
            self.frontend_process = subprocess.Popen([
                sys.executable, '-m', 'http.server', str(FRONTEND_PORT),
                '--bind', '127.0.0.1'
            ], cwd=str(frontend_build_dir))
            
            time.sleep(3)
            
            if self.frontend_process.poll() is not None:
                print("ERRO: Frontend falhou ao iniciar")
                return False
                
            print("OK: Frontend iniciado com sucesso!")
            return True
            
        except Exception as e:
            print(f"ERRO ao iniciar frontend: {e}")
            return False
    
    def open_browser(self):
        """Abrir navegador"""
        try:
            print(f"Abrindo navegador: {FRONTEND_URL}")
            webbrowser.open(FRONTEND_URL)
            print("OK: Navegador aberto!")
        except Exception as e:
            print(f"ERRO ao abrir navegador: {e}")
            print(f"Abra manualmente: {FRONTEND_URL}")
    
    def stop_services(self):
        """Parar servicos"""
        self.running = False
        print("\nParando servicos...")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("Frontend parado")
            except:
                self.frontend_process.kill()
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate() 
                self.backend_process.wait(timeout=5)
                print("Backend parado")
            except:
                self.backend_process.kill()
    
    def signal_handler(self, signum, frame):
        """Handler para Ctrl+C"""
        print("\nCtrl+C detectado...")
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Executar aplicacao"""
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
        except:
            pass
        
        print("GERENCIADOR DE GRANJAS DE FRANGO - INICIANDO...")
        print("=" * 50)
        
        try:
            # Verificar dependencias criticas
            try:
                import fastapi, uvicorn, pydantic, reportlab
                print("OK: Dependencias verificadas")
            except ImportError as e:
                print(f"ERRO: Dependencia faltando: {e}")
                print("Execute novamente o INICIAR_WINDOWS.bat")
                input("Pressione Enter para sair...")
                return 1
            
            # Iniciar servicos
            if not self.start_backend():
                print("ERRO: Falha critica no backend")
                input("Pressione Enter para sair...")
                return 1
            
            if not self.start_frontend():
                print("ERRO: Falha critica no frontend")
                input("Pressione Enter para sair...")
                return 1
            
            # Abrir navegador
            self.open_browser()
            
            print("\n" + "=" * 50)
            print("APLICACAO FUNCIONANDO!")
            print(f"URL: {FRONTEND_URL}")
            print("Banco: broiler_data.db")
            print("Relatorios: exports/")
            print("\nMANTENHA esta janela aberta!")
            print("Para parar: Pressione Ctrl+C")
            print("=" * 50)
            
            # Loop principal
            while self.running:
                time.sleep(1)
                
                # Verificar se processos ainda estao rodando
                if self.backend_process and self.backend_process.poll() is not None:
                    print("AVISO: Backend parou inesperadamente")
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("AVISO: Frontend parou inesperadamente")
                    break
                    
        except KeyboardInterrupt:
            print("\nInterrupcao detectada...")
        except Exception as e:
            print(f"ERRO critico: {e}")
            input("Pressione Enter para sair...")
            return 1
        finally:
            self.stop_services()
            print("\nAplicacao encerrada!")
        
        input("Pressione Enter para sair...")
        return 0

if __name__ == "__main__":
    launcher = AppLauncherSimple()
    sys.exit(launcher.run())