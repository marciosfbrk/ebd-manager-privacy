#!/usr/bin/env python3
"""
Script para registrar dados da turma Soldados de Cristo
"""

import json
import requests

BASE_URL = "https://sunday-bible.preview.emergentagent.com/api"
TURMA_ID = "16d372d3-fd23-46d1-b560-32a4e18ce9ee"  # Soldados de Cristo

# Dados fornecidos pelo usuário
dados = [
    {
        "data": "2025-07-06",
        "revista_biblia": 13,
        "oferta": 16.20,
        "presencas": [
            {"nome": "Alexandre Tavares", "presente": True},
            {"nome": "Amilton", "presente": False},
            {"nome": "André Afonso Lana", "presente": True},
            {"nome": "Daniel Corsine", "presente": True},
            {"nome": "Elias Barbosa", "presente": False},
            {"nome": "Elizeu Barbosa", "presente": True},
            {"nome": "Gerônimo", "presente": True},
            {"nome": "Isaias Abreu", "presente": False},
            {"nome": "Jair Benedito", "presente": False},
            {"nome": "Jesiel José", "presente": False},
            {"nome": "Jessé Araújo", "presente": False},
            {"nome": "Joedilson", "presente": True},
            {"nome": "Joel Cruz", "presente": False},
            {"nome": "José Arcanjo", "presente": True},
            {"nome": "José Domingos", "presente": True},
            {"nome": "Luiz Felipe", "presente": True},
            {"nome": "Manoel Lopes", "presente": False},
            {"nome": "Messias Rodrigues", "presente": True},
            {"nome": "Nylon", "presente": False},
            {"nome": "Ronaldo Rabelo", "presente": True},
            {"nome": "Tiago Henrique", "presente": True},
            {"nome": "Fernando Paulo", "presente": False},
            {"nome": "Gideão", "presente": False},
            {"nome": "Djalma", "presente": False},
            {"nome": "José Maria", "presente": False},
            {"nome": "Willian Medeiros Alves", "presente": True},
            {"nome": "Diego Augusto", "presente": False},
            {"nome": "Reginaldo", "presente": True},
            {"nome": "Daniel José", "presente": False},
            {"nome": "Daniel Mousinho de Araújo", "presente": False},
            {"nome": "Gabriel Lana", "presente": False}
        ]
    },
    {
        "data": "2025-07-13",
        "revista_biblia": 12,
        "oferta": 18.70,
        "presencas": [
            {"nome": "Alexandre Tavares", "presente": False},
            {"nome": "Amilton", "presente": True},
            {"nome": "André Afonso Lana", "presente": True},
            {"nome": "Daniel Corsine", "presente": False},
            {"nome": "Elias Barbosa", "presente": False},
            {"nome": "Elizeu Barbosa", "presente": False},
            {"nome": "Gerônimo", "presente": True},
            {"nome": "Isaias Abreu", "presente": False},
            {"nome": "Jair Benedito", "presente": False},
            {"nome": "Jesiel José", "presente": False},
            {"nome": "Jessé Araújo", "presente": True},
            {"nome": "Joedilson", "presente": False},
            {"nome": "Joel Cruz", "presente": False},
            {"nome": "José Arcanjo", "presente": True},
            {"nome": "José Domingos", "presente": False},
            {"nome": "Luiz Felipe", "presente": True},
            {"nome": "Manoel Lopes", "presente": False},
            {"nome": "Messias Rodrigues", "presente": True},
            {"nome": "Nylon", "presente": False},
            {"nome": "Ronaldo Rabelo", "presente": True},
            {"nome": "Tiago Henrique", "presente": False},
            {"nome": "Fernando Paulo", "presente": False},
            {"nome": "Gideão", "presente": False},
            {"nome": "Djalma", "presente": False},
            {"nome": "José Maria", "presente": True},
            {"nome": "Willian Medeiros Alves", "presente": False},
            {"nome": "Diego Augusto", "presente": False},
            {"nome": "Reginaldo", "presente": False},
            {"nome": "Daniel José", "presente": False},
            {"nome": "Daniel Mousinho de Araújo", "presente": False},
            {"nome": "Gabriel Lana", "presente": False}
        ]
    }
]

def obter_mapeamento_soldados():
    """Busca todos os soldados da turma e cria mapeamento nome->ID"""
    print("⚔️ Buscando soldados da turma Soldados de Cristo...")
    
    response = requests.get(f"{BASE_URL}/students?turma_id={TURMA_ID}")
    if response.status_code == 200:
        students = response.json()
        mapping = {}
        print(f"   Encontrados {len(students)} soldados:")
        
        for student in students:
            nome_completo = student["nome_completo"]
            mapping[nome_completo] = student["id"]
            
            # Criar mapeamentos alternativos para facilitar busca
            primeiro_nome = nome_completo.split()[0]
            mapping[primeiro_nome] = student["id"]
        
        return mapping, students
    else:
        print(f"❌ Erro ao buscar soldados: {response.status_code}")
        return {}, []

def encontrar_melhor_match_soldados(nome_busca, students):
    """Encontra o melhor match para um nome de soldado"""
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
        
        # Match por primeiro nome
        primeiro_nome_busca = nome_busca_lower.split()[0]
        primeiro_nome_db = nome_db.split()[0]
        
        if primeiro_nome_busca == primeiro_nome_db:
            return student["id"]
        
        # Match por partes do nome
        parts_busca = nome_busca_lower.split()
        parts_db = nome_db.split()
        
        matches = 0
        for part_busca in parts_busca:
            for part_db in parts_db:
                if part_busca == part_db:
                    matches += 1
        
        # Se mais de 50% das partes coincidem
        if matches >= len(parts_busca) * 0.5 and matches >= len(parts_db) * 0.5:
            return student["id"]
    
    return None

def registrar_presenca_soldados(dia_data, name_mapping, students):
    total_presentes = sum(1 for p in dia_data["presencas"] if p["presente"])
    
    bulk_attendance = []
    presentes_nomes = []
    nao_encontrados = []
    
    # Processar todos os soldados
    for presenca in dia_data["presencas"]:
        nome = presenca["nome"]
        presente = presenca["presente"]
        
        # Tentar encontrar o ID do soldado
        aluno_id = None
        
        if nome in name_mapping:
            aluno_id = name_mapping[nome]
        else:
            # Buscar por match inteligente
            aluno_id = encontrar_melhor_match_soldados(nome, students)
        
        if not aluno_id:
            nao_encontrados.append(nome)
            continue
        
        status = "presente" if presente else "ausente"
        
        if presente:
            primeiro_nome = nome.split()[0]
            presentes_nomes.append(primeiro_nome)
            
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
        print(f"⚠️  Soldados não encontrados: {', '.join(nao_encontrados[:5])}{'...' if len(nao_encontrados) > 5 else ''}")
    
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

print("⚔️ Registrando presença turma Soldados de Cristo...")

# Obter mapeamento real
name_mapping, students = obter_mapeamento_soldados()

if name_mapping:
    for dia in dados:
        registrar_presenca_soldados(dia, name_mapping, students)
    print("🎉 Dados registrados!")
else:
    print("❌ Não foi possível obter os dados dos soldados.")