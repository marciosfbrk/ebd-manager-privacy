#!/usr/bin/env python3
"""
Script para importar dados de chamada da turma Ebenezer (Obreiros)
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

async def import_ebenezer_attendance():
    """Importa dados de chamada da turma Ebenezer (Obreiros)"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔄 Importando dados da turma Ebenezer (Obreiros)...")
        
        # Buscar turma Ebenezer (Obreiros)
        turma = await db.turmas.find_one({'nome': 'Ebenezer (Obreiros)'})
        if not turma:
            print("❌ Turma 'Ebenezer (Obreiros)' não encontrada!")
            return
        
        turma_id = turma['id']
        print(f"✅ Turma encontrada: {turma['nome']} (ID: {turma_id})")
        
        # Buscar alunos da turma
        alunos = []
        async for aluno in db.students.find({'turma_id': turma_id}):
            alunos.append(aluno)
        
        print(f"✅ Encontrados {len(alunos)} alunos na turma")
        
        # Dados de chamada dos Ebenezer (Obreiros)
        dados_chamada = {
            "2025-07-06": {
                "Coop Antônio": True,
                "Coop Denys": False,
                "Coop Elias Barbosa": True,
                "Coop Emanuel": False,
                "Coop Evandro": True,
                "Coop Francisco": True,
                "Coop João Gregório": True,
                "Coop Roberto Dantas": True,
                "Coop Valdeci": False,
                "Diac Emílio": True,
                "Diac Luiz Borges": True,
                "Diac Marcos": False,
                "Pb Almir": True,
                "Pb Bernardo": False,
                "Pb Cosmo": True,
                "Pb Geovane": True,
                "Pb Ismael": True,
                "Pb Thiago Tavares": True,
                "Coop. Walmir": False,
                "Coop. Alessandro": False,
                "Pb. Isaac": True,
                "Coop. Edson": False
            },
            "2025-07-13": {
                "Coop Antônio": True,
                "Coop Denys": False,
                "Coop Elias Barbosa": True,
                "Coop Emanuel": False,
                "Coop Evandro": True,
                "Coop Francisco": True,
                "Coop João Gregório": False,
                "Coop Roberto Dantas": True,
                "Coop Valdeci": False,
                "Diac Emílio": False,
                "Diac Luiz Borges": False,
                "Diac Marcos": False,
                "Pb Almir": True,
                "Pb Bernardo": False,
                "Pb Cosmo": False,
                "Pb Geovane": False,
                "Pb Ismael": False,
                "Pb Thiago Tavares": False,
                "Coop. Walmir": False,
                "Coop. Alessandro": False,
                "Pb. Isaac": False,
                "Coop. Edson": False
            },
            "2025-07-20": {
                "Coop Antônio": True,
                "Coop Denys": True,
                "Coop Elias Barbosa": True,
                "Coop Emanuel": True,
                "Coop Evandro": False,
                "Coop Francisco": False,
                "Coop João Gregório": False,
                "Coop Roberto Dantas": True,
                "Coop Valdeci": True,
                "Diac Emílio": True,
                "Diac Luiz Borges": True,
                "Diac Marcos": True,
                "Pb Almir": True,
                "Pb Bernardo": True,
                "Pb Cosmo": True,
                "Pb Geovane": True,
                "Pb Ismael": True,
                "Pb Thiago Tavares": True,
                "Coop. Walmir": True,
                "Coop. Alessandro": True,
                "Pb. Isaac": True,
                "Coop. Edson": True
            },
            "2025-07-27": {
                "Coop Antônio": False,
                "Coop Denys": True,
                "Coop Elias Barbosa": True,
                "Coop Emanuel": False,
                "Coop Evandro": True,
                "Coop Francisco": False,
                "Coop João Gregório": True,
                "Coop Roberto Dantas": True,
                "Coop Valdeci": False,
                "Diac Emílio": False,
                "Diac Luiz Borges": True,
                "Diac Marcos": False,
                "Pb Almir": True,
                "Pb Bernardo": False,
                "Pb Cosmo": True,
                "Pb Geovane": True,
                "Pb Ismael": True,
                "Pb Thiago Tavares": True,
                "Coop. Walmir": True,
                "Coop. Alessandro": False,
                "Pb. Isaac": False,
                "Coop. Edson": False
            }
        }
        
        # Limpar chamadas antigas da turma Ebenezer
        await db.attendance.delete_many({'turma_id': turma_id})
        print("🧹 Chamadas antigas dos Ebenezer removidas")
        
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
                        'oferta': 6.0 if presente else 0.0,  # Oferta maior para obreiros/liderança
                        'biblias_entregues': 1 if presente else 0,
                        'revistas_entregues': 1 if presente else 0,
                        'criado_em': datetime.utcnow().isoformat()
                    }
                    registros_attendance.append(attendance_record)
                    total_imported += 1
                else:
                    if nome_aluno not in alunos_nao_encontrados:
                        alunos_nao_encontrados.append(nome_aluno)
                        print(f"   ⚠️  Obreiro '{nome_aluno}' não encontrado")
        
        # Inserir todos os registros
        if registros_attendance:
            await db.attendance.insert_many(registros_attendance)
            print(f"✅ {len(registros_attendance)} registros de presença inseridos")
        
        # Verificar resultado
        print(f"\n📊 Resumo da importação - Turma Ebenezer (Obreiros):")
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
        
        print(f"\n🎉 Importação dos Ebenezer concluída!")
        print(f"📋 Total de registros: {total_imported}")
        
        if alunos_nao_encontrados:
            print(f"⚠️  Obreiros não encontrados: {len(alunos_nao_encontrados)}")
            for obreiro in alunos_nao_encontrados[:10]:
                print(f"    - {obreiro}")
            if len(alunos_nao_encontrados) > 10:
                print(f"    ... e mais {len(alunos_nao_encontrados) - 10}")
        else:
            print("✅ Todos os obreiros foram encontrados e importados!")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_ebenezer_attendance())