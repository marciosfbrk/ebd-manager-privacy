#!/usr/bin/env python3
"""
Script para registrar dados da turma Ebenezer (Obreiros)
"""

import json
import requests

BASE_URL = "https://sunday-bible.preview.emergentagent.com/api"
TURMA_ID = "24ece9aa-2f57-47bf-8a9e-56d2874118ed"  # Ebenezer (Obreiros)

# Dados fornecidos pelo usuário
dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 9,
        "oferta": 14.70,
        "presencas": [
            {"nome": "Coop Antônio", "presente": True},
            {"nome": "Coop Denys", "presente": True},
            {"nome": "Coop Elias Barbosa", "presente": False},
            {"nome": "Coop Emanuel", "presente": False},
            {"nome": "Coop Evandro", "presente": False},
            {"nome": "Coop Francisco", "presente": True},
            {"nome": "Coop João Gregório", "presente": False},
            {"nome": "Coop Roberto Dantas", "presente": True},
            {"nome": "Coop Valdeci", "presente": False},
            {"nome": "Diac Emílio", "presente": False},
            {"nome": "Diac Luiz Borges", "presente": False},
            {"nome": "Diac Marcos", "presente": False},
            {"nome": "Pb Almir", "presente": False},
            {"nome": "Pb Bernardo", "presente": False},
            {"nome": "Pb Cosmo", "presente": True},
            {"nome": "Pb Geovane", "presente": True},
            {"nome": "Pb Ismael", "presente": True},
            {"nome": "Pb Thiago Tavares", "presente": True},
            {"nome": "Coop. Walmir", "presente": True},
            {"nome": "Coop. Alessandro", "presente": False},
            {"nome": "Pb. Isaac", "presente": False},
            {"nome": "Coop. Edson", "presente": False}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 13,
        "oferta": 17.90,
        "presencas": [
            {"nome": "Coop Antônio", "presente": True},
            {"nome": "Coop Denys", "presente": True},
            {"nome": "Coop Elias Barbosa", "presente": True},
            {"nome": "Coop Emanuel", "presente": True},
            {"nome": "Coop Evandro", "presente": False},
            {"nome": "Coop Francisco", "presente": False},
            {"nome": "Coop João Gregório", "presente": True},
            {"nome": "Coop Roberto Dantas", "presente": True},
            {"nome": "Diac Emílio", "presente": True},
            {"nome": "Diac Luiz Borges", "presente": True},
            {"nome": "Diac Marcos", "presente": True},
            {"nome": "Pb Almir", "presente": False},
            {"nome": "Pb Bernardo", "presente": True},
            {"nome": "Pb Cosmo", "presente": True},
            {"nome": "Pb Geovane", "presente": False},
            {"nome": "Pb Ismael", "presente": False},
            {"nome": "Pb Thiago Tavares", "presente": True},
            {"nome": "Coop. Walmir", "presente": True},
            {"nome": "Coop. Alessandro", "presente": False},
            {"nome": "Pb. Isaac", "presente": False},
            {"nome": "Coop. Edson", "presente": False}
        ]
    }
]

def obter_mapeamento_ebenezer():
    """Busca todos os obreiros da turma Ebenezer e cria mapeamento nome->ID"""
    print("📋 Buscando obreiros da turma Ebenezer...")
    
    response = requests.get(f"{BASE_URL}/students?turma_id={TURMA_ID}")
    if response.status_code == 200:
        students = response.json()
        mapping = {}
        print(f"   Encontrados {len(students)} obreiros:")
        
        for student in students:
            nome_completo = student["nome_completo"]
            mapping[nome_completo] = student["id"]
            
            # Criar mapeamentos alternativos
            # Sem pontos finais
            nome_sem_ponto = nome_completo.replace(".", "")
            if nome_sem_ponto != nome_completo:
                mapping[nome_sem_ponto] = student["id"]
            
            # Com ponto final
            if not nome_completo.endswith("."):
                mapping[nome_completo + "."] = student["id"]
        
        return mapping, students
    else:
        print(f"❌ Erro ao buscar obreiros: {response.status_code}")
        return {}, []

def encontrar_melhor_match_ebenezer(nome_busca, students):
    """Encontra o melhor match para um nome de obreiro"""
    nome_busca_lower = nome_busca.lower().replace(".", "")
    
    for student in students:
        nome_db = student["nome_completo"].lower().replace(".", "")
        
        # Match exato
        if nome_busca_lower == nome_db:
            return student["id"]
        
        # Nome está contido no nome do DB
        if nome_busca_lower in nome_db:
            return student["id"]
        
        # Nome do DB está contido no nome da busca
        if nome_db in nome_busca_lower:
            return student["id"]
        
        # Match por partes (ex: "Coop Antônio" vs "Coop Antonio")
        parts_busca = nome_busca_lower.split()
        parts_db = nome_db.split()
        
        if len(parts_busca) >= 2 and len(parts_db) >= 2:
            if parts_busca[0] == parts_db[0] and parts_busca[1] in parts_db[1]:
                return student["id"]
    
    return None

def registrar_presenca_ebenezer(dia_data, name_mapping, students):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    presentes_nomes = []
    nao_encontrados = []
    
    # Processar todos os obreiros
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        # Tentar encontrar o ID do obreiro
        aluno_id = None
        
        if nome in name_mapping:
            aluno_id = name_mapping[nome]
        else:
            # Buscar por match inteligente
            aluno_id = encontrar_melhor_match_ebenezer(nome, students)
        
        if not aluno_id:
            nao_encontrados.append(nome)
            continue
        
        status = "presente" if presente else "ausente"
        
        if presente:
            # Extrair nome simples (remover titulo)
            nome_simples = nome.replace("Coop ", "").replace("Diac ", "").replace("Pb ", "").replace(".", "").split()[0]
            presentes_nomes.append(nome_simples)
            
            oferta_individual = dia_data["oferta"] / total_presentes if total_presentes > 0 else 0.0
            revista_individual = dia_data["revista_biblia"] / total_presentes if total_presentes > 0 else 0
        else:
            oferta_individual = 0.0
            revista_individual = 0
        
        bulk_attendance.append({
            "aluno_id": aluno_id,
            "status": status,
            "oferta": oferta_individual,
            "biblias_entregues": int(revista_individual),
            "revistas_entregues": int(revista_individual)
        })
    
    if nao_encontrados:
        print(f"⚠️  Obreiros não encontrados: {', '.join(nao_encontrados[:5])}{'...' if len(nao_encontrados) > 5 else ''}")
    
    # Registrar via API
    url = f"{BASE_URL}/attendance/bulk/{TURMA_ID}?data={dia_data['data']}"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=bulk_attendance)
    
    if response.status_code == 200:
        ausentes_count = len(dia_data["presencas"]) - total_presentes
        print(f"✅ {dia_data['data']}: {total_presentes} presentes, {ausentes_count} ausentes, R$ {dia_data['oferta']:.2f}")
        if presentes_nomes:
            print(f"   Presentes: {', '.join(presentes_nomes[:6])}{'...' if len(presentes_nomes) > 6 else ''}")
        return True
    else:
        print(f"❌ Erro em {dia_data['data']}: {response.text}")
        return False

print("⚡ Registrando presença turma Ebenezer (Obreiros)...")

# Obter mapeamento real
name_mapping, students = obter_mapeamento_ebenezer()

if name_mapping:
    for dia in dados:
        registrar_presenca_ebenezer(dia, name_mapping, students)
    print("🎉 Dados registrados!")
else:
    print("❌ Não foi possível obter os dados dos obreiros.")