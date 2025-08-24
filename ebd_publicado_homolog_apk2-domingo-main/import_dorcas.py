#!/usr/bin/env python3
"""
Script para importar dados de chamada da turma Dorcas (irmãs)
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

async def import_dorcas_attendance():
    """Importa dados de chamada da turma Dorcas (irmãs)"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print("🔄 Importando dados da turma Dorcas (irmãs)...")
        
        # Buscar turma Dorcas (irmãs)
        turma = await db.turmas.find_one({'nome': 'Dorcas (irmãs)'})
        if not turma:
            print("❌ Turma 'Dorcas (irmãs)' não encontrada!")
            return
        
        turma_id = turma['id']
        print(f"✅ Turma encontrada: {turma['nome']} (ID: {turma_id})")
        
        # Buscar alunos da turma
        alunos = []
        async for aluno in db.students.find({'turma_id': turma_id}):
            alunos.append(aluno)
        
        print(f"✅ Encontrados {len(alunos)} alunos na turma")
        
        # Dados de chamada das Dorcas - dados enormes!
        dados_chamada = {
            "2025-07-06": {
                "Ana Alexio": False, "Angelica": True, "Bruna": False, "Carla": False,
                "Carla Santana": True, "Claudia": False, "Cristiane Gomes": False, "Daiane Balleiro": False,
                "Denise Rodrigues": True, "Dirce dos Santos": False, "Eliane Cardoso": False, "Eliene Viana": False,
                "Érica": True, "Ester Ferreira": True, "Eula": False, "Evanilda": True,
                "Geni": True, "Geovan Silva": False, "Geovanna Tavares": False, "Gildete Dias dos Santos": False,
                "Graciete": False, "Graucia Campos": True, "Iraci": False, "Jô": False,
                "Jovina": True, "Jucileide": False, "Kennyc": False, "Lenilde": True,
                "Lilian": True, "Lourdes Oliveira": True, "Maria": True, "Maria de Loudes Ayala": True,
                "Maria Helna Lourenço": True, "Marli de Paula": False, "Maya": True, "Nalva": True,
                "Neuza Guimarães": False, "Nilza Arcanjo": True, "Raimunda da Conceição": True, "Rosenilda": True,
                "Rute Morete": True, "Sandra Assis": True, "Sara Ribeiro": False, "Sarah Reis": False,
                "Simone Tavares": True, "Sandra Magalhães": True, "Tania": False, "Valdirene": False,
                "Vera Lucia Aparecida": False, "Vera Ricardo": False, "Laudiceia": False, "Rosana": False,
                "Augusta": False, "Deise Farias": True, "Miriam Menezes": False, "Regiane": False,
                "Danieli": False, "Gleyse": True, "Lucilene": True, "Tia Kesia": True,
                "Leicida": True, "Márcia Regina": True
            },
            "2025-07-13": {
                "Ana Alexio": True, "Angelica": False, "Bruna": False, "Carla": False,
                "Carla Santana": False, "Claudia": False, "Cristiane Gomes": False, "Daiane Balleiro": False,
                "Denise Rodrigues": True, "Dirce dos Santos": True, "Eliane Cardoso": False, "Eliene Viana": True,
                "Érica": True, "Ester Ferreira": True, "Eula": False, "Evanilda": False,
                "Geni": False, "Geovan Silva": False, "Geovanna Tavares": False, "Gildete Dias dos Santos": True,
                "Graciete": False, "Graucia Campos": True, "Iraci": False, "Jô": False,
                "Jovina": False, "Jucileide": True, "Kennyc": True, "Lenilde": False,
                "Lilian": False, "Lourdes Oliveira": False, "Maria": True, "Maria de Loudes Ayala": True,
                "Maria Helna Lourenço": False, "Marli de Paula": False, "Maya": True, "Nalva": False,
                "Neuza Guimarães": False, "Nilza Arcanjo": True, "Raimunda da Conceição": False, "Rosenilda": True,
                "Rute Morete": True, "Sandra Assis": True, "Sara Ribeiro": False, "Sarah Reis": False,
                "Simone Tavares": True, "Sandra Magalhães": True, "Tania": False, "Valdirene": False,
                "Vera Lucia Aparecida": False, "Vera Ricardo": False, "Laudiceia": False, "Rosana": False,
                "Augusta": False, "Deise Farias": False, "Miriam Menezes": False, "Regiane": True,
                "Danieli": True, "Gleyse": False, "Lucilene": False, "Tia Kesia": False,
                "Leicida": False, "Márcia Regina": True
            },
            "2025-07-20": {
                "Ana Alexio": False, "Angelica": False, "Bruna": True, "Carla": True,
                "Carla Santana": True, "Claudia": True, "Cristiane Gomes": True, "Daiane Balleiro": True,
                "Denise Rodrigues": False, "Dirce dos Santos": False, "Eliane Cardoso": True, "Eliene Viana": False,
                "Érica": True, "Ester Ferreira": False, "Eula": False, "Evanilda": True,
                "Geni": True, "Geovan Silva": True, "Geovanna Tavares": True, "Gildete Dias dos Santos": False,
                "Graciete": True, "Graucia Campos": False, "Iraci": True, "Jô": True,
                "Jovina": True, "Jucileide": False, "Kennyc": False, "Lenilde": True,
                "Lilian": True, "Lourdes Oliveira": False, "Maria": False, "Maria de Loudes Ayala": False,
                "Maria Helna Lourenço": True, "Marli de Paula": True, "Maya": False, "Nalva": False,
                "Neuza Guimarães": True, "Nilza Arcanjo": False, "Raimunda da Conceição": True, "Rosenilda": False,
                "Rute Morete": False, "Sandra Assis": False, "Sara Ribeiro": True, "Sarah Reis": True,
                "Simone Tavares": False, "Sandra Magalhães": False, "Tania": True, "Valdirene": True,
                "Vera Lucia Aparecida": True, "Vera Ricardo": True, "Laudiceia": True, "Rosana": True,
                "Augusta": True, "Deise Farias": False, "Miriam Menezes": True, "Regiane": False,
                "Danieli": False, "Gleyse": False, "Lucilene": False, "Tia Kesia": False,
                "Leicida": False, "Márcia Regina": False
            },
            "2025-07-27": {
                "Ana Alexio": False, "Angelica": False, "Bruna": False, "Carla": False,
                "Carla Santana": True, "Claudia": False, "Cristiane Gomes": False, "Daiane Balleiro": False,
                "Denise Rodrigues": True, "Dirce dos Santos": True, "Eliane Cardoso": False, "Eliene Viana": True,
                "Érica": True, "Ester Ferreira": True, "Eula": True, "Evanilda": False,
                "Geni": False, "Geovan Silva": False, "Geovanna Tavares": False, "Gildete Dias dos Santos": True,
                "Graciete": False, "Graucia Campos": True, "Iraci": False, "Jô": False,
                "Jovina": False, "Jucileide": True, "Kennyc": True, "Lenilde": False,
                "Lilian": False, "Lourdes Oliveira": True, "Maria": True, "Maria de Loudes Ayala": True,
                "Maria Helna Lourenço": False, "Marli de Paula": False, "Maya": True, "Nalva": False,
                "Neuza Guimarães": False, "Nilza Arcanjo": True, "Raimunda da Conceição": False, "Rosenilda": True,
                "Rute Morete": True, "Sandra Assis": True, "Sara Ribeiro": False, "Sarah Reis": False,
                "Simone Tavares": True, "Sandra Magalhães": True, "Tania": False, "Valdirene": False,
                "Vera Lucia Aparecida": False, "Vera Ricardo": False, "Laudiceia": False, "Rosana": False,
                "Augusta": False, "Deise Farias": True, "Miriam Menezes": False, "Regiane": True,
                "Danieli": True, "Gleyse": True, "Lucilene": True, "Tia Kesia": True,
                "Leicida": True, "Márcia Regina": True
            }
        }
        
        # Limpar chamadas antigas da turma Dorcas
        await db.attendance.delete_many({'turma_id': turma_id})
        print("🧹 Chamadas antigas das Dorcas removidas")
        
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
                        'oferta': 4.0 if presente else 0.0,  # Oferta para irmãs adultas
                        'biblias_entregues': 1 if presente else 0,
                        'revistas_entregues': 1 if presente else 0,
                        'criado_em': datetime.utcnow().isoformat()
                    }
                    registros_attendance.append(attendance_record)
                    total_imported += 1
                else:
                    if nome_aluno not in alunos_nao_encontrados:
                        alunos_nao_encontrados.append(nome_aluno)
                        print(f"   ⚠️  Aluna '{nome_aluno}' não encontrada")
        
        # Inserir todos os registros
        if registros_attendance:
            await db.attendance.insert_many(registros_attendance)
            print(f"✅ {len(registros_attendance)} registros de presença inseridos")
        
        # Verificar resultado
        print(f"\n📊 Resumo da importação - Turma Dorcas (irmãs):")
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
        
        print(f"\n🎉 Importação das Dorcas concluída!")
        print(f"📋 Total de registros: {total_imported}")
        
        if alunos_nao_encontrados:
            print(f"⚠️  Alunas não encontradas: {len(alunos_nao_encontrados)}")
            for aluna in alunos_nao_encontrados[:10]:  # Mostrar só as primeiras 10
                print(f"    - {aluna}")
            if len(alunos_nao_encontrados) > 10:
                print(f"    ... e mais {len(alunos_nao_encontrados) - 10}")
        else:
            print("✅ Todas as irmãs foram encontradas e importadas!")
        
    except Exception as e:
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_dorcas_attendance())