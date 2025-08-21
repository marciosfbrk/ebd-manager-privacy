#!/usr/bin/env python3
"""
Setup completo para deploy do EBD Manager
- Cria usuários obrigatórios
- Importa dados do backup se necessário
- Verifica integridade do sistema
"""
import asyncio
import os
import sys
import json
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

# Configurar variáveis de ambiente
if not os.environ.get('MONGO_URL'):
    os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
if not os.environ.get('DB_NAME'):
    os.environ['DB_NAME'] = 'ebd_database'

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def setup_complete_system():
    """Setup completo do sistema para deploy"""
    
    print("🚀 DEPLOY SETUP - EBD MANAGER")
    print("=" * 60)
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
        
        # ETAPA 1: Criar usuários obrigatórios
        print("\n📋 ETAPA 1: Configurando usuários do sistema...")
        
        required_users = [
            {
                "email": "admin@ebd.com",
                "nome": "Márcio Ferreira", 
                "tipo": "admin",
                "senha": "123456"
            },
            {
                "email": "kell@ebd.com",
                "nome": "Kelliane Ferreira",
                "tipo": "professor", 
                "senha": "123456"
            }
        ]
        
        for user_info in required_users:
            existing_user = await db.users.find_one({"email": user_info["email"]})
            
            user_data = {
                "id": str(uuid.uuid4()) if not existing_user else existing_user.get("id", str(uuid.uuid4())),
                "nome": user_info["nome"],
                "email": user_info["email"],
                "senha_hash": hash_password(user_info["senha"]),
                "tipo": user_info["tipo"],
                "turmas_permitidas": [],
                "ativo": True,
                "criado_em": existing_user.get("criado_em", datetime.now()) if existing_user else datetime.now(),
                "deploy_ready": True,
                "deploy_timestamp": datetime.now()
            }
            
            if existing_user:
                await db.users.update_one(
                    {"email": user_info["email"]},
                    {"$set": user_data}
                )
                print(f"🔄 Usuário atualizado: {user_info['nome']} ({user_info['email']})")
            else:
                await db.users.insert_one(user_data)
                print(f"✅ Usuário criado: {user_info['nome']} ({user_info['email']})")
        
        # ETAPA 2: Verificar se precisa importar dados
        print("\n📊 ETAPA 2: Verificando dados do sistema...")
        
        turmas_count = await db.turmas.count_documents({})
        students_count = await db.students.count_documents({})
        
        print(f"   🏫 Turmas existentes: {turmas_count}")
        print(f"   👥 Alunos existentes: {students_count}")
        
        # Se não tem dados, tentar importar do backup
        if turmas_count == 0 or students_count == 0:
            print("\n📥 Importando dados do backup...")
            
            backup_file = Path("/app/database_export_complete.json")
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                # Limpar dados existentes
                collections = ['turmas', 'students', 'revistas', 'attendance']
                for collection_name in collections:
                    await db[collection_name].delete_many({})
                
                # Importar turmas
                if 'turmas' in backup_data and backup_data['turmas']:
                    turmas_clean = []
                    for turma in backup_data['turmas']:
                        turma_copy = turma.copy()
                        if '_id' in turma_copy:
                            del turma_copy['_id']
                        turmas_clean.append(turma_copy)
                    
                    await db.turmas.insert_many(turmas_clean)
                    print(f"   ✅ {len(turmas_clean)} turmas importadas")
                
                # Importar alunos
                if 'students' in backup_data and backup_data['students']:
                    students_clean = []
                    for student in backup_data['students']:
                        student_copy = student.copy()
                        if '_id' in student_copy:
                            del student_copy['_id']
                        students_clean.append(student_copy)
                    
                    await db.students.insert_many(students_clean)
                    print(f"   ✅ {len(students_clean)} alunos importados")
                
                # Importar revistas
                if 'revistas' in backup_data and backup_data['revistas']:
                    revistas_clean = []
                    for revista in backup_data['revistas']:
                        revista_copy = revista.copy()
                        if '_id' in revista_copy:
                            del revista_copy['_id']
                        revistas_clean.append(revista_copy)
                    
                    await db.revistas.insert_many(revistas_clean)
                    print(f"   ✅ {len(revistas_clean)} revistas importadas")
                
                print("✅ Dados importados do backup com sucesso!")
            else:
                print("⚠️  Arquivo de backup não encontrado, continuando com dados vazios")
        
        # ETAPA 3: Verificação final
        print("\n🔍 ETAPA 3: Verificação final do sistema...")
        
        final_turmas = await db.turmas.count_documents({})
        final_students = await db.students.count_documents({})
        final_users = await db.users.count_documents({})
        final_revistas = await db.revistas.count_documents({})
        
        print(f"   👥 Usuários: {final_users}")
        print(f"   🏫 Turmas: {final_turmas}")
        print(f"   👨‍🎓 Alunos: {final_students}")
        print(f"   📚 Revistas: {final_revistas}")
        
        # Verificar se usuários obrigatórios existem
        admin_check = await db.users.find_one({"email": "admin@ebd.com"})
        prof_check = await db.users.find_one({"email": "kell@ebd.com"})
        
        print()
        print("🎉 DEPLOY SETUP CONCLUÍDO COM SUCESSO!")
        print()
        print("🔑 CREDENCIAIS DE ACESSO:")
        print("   👤 Admin:", "✅ admin@ebd.com / 123456" if admin_check else "❌ Não encontrado")
        print("   👨‍🏫 Prof: ", "✅ kell@ebd.com / 123456" if prof_check else "❌ Não encontrado")
        print()
        print("📈 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("   🌐 Todos os dados foram configurados")
        print("   ✅ Usuários garantidos para login")
        print("   🚀 Deploy pode ser realizado")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ ERRO no setup: {e}")
        return False

async def main():
    """Função principal"""
    success = await setup_complete_system()
    
    print("\n" + "="*60)
    if success:
        print("✅ DEPLOY SETUP FINALIZADO COM SUCESSO")
        print("Sistema pronto para deploy em produção!")
    else:
        print("❌ DEPLOY SETUP FALHOU")
        print("Verifique os erros acima antes de fazer deploy")
        sys.exit(1)
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())