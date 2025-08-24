#!/usr/bin/env python3
"""
Script para verificar vinculação de turmas às revistas
"""

import asyncio
import aiohttp
import json

# URL da API
API_BASE = "http://localhost:8001/api"

async def get_turma_name_by_id(session, turma_id):
    """Buscar nome da turma pelo ID"""
    try:
        async with session.get(f"{API_BASE}/turmas/{turma_id}") as response:
            if response.status == 200:
                turma = await response.json()
                return turma.get('nome', 'Nome não encontrado')
            else:
                return f"Erro {response.status}"
    except Exception as e:
        return f"Erro: {e}"

async def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DE VINCULAÇÃO TURMAS ↔ REVISTAS")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Buscar todas as revistas
        async with session.get(f"{API_BASE}/revistas") as response:
            if response.status == 200:
                revistas = await response.json()
                
                for revista in revistas:
                    print(f"\n📚 REVISTA: {revista['tema'][:50]}...")
                    print(f"   ID: {revista['id']}")
                    print(f"   Turmas vinculadas: {len(revista['turma_ids'])}")
                    
                    if revista['turma_ids']:
                        for turma_id in revista['turma_ids']:
                            turma_nome = await get_turma_name_by_id(session, turma_id)
                            print(f"      • {turma_nome} (ID: {turma_id[:8]}...)")
                    else:
                        print("      • Nenhuma turma vinculada")
                    
                    print(f"   Lições: {len(revista['licoes'])}")
                    print("-" * 60)
            else:
                print(f"❌ Erro ao buscar revistas: {response.status}")

if __name__ == "__main__":
    asyncio.run(main())