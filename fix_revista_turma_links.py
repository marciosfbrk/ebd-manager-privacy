#!/usr/bin/env python3
"""
Script para corrigir vinculações das revistas com turmas corretas
"""

import asyncio
import aiohttp
import json

# URL da API
API_BASE = "http://localhost:8001/api"

# Mapeamento das revistas para as turmas corretas
revista_turma_mapping = {
    # Revista de Adultos (múltiplas turmas)
    "A Igreja em Jerusalém — Doutrina, Comunhão e Fé": [
        "Professores e Oficiais", "Dorcas (irmãs)", "Ebenezer (Obreiros)", "Soldados de Cristo"
    ],
    # Revistas específicas por turma
    "A Liberdade em Cristo — Vivendo o verdadeiro Evangelho": ["Jovens"],
    "Grandes Cartas para Nós": ["Adolescentes"],
    "Recebendo o Batismo no Espírito Santo": ["Pré-Adolescentes"],
    "Verdades que Jesus ensinou": ["Juniores"],
    "As aventuras de um Grande Missionário": ["Primarios"]
}

async def get_all_turmas(session):
    """Buscar todas as turmas e criar mapeamento nome->ID"""
    try:
        async with session.get(f"{API_BASE}/turmas") as response:
            if response.status == 200:
                turmas = await response.json()
                turma_map = {}
                for turma in turmas:
                    turma_map[turma['nome']] = turma['id']
                return turma_map
            else:
                print(f"❌ Erro ao buscar turmas: {response.status}")
                return {}
    except Exception as e:
        print(f"❌ Erro ao buscar turmas: {e}")
        return {}

async def get_all_revistas(session):
    """Buscar todas as revistas"""
    try:
        async with session.get(f"{API_BASE}/revistas") as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"❌ Erro ao buscar revistas: {response.status}")
                return []
    except Exception as e:
        print(f"❌ Erro ao buscar revistas: {e}")
        return []

async def update_revista_turmas(session, revista_id, turma_ids, tema):
    """Atualizar vinculação de turmas para uma revista"""
    try:
        # Buscar dados atuais da revista
        async with session.get(f"{API_BASE}/revistas") as response:
            if response.status == 200:
                revistas = await response.json()
                revista_atual = next((r for r in revistas if r['id'] == revista_id), None)
                
                if not revista_atual:
                    print(f"❌ Revista {revista_id} não encontrada")
                    return False
                
                # Preparar dados para atualização
                update_data = {
                    "tema": revista_atual['tema'],
                    "licoes": revista_atual['licoes'],
                    "turma_ids": turma_ids
                }
                
                # Atualizar revista
                async with session.put(f"{API_BASE}/revistas/{revista_id}", json=update_data) as update_response:
                    if update_response.status == 200:
                        print(f"✅ Revista '{tema[:40]}...' atualizada com {len(turma_ids)} turmas")
                        return True
                    else:
                        error_text = await update_response.text()
                        print(f"❌ Erro ao atualizar revista: {update_response.status} - {error_text}")
                        return False
            else:
                print(f"❌ Erro ao buscar revistas para atualização: {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao atualizar revista {revista_id}: {e}")
        return False

async def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE VINCULAÇÕES REVISTAS ↔ TURMAS")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Buscar turmas e revistas
        turma_map = await get_all_turmas(session)
        revistas = await get_all_revistas(session)
        
        if not turma_map or not revistas:
            print("❌ Não foi possível buscar dados necessários")
            return
        
        print(f"📊 Encontradas: {len(turma_map)} turmas e {len(revistas)} revistas")
        
        updates_made = 0
        
        # Processar cada revista
        for revista in revistas:
            tema = revista['tema']
            revista_id = revista['id']
            
            # Encontrar mapeamento para esta revista
            turma_names = None
            for tema_key, turmas_esperadas in revista_turma_mapping.items():
                if tema_key in tema:
                    turma_names = turmas_esperadas
                    break
            
            if not turma_names:
                print(f"⚠️ Revista '{tema[:40]}...' não encontrada no mapeamento")
                continue
            
            # Converter nomes de turmas para IDs
            turma_ids = []
            for turma_name in turma_names:
                if turma_name in turma_map:
                    turma_ids.append(turma_map[turma_name])
                else:
                    print(f"⚠️ Turma '{turma_name}' não encontrada")
            
            if turma_ids:
                print(f"\n🔄 Atualizando '{tema[:40]}...'")
                print(f"   Turmas: {', '.join(turma_names)}")
                
                success = await update_revista_turmas(session, revista_id, turma_ids, tema)
                if success:
                    updates_made += 1
        
        print(f"\n=" * 60)
        print(f"📋 RESUMO:")
        print(f"   Revistas processadas: {len(revistas)}")
        print(f"   Atualizações feitas: {updates_made}")
        print(f"   ✅ Correção concluída!")

if __name__ == "__main__":
    asyncio.run(main())