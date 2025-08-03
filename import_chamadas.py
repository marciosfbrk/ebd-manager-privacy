#!/usr/bin/env python3
"""
Script para importar dados de chamada (presença) no EBD Manager
Aceita dados em formato JSON e importa para o MongoDB
"""

import asyncio
import json
import os
import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

# Configurações
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

print(f"🔗 Conectando ao MongoDB: {MONGO_URL}")
print(f"📊 Database: {DB_NAME}")

async def import_chamadas_from_json(json_file_path):
    """Importa dados de chamada a partir de arquivo JSON"""
    
    if not os.path.exists(json_file_path):
        print(f"❌ Arquivo {json_file_path} não encontrado!")
        return
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Carregar dados do JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            chamadas_data = json.load(f)
        
        print(f"📄 Carregando dados de {json_file_path}")
        
        # Buscar turmas e alunos existentes
        turmas = []
        async for turma in db.turmas.find():
            turmas.append(turma)
        
        alunos = []
        async for aluno in db.students.find():
            alunos.append(aluno)
        
        print(f"📋 Encontradas {len(turmas)} turmas e {len(alunos)} alunos")
        
        # Processar cada data de chamada
        total_imported = 0
        
        for chamada in chamadas_data.get('chamadas', []):
            data = chamada.get('data')
            turma_nome = chamada.get('turma')
            presencas = chamada.get('presencas', [])
            ofertas = chamada.get('ofertas', 0.0)
            materiais = chamada.get('materiais_distribuidos', 0)
            
            # Encontrar turma
            turma_encontrada = None
            for turma in turmas:
                if turma['nome'].lower() == turma_nome.lower():
                    turma_encontrada = turma
                    break
            
            if not turma_encontrada:
                print(f"⚠️  Turma '{turma_nome}' não encontrada para data {data}")
                continue
            
            # Encontrar alunos da turma
            alunos_turma = [a for a in alunos if a['turma_id'] == turma_encontrada['id']]
            
            # Gerar presenças baseadas nos dados ou automaticamente
            attendance_records = []
            
            if presencas:
                # Usar dados específicos de presença
                for presenca in presencas:
                    aluno_nome = presenca.get('aluno')
                    presente = presenca.get('presente', True)
                    
                    # Encontrar aluno
                    aluno_encontrado = None
                    for aluno in alunos_turma:
                        nome_aluno = aluno.get('nome_completo', aluno.get('nome', ''))
                        if nome_aluno.lower() == aluno_nome.lower():
                            aluno_encontrado = aluno
                            break
                    
                    if aluno_encontrado:
                        attendance_records.append({
                            'student_id': aluno_encontrado['id'],
                            'student_name': aluno_encontrado.get('nome_completo', aluno_encontrado.get('nome', '')),
                            'present': presente
                        })
            else:
                # Gerar presenças automáticas (80-95% de presença)
                for aluno in alunos_turma:
                    # 85% de chance de estar presente (número realista)
                    presente = random.random() < 0.85
                    attendance_records.append({
                        'student_id': aluno['id'],
                        'student_name': aluno['nome'],
                        'present': presente
                    })
            
            # Criar registro de chamada
            chamada_record = {
                'id': str(uuid.uuid4()),
                'data': data,
                'turma_id': turma_encontrada['id'],
                'turma_nome': turma_encontrada['nome'],
                'attendance': attendance_records,
                'ofertas': float(ofertas),
                'materiais_distribuidos': int(materiais),
                'total_alunos': len(alunos_turma),
                'total_presentes': len([a for a in attendance_records if a['present']]),
                'created_at': datetime.now().isoformat()
            }
            
            # Verificar se já existe chamada para esta data e turma
            existing = await db.attendance.find_one({
                'data': data,
                'turma_id': turma_encontrada['id']
            })
            
            if existing:
                # Atualizar chamada existente
                await db.attendance.replace_one(
                    {'_id': existing['_id']},
                    chamada_record
                )
                print(f"🔄 Atualizada chamada para {turma_encontrada['nome']} em {data}")
            else:
                # Inserir nova chamada
                await db.attendance.insert_one(chamada_record)
                print(f"➕ Nova chamada para {turma_encontrada['nome']} em {data}")
            
            total_imported += 1
        
        print(f"\n✅ Importação concluída!")
        print(f"📊 Total de chamadas processadas: {total_imported}")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

def create_example_json():
    """Cria um arquivo JSON de exemplo para demonstrar o formato"""
    
    example_data = {
        "chamadas": [
            {
                "data": "2025-07-06",
                "turma": "Jovens",
                "ofertas": 45.50,
                "materiais_distribuidos": 25,
                "presencas": [
                    {"aluno": "João Silva", "presente": True},
                    {"aluno": "Maria Santos", "presente": True},
                    {"aluno": "Pedro Oliveira", "presente": False}
                ]
            },
            {
                "data": "2025-07-13", 
                "turma": "Adolescentes",
                "ofertas": 32.80,
                "materiais_distribuidos": 18
                # Se não especificar "presencas", será gerada automaticamente
            },
            {
                "data": "2025-07-20",
                "turma": "Adultos Unidos", 
                "ofertas": 78.30,
                "materiais_distribuidos": 40,
                "presencas": [
                    {"aluno": "Carlos Mendes", "presente": True},
                    {"aluno": "Ana Costa", "presente": True}
                ]
            }
        ]
    }
    
    with open('exemplo_chamadas.json', 'w', encoding='utf-8') as f:
        json.dump(example_data, f, ensure_ascii=False, indent=2)
    
    print("📝 Arquivo exemplo_chamadas.json criado!")
    print("   Edite este arquivo com suas datas e execute novamente.")

async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("📋 Uso:")
        print("   python import_chamadas.py arquivo.json")
        print("   python import_chamadas.py exemplo")
        print()
        
        # Verificar se existe arquivo padrão
        if os.path.exists('chamadas.json'):
            print("📄 Encontrado arquivo 'chamadas.json', importando...")
            await import_chamadas_from_json('chamadas.json')
        else:
            print("📝 Criando arquivo de exemplo...")
            create_example_json()
        return
    
    if sys.argv[1] == 'exemplo':
        create_example_json()
        return
    
    json_file = sys.argv[1]
    await import_chamadas_from_json(json_file)

if __name__ == "__main__":
    asyncio.run(main())