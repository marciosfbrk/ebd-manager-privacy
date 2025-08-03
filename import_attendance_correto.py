#!/usr/bin/env python3
"""
Script para converter e importar dados de chamada no formato correto
Converte do formato agrupado para registros individuais por aluno
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

# Configurações
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def convert_and_import_attendance():
    """Converte dados agrupados em registros individuais de presença"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔄 Convertendo dados de chamada para formato correto...")
        
        # Buscar turma Professores e Oficiais
        turma = await db.turmas.find_one({'nome': 'Professores e Oficiais'})
        if not turma:
            print("❌ Turma 'Professores e Oficiais' não encontrada!")
            return
        
        turma_id = turma['id']
        print(f"✅ Turma encontrada: {turma['nome']} (ID: {turma_id})")
        
        # Buscar alunos da turma
        alunos = []
        async for aluno in db.students.find({'turma_id': turma_id}):
            alunos.append(aluno)
        
        print(f"✅ Encontrados {len(alunos)} alunos na turma")
        
        # Dados de chamada (os mesmos que você passou)
        dados_chamada = {
            "2025-07-06": {
                "Pr. Henrique": False,
                "Pb Paulo": False,
                "Pb Elias": False,
                "Coop Carlos": False,
                "Coop Elias Filho": False,
                "Coop Jailton": False,
                "Coop Santiago": False,
                "Irmã Dorcas": True,
                "Irmã Ester Carvalho": False,
                "Irmã Marry": True,
                "Irmã Renata": False,
                "Irmã Rosa": True,
                "Irmão Rubens": False,
                "Izabelle": False,
                "Juliana Silva": True,
                "Kesia Ferreira": True,
                "Márcio Ferreira": True,
                "Pb Sebastião": False,
                "Tia Ana Paula": False,
                "Tia Deise": False,
                "Tia Eliane": True,
                "Tia Evelyn": False,
                "Tia Flávia André": False,
                "Tia Kelly": False,
                "Tia Lu": False,
                "Tia Natália": True,
                "Tia Riane": True,
                "Tio Ítalo": True,
                "Pb Carlinhos": True,
                "Sidney Custodio": True,
                "Juliane Reis": True,
                "Vitória Ferreira": False
            },
            "2025-07-13": {
                "Pr. Henrique": True,
                "Pb Paulo": True,
                "Pb Elias": True,
                "Coop Carlos": False,
                "Coop Elias Filho": True,
                "Coop Jailton": True,
                "Coop Santiago": False,
                "Irmã Dorcas": False,
                "Irmã Ester Carvalho": False,
                "Irmã Marry": False,
                "Irmã Renata": False,
                "Irmã Rosa": True,
                "Irmão Rubens": False,
                "Izabelle": False,
                "Juliana Silva": True,
                "Kesia Ferreira": True,
                "Márcio Ferreira": False,
                "Pb Sebastião": False,
                "Tia Ana Paula": True,
                "Tia Deise": True,
                "Tia Eliane": True,
                "Tia Evelyn": True,
                "Tia Flávia André": False,
                "Tia Kelly": True,
                "Tia Lu": True,
                "Tia Natália": True,
                "Tia Riane": True,
                "Tio Ítalo": False,
                "Pb Carlinhos": False,
                "Sidney Custodio": False,
                "Juliane Reis": False,
                "Vitória Ferreira": False
            },
            "2025-07-20": {
                "Pr. Henrique": True,
                "Pb Paulo": True,
                "Pb Elias": False,
                "Coop Carlos": False,
                "Coop Elias Filho": False,
                "Coop Jailton": False,
                "Coop Santiago": True,
                "Irmã Dorcas": False,
                "Irmã Ester Carvalho": True,
                "Irmã Marry": False,
                "Irmã Renata": False,
                "Irmã Rosa": True,
                "Irmão Rubens": True,
                "Izabelle": True,
                "Juliana Silva": False,
                "Kesia Ferreira": False,
                "Márcio Ferreira": False,
                "Pb Sebastião": True,
                "Tia Ana Paula": False,
                "Tia Deise": True,
                "Tia Eliane": True,
                "Tia Evelyn": True,
                "Tia Flávia André": False,
                "Tia Kelly": True,
                "Tia Lu": False,
                "Tia Natália": True,
                "Tia Riane": True,
                "Tio Ítalo": True,
                "Pb Carlinhos": False,
                "Sidney Custodio": False,
                "Juliane Reis": False,
                "Vitória Ferreira": False
            },
            "2025-07-27": {
                "Pr. Henrique": False,
                "Pb Paulo": False,
                "Pb Elias": False,
                "Coop Carlos": False,
                "Coop Elias Filho": False,
                "Coop Jailton": False,
                "Coop Santiago": False,
                "Irmã Dorcas": False,
                "Irmã Ester Carvalho": False,
                "Irmã Marry": False,
                "Irmã Renata": False,
                "Irmã Rosa": False,
                "Irmão Rubens": False,
                "Izabelle": True,
                "Juliana Silva": False,
                "Kesia Ferreira": False,
                "Márcio Ferreira": False,
                "Pb Sebastião": False,
                "Tia Ana Paula": False,
                "Tia Deise": True,
                "Tia Eliane": True,
                "Tia Evelyn": True,
                "Tia Flávia André": False,
                "Tia Kelly": False,
                "Tia Lu": False,
                "Tia Natália": True,
                "Tia Riane": True,
                "Tio Ítalo": False,
                "Pb Carlinhos": False,
                "Sidney Custodio": False,
                "Juliane Reis": False,
                "Vitória Ferreira": False
            }
        }
        
        # Limpar chamadas antigas da turma
        await db.attendance.delete_many({'turma_id': turma_id})
        print("🧹 Chamadas antigas removidas")
        
        # Converter para registros individuais
        registros_attendance = []
        total_imported = 0
        
        for data, presencas in dados_chamada.items():
            print(f"📅 Processando {data}...")
            
            for nome_aluno, presente in presencas.items():
                # Encontrar aluno
                aluno_encontrado = None
                for aluno in alunos:
                    nome_completo = aluno.get('nome_completo', '')
                    if nome_completo.lower() == nome_aluno.lower():
                        aluno_encontrado = aluno
                        break
                
                if aluno_encontrado:
                    # Criar registro de attendance individual
                    attendance_record = {
                        'id': str(uuid.uuid4()),
                        'aluno_id': aluno_encontrado['id'],
                        'turma_id': turma_id,
                        'data': data,
                        'status': 'presente' if presente else 'ausente',
                        'oferta': 2.5 if presente else 0.0,  # Oferta média por pessoa presente
                        'biblias_entregues': 1 if presente else 0,
                        'revistas_entregues': 1 if presente else 0,
                        'criado_em': datetime.utcnow().isoformat()
                    }
                    registros_attendance.append(attendance_record)
                    total_imported += 1
                else:
                    print(f"   ⚠️  Aluno '{nome_aluno}' não encontrado")
        
        # Inserir todos os registros
        if registros_attendance:
            await db.attendance.insert_many(registros_attendance)
            print(f"✅ {len(registros_attendance)} registros de presença inseridos")
        
        # Verificar resultado
        for data in dados_chamada.keys():
            presentes = await db.attendance.count_documents({
                'turma_id': turma_id,
                'data': data,
                'status': 'presente'
            })
            total = await db.attendance.count_documents({
                'turma_id': turma_id,
                'data': data
            })
            print(f"📊 {data}: {presentes}/{total} presentes ({presentes/total*100:.1f}%)")
        
        print(f"\n🎉 Importação concluída com sucesso!")
        print(f"📋 Total de registros: {total_imported}")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(convert_and_import_attendance())