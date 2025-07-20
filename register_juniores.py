#!/usr/bin/env python3
"""
Script para registrar dados da turma Juniores (Pré-Adolescentes)
"""

import json
import requests

BASE_URL = "https://341b9440-3e60-40b5-8139-767e514488b7.preview.emergentagent.com/api"
TURMA_ID = "c1811f9d-8f7d-4fdf-838d-0d6d5817b4b6"  # Juniores

# Mapeamento dos alunos
name_to_id = {
    "Beatriz Pedro de Lima": "a72bca71-b6f6-4529-9757-51110c7a89d1",
    "Davi Afonso Lana": "6dbab8c4-01b2-42c4-896d-cc111504e7ac",
    "Enzo Leonardo Bitencourt Souza": "29efe8bb-7e45-4ac4-b083-f3ae3eed722d",
    "Felype Augusto Oliveira de Jesus": "b03245d1-1b09-41b6-a610-27ec9126168a",
    "Gustavo Lorenzo Ferreira": "8c1b1d8e-036e-476b-97ca-86f2b89ed4da",
    "Mariana Lima de Sousa": "43be027d-e2c9-493d-926d-d92af8f86f8b",
    "Isabelle Sophia Da Costa De Almeida": "999d1af2-d248-4a73-9825-c4b141d25d13",
    "Luíza (Suellen Tayrone)": "2952f09e-e10b-48e4-9795-062aa8c5f523",
    "Hadassah Victoria Gabriel Tavares": "b54b7351-0af6-4e74-9654-58295c83bbe5",
    "Davi Caldeira Rodrigues": "84375e1d-f639-4747-9bb6-3d1b32e5021a",
    "Ana Luiza Santana de Moura": "6a43d1c8-7eae-48f1-be87-ea11efb279c7",
    "Kemuel Brito": "24e586b5-649c-464b-8a5d-a70069ecd06c"
}

# Dados fornecidos pelo usuário
dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 3,
        "oferta": 11.90,
        "presencas": [
            {"nome": "Beatriz Pedro de Lima", "presente": False},
            {"nome": "Davi Afonso Lana", "presente": False},
            {"nome": "Enzo Leonardo Bitencourt Souza", "presente": True},
            {"nome": "Felype Augusto Oliveira de Jesus", "presente": False},
            {"nome": "Gustavo Lorenzo Ferreira", "presente": True},
            {"nome": "Mariana Lima de Sousa", "presente": False},
            {"nome": "Isabelle Sophia Da Costa De Almeida", "presente": True},
            {"nome": "Luíza (Suellen Tayrone)", "presente": False},
            {"nome": "Hadassah Victoria Gabriel Tavares", "presente": False},
            {"nome": "Davi Caldeira Rodrigues", "presente": False},
            {"nome": "Ana Luiza Santana de Moura", "presente": False},
            {"nome": "Kemuel Brito", "presente": False}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 5,
        "oferta": 16.40,
        "presencas": [
            {"nome": "Beatriz Pedro de Lima", "presente": True},
            {"nome": "Davi Afonso Lana", "presente": False},
            {"nome": "Enzo Leonardo Bitencourt Souza", "presente": True},
            {"nome": "Felype Augusto Oliveira de Jesus", "presente": False},
            {"nome": "Gustavo Lorenzo Ferreira", "presente": True},
            {"nome": "Mariana Lima de Sousa", "presente": False},
            {"nome": "Isabelle Sophia Da Costa De Almeida", "presente": False},
            {"nome": "Luíza (Suellen Tayrone)", "presente": False},
            {"nome": "Hadassah Victoria Gabriel Tavares", "presente": True},
            {"nome": "Davi Caldeira Rodrigues", "presente": False},
            {"nome": "Ana Luiza Santana de Moura", "presente": False},
            {"nome": "Kemuel Brito", "presente": False}
        ]
    }
]

def registrar_presenca(dia_data):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    presentes_nomes = []
    
    # Processar todos os alunos
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        if nome not in name_to_id:
            print(f"⚠️  Nome não encontrado: {nome}")
            continue
            
        aluno_id = name_to_id[nome]
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

print("🎓 Registrando presença turma Juniores (Pré-Adolescentes)...")

for dia in dados:
    registrar_presenca(dia)

print("🎉 Dados registrados!")