#!/usr/bin/env python3
"""
Script para remover revistas duplicadas do sistema EBD Manager
"""

import asyncio
import aiohttp
import json

# URL da API
API_BASE = "http://localhost:8001/api"

# IDs das revistas duplicadas que devem ser removidas (mantemos as primeiras)
revistas_para_remover = [
    "7273e15a-a6f7-4e3d-8cf2-606caf29b2b2",  # A Liberdade em Cristo (duplicata)
    "147544d7-a74f-43fd-b276-fa9293836472",  # Grandes Cartas para Nós (duplicata)
    "a1961a06-949c-47d2-9865-76354d63abf7",  # Recebendo o Batismo no Espírito Santo (duplicata)
    "da6a7a5e-86d1-4fa3-927a-fcb769631412",  # Verdades que Jesus ensinou (duplicata)
    "7405d229-1627-44de-b220-33f29880560f",  # As aventuras de um Grande Missionário (duplicata)
    "4ab4b0ca-8ccb-4a05-8e77-a92b10d82bb3"   # A Igreja em Jerusalém (duplicata)
]

async def delete_revista(session, revista_id):
    """Remover uma revista duplicada"""
    try:
        print(f"🗑️ Removendo revista duplicada: {revista_id}")
        
        async with session.delete(f"{API_BASE}/revistas/{revista_id}") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Revista {revista_id} removida com sucesso")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Erro ao remover revista {revista_id}: {response.status} - {error_text}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao processar revista {revista_id}: {e}")
        return False

async def list_revistas_before_after(session, when):
    """Listar revistas antes e depois da limpeza"""
    try:
        async with session.get(f"{API_BASE}/revistas") as response:
            if response.status == 200:
                revistas = await response.json()
                print(f"\n📚 REVISTAS {when.upper()}:")
                for revista in revistas:
                    print(f"   • {revista['tema'][:60]}... (ID: {revista['id'][:8]}...)")
                print(f"   TOTAL: {len(revistas)} revistas\n")
                return len(revistas)
            else:
                print(f"❌ Erro ao listar revistas: {response.status}")
                return 0
    except Exception as e:
        print(f"❌ Erro ao listar revistas: {e}")
        return 0

async def main():
    """Função principal"""
    print("🧹 LIMPEZA DE REVISTAS DUPLICADAS")
    print("=" * 50)
    
    removed_count = 0
    
    async with aiohttp.ClientSession() as session:
        # Listar revistas antes da limpeza
        total_before = await list_revistas_before_after(session, "ANTES DA LIMPEZA")
        
        # Remover duplicatas
        print("🚀 Iniciando remoção de duplicatas...")
        for revista_id in revistas_para_remover:
            success = await delete_revista(session, revista_id)
            if success:
                removed_count += 1
        
        print(f"\n✅ Remoção concluída!")
        print(f"📊 Revistas removidas: {removed_count}/{len(revistas_para_remover)}")
        
        # Listar revistas após a limpeza
        total_after = await list_revistas_before_after(session, "APÓS LIMPEZA")
        
        print("=" * 50)
        print("📋 RESUMO FINAL:")
        print(f"   Revistas antes: {total_before}")
        print(f"   Revistas removidas: {removed_count}")
        print(f"   Revistas depois: {total_after}")
        print(f"   ✅ Sistema limpo!")

if __name__ == "__main__":
    asyncio.run(main())