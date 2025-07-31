#!/usr/bin/env python3
"""
Script para cadastrar as revistas no sistema EBD Manager
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URL da API
API_BASE = "http://localhost:8001/api"

# Dados das revistas a serem cadastradas
revistas_data = [
    {
        "turma_nome": "Jovens",
        "tema": "A Liberdade em Cristo — Vivendo o verdadeiro Evangelho conforme a Carta de Paulo aos Gálatas",
        "licoes": [
            {"titulo": "Gálatas: a carta da liberdade cristã", "data": "2025-07-06"},
            {"titulo": "O falso evangelho", "data": "2025-07-13"},
            {"titulo": "Paulo e sua chamada", "data": "2025-07-20"},
            {"titulo": "O encontro em Jerusalém e os falsos irmãos", "data": "2025-07-27"},
            {"titulo": "Advertência contra o legalismo", "data": "2025-08-03"},
            {"titulo": "Justificados pela fé em Jesus Cristo", "data": "2025-08-10"},
            {"titulo": "A promessa que não pode ser revogada", "data": "2025-08-17"},
            {"titulo": "Filhos e herdeiros", "data": "2025-08-24"},
            {"titulo": "Filhos de Deus e descendência de Abraão", "data": "2025-08-31"},
            {"titulo": "A liberdade que Cristo nos deu", "data": "2025-09-07"},
            {"titulo": "A carne e o Espírito: a luta que existe em nós", "data": "2025-09-14"},
            {"titulo": "O que você semear, ceifará", "data": "2025-09-21"},
            {"titulo": "As marcas de Cristo", "data": "2025-09-28"}
        ]
    },
    {
        "turma_nome": "Adolescentes",
        "tema": "Grandes Cartas para Nós",
        "licoes": [
            {"titulo": "A importância da comunicação", "data": "2025-07-06"},
            {"titulo": "Hebreus, uma Carta sobre Jesus", "data": "2025-07-13"},
            {"titulo": "A poderosa mensagem da Carta aos Hebreus", "data": "2025-07-20"},
            {"titulo": "A questão da fé na Carta aos Hebreus", "data": "2025-07-27"},
            {"titulo": "Vamos conhecer a Carta de Tiago", "data": "2025-08-03"},
            {"titulo": "Aprendendo com a Carta de Tiago", "data": "2025-08-10"},
            {"titulo": "Vamos conhecer a 1ª Carta de Pedro", "data": "2025-08-17"},
            {"titulo": "Vamos aprender com a 2ª Carta de Pedro", "data": "2025-08-24"},
            {"titulo": "Vamos conhecer a 1ª Carta de João", "data": "2025-08-31"},
            {"titulo": "Vamos conhecer a 2ª Carta de João", "data": "2025-09-07"},
            {"titulo": "Vamos conhecer a 3ª Carta de João", "data": "2025-09-14"},
            {"titulo": "Vamos conhecer a Carta de Judas", "data": "2025-09-21"},
            {"titulo": "Vamos praticar a palavra!", "data": "2025-09-28"}
        ]
    },
    {
        "turma_nome": "Pré-adolescentes",
        "tema": "Recebendo o Batismo no Espírito Santo",
        "licoes": [
            {"titulo": "A Promessa do Derramamento do Espírito Santo", "data": "2025-07-06"},
            {"titulo": "O Poder do Alto no Dia de Pentecoste", "data": "2025-07-13"},
            {"titulo": "O Poder do Espírito na vida de Pedro e João", "data": "2025-07-20"},
            {"titulo": "O Espírito Santo na vida de Paulo", "data": "2025-07-27"},
            {"titulo": "O Mover do Espírito na Casa de Cornélio", "data": "2025-08-03"},
            {"titulo": "O Evangelho em Éfeso e o Revestimento de Poder", "data": "2025-08-10"},
            {"titulo": "As Línguas Estranhas como Evidência do Batismo", "data": "2025-08-17"},
            {"titulo": "O Dom de Interpretar as Línguas", "data": "2025-08-24"},
            {"titulo": "O Exercício dos Dons Espirituais", "data": "2025-08-31"},
            {"titulo": "O Batismo no Espírito e a Santificação do Crente", "data": "2025-09-07"},
            {"titulo": "O Batismo no Espírito e o Testemunho da Igreja", "data": "2025-09-14"},
            {"titulo": "Vivendo o Avivamento Espiritual", "data": "2025-09-21"},
            {"titulo": "Buscando o Batismo no Espírito Santo", "data": "2025-09-28"}
        ]
    },
    {
        "turma_nome": "Juniores",
        "tema": "Verdades que Jesus ensinou",
        "licoes": [
            {"titulo": "A lição sobre o Reino de Deus", "data": "2025-07-06"},
            {"titulo": "A lição sobre a oração", "data": "2025-07-13"},
            {"titulo": "A lição das duas casas", "data": "2025-07-20"},
            {"titulo": "A lição da tempestade", "data": "2025-07-27"},
            {"titulo": "A lição da árvore e os seus frutos", "data": "2025-08-03"},
            {"titulo": "A lição do semeador", "data": "2025-08-10"},
            {"titulo": "A lição do perdão", "data": "2025-08-17"},
            {"titulo": "A lição da ovelha perdida", "data": "2025-08-24"},
            {"titulo": "A lição do filho arrependido", "data": "2025-08-31"},
            {"titulo": "A lição do jovem rico", "data": "2025-09-07"},
            {"titulo": "A lição dos servos maus", "data": "2025-09-14"},
            {"titulo": "A lição dos talentos", "data": "2025-09-21"},
            {"titulo": "A lição do amor na cruz", "data": "2025-09-28"}
        ]
    },
    {
        "turma_nome": "Primários",
        "tema": "As aventuras de um Grande Missionário",
        "licoes": [
            {"titulo": "O caçador de cristãos", "data": "2025-07-06"},
            {"titulo": "De perseguidor a missionário", "data": "2025-07-13"},
            {"titulo": "Paulo em sua primeira viagem missionária", "data": "2025-07-20"},
            {"titulo": "Um mágico enganador é desmascarado", "data": "2025-07-27"},
            {"titulo": "Deuses ou missionários", "data": "2025-08-03"},
            {"titulo": "Amizades missionárias", "data": "2025-08-10"},
            {"titulo": "Mudança de planos", "data": "2025-08-17"},
            {"titulo": "Oração e louvor causam grande tremor", "data": "2025-08-24"},
            {"titulo": "A grande recompensa dos missionários", "data": "2025-08-31"},
            {"titulo": "Os falsos missionários", "data": "2025-09-07"},
            {"titulo": "A ressurreição durante a pregação", "data": "2025-09-14"},
            {"titulo": "Paulo evangeliza um rei", "data": "2025-09-21"},
            {"titulo": "Fé em meio às tempestades", "data": "2025-09-28"}
        ]
    }
]

async def get_turma_id_by_name(session, turma_nome):
    """Buscar ID da turma pelo nome"""
    try:
        async with session.get(f"{API_BASE}/turmas") as response:
            if response.status == 200:
                turmas = await response.json()
                for turma in turmas:
                    if turma['nome'] == turma_nome:
                        return turma['id']
                print(f"❌ Turma '{turma_nome}' não encontrada!")
                return None
            else:
                print(f"❌ Erro ao buscar turmas: {response.status}")
                return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

async def create_revista(session, revista_data):
    """Criar uma revista"""
    try:
        turma_nome = revista_data['turma_nome']
        print(f"📚 Processando revista para turma: {turma_nome}")
        
        # Buscar ID da turma
        turma_id = await get_turma_id_by_name(session, turma_nome)
        if not turma_id:
            return False
            
        # Preparar dados da revista
        payload = {
            "tema": revista_data['tema'],
            "turma_ids": [turma_id],
            "licoes": revista_data['licoes']
        }
        
        # Fazer POST para criar a revista
        async with session.post(f"{API_BASE}/revistas", json=payload) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Revista criada para turma '{turma_nome}'")
                print(f"   Tema: {revista_data['tema'][:60]}...")
                print(f"   Lições: {len(revista_data['licoes'])}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Erro ao criar revista para '{turma_nome}': {response.status} - {error_text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao processar revista para '{turma_nome}': {e}")
        return False

async def main():
    """Função principal"""
    print("🚀 Iniciando cadastro das revistas...")
    print(f"📊 Total de revistas a cadastrar: {len(revistas_data)}\n")
    
    created_count = 0
    
    async with aiohttp.ClientSession() as session:
        for revista_data in revistas_data:
            success = await create_revista(session, revista_data)
            if success:
                created_count += 1
            print()  # Linha em branco para separar
    
    print("📋 RESUMO:")
    print(f"✅ Revistas criadas com sucesso: {created_count}")
    print(f"❌ Falhas: {len(revistas_data) - created_count}")
    print(f"📚 Total processado: {len(revistas_data)}")

if __name__ == "__main__":
    asyncio.run(main())