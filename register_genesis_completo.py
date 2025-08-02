#!/usr/bin/env python3
"""
Script para registrar dados completos da turma Genesis (Alunos) - incluindo ausentes
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

# Dados completos fornecidos pelo usuário
dados_completos = [
    {
        "data": "2025-07-06",
        "revista_biblia": 6,
        "oferta": 14.50,
        "presencas": [
            {"nome": "Agatha Mirella Souza Martins", "presente": False},
            {"nome": "Arthur Galvão Costa da Silva", "presente": False},
            {"nome": "Benjamim Henrique de Carvalho André", "presente": False},
            {"nome": "Helena Marques Dantas", "presente": True},
            {"nome": "Lara Heloíse Santos de Jesus", "presente": True},
            {"nome": "Luiza Oliveira Reis", "presente": True},
            {"nome": "Manuela de Azevedo Santos", "presente": False},
            {"nome": "Otton Gomes Santos Albuquerque", "presente": False},
            {"nome": "Ayla Sophia Souza Martins", "presente": False},
            {"nome": "Isadora de Oliveira Santos Alves", "presente": False},
            {"nome": "Leandro Pedro de Lima", "presente": False},
            {"nome": "Mariana Rodrigues Augusto", "presente": False},
            {"nome": "Miguel Silva dos Santos", "presente": False}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 8,
        "oferta": 18.75,
        "presencas": [
            {"nome": "Agatha Mirella Souza Martins", "presente": True},
            {"nome": "Arthur Galvão Costa da Silva", "presente": True},
            {"nome": "Benjamim Henrique de Carvalho André", "presente": False},
            {"nome": "Helena Marques Dantas", "presente": True},
            {"nome": "Lara Heloíse Santos de Jesus", "presente": True},
            {"nome": "Luiza Oliveira Reis", "presente": True},
            {"nome": "Manuela de Azevedo Santos", "presente": True},
            {"nome": "Otton Gomes Santos Albuquerque", "presente": False},
            {"nome": "Ayla Sophia Souza Martins", "presente": False},
            {"nome": "Isadora de Oliveira Santos Alves", "presente": True},
            {"nome": "Leandro Pedro de Lima", "presente": True},
            {"nome": "Mariana Rodrigues Augusto", "presente": False},
            {"nome": "Miguel Silva dos Santos", "presente": False}
        ]
    }
]

def registrar_presenca_completa(dia_data):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    
    # Processar todos os alunos com dados específicos
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        if nome not in name_to_id:
            print(f"⚠️  Nome não encontrado: {nome}")
            continue
            
        aluno_id = name_to_id[nome]
        status = "presente" if presente else "ausente"
        
        if presente and total_presentes > 0:
            oferta_individual = dia_data["oferta"] / total_presentes
            revista_individual = dia_data["revista_biblia"] / total_presentes
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
        presentes_list = [p["nome"] for p in dia_data["presencas"] if p["presente"]]
        ausentes_count = len(dia_data["presencas"]) - total_presentes
        print(f"✅ {dia_data['data']}: {total_presentes} presentes, {ausentes_count} ausentes, R$ {dia_data['oferta']:.2f}")
        print(f"   Presentes: {', '.join(presentes_list[:3])}{'...' if len(presentes_list) > 3 else ''}")
        return True
    else:
        print(f"❌ Erro em {dia_data['data']}: {response.text}")
        return False

print("🎓 Registrando presença COMPLETA turma Genesis (Alunos)...")

for dia in dados_completos:
    registrar_presenca_completa(dia)

print("🎉 Dados completos registrados!")