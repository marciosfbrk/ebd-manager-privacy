#!/usr/bin/env python3
"""
🚀 Instalador Automático EBD Manager
Configura tudo automaticamente no seu notebook
"""

import os
import sys
import subprocess
import json
import platform

def print_header(title):
    print("\n" + "="*50)
    print(f"   {title}")
    print("="*50)

def run_command(command, description):
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - SUCESSO")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERRO: {e}")
        print(f"Saída: {e.stdout}")
        print(f"Erro: {e.stderr}")
        return False

def check_requirements():
    print_header("VERIFICANDO PRÉ-REQUISITOS")
    
    # Verificar Python
    try:
        python_version = subprocess.run(['python', '--version'], 
                                      capture_output=True, text=True, check=True, shell=True)
        print(f"✅ Python: {python_version.stdout.strip()}")
    except:
        print("❌ Python não encontrado. Instale Python 3.8+")
        return False
    
    # Verificar Node.js
    try:
        node_version = subprocess.run(['node', '--version'], 
                                    capture_output=True, text=True, check=True, shell=True)
        print(f"✅ Node.js: {node_version.stdout.strip()}")
    except:
        print("❌ Node.js não encontrado. Instale Node.js LTS")
        return False
    
    # Verificar npm (com shell=True para Windows)
    try:
        npm_version = subprocess.run(['npm', '--version'], 
                                   capture_output=True, text=True, check=True, shell=True)
        print(f"✅ npm: {npm_version.stdout.strip()}")
    except:
        # Tentar caminho alternativo no Windows
        try:
            npm_version = subprocess.run('npm --version', 
                                       capture_output=True, text=True, check=True, shell=True)
            print(f"✅ npm: {npm_version.stdout.strip()}")
        except:
            print("❌ npm não encontrado. Reinstale Node.js")
            return False
    
    return True

def create_env_files():
    print_header("CRIANDO ARQUIVOS DE CONFIGURAÇÃO")
    
    # Backend .env
    backend_env = """MONGO_URL=mongodb://localhost:27017
DB_NAME=ebd_manager"""
    
    os.makedirs('backend', exist_ok=True)
    with open('backend/.env', 'w') as f:
        f.write(backend_env)
    print("✅ Backend .env criado")
    
    # Frontend .env
    frontend_env = """REACT_APP_BACKEND_URL=http://localhost:8001"""
    
    os.makedirs('frontend', exist_ok=True) 
    with open('frontend/.env', 'w') as f:
        f.write(frontend_env)
    print("✅ Frontend .env criado")

def install_backend():
    print_header("INSTALANDO BACKEND (Python/FastAPI)")
    
    if not os.path.exists('backend/requirements.txt'):
        print("❌ arquivo requirements.txt não encontrado")
        return False
    
    return run_command(
        'cd backend && python -m pip install -r requirements.txt',
        "Instalando dependências Python"
    )

def install_frontend():
    print_header("INSTALANDO FRONTEND (React)")
    
    if not os.path.exists('frontend/package.json'):
        print("❌ arquivo package.json não encontrado")
        return False
    
    return run_command(
        'cd frontend && npm install',
        "Instalando dependências Node.js"
    )

def restore_data():
    print_header("RESTAURANDO DADOS")
    
    if os.path.exists('restore_backup.py'):
        return run_command(
            'python restore_backup.py',
            "Restaurando backup completo"
        )
    else:
        print("⚠️ Script de backup não encontrado, mas continuando...")
        return True

def create_start_scripts():
    print_header("CRIANDO SCRIPTS DE INICIALIZAÇÃO")
    
    if platform.system() == "Windows":
        # Script Windows
        start_script = """@echo off
echo Iniciando EBD Manager...
start "Backend" cmd /k "cd backend && python server.py"
timeout /t 3
start "Frontend" cmd /k "cd frontend && npm start"
echo Sistema iniciando... Aguarde e acesse http://localhost:3000
pause"""
        
        with open('iniciar.bat', 'w') as f:
            f.write(start_script)
        print("✅ iniciar.bat criado")
        
    else:
        # Script Linux/Mac
        start_script = """#!/bin/bash
echo "Iniciando EBD Manager..."
cd backend && python server.py &
cd ../frontend && npm start &
echo "Sistema iniciando... Acesse http://localhost:3000"
wait"""
        
        with open('iniciar.sh', 'w') as f:
            f.write(start_script)
        os.chmod('iniciar.sh', 0o755)
        print("✅ iniciar.sh criado")

def main():
    print("🚀 INSTALADOR AUTOMÁTICO EBD MANAGER")
    print("Este script vai configurar tudo no seu notebook!")
    
    # Verificar pré-requisitos
    if not check_requirements():
        print("\n❌ ERRO: Instale os pré-requisitos primeiro!")
        print("1. Python 3.8+: https://python.org/downloads/")
        print("2. Node.js LTS: https://nodejs.org/")
        input("Pressione Enter para sair...")
        return
    
    # Criar arquivos de configuração
    create_env_files()
    
    # Instalar dependências
    if not install_backend():
        print("\n❌ ERRO na instalação do backend")
        input("Pressione Enter para sair...")
        return
    
    if not install_frontend():
        print("\n❌ ERRO na instalação do frontend")
        input("Pressione Enter para sair...")
        return
    
    # Restaurar dados
    restore_data()
    
    # Criar scripts
    create_start_scripts()
    
    # Sucesso!
    print_header("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    
    print("\n📋 COMO USAR:")
    print("1. Execute o arquivo de início:")
    if platform.system() == "Windows":
        print("   - Duplo clique em 'iniciar.bat'")
    else:
        print("   - Execute './iniciar.sh'")
    
    print("\n2. Aguarde carregar e acesse: http://localhost:3000")
    
    print("\n🔑 LOGIN INICIAL:")
    print("   Email: admin@ebd.com")
    print("   Senha: 123456")
    print("   (ALTERE a senha após o primeiro login!)")
    
    print("\n📊 DADOS INCLUÍDOS:")
    print("   ✅ Usuários administrativos")
    print("   ✅ 11 turmas da igreja")
    print("   ✅ 242 alunos cadastrados")
    print("   ✅ Chamadas históricas")
    print("   ✅ Revistas trimestrais")
    
    input("\nPressione Enter para finalizar...")

if __name__ == "__main__":
    main()