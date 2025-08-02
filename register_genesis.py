#!/usr/bin/env python3
"""
Script rápido para registrar dados da turma Genesis (Alunos)
"""

import json
import requests

BASE_URL = "https://05ec9a3d-a8ee-4de8-ad13-f8f4dfa912ec.preview.emergentagent.com/api"
TURMA_ID = "3ed3f003-00ba-4547-a9ab-f73825ece0a7"  # Genesis

# Mapeamento dos alunos
name_to_id = {
    "Agatha Mirella Souza Martins": "ddb2250c-2846-4159-8608-5739f60b8ea2",
    "Arthur Galvão Costa da Silva": "018f6c1f-a452-48a5-b8da-a6f115d3aa0d",
    "Benjamim Henrique de Carvalho André": "1a954e4c-8c7c-4b4c-8d85-9a308d7265df",
    "Helena Marques Dantas": "0dab5bc1-afc9-4946-b8ad-59e7132299e7",
    "Lara Heloíse Santos de Jesus": "7a97b949-56c8-4ac3-8fbe-1c67d72d380b",
    "Luiza Oliveira Reis": "6d66230d-c8d1-4608-8632-06b2c02b9e47",
    "Manuela de Azevedo Santos": "5d5e1b9f-a567-4ecf-934a-60cefa13fa65",
    "Otton Gomes Santos Albuquerque": "7750d845-d288-4f34-9729-c2055791dbbe",
    "Ayla Sophia Souza Martins": "e7806a34-08f0-4fb5-ac42-fec0c068c91d",
    "Isadora de Oliveira Santos Alves": "40046a6d-7279-4bdf-9632-d33d684c44a7",
    "Leandro Pedro de Lima": "623fb79d-8b4b-4c06-a7b3-616dc16c2904",
    "Mariana Rodrigues Augusto": "219856f8-afae-49c0-aed6-a4cc37806fed",
    "Miguel Silva dos Santos": "f6c7c68a-2b4d-47af-8419-c53b3cfdb080"
}

dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 6,
        "oferta": 14.50,
        "presencas": [
            {"nome": "Helena Marques Dantas", "presente": True},
            {"nome": "Lara Heloíse Santos de Jesus", "presente": True},
            {"nome": "Luiza Oliveira Reis", "presente": True}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 8,
        "oferta": 18.75,
        "presencas": [
            {"nome": "Agatha Mirella Souza Martins", "presente": True},
            {"nome": "Arthur Galvão Costa da Silva", "presente": True},
            {"nome": "Helena Marques Dantas", "presente": True},
            {"nome": "Lara Heloíse Santos de Jesus", "presente": True},
            {"nome": "Luiza Oliveira Reis", "presente": True},
            {"nome": "Manuela de Azevedo Santos", "presente": True},
            {"nome": "Isadora de Oliveira Santos Alves", "presente": True},
            {"nome": "Leandro Pedro de Lima", "presente": True}
        ]
    }
]

def registrar_presenca(data_info):
    presentes = [p["nome"] for p in data_info["presencas"] if p["presente"]]
    total_presentes = len(presentes)
    
    bulk_attendance = []
    
    # Processar todos os alunos
    for nome, aluno_id in name_to_id.items():
        presente = nome in presentes
        status = "presente" if presente else "ausente"
        
        if presente and total_presentes > 0:
            oferta_individual = data_info["oferta"] / total_presentes
            revista_individual = data_info["revista_biblia"] / total_presentes
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
    url = f"{BASE_URL}/attendance/bulk/{TURMA_ID}?data={data_info['data']}"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=bulk_attendance)
    
    if response.status_code == 200:
        print(f"✅ {data_info['data']}: {total_presentes} presentes, R$ {data_info['oferta']:.2f}")
        return True
    else:
        print(f"❌ Erro em {data_info['data']}: {response.text}")
        return False

print("🎓 Registrando presença turma Genesis (Alunos)...")

for dia in dados:
    registrar_presenca(dia)

print("🎉 Concluído!")