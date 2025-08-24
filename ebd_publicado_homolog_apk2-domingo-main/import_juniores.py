#!/usr/bin/env python3
"""
Script para importar dados de chamada da turma Juniores
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

async def import_juniores_attendance():
    """Importa dados de chamada da turma Juniores"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔄 Importando dados da turma Juniores...")
        
        # Buscar turma Juniores
        turma = await db.turmas.find_one({'nome': 'Juniores'})
        if not turma:
            print("❌ Turma 'Juniores' não encontrada!")
            return
        
        turma_id = turma['id']
        print(f"✅ Turma encontrada: {turma['nome']} (ID: {turma_id})")
        
        # Buscar alunos da turma
        alunos = []
        async for aluno in db.students.find({'turma_id': turma_id}):
            alunos.append(aluno)
        
        print(f"✅ Encontrados {len(alunos)} alunos na turma")
        
        # Dados de chamada dos Juniores
        dados_chamada = {
            "2025-07-06": {
                "Beatriz Pedro de Lima": False,
                "Davi Afonso Lana": False,
                "Enzo Leonardo Bitencourt Souza": True,
                "Felype Augusto Oliveira de Jesus": False,
                "Gustavo Lorenzo Ferreira": True,
                "Mariana Lima de Sousa": False,
                "Isabelle Sophia Da Costa De A": True,
                "Luíza (Suellen Tayrone)": False,
                "Hadassah Victoria Gabriel Tavares": False,
                "Davi Caldeira Rodrigues": False,
                "Ana Luiza Santana de Moura": False,
                "Kemuel Brito": False
            },
            "2025-07-13": {
                "Beatriz Pedro de Lima": True,
                "Davi Afonso Lana": False,
                "Enzo Leonardo Bitencourt Souza": True,
                "Felype Augusto Oliveira de Jesus": True,
                "Gustavo Lorenzo Ferreira": True,
                "Mariana Lima de Sousa": False,
                "Isabelle Sophia Da Costa De A": False,
                "Luíza (Suellen Tayrone)": False,
                "Hadassah Victoria Gabriel Tavares": True,
                "Davi Caldeira Rodrigues": False,
                "Ana Luiza Santana de Moura": False,
                "Kemuel Brito": False
            },
            "2025-07-20": {
                "Beatriz Pedro de Lima": False,
                "Davi Afonso Lana": False,
                "Enzo Leonardo Bitencourt Souza": True,
                "Felype Augusto Oliveira de Jesus": False,
                "Gustavo Lorenzo Ferreira": False,
                "Mariana Lima de Sousa": False,
                "Isabelle Sophia Da Costa De A": False,
                "Luíza (Suellen Tayrone)": False,
                "Hadassah Victoria Gabriel Tavares": True,
                "Davi Caldeira Rodrigues": False,
                "Ana Luiza Santana de Moura": False,
                "Kemuel Brito": False
            },
            "2025-07-27": {
                "Beatriz Pedro de Lima": False,
                "Davi Afonso Lana": False,
                "Enzo Leonardo Bitencourt Souza": False,
                "Felype Augusto Oliveira de Jesus": False,
                "Gustavo Lorenzo Ferreira": False,
                "Mariana Lima de Sousa": False,
                "Isabelle Sophia Da Costa De A": False,
                "Luíza (Suellen Tayrone)": False,
                "Hadassah Victoria Gabriel Tavares": False,
                "Davi Caldeira Rodrigues": False,
                "Ana Luiza Santana de Moura": False,
                "Kemuel Brito": True
            }
        }
        
        # Limpar chamadas antigas da turma Juniores
        await db.attendance.delete_many({'turma_id': turma_id})
        print("🧹 Chamadas antigas dos Juniores removidas")
        
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
                        'oferta': 2.0 if presente else 0.0,  # Oferta para juniores
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
        print(f"\n📊 Resumo da importação - Turma Juniores:")
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
            
            percentage = (presentes/total*100) if total > 0 else 0
            print(f"📅 {data}: {presentes}/{total} presentes ({percentage:.1f}%) - R$ {ofertas_total:.2f}")
        
        print(f"\n🎉 Importação dos Juniores concluída!")
        print(f"📋 Total de registros: {total_imported}")
        
        if alunos_nao_encontrados:
            print(f"⚠️  Alunos não encontrados: {len(alunos_nao_encontrados)}")
            for aluno in alunos_nao_encontrados:
                print(f"    - {aluno}")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_juniores_attendance())