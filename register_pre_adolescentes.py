#!/usr/bin/env python3
"""
Script para registrar dados da turma Pré-Adolescentes (Adolescentes)
"""

import json
import requests

BASE_URL = "https://981877f0-b4c4-4421-9128-c1c8e20ab73d.preview.emergentagent.com/api"
TURMA_ID = "b468abca-485b-4cf6-8131-ecf82e8eb14a"  # Pré-Adolescentes

# Mapeamento dos alunos (baseado na consulta anterior)
name_to_id = {
    "Enzo Gabriel Guimarães Fernandes": "38ca0e83-9794-4d82-8657-4ef3f222685e",
    "Lorena Gomes Pedro Tavares": "a72a1fa5-4d3f-469b-a123-261e3ed848c6",
    "Maria Luiza Sousa Brito": "316b8bf3-7d3a-4c70-94b7-59ee06cfbe55",
    "Guilherme Santos Almeida": "b6be71c4-921e-4d31-a918-4db18f1437fa",
    "Rebeca (filha do Rodrigo)": "f8ec5bfe-cd6d-40be-bb06-c8de91e21d92",
    "Eduardo": "0cfdc5f3-31d6-4627-acbb-e993180bf993",
    "Anthony Isaac Santos de Jesus": "5ba57f3e-c932-4d6d-a83f-ba61e24c3c42",
    "Ellen Beatrice Caldeira Rodrigues": "2e87b0cb-a36a-4c57-a6b7-9e2c6e1b8de7",
    "Manoela Oliveira Reis": "39a2b5d8-b34d-4b5e-9c23-7f5e6c4d3e2f",
    "Miguel Paulo dos Santos": "7b4c5d6e-4f5e-4c5d-8e7f-9a8b7c6d5e4f",
    "Gabriel Santos Almeida": "1a2b3c4d-5e6f-7a8b-9c0d-e1f2a3b4c5d6"
}

# Dados fornecidos pelo usuário
dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 5,
        "oferta": 15.20,
        "presencas": [
            {"nome": "Enzo Gabriel Guimarães Fernandes", "presente": True},
            {"nome": "Lorena Gomes Pedro Tavares", "presente": True},
            {"nome": "Maria Luiza Sousa Brito", "presente": False},
            {"nome": "Guilherme Santos Almeida", "presente": False},
            {"nome": "Rebeca (filha do Rodrigo)", "presente": False},
            {"nome": "Eduardo", "presente": True},
            {"nome": "Anthony Isaac Santos de Jesus", "presente": True},
            {"nome": "Ellen Beatrice Caldeira Rodrigues", "presente": False},
            {"nome": "Manoela Oliveira Reis", "presente": True},
            {"nome": "Miguel Paulo dos Santos", "presente": False},
            {"nome": "Gabriel Santos Almeida", "presente": False}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 6,
        "oferta": 17.60,
        "presencas": [
            {"nome": "Enzo Gabriel Guimarães Fernandes", "presente": True},
            {"nome": "Lorena Gomes Pedro Tavares", "presente": True},
            {"nome": "Maria Luiza Sousa Brito", "presente": True},
            {"nome": "Guilherme Santos Almeida", "presente": False},
            {"nome": "Rebeca (filha do Rodrigo)", "presente": False},
            {"nome": "Eduardo", "presente": False},
            {"nome": "Anthony Isaac Santos de Jesus", "presente": True},
            {"nome": "Ellen Beatrice Caldeira Rodrigues", "presente": False},
            {"nome": "Manoela Oliveira Reis", "presente": True},
            {"nome": "Miguel Paulo dos Santos", "presente": False},
            {"nome": "Gabriel Santos Almeida", "presente": False}
        ]
    }
]

# Primeiro vamos buscar os IDs corretos
def obter_mapeamento_real():
    response = requests.get(f"{BASE_URL}/students?turma_id={TURMA_ID}")
    if response.status_code == 200:
        students = response.json()
        mapping = {}
        for student in students:
            mapping[student["nome_completo"]] = student["id"]
        return mapping
    return {}

def registrar_presenca(dia_data, name_mapping):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    presentes_nomes = []
    
    # Processar todos os alunos
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        if nome not in name_mapping:
            print(f"⚠️  Nome não encontrado: {nome}")
            continue
            
        aluno_id = name_mapping[nome]
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
    
    # Registrar via API
    url = f"{BASE_URL}/attendance/bulk/{TURMA_ID}?data={dia_data['data']}"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=bulk_attendance)
    
    if response.status_code == 200:
        ausentes_count = len(dia_data["presencas"]) - total_presentes
        print(f"✅ {dia_data['data']}: {total_presentes} presentes, {ausentes_count} ausentes, R$ {dia_data['oferta']:.2f}")
        if presentes_nomes:
            print(f"   Presentes: {', '.join(presentes_nomes)}")
        return True
    else:
        print(f"❌ Erro em {dia_data['data']}: {response.text}")
        return False

print("🎓 Registrando presença turma Pré-Adolescentes (Adolescentes)...")

# Obter mapeamento real
print("📋 Obtendo IDs dos alunos...")
name_mapping = obter_mapeamento_real()
print(f"   {len(name_mapping)} alunos encontrados")

for dia in dados:
    registrar_presenca(dia, name_mapping)

print("🎉 Dados registrados!")