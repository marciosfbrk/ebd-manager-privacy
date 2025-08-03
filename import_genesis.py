#!/usr/bin/env python3
"""
Script para importar dados de chamada da turma Genesis
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

async def import_genesis_attendance():
    """Importa dados de chamada da turma Genesis"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔄 Importando dados da turma Genesis...")
        
        # Buscar turma Genesis
        turma = await db.turmas.find_one({'nome': 'Genesis'})
        if not turma:
            print("❌ Turma 'Genesis' não encontrada!")
            return
        
        turma_id = turma['id']
        print(f"✅ Turma encontrada: {turma['nome']} (ID: {turma_id})")
        
        # Buscar alunos da turma
        alunos = []
        async for aluno in db.students.find({'turma_id': turma_id}):
            alunos.append(aluno)
        
        print(f"✅ Encontrados {len(alunos)} alunos na turma")
        
        # Dados de chamada da Genesis
        dados_chamada = {
            "2025-07-06": {
                "Agatha Mirella Souza Martins": False,
                "Arthur Galvão Costa da Silva": False,
                "Benjamin Henrique de Carvalho André": False,
                "Helena Marques Dantas": False,
                "Lara Heloíse Santos de Jesus": True,
                "Luiza Oliveira Reis": True,
                "Manuela de Azevedo Santos": True,
                "Otton Gomes Santos Albuquerque": False,
                "Ayla Sophia Souza Martins": False,
                "Isadora de Oliveira Santos Alves": True,
                "Leandro Pedro de Lima": True,
                "Mariana Rodrigues Augusto": False,
                "Miguel Silva dos Santos": False
            },
            "2025-07-13": {
                "Agatha Mirella Souza Martins": False,
                "Arthur Galvão Costa da Silva": False,
                "Benjamin Henrique de Carvalho André": False,
                "Helena Marques Dantas": True,
                "Lara Heloíse Santos de Jesus": True,
                "Luiza Oliveira Reis": True,
                "Manuela de Azevedo Santos": False,
                "Otton Gomes Santos Albuquerque": False,
                "Ayla Sophia Souza Martins": False,
                "Isadora de Oliveira Santos Alves": True,
                "Leandro Pedro de Lima": False,
                "Mariana Rodrigues Augusto": False,
                "Miguel Silva dos Santos": False
            },
            "2025-07-20": {
                "Agatha Mirella Souza Martins": True,
                "Arthur Galvão Costa da Silva": True,
                "Benjamin Henrique de Carvalho André": False,
                "Helena Marques Dantas": True,
                "Lara Heloíse Santos de Jesus": False,
                "Luiza Oliveira Reis": False,
                "Manuela de Azevedo Santos": True,
                "Otton Gomes Santos Albuquerque": False,
                "Ayla Sophia Souza Martins": False,
                "Isadora de Oliveira Santos Alves": False,
                "Leandro Pedro de Lima": True,
                "Mariana Rodrigues Augusto": False,
                "Miguel Silva dos Santos": False
            },
            "2025-07-27": {
                "Agatha Mirella Souza Martins": True,
                "Arthur Galvão Costa da Silva": False,
                "Benjamin Henrique de Carvalho André": False,
                "Helena Marques Dantas": True,
                "Lara Heloíse Santos de Jesus": True,
                "Luiza Oliveira Reis": True,
                "Manuela de Azevedo Santos": True,
                "Otton Gomes Santos Albuquerque": False,
                "Ayla Sophia Souza Martins": False,
                "Isadora de Oliveira Santos Alves": False,
                "Leandro Pedro de Lima": False,
                "Mariana Rodrigues Augusto": False,
                "Miguel Silva dos Santos": True
            }
        }
        
        # Limpar chamadas antigas da turma Genesis
        await db.attendance.delete_many({'turma_id': turma_id})
        print("🧹 Chamadas antigas da Genesis removidas")
        
        # Converter para registros individuais
        registros_attendance = []
        total_imported = 0
        alunos_nao_encontrados = []
        
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
                        'oferta': 3.0 if presente else 0.0,  # Oferta média Genesis (jovens)
                        'biblias_entregues': 1 if presente else 0,
                        'revistas_entregues': 1 if presente else 0,
                        'criado_em': datetime.utcnow().isoformat()
                    }
                    registros_attendance.append(attendance_record)
                    total_imported += 1
                else:
                    if nome_aluno not in alunos_nao_encontrados:
                        alunos_nao_encontrados.append(nome_aluno)
                        print(f"   ⚠️  Aluno '{nome_aluno}' não encontrado")
        
        # Inserir todos os registros
        if registros_attendance:
            await db.attendance.insert_many(registros_attendance)
            print(f"✅ {len(registros_attendance)} registros de presença inseridos")
        
        # Verificar resultado
        print(f"\n📊 Resumo da importação - Turma Genesis:")
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
            ofertas_total = 0
            async for record in db.attendance.find({
                'turma_id': turma_id,
                'data': data,
                'status': 'presente'
            }):
                ofertas_total += record.get('oferta', 0)
            
            print(f"📅 {data}: {presentes}/{total} presentes ({presentes/total*100:.1f}%) - R$ {ofertas_total:.2f}")
        
        print(f"\n🎉 Importação da Genesis concluída!")
        print(f"📋 Total de registros: {total_imported}")
        
        if alunos_nao_encontrados:
            print(f"⚠️  Alunos não encontrados: {len(alunos_nao_encontrados)}")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_genesis_attendance())