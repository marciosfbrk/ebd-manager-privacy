#!/usr/bin/env python3
"""
Script para restaurar backup completo do EBD Manager
"""

import asyncio
import json
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

# Configurações
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def restore_backup(backup_file):
    """Restaura backup completo do sistema"""
    
    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup {backup_file} não encontrado!")
        return False
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Carregar dados do backup
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"🔄 Iniciando restauração do backup...")
        print(f"📁 Arquivo: {backup_file}")
        print(f"📅 Criado em: {backup_data['backup_info']['created_at']}")
        print(f"📝 Descrição: {backup_data['backup_info']['description']}")
        print()
        
        # Confirmar restauração (pular confirmação se for automático)
        if len(sys.argv) < 3 or sys.argv[2] != '--auto':
            confirm = input("⚠️  Esta operação irá SOBRESCREVER todos os dados atuais. Confirma? (digite 'SIM'): ")
            if confirm != 'SIM':
                print("❌ Restauração cancelada.")
                return False
        else:
            print("🤖 Modo automático - restaurando sem confirmação...")
        
        # Limpar collections existentes
        print("🧹 Limpando dados existentes...")
        collections = ['turmas', 'students', 'users', 'attendance', 'revistas', 'sessions']
        for collection_name in collections:
            await db[collection_name].delete_many({})
        
        # Restaurar dados
        print("📊 Restaurando dados...")
        
        # Restaurar turmas
        if backup_data['turmas']:
            # Remover _id para permitir reinserção
            turmas_data = []
            for turma in backup_data['turmas']:
                turma_copy = turma.copy()
                turma_copy.pop('_id', None)
                turmas_data.append(turma_copy)
            await db.turmas.insert_many(turmas_data)
            print(f"✅ Turmas restauradas: {len(turmas_data)}")
        
        # Restaurar alunos
        if backup_data['students']:
            students_data = []
            for student in backup_data['students']:
                student_copy = student.copy()
                student_copy.pop('_id', None)
                students_data.append(student_copy)
            await db.students.insert_many(students_data)
            print(f"✅ Alunos restaurados: {len(students_data)}")
        
        # Restaurar usuários
        if backup_data['users']:
            users_data = []
            for user in backup_data['users']:
                user_copy = user.copy()
                user_copy.pop('_id', None)
                users_data.append(user_copy)
            await db.users.insert_many(users_data)
            print(f"✅ Usuários restaurados: {len(users_data)}")
        
        # Restaurar presenças
        if backup_data['attendance']:
            attendance_data = []
            for att in backup_data['attendance']:
                att_copy = att.copy()
                att_copy.pop('_id', None)
                attendance_data.append(att_copy)
            await db.attendance.insert_many(attendance_data)
            print(f"✅ Presenças restauradas: {len(attendance_data)}")
        
        # Restaurar revistas
        if backup_data['revistas']:
            revistas_data = []
            for revista in backup_data['revistas']:
                revista_copy = revista.copy()
                revista_copy.pop('_id', None)
                revistas_data.append(revista_copy)
            await db.revistas.insert_many(revistas_data)
            print(f"✅ Revistas restauradas: {len(revistas_data)}")
        
        # Restaurar sessões
        if backup_data['sessions']:
            sessions_data = []
            for session in backup_data['sessions']:
                session_copy = session.copy()
                session_copy.pop('_id', None)
                sessions_data.append(session_copy)
            await db.sessions.insert_many(sessions_data)
            print(f"✅ Sessões restauradas: {len(sessions_data)}")
        
        print()
        print("🎉 Restauração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante restauração: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        client.close()

def list_backups():
    """Lista todos os backups disponíveis"""
    import glob
    
    backups = glob.glob("backup_ebd_*.json")
    if not backups:
        print("❌ Nenhum backup encontrado.")
        return
    
    print("📁 Backups disponíveis:")
    for backup in sorted(backups, reverse=True):
        try:
            with open(backup, 'r', encoding='utf-8') as f:
                data = json.load(f)
                info = data['backup_info']
                print(f"   - {backup}")
                print(f"     📅 {info['created_at']}")
                print(f"     📝 {info['description']}")
                print(f"     📊 Turmas: {info.get('total_turmas', 'N/A')}")
                print()
        except:
            print(f"   - {backup} (erro ao ler)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 Uso:")
        print("   python restore_backup.py <arquivo_backup>")
        print("   python restore_backup.py list")
        print()
        list_backups()
    elif sys.argv[1] == "list":
        list_backups()
    else:
        asyncio.run(restore_backup(sys.argv[1]))