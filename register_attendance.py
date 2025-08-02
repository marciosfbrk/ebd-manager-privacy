#!/usr/bin/env python3
"""
Script para registrar dados históricos de presença no sistema EBD Manager
"""

import json
import requests
import sys
from datetime import datetime

# URL do sistema hospedado
BASE_URL = "https://05ec9a3d-a8ee-4de8-ad13-f8f4dfa912ec.preview.emergentagent.com/api"

# ID da turma "Professores e Oficiais"
TURMA_ID = "2e827638-8fff-46cf-9dd3-cfa24ea045e1"

# Dados de presença fornecidos pelo usuário
attendance_data = {
  "sala": "Professores e Oficiais",
  "dias": [
    {
      "data": "2025-07-06",
      "revista_biblia": 33,
      "oferta": 33,
      "presencas": [
        {"nome": "Pr. Henrique", "presente": True},
        {"nome": "Pb Paulo", "presente": True},
        {"nome": "Pb Elias", "presente": True},
        {"nome": "Coop Carlos", "presente": False},
        {"nome": "Coop Elias Filho", "presente": False},
        {"nome": "Coop Jailton", "presente": False},
        {"nome": "Coop Santiago", "presente": True},
        {"nome": "Irmã Dorcas", "presente": False},
        {"nome": "Irmã Ester Carvalho", "presente": True},
        {"nome": "Irmã Marry", "presente": True},
        {"nome": "Irmã Renata", "presente": False},
        {"nome": "Irmã Rosa", "presente": False},
        {"nome": "Irmão Rubens", "presente": False},
        {"nome": "Izabelle", "presente": True},
        {"nome": "Juliana Silva", "presente": True},
        {"nome": "Kesia Ferreira", "presente": True},
        {"nome": "Márcio Ferreira", "presente": True},
        {"nome": "Pb Sebastião", "presente": False},
        {"nome": "Tia Ana Paula", "presente": False},
        {"nome": "Tia Deise", "presente": False},
        {"nome": "Tia Eliane", "presente": False},
        {"nome": "Tia Evelyn", "presente": True},
        {"nome": "Tia Flávia André", "presente": True},
        {"nome": "Tia Kelly", "presente": False},
        {"nome": "Tia Lu", "presente": True},
        {"nome": "Tia Natália", "presente": True},
        {"nome": "Tia Riane", "presente": True},
        {"nome": "Tio Italo", "presente": True},
        {"nome": "Pb Carlinhos", "presente": False},
        {"nome": "Sidney Custodio", "presente": False},
        {"nome": "Juliane Reis", "presente": True},
        {"nome": "Vitória Ferreira", "presente": True}
      ]
    },
    {
      "data": "2025-07-13",
      "revista_biblia": 40,
      "oferta": 40,
      "presencas": [
        {"nome": "Pr. Henrique", "presente": False},
        {"nome": "Pb Paulo", "presente": True},
        {"nome": "Pb Elias", "presente": True},
        {"nome": "Coop Carlos", "presente": False},
        {"nome": "Coop Elias Filho", "presente": True},
        {"nome": "Coop Jailton", "presente": True},
        {"nome": "Coop Santiago", "presente": False},
        {"nome": "Irmã Dorcas", "presente": False},
        {"nome": "Irmã Ester Carvalho", "presente": False},
        {"nome": "Irmã Marry", "presente": False},
        {"nome": "Irmã Renata", "presente": False},
        {"nome": "Irmã Rosa", "presente": True},
        {"nome": "Irmão Rubens", "presente": True},
        {"nome": "Izabelle", "presente": False},
        {"nome": "Juliana Silva", "presente": False},
        {"nome": "Kesia Ferreira", "presente": True},
        {"nome": "Márcio Ferreira", "presente": True},
        {"nome": "Pb Sebastião", "presente": False},
        {"nome": "Tia Ana Paula", "presente": True},
        {"nome": "Tia Deise", "presente": False},
        {"nome": "Tia Eliane", "presente": False},
        {"nome": "Tia Evelyn", "presente": True},
        {"nome": "Tia Flávia André", "presente": False},
        {"nome": "Tia Kelly", "presente": False},
        {"nome": "Tia Lu", "presente": True},
        {"nome": "Tia Natália", "presente": False},
        {"nome": "Tia Riane", "presente": True},
        {"nome": "Tio Italo", "presente": True},
        {"nome": "Pb Carlinhos", "presente": True},
        {"nome": "Sidney Custodio", "presente": False},
        {"nome": "Juliane Reis", "presente": True},
        {"nome": "Vitória Ferreira", "presente": False}
      ]
    }
  ]
}

def get_students():
    """Buscar todos os estudantes da turma Professores e Oficiais"""
    print("🔍 Buscando estudantes da turma Professores e Oficiais...")
    
    try:
        response = requests.get(f"{BASE_URL}/students?turma_id={TURMA_ID}")
        response.raise_for_status()
        students = response.json()
        
        print(f"✅ Encontrados {len(students)} estudantes")
        
        # Criar mapeamento nome -> id
        name_to_id = {}
        for student in students:
            name_to_id[student["nome_completo"]] = student["id"]
        
        return name_to_id
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao buscar estudantes: {e}")
        return None

def register_attendance_for_date(date_str, attendance_list, revista_biblia, oferta, name_to_id):
    """Registrar presença para uma data específica"""
    print(f"\n📅 Registrando presença para {date_str}...")
    
    # Contar presentes primeiro
    present_count = sum(1 for att in attendance_list if att["presente"])
    
    # Preparar lista de presenças para a API
    bulk_attendance = []
    total_present = 0
    total_absent = 0
    not_found = []
    
    for attendance in attendance_list:
        nome = attendance["nome"]
        presente = attendance["presente"]
        
        if nome not in name_to_id:
            not_found.append(nome)
            continue
        
        student_id = name_to_id[nome]
        status = "presente" if presente else "ausente"
        
        # Calcular oferta e revista individual apenas para quem está presente
        if presente and present_count > 0:
            individual_offer = oferta / present_count
            individual_revista = revista_biblia / present_count
        else:
            individual_offer = 0.0
            individual_revista = 0
        
        bulk_attendance.append({
            "aluno_id": student_id,
            "status": status,
            "oferta": individual_offer,
            "biblias_entregues": int(individual_revista),
            "revistas_entregues": int(individual_revista)
        })
        
        if presente:
            total_present += 1
        else:
            total_absent += 1
    
    if not_found:
        print(f"⚠️  Nomes não encontrados no sistema: {', '.join(not_found)}")
    
    print(f"📊 Resumo: {total_present} presentes, {total_absent} ausentes")
    if total_present > 0:
        individual_offer_display = oferta / present_count
        individual_revista_display = revista_biblia / present_count
        print(f"💰 Oferta individual: R$ {individual_offer_display:.2f} (para presentes)")
        print(f"📖 Revistas/Bíblias individuais: {individual_revista_display:.1f} (para presentes)")
    
    # Fazer chamada para a API
    try:
        url = f"{BASE_URL}/attendance/bulk/{TURMA_ID}?data={date_str}"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, headers=headers, json=bulk_attendance)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ {result['message']}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao registrar presença: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Detalhes: {e.response.text}")
        return False

def main():
    """Função principal"""
    print("🎓 Sistema EBD Manager - Registro de Presença Histórica")
    print("=" * 60)
    
    # Buscar estudantes
    name_to_id = get_students()
    if not name_to_id:
        print("❌ Não foi possível buscar os estudantes. Abortando.")
        sys.exit(1)
    
    print(f"\n📋 Mapeamento de nomes (primeiros 5):")
    for i, (nome, student_id) in enumerate(name_to_id.items()):
        if i < 5:
            print(f"   • {nome} -> {student_id}")
        else:
            break
    print(f"   ... e mais {len(name_to_id) - 5} estudantes")
    
    # Registrar presenças para cada dia
    success_count = 0
    for dia in attendance_data["dias"]:
        success = register_attendance_for_date(
            dia["data"], 
            dia["presencas"], 
            dia["revista_biblia"], 
            dia["oferta"],
            name_to_id
        )
        if success:
            success_count += 1
    
    print(f"\n🎉 Processo concluído!")
    print(f"   ✅ {success_count}/{len(attendance_data['dias'])} datas registradas com sucesso")
    
    if success_count == len(attendance_data["dias"]):
        print("   🎊 Todos os dados foram registrados com sucesso!")
    else:
        print("   ⚠️  Alguns registros falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()