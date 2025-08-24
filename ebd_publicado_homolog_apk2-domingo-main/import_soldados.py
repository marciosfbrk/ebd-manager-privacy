#!/usr/bin/env python3
"""
Script para importar dados de chamada da turma Soldados de Cristo
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

async def import_soldados_attendance():
    """Importa dados de chamada da turma Soldados de Cristo"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔄 Importando dados da turma Soldados de Cristo...")
        
        # Buscar turma Soldados de Cristo
        turma = await db.turmas.find_one({'nome': 'Soldados de Cristo'})
        if not turma:
            print("❌ Turma 'Soldados de Cristo' não encontrada!")
            return
        
        turma_id = turma['id']
        print(f"✅ Turma encontrada: {turma['nome']} (ID: {turma_id})")
        
        # Buscar alunos da turma
        alunos = []
        async for aluno in db.students.find({'turma_id': turma_id}):
            alunos.append(aluno)
        
        print(f"✅ Encontrados {len(alunos)} alunos na turma")
        
        # Dados de chamada dos Soldados de Cristo
        dados_chamada = {
            "2025-07-06": {
                "Alexandre Tavares": True, "Amilton": True, "André Afonso Lana": True, "Daniel Corsine": False,
                "Elias Barbosa": True, "Elizeu Barbosa": True, "Gerônimo": True, "Isaias Abreu": False,
                "Jair Benedito": True, "Jesiel José": True, "Jessé Araújo": True, "Joedilson": True,
                "Joel Cruz": True, "José Arcanjo": True, "José Domingos": True, "Luiz Felipe": True,
                "Manoel Lopes": True, "Messias Rodrigues": True, "Nylon": True, "Ronaldo Rabelo": False,
                "Tiago Henrique": False, "Fernando Paulo": False, "Gideão": False, "Djalma": True,
                "José Maria": True, "William Medeiros Alves": True, "Diego Augusto": False, "Reginaldo": False,
                "Daniel José": True, "Daniel Mousinho de Araújo": False, "Gabriel Lana": False
            },
            "2025-07-13": {
                "Alexandre Tavares": False, "Amilton": False, "André Afonso Lana": False, "Daniel Corsine": False,
                "Elias Barbosa": True, "Elizeu Barbosa": False, "Gerônimo": False, "Isaias Abreu": False,
                "Jair Benedito": False, "Jesiel José": False, "Jessé Araújo": False, "Joedilson": False,
                "Joel Cruz": False, "José Arcanjo": False, "José Domingos": False, "Luiz Felipe": False,
                "Manoel Lopes": False, "Messias Rodrigues": False, "Nylon": False, "Ronaldo Rabelo": False,
                "Tiago Henrique": False, "Fernando Paulo": False, "Gideão": False, "Djalma": False,
                "José Maria": False, "William Medeiros Alves": False, "Diego Augusto": False, "Reginaldo": False,
                "Daniel José": False, "Daniel Mousinho de Araújo": False, "Gabriel Lana": False
            },
            "2025-07-20": {
                "Alexandre Tavares": True, "Amilton": True, "André Afonso Lana": True, "Daniel Corsine": False,
                "Elias Barbosa": True, "Elizeu Barbosa": True, "Gerônimo": True, "Isaias Abreu": False,
                "Jair Benedito": True, "Jesiel José": True, "Jessé Araújo": True, "Joedilson": True,
                "Joel Cruz": True, "José Arcanjo": True, "José Domingos": True, "Luiz Felipe": True,
                "Manoel Lopes": True, "Messias Rodrigues": True, "Nylon": True, "Ronaldo Rabelo": False,
                "Tiago Henrique": False, "Fernando Paulo": False, "Gideão": False, "Djalma": True,
                "José Maria": True, "William Medeiros Alves": True, "Diego Augusto": False, "Reginaldo": False,
                "Daniel José": True, "Daniel Mousinho de Araújo": False, "Gabriel Lana": False
            },
            "2025-07-27": {
                "Alexandre Tavares": True, "Amilton": True, "André Afonso Lana": True, "Daniel Corsine": False,
                "Elias Barbosa": True, "Elizeu Barbosa": True, "Gerônimo": True, "Isaias Abreu": False,
                "Jair Benedito": True, "Jesiel José": True, "Jessé Araújo": True, "Joedilson": True,
                "Joel Cruz": True, "José Arcanjo": True, "José Domingos": True, "Luiz Felipe": True,
                "Manoel Lopes": True, "Messias Rodrigues": True, "Nylon": True, "Ronaldo Rabelo": False,
                "Tiago Henrique": False, "Fernando Paulo": False, "Gideão": False, "Djalma": True,
                "José Maria": True, "William Medeiros Alves": True, "Diego Augusto": False, "Reginaldo": False,
                "Daniel José": True, "Daniel Mousinho de Araújo": False, "Gabriel Lana": False
            }
        }
        
        # Limpar chamadas antigas da turma Soldados
        await db.attendance.delete_many({'turma_id': turma_id})
        print("🧹 Chamadas antigas dos Soldados de Cristo removidas")
        
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
                        'oferta': 4.5 if presente else 0.0,  # Oferta para homens adultos
                        'biblias_entregues': 1 if presente else 0,
                        'revistas_entregues': 1 if presente else 0,
                        'criado_em': datetime.utcnow().isoformat()
                    }
                    registros_attendance.append(attendance_record)
                    total_imported += 1
                else:
                    if nome_aluno not in alunos_nao_encontrados:
                        alunos_nao_encontrados.append(nome_aluno)
                        print(f"   ⚠️  Soldado '{nome_aluno}' não encontrado")
        
        # Inserir todos os registros
        if registros_attendance:
            await db.attendance.insert_many(registros_attendance)
            print(f"✅ {len(registros_attendance)} registros de presença inseridos")
        
        # Verificar resultado
        print(f"\n📊 Resumo da importação - Turma Soldados de Cristo:")
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
        
        print(f"\n🎉 Importação dos Soldados de Cristo concluída!")
        print(f"📋 Total de registros: {total_imported}")
        
        if alunos_nao_encontrados:
            print(f"⚠️  Soldados não encontrados: {len(alunos_nao_encontrados)}")
            for soldado in alunos_nao_encontrados[:10]:
                print(f"    - {soldado}")
            if len(alunos_nao_encontrados) > 10:
                print(f"    ... e mais {len(alunos_nao_encontrados) - 10}")
        else:
            print("✅ Todos os soldados foram encontrados e importados!")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_soldados_attendance())