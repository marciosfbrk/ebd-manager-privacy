#!/usr/bin/env python3
"""
Script para registrar dados da turma Dorcas (irmãs)
"""

import json
import requests

BASE_URL = "https://341b9440-3e60-40b5-8139-767e514488b7.preview.emergentagent.com/api"
TURMA_ID = "d6b9855e-bfc5-4539-be92-414f6a3e6df2"  # Dorcas (irmãs)

# Dados fornecidos pelo usuário
dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 17,
        "oferta": 18.30,
        "presencas": [
            {"nome": "Ana Aleixo", "presente": False},
            {"nome": "Angelica", "presente": True},
            {"nome": "Bruna", "presente": True},
            {"nome": "Carla", "presente": False},
            {"nome": "Carla Santana", "presente": False},
            {"nome": "Claudia", "presente": False},
            {"nome": "Cristiane Gomes", "presente": False},
            {"nome": "Daiane Balleiro", "presente": False},
            {"nome": "Denise Rodrigues", "presente": True},
            {"nome": "Dirce dos Santos", "presente": False},
            {"nome": "Eliane Cardoso", "presente": False},
            {"nome": "Eliene Viana", "presente": False},
            {"nome": "Érica", "presente": False},
            {"nome": "Ester Ferreira", "presente": True},
            {"nome": "Eula", "presente": False},
            {"nome": "Evanilda", "presente": False},
            {"nome": "Geni", "presente": False},
            {"nome": "Geovan Silva", "presente": True},
            {"nome": "Geovanna Tavares", "presente": False},
            {"nome": "Gildete Dias dos Santos", "presente": False},
            {"nome": "Graciete", "presente": False},
            {"nome": "Graucia Campos", "presente": False},
            {"nome": "Iraci", "presente": False},
            {"nome": "Jô", "presente": False},
            {"nome": "Jovina", "presente": False},
            {"nome": "Jucileide", "presente": False},
            {"nome": "Kennye", "presente": True},
            {"nome": "Lenilde", "presente": True},
            {"nome": "Lilian", "presente": False},
            {"nome": "Lourdes Oliveira", "presente": False},
            {"nome": "Maria", "presente": False},
            {"nome": "Maria de Loudes Ayala", "presente": True},
            {"nome": "Maria Helna Lourenço", "presente": False},
            {"nome": "Marli de Paula", "presente": False},
            {"nome": "Maya", "presente": True},
            {"nome": "Nalva", "presente": True},
            {"nome": "Neuza Guimarães", "presente": False},
            {"nome": "Nilza Arcanjo", "presente": False},
            {"nome": "Raimunda da Conceição", "presente": False},
            {"nome": "Rosenilda", "presente": False},
            {"nome": "Rute Morete", "presente": False},
            {"nome": "Sandra Assis", "presente": True},
            {"nome": "Sara Ribeiro", "presente": False},
            {"nome": "Sarah Reis", "presente": True},
            {"nome": "Simone Tavares", "presente": True},
            {"nome": "Sandra Magalhães", "presente": True},
            {"nome": "Tania", "presente": True},
            {"nome": "Valdirene", "presente": True},
            {"nome": "Vera Lucia Aparecida", "presente": False},
            {"nome": "Vera Ricardo", "presente": False},
            {"nome": "Laudiceia", "presente": True},
            {"nome": "Rosana", "presente": False},
            {"nome": "Augusta", "presente": False},
            {"nome": "Deise Farias", "presente": True},
            {"nome": "Mirian Menezes", "presente": False},
            {"nome": "Regiane", "presente": False},
            {"nome": "Danieli", "presente": False},
            {"nome": "Gleyse", "presente": False},
            {"nome": "Lucilene", "presente": True},
            {"nome": "Tia Kesia", "presente": False},
            {"nome": "Leicida", "presente": True},
            {"nome": "Márcia Regina", "presente": True}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 25,
        "oferta": 19.90,
        "presencas": [
            {"nome": "Ana Aleixo", "presente": False},
            {"nome": "Angelica", "presente": True},
            {"nome": "Bruna", "presente": True},
            {"nome": "Carla", "presente": False},
            {"nome": "Carla Santana", "presente": False},
            {"nome": "Claudia", "presente": False},
            {"nome": "Cristiane Gomes", "presente": False},
            {"nome": "Daiane Balleiro", "presente": False},
            {"nome": "Denise Rodrigues", "presente": True},
            {"nome": "Dirce dos Santos", "presente": False},
            {"nome": "Eliane Cardoso", "presente": False},
            {"nome": "Eliene Viana", "presente": True},
            {"nome": "Érica", "presente": True},
            {"nome": "Ester Ferreira", "presente": False},
            {"nome": "Eula", "presente": True},
            {"nome": "Evanilda", "presente": False},
            {"nome": "Geni", "presente": False},
            {"nome": "Geovan Silva", "presente": True},
            {"nome": "Geovanna Tavares", "presente": False},
            {"nome": "Gildete Dias dos Santos", "presente": False},
            {"nome": "Graciete", "presente": True},
            {"nome": "Graucia Campos", "presente": False},
            {"nome": "Iraci", "presente": False},
            {"nome": "Jô", "presente": True},
            {"nome": "Jovina", "presente": False},
            {"nome": "Jucileide", "presente": False},
            {"nome": "Kennye", "presente": True},
            {"nome": "Lenilde", "presente": False},
            {"nome": "Lilian", "presente": False},
            {"nome": "Lourdes Oliveira", "presente": False},
            {"nome": "Maria", "presente": False},
            {"nome": "Maria de Loudes Ayala", "presente": False},
            {"nome": "Maria Helna Lourenço", "presente": False},
            {"nome": "Marli de Paula", "presente": False},
            {"nome": "Maya", "presente": False},
            {"nome": "Nalva", "presente": True},
            {"nome": "Neuza Guimarães", "presente": False},
            {"nome": "Nilza Arcanjo", "presente": False},
            {"nome": "Raimunda da Conceição", "presente": False},
            {"nome": "Rosenilda", "presente": False},
            {"nome": "Rute Morete", "presente": False},
            {"nome": "Sandra Assis", "presente": True},
            {"nome": "Sara Ribeiro", "presente": False},
            {"nome": "Sarah Reis", "presente": True},
            {"nome": "Simone Tavares", "presente": True},
            {"nome": "Sandra Magalhães", "presente": False},
            {"nome": "Tania", "presente": False},
            {"nome": "Valdirene", "presente": False},
            {"nome": "Vera Lucia Aparecida", "presente": False},
            {"nome": "Vera Ricardo", "presente": False},
            {"nome": "Laudiceia", "presente": False},
            {"nome": "Rosana", "presente": True},
            {"nome": "Augusta", "presente": False},
            {"nome": "Deise Farias", "presente": True},
            {"nome": "Mirian Menezes", "presente": False},
            {"nome": "Regiane", "presente": False},
            {"nome": "Danieli", "presente": False},
            {"nome": "Gleyse", "presente": False},
            {"nome": "Lucilene", "presente": False},
            {"nome": "Tia Kesia", "presente": False},
            {"nome": "Leicida", "presente": True},
            {"nome": "Márcia Regina", "presente": True}
        ]
    }
]

def obter_mapeamento_dorcas():
    """Busca todos os alunos da turma Dorcas e cria mapeamento nome->ID"""
    print("📋 Buscando irmãs da turma Dorcas...")
    
    response = requests.get(f"{BASE_URL}/students?turma_id={TURMA_ID}")
    if response.status_code == 200:
        students = response.json()
        mapping = {}
        print(f"   Encontradas {len(students)} irmãs:")
        
        for student in students:
            nome_completo = student["nome_completo"]
            mapping[nome_completo] = student["id"]
            
            # Criar mapeamentos alternativos para facilitar a busca
            # Primeiro nome
            primeiro_nome = nome_completo.split()[0]
            if primeiro_nome not in mapping:
                mapping[primeiro_nome] = student["id"]
            
            # Nome sem acentos (simplificado)
            nome_simples = nome_completo.replace("á", "a").replace("ã", "a").replace("ç", "c").replace("é", "e")
            if nome_simples != nome_completo:
                mapping[nome_simples] = student["id"]
        
        return mapping, students
    else:
        print(f"❌ Erro ao buscar irmãs: {response.status_code}")
        return {}, []

def encontrar_melhor_match(nome_busca, students):
    """Encontra o melhor match para um nome"""
    nome_busca_lower = nome_busca.lower()
    
    for student in students:
        nome_db = student["nome_completo"].lower()
        
        # Match exato
        if nome_busca_lower == nome_db:
            return student["id"]
        
        # Nome está contido no nome do DB
        if nome_busca_lower in nome_db:
            return student["id"]
        
        # Nome do DB está contido no nome da busca
        if nome_db in nome_busca_lower:
            return student["id"]
        
        # Primeiro nome match
        if nome_busca_lower == nome_db.split()[0]:
            return student["id"]
    
    return None

def registrar_presenca_dorcas(dia_data, name_mapping, students):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    presentes_nomes = []
    nao_encontrados = []
    
    # Processar todas as irmãs
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        # Tentar encontrar o ID da irmã
        aluno_id = None
        
        if nome in name_mapping:
            aluno_id = name_mapping[nome]
        else:
            # Buscar por match inteligente
            aluno_id = encontrar_melhor_match(nome, students)
        
        if not aluno_id:
            nao_encontrados.append(nome)
            continue
        
        status = "presente" if presente else "ausente"
        
        if presente:
            presentes_nomes.append(nome.split()[0])  # Primeiro nome
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
        print(f"⚠️  Irmãs não encontradas: {', '.join(nao_encontrados[:5])}{'...' if len(nao_encontrados) > 5 else ''}")
    
    # Registrar via API
    url = f"{BASE_URL}/attendance/bulk/{TURMA_ID}?data={dia_data['data']}"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=bulk_attendance)
    
    if response.status_code == 200:
        ausentes_count = len(dia_data["presencas"]) - total_presentes
        print(f"✅ {dia_data['data']}: {total_presentes} presentes, {ausentes_count} ausentes, R$ {dia_data['oferta']:.2f}")
        if presentes_nomes:
            print(f"   Presentes: {', '.join(presentes_nomes[:8])}{'...' if len(presentes_nomes) > 8 else ''}")
        return True
    else:
        print(f"❌ Erro em {dia_data['data']}: {response.text}")
        return False

print("👩 Registrando presença turma Dorcas (irmãs)...")

# Obter mapeamento real
name_mapping, students = obter_mapeamento_dorcas()

if name_mapping:
    for dia in dados:
        registrar_presenca_dorcas(dia, name_mapping, students)
    print("🎉 Dados registrados!")
else:
    print("❌ Não foi possível obter os dados das irmãs.")