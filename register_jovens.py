#!/usr/bin/env python3
"""
Script para registrar dados da turma Jovens
"""

import json
import requests

BASE_URL = "https://git-restore.preview.emergentagent.com/api"
TURMA_ID = "49c33e68-2aaa-4e2b-b0b3-84d0ad1a2383"  # Jovens

# Dados fornecidos pelo usuário
dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 10,
        "oferta": 13.80,
        "presencas": [
            {"nome": "Abmael", "presente": True},
            {"nome": "Almir", "presente": False},
            {"nome": "Ana", "presente": False},
            {"nome": "Emanuel", "presente": True},
            {"nome": "Gustavo", "presente": True},
            {"nome": "Ingrid", "presente": False},
            {"nome": "Janecelia", "presente": True},
            {"nome": "Jhenniffer", "presente": False},
            {"nome": "Júlio", "presente": False},
            {"nome": "Kessia", "presente": True},
            {"nome": "Misma", "presente": True},
            {"nome": "Natalia Silva", "presente": True},
            {"nome": "Solange", "presente": False},
            {"nome": "Vitória Soares", "presente": False},
            {"nome": "Yan", "presente": True},
            {"nome": "Abner", "presente": False},
            {"nome": "Dannilo Duany", "presente": True},
            {"nome": "Lucas Brito", "presente": False},
            {"nome": "Ana Carolina", "presente": False},
            {"nome": "Danilo", "presente": False},
            {"nome": "Matheus Assis", "presente": False},
            {"nome": "Ademir Junior", "presente": True}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 15,
        "oferta": 19.50,
        "presencas": [
            {"nome": "Abmael", "presente": True},
            {"nome": "Almir", "presente": True},
            {"nome": "Ana", "presente": False},
            {"nome": "Emanuel", "presente": True},
            {"nome": "Gustavo", "presente": True},
            {"nome": "Ingrid", "presente": True},
            {"nome": "Janecelia", "presente": True},
            {"nome": "Jhenniffer", "presente": False},
            {"nome": "Júlio", "presente": False},
            {"nome": "Kessia", "presente": True},
            {"nome": "Misma", "presente": True},
            {"nome": "Natalia Silva", "presente": True},
            {"nome": "Solange", "presente": True},
            {"nome": "Vitória Soares", "presente": False},
            {"nome": "Yan", "presente": False},
            {"nome": "Abner", "presente": True},
            {"nome": "Dannilo Duany", "presente": True},
            {"nome": "Lucas Brito", "presente": True},
            {"nome": "Ana Carolina", "presente": True},
            {"nome": "Danilo", "presente": True},
            {"nome": "Matheus Assis", "presente": False},
            {"nome": "Ademir Junior", "presente": False}
        ]
    }
]

def obter_mapeamento_jovens():
    """Busca todos os alunos da turma Jovens e cria mapeamento nome->ID"""
    print("📋 Buscando alunos da turma Jovens...")
    
    response = requests.get(f"{BASE_URL}/students?turma_id={TURMA_ID}")
    if response.status_code == 200:
        students = response.json()
        mapping = {}
        print(f"   Encontrados {len(students)} alunos:")
        
        for student in students:
            nome_completo = student["nome_completo"]
            # Tentar mapear nomes simples
            nome_simples = nome_completo.split()[0]  # Primeiro nome
            mapping[nome_completo] = student["id"]
            mapping[nome_simples] = student["id"]
            print(f"   • {nome_completo} -> {student['id']}")
        
        return mapping
    else:
        print(f"❌ Erro ao buscar alunos: {response.status_code}")
        return {}

def registrar_presenca_jovens(dia_data, name_mapping):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    presentes_nomes = []
    nao_encontrados = []
    
    # Processar todos os alunos
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        # Tentar encontrar por nome exato ou similar
        aluno_id = None
        if nome in name_mapping:
            aluno_id = name_mapping[nome]
        else:
            # Tentar encontrar por nome parcial
            for nome_db, id_db in name_mapping.items():
                if nome.lower() in nome_db.lower() or nome_db.lower().startswith(nome.lower()):
                    aluno_id = id_db
                    break
        
        if not aluno_id:
            nao_encontrados.append(nome)
            continue
        
        status = "presente" if presente else "ausente"
        
        if presente:
            presentes_nomes.append(nome)
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
        print(f"⚠️  Nomes não encontrados: {', '.join(nao_encontrados)}")
    
    # Registrar via API
    url = f"{BASE_URL}/attendance/bulk/{TURMA_ID}?data={dia_data['data']}"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=bulk_attendance)
    
    if response.status_code == 200:
        ausentes_count = len(dia_data["presencas"]) - total_presentes
        print(f"✅ {dia_data['data']}: {total_presentes} presentes, {ausentes_count} ausentes, R$ {dia_data['oferta']:.2f}")
        if presentes_nomes:
            print(f"   Presentes: {', '.join(presentes_nomes[:5])}{'...' if len(presentes_nomes) > 5 else ''}")
        return True
    else:
        print(f"❌ Erro em {dia_data['data']}: {response.text}")
        return False

print("🎓 Registrando presença turma Jovens...")

# Obter mapeamento real
name_mapping = obter_mapeamento_jovens()

if name_mapping:
    for dia in dados:
        registrar_presenca_jovens(dia, name_mapping)
    print("🎉 Dados registrados!")
else:
    print("❌ Não foi possível obter os dados dos alunos.")