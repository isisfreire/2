#!/usr/bin/env python3
"""
Gerenciador de Granjas de Frango - Versão Windows
Lançador compatível com Windows que usa Python diretamente
"""

import subprocess
import time
import webbrowser
import os
import sys
import signal
import threading
from pathlib import Path

# Configuração
FRONTEND_PORT = 3000
BACKEND_PORT = 8001
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

class GerenciadorGranjaFrango:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        
    def verificar_python(self):
        """Verificar se Python está disponível"""
        try:
            python_cmd = 'python' if os.name == 'nt' else 'python3'
            result = subprocess.run([python_cmd, '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Python encontrado: {result.stdout.strip()}")
            return python_cmd
        except Exception as e:
            print(f"❌ Python não encontrado: {e}")
            print("Por favor, instale Python 3.7+ do site python.org")
            return None
            
    def instalar_dependencias(self):
        """Instalar dependências do backend se necessário"""
        try:
            python_cmd = self.verificar_python()
            if not python_cmd:
                return False
                
            print("🔍 Verificando dependências...")
            
            # Verificar se as dependências estão instaladas
            required_packages = ['fastapi', 'uvicorn', 'pydantic', 'reportlab']
            missing_packages = []
            
            for package in required_packages:
                try:
                    subprocess.run([python_cmd, '-c', f'import {package}'], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    missing_packages.append(package)
            
            if missing_packages:
                print(f"📦 Instalando dependências faltantes: {missing_packages}")
                subprocess.run([python_cmd, '-m', 'pip', 'install'] + missing_packages, 
                             check=True)
                print("✅ Dependências instaladas com sucesso!")
            else:
                print("✅ Todas as dependências estão instaladas!")
                
            return True
            
        except Exception as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            return False
        
    def iniciar_backend(self):
        """Iniciar o servidor backend usando Python"""
        try:
            python_cmd = self.verificar_python()
            if not python_cmd:
                return False
                
            print("🚀 Iniciando servidor backend...")
            
            # Usar uvicorn para iniciar o servidor
            self.backend_process = subprocess.Popen([
                python_cmd, '-m', 'uvicorn', 'server:app',
                '--host', '127.0.0.1',
                '--port', str(BACKEND_PORT),
                '--reload'
            ], cwd=str(self.base_dir))
            
            # Aguardar o backend iniciar
            print("⏳ Aguardando backend inicializar...")
            time.sleep(5)
            
            # Verificar se o processo ainda está rodando
            if self.backend_process.poll() is not None:
                print("❌ Backend falhou ao iniciar")
                return False
                
            # Testar conectividade
            try:
                import requests
                response = requests.get(f'http://127.0.0.1:{BACKEND_PORT}/api/', timeout=5)
                if response.status_code == 200:
                    print(f"✅ Backend iniciado com sucesso (PID: {self.backend_process.pid})")
                    return True
                else:
                    print(f"❌ Backend não respondeu corretamente: {response.status_code}")
                    return False
            except ImportError:
                # Se requests não estiver disponível, assumir que funcionou
                print(f"✅ Backend iniciado (PID: {self.backend_process.pid})")
                return True
            except Exception as e:
                print(f"❌ Erro ao testar backend: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
    
    def iniciar_frontend(self):
        """Iniciar o servidor frontend"""
        try:
            python_cmd = self.verificar_python()
            if not python_cmd:
                return False
                
            frontend_build_dir = self.base_dir / "frontend" / "build"
            if not frontend_build_dir.exists():
                print("❌ Frontend build não encontrado. Executando build...")
                return self.build_frontend()
            
            print("🌐 Iniciando servidor frontend...")
            
            # Iniciar servidor HTTP Python para frontend
            self.frontend_process = subprocess.Popen([
                python_cmd, '-m', 'http.server', str(FRONTEND_PORT),
                '--bind', '127.0.0.1'
            ], cwd=str(frontend_build_dir),
               stdout=subprocess.DEVNULL, 
               stderr=subprocess.DEVNULL)
            
            # Aguardar o frontend iniciar
            time.sleep(3)
            
            if self.frontend_process.poll() is not None:
                print("❌ Servidor frontend falhou ao iniciar")
                return False
                
            print(f"✅ Servidor frontend iniciado (PID: {self.frontend_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Falha ao iniciar frontend: {e}")
            return False
    
    def build_frontend(self):
        """Construir o frontend se necessário"""
        try:
            frontend_dir = self.base_dir / "frontend"
            if not frontend_dir.exists():
                print("❌ Diretório frontend não encontrado")
                return False
                
            print("🔨 Construindo frontend...")
            
            # Verificar se npm/yarn está disponível
            npm_cmd = 'npm'
            if os.name == 'nt':
                npm_cmd = 'npm.cmd'
                
            # Instalar dependências
            subprocess.run([npm_cmd, 'install'], cwd=str(frontend_dir), check=True)
            
            # Build
            subprocess.run([npm_cmd, 'run', 'build'], cwd=str(frontend_dir), check=True)
            
            print("✅ Frontend construído com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao construir frontend: {e}")
            print("💡 Certifique-se de que Node.js está instalado")
            return False
    
    def abrir_navegador(self):
        """Abrir a aplicação no navegador padrão"""
        try:
            print(f"🌐 Abrindo navegador em {FRONTEND_URL}...")
            webbrowser.open(FRONTEND_URL)
            print("✅ Navegador aberto com sucesso")
        except Exception as e:
            print(f"❌ Falha ao abrir navegador: {e}")
            print(f"🔗 Por favor, abra manualmente: {FRONTEND_URL}")
    
    def parar_servicos(self):
        """Parar todos os serviços"""
        print("\n🛑 Parando serviços...")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                print("✅ Servidor frontend parado")
            except:
                self.frontend_process.kill()
                print("🔥 Servidor frontend forçado a parar")
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("✅ Servidor backend parado")
            except:
                self.backend_process.kill()
                print("🔥 Servidor backend forçado a parar")
    
    def manipulador_sinal(self, signum, frame):
        """Manipular Ctrl+C e outros sinais de terminação"""
        print("\n⚠️ Sinal de terminação recebido...")
        self.parar_servicos()
        sys.exit(0)
    
    def executar(self):
        """Ponto de entrada principal da aplicação"""
        # Configurar manipuladores de sinal
        try:
            signal.signal(signal.SIGINT, self.manipulador_sinal)
            signal.signal(signal.SIGTERM, self.manipulador_sinal)
        except:
            pass  # Windows pode não suportar todos os sinais
        
        print("🐔 GERENCIADOR DE GRANJAS DE FRANGO - VERSÃO WINDOWS")
        print("=" * 60)
        print("🇧🇷 Interface 100% em Português Brasileiro")
        print("💻 Compatível com Windows, Linux e macOS")
        print("=" * 60)
        
        try:
            # Verificar Python
            if not self.verificar_python():
                input("Pressione Enter para sair...")
                return 1
            
            # Instalar dependências
            if not self.instalar_dependencias():
                input("Pressione Enter para sair...")
                return 1
            
            # Iniciar backend
            print("\n🔧 INICIALIZANDO SERVIÇOS...")
            if not self.iniciar_backend():
                print("❌ Falha crítica no backend")
                input("Pressione Enter para sair...")
                return 1
            
            # Iniciar frontend  
            if not self.iniciar_frontend():
                print("❌ Falha crítica no frontend")
                input("Pressione Enter para sair...")
                return 1
            
            # Abrir navegador
            self.abrir_navegador()
            
            print("\n" + "=" * 60)
            print("🎉 GERENCIADOR DE GRANJAS DE FRANGO ESTÁ FUNCIONANDO!")
            print(f"🌐 Acesse a aplicação em: {FRONTEND_URL}")
            print("💾 Dados são armazenados em: broiler_data.db")
            print("📄 Relatórios são salvos em: exports/")
            print("🇧🇷 Interface completamente em português!")
            print("\n⚠️  Para parar a aplicação: Pressione Ctrl+C ou feche esta janela")
            print("=" * 60)
            
            # Manter a aplicação executando
            try:
                while True:
                    time.sleep(1)
                    # Verificar se processos ainda estão executando
                    backend_running = self.backend_process and self.backend_process.poll() is None
                    frontend_running = self.frontend_process and self.frontend_process.poll() is None
                    
                    if not backend_running:
                        print("⚠️  Servidor backend parou inesperadamente")
                        break
                    if not frontend_running:
                        print("⚠️  Servidor frontend parou inesperadamente")
                        break
                        
            except KeyboardInterrupt:
                print("\n⚠️ Ctrl+C detectado...")
                
        except Exception as e:
            print(f"❌ Erro crítico na aplicação: {e}")
            return 1
        finally:
            self.parar_servicos()
            print("\n👋 Aplicação encerrada. Obrigado por usar o Gerenciador de Granjas de Frango!")
        
        return 0

if __name__ == "__main__":
    app = GerenciadorGranjaFrango()
    exit_code = app.executar()
    if exit_code != 0:
        input("Pressione Enter para sair...")
    sys.exit(exit_code)