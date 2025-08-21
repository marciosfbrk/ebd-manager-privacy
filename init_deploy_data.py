#!/usr/bin/env python3
"""
Script de inicialização para deploy
Garante que usuários padrão sejam criados quando o sistema for deployado
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
import uuid
from datetime import datetime

# Configurar variáveis de ambiente padrão se não existirem
if not os.environ.get('MONGO_URL'):
    os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
if not os.environ.get('DB_NAME'):
    os.environ['DB_NAME'] = 'ebd_database'

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

def hash_password(password: str) -> str:
    """Hash da senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

async def init_deploy_users():
    """
    Inicializar usuários padrão para deploy
    Sempre executado quando o sistema subir
    """
    print("🚀 INICIALIZAÇÃO PARA DEPLOY - EBD MANAGER")
    print("=" * 50)
    print(f"📡 MongoDB: {MONGO_URL}")
    print(f"💾 Database: {DB_NAME}")
    print()
    
    try:
        # Conectar ao banco
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conexão com MongoDB estabelecida")
        
        # Usuários obrigatórios para deploy
        required_users = [
            {
                "email": "admin@ebd.com",
                "nome": "Márcio Ferreira",
                "tipo": "admin",
                "senha": "123456",
                "descricao": "Administrador do sistema"
            },
            {
                "email": "kell@ebd.com",
                "nome": "Kelliane Ferreira", 
                "tipo": "professor",
                "senha": "123456",
                "descricao": "Professor(a) da EBD"
            }
        ]
        
        print("👥 Verificando/criando usuários obrigatórios...")
        
        for user_info in required_users:
            existing_user = await db.users.find_one({"email": user_info["email"]})
            
            if existing_user:
                # Usuário existe - verificar se precisa de updates
                updates = {}
                
                # Verificar senha (deve ser sempre 123456 para deploy)
                if existing_user.get("senha_hash") != hash_password("123456"):
                    updates["senha_hash"] = hash_password("123456")
                
                # Verificar se está ativo
                if not existing_user.get("ativo", True):
                    updates["ativo"] = True
                
                # Verificar nome
                if existing_user.get("nome") != user_info["nome"]:
                    updates["nome"] = user_info["nome"]
                
                # Marcar como pronto para deploy
                updates["deploy_ready"] = True
                updates["last_deploy_check"] = datetime.now()
                
                if updates:
                    await db.users.update_one(
                        {"email": user_info["email"]},
                        {"$set": updates}
                    )
                    print(f"🔄 {user_info['descricao']} atualizado: {user_info['email']}")
                else:
                    print(f"✓ {user_info['descricao']} já existe: {user_info['email']}")
            else:
                # Criar novo usuário
                new_user = {
                    "id": str(uuid.uuid4()),
                    "nome": user_info["nome"],
                    "email": user_info["email"],
                    "senha_hash": hash_password(user_info["senha"]),
                    "tipo": user_info["tipo"],
                    "turmas_permitidas": [],
                    "ativo": True,
                    "criado_em": datetime.now(),
                    "deploy_ready": True,
                    "created_by_deploy": True
                }
                
                await db.users.insert_one(new_user)
                print(f"✅ {user_info['descricao']} criado: {user_info['email']}")
        
        # Verificar se temos dados básicos (turmas)
        turmas_count = await db.turmas.count_documents({})
        students_count = await db.students.count_documents({})
        
        print()
        print("📊 STATUS DO BANCO DE DADOS:")
        print(f"   🏫 Turmas: {turmas_count}")
        print(f"   👥 Alunos: {students_count}")
        
        if turmas_count == 0:
            print("⚠️  AVISO: Nenhuma turma encontrada!")
            print("   Execute o script de importação de dados se necessário.")
        
        print()
        print("🎉 INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("🌐 Credenciais para login:")
        print("   👤 Admin: admin@ebd.com / 123456")
        print("   👨‍🏫 Prof:  kell@ebd.com / 123456")
        print()
        print("✅ Sistema pronto para uso em produção!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ ERRO na inicialização: {e}")
        print("⚠️  Verifique a conexão com MongoDB e tente novamente")
        return False

async def main():
    """Função principal"""
    success = await init_deploy_users()
    if not success:
        sys.exit(1)
    
    print("\n" + "="*50)
    print("SCRIPT DE INICIALIZAÇÃO FINALIZADO")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())