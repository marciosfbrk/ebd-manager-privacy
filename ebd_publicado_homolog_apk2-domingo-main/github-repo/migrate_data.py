import os
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient

# Configurações
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'ebd_manager')

async def export_data():
    """Exporta dados do MongoDB local para arquivo JSON"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Dados para exportar
    data = {
        'turmas': [],
        'students': [],
        'users': [],
        'attendance': []
    }
    
    try:
        # Exportar turmas
        async for turma in db.turmas.find():
            turma['_id'] = str(turma['_id'])
            data['turmas'].append(turma)
        
        # Exportar alunos
        async for student in db.students.find():
            student['_id'] = str(student['_id'])
            data['students'].append(student)
        
        # Exportar usuários
        async for user in db.users.find():
            user['_id'] = str(user['_id'])
            data['users'].append(user)
        
        # Exportar presenças
        async for attendance in db.attendance.find():
            attendance['_id'] = str(attendance['_id'])
            data['attendance'].append(attendance)
        
        # Salvar no arquivo
        with open('database_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dados exportados com sucesso!")
        print(f"   - Turmas: {len(data['turmas'])}")
        print(f"   - Alunos: {len(data['students'])}")
        print(f"   - Usuários: {len(data['users'])}")
        print(f"   - Presenças: {len(data['attendance'])}")
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")
    
    finally:
        client.close()

async def import_data():
    """Importa dados do arquivo JSON para MongoDB Atlas"""
    if not os.path.exists('database_export.json'):
        print("❌ Arquivo database_export.json não encontrado!")
        return
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        with open('database_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Limpar collections existentes
        await db.turmas.delete_many({})
        await db.students.delete_many({})
        await db.users.delete_many({})
        await db.attendance.delete_many({})
        
        # Importar dados (removendo _id para evitar conflitos)
        for turma in data['turmas']:
            turma.pop('_id', None)
        await db.turmas.insert_many(data['turmas'])
        
        for student in data['students']:
            student.pop('_id', None)
        await db.students.insert_many(data['students'])
        
        for user in data['users']:
            user.pop('_id', None)
        await db.users.insert_many(data['users'])
        
        for attendance in data['attendance']:
            attendance.pop('_id', None)
        await db.attendance.insert_many(data['attendance'])
        
        print(f"✅ Dados importados com sucesso!")
        print(f"   - Turmas: {len(data['turmas'])}")
        print(f"   - Alunos: {len(data['students'])}")
        print(f"   - Usuários: {len(data['users'])}")
        print(f"   - Presenças: {len(data['attendance'])}")
        
    except Exception as e:
        print(f"❌ Erro ao importar dados: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'import':
        asyncio.run(import_data())
    else:
        asyncio.run(export_data())