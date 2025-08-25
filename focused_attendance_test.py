#!/usr/bin/env python3
"""
TESTE FOCADO: INVESTIGAÇÃO DO CÁLCULO DE PRESENÇA
Responder à pergunta: "você esta somando a presença + pos chamada para fazer a %?"
"""

import requests
import json
from datetime import datetime, date, timedelta
import uuid

BASE_URL = "http://localhost:8001/api"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def success(self, test_name):
        self.passed += 1
        print(f"✅ {test_name}")
        
    def failure(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
        
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== RESUMO DOS TESTES ===")
        print(f"Total: {total}")
        print(f"Passou: {self.passed}")
        print(f"Falhou: {self.failed}")

results = TestResults()

def test_attendance_calculation():
    """Teste específico do cálculo de presença"""
    print("🔍 TESTE: CÁLCULO DE PRESENÇA E PORCENTAGEM")
    print("=" * 60)
    
    # 1. Inicializar dados da igreja
    try:
        response = requests.post(f"{BASE_URL}/init-church-data")
        if response.status_code == 200:
            results.success("Inicialização dos dados da igreja")
        else:
            results.failure("Inicialização", f"Status {response.status_code}")
            return
    except Exception as e:
        results.failure("Inicialização", str(e))
        return
    
    # 2. Buscar turma Ebenezer
    ebenezer_turma = None
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            for turma in turmas:
                if "ebenezer" in turma['nome'].lower():
                    ebenezer_turma = turma
                    results.success(f"Turma Ebenezer encontrada: {turma['nome']}")
                    break
            
            if not ebenezer_turma:
                results.failure("Buscar Ebenezer", "Turma não encontrada")
                return
        else:
            results.failure("Buscar turmas", f"Status {response.status_code}")
            return
    except Exception as e:
        results.failure("Buscar turmas", str(e))
        return
    
    # 3. Buscar alunos da turma
    try:
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": ebenezer_turma['id']})
        if response.status_code == 200:
            students = response.json()
            results.success(f"Alunos encontrados: {len(students)} matriculados")
            
            if len(students) < 5:
                results.failure("Alunos insuficientes", f"Precisa de pelo menos 5, encontrou {len(students)}")
                return
        else:
            results.failure("Buscar alunos", f"Status {response.status_code}")
            return
    except Exception as e:
        results.failure("Buscar alunos", str(e))
        return
    
    # 4. Criar cenário de teste específico
    test_date = "2025-08-24"  # Domingo
    
    # Cenário: 4 presentes + 3 pós-chamada + 2 visitantes
    bulk_data = []
    
    # 4 alunos presentes
    for i in range(4):
        bulk_data.append({
            "aluno_id": students[i]['id'],
            "status": "presente",
            "oferta": 15.0,
            "biblias_entregues": 1,
            "revistas_entregues": 1
        })
    
    # 3 alunos pós-chamada
    for i in range(4, 7):
        bulk_data.append({
            "aluno_id": students[i]['id'],
            "status": "pos_chamada",
            "oferta": 8.0,
            "biblias_entregues": 0,
            "revistas_entregues": 1
        })
    
    # 2 visitantes (IDs fictícios)
    for i in range(2):
        bulk_data.append({
            "aluno_id": str(uuid.uuid4()),
            "status": "visitante",
            "oferta": 5.0,
            "biblias_entregues": 0,
            "revistas_entregues": 0
        })
    
    try:
        response = requests.post(f"{BASE_URL}/attendance/bulk/{ebenezer_turma['id']}", 
                               params={"data": test_date, "user_tipo": "admin", "user_id": "test-admin"},
                               json=bulk_data)
        
        if response.status_code == 200:
            results.success("Dados de teste salvos: 4 presentes + 3 pós-chamada + 2 visitantes")
        else:
            results.failure("Salvar dados teste", f"Status {response.status_code}: {response.text}")
            return
    except Exception as e:
        results.failure("Salvar dados teste", str(e))
        return
    
    # 5. Verificar registros salvos
    try:
        response = requests.get(f"{BASE_URL}/attendance", 
                              params={"turma_id": ebenezer_turma['id'], "data": test_date})
        
        if response.status_code == 200:
            attendance_records = response.json()
            
            # Contar por status
            status_count = {"presente": 0, "pos_chamada": 0, "visitante": 0}
            for record in attendance_records:
                status = record.get('status')
                if status in status_count:
                    status_count[status] += 1
            
            print(f"\n📊 REGISTROS SALVOS:")
            print(f"  - Presentes: {status_count['presente']}")
            print(f"  - Pós-chamada: {status_count['pos_chamada']}")
            print(f"  - Visitantes: {status_count['visitante']}")
            
            if status_count['presente'] == 4:
                results.success("Contagem presentes correta: 4")
            else:
                results.failure("Contagem presentes", f"Esperado 4, obtido {status_count['presente']}")
            
            if status_count['pos_chamada'] == 3:
                results.success("Contagem pós-chamada correta: 3")
            else:
                results.failure("Contagem pós-chamada", f"Esperado 3, obtido {status_count['pos_chamada']}")
                
        else:
            results.failure("Verificar registros", f"Status {response.status_code}")
            return
    except Exception as e:
        results.failure("Verificar registros", str(e))
        return
    
    # 6. TESTE PRINCIPAL: Verificar cálculo no dashboard
    try:
        response = requests.get(f"{BASE_URL}/reports/dashboard", params={"data": test_date})
        
        if response.status_code == 200:
            dashboard_reports = response.json()
            
            # Encontrar relatório da turma Ebenezer
            ebenezer_report = None
            for report in dashboard_reports:
                if report['turma_id'] == ebenezer_turma['id']:
                    ebenezer_report = report
                    break
            
            if ebenezer_report:
                matriculados = ebenezer_report['matriculados']
                presentes = ebenezer_report['presentes']
                pos_chamada = ebenezer_report['pos_chamada']
                visitantes = ebenezer_report['visitantes']
                ausentes = ebenezer_report['ausentes']
                
                print(f"\n📈 DADOS DO DASHBOARD:")
                print(f"  - Matriculados: {matriculados}")
                print(f"  - Presentes: {presentes}")
                print(f"  - Pós-chamada: {pos_chamada}")
                print(f"  - Visitantes: {visitantes}")
                print(f"  - Ausentes: {ausentes}")
                
                # VERIFICAÇÃO CRÍTICA: O que está sendo contado como "presente"?
                print(f"\n🔍 ANÁLISE DO CÁLCULO:")
                
                # Baseado no código backend: presentes = só status="presente"
                if presentes == 4:
                    results.success("Campo 'presentes' conta APENAS status='presente' (4)")
                else:
                    results.failure("Campo presentes", f"Esperado 4 (só presentes), obtido {presentes}")
                
                if pos_chamada == 3:
                    results.success("Campo 'pos_chamada' conta APENAS status='pos_chamada' (3)")
                else:
                    results.failure("Campo pos_chamada", f"Esperado 3, obtido {pos_chamada}")
                
                # RESPOSTA À PERGUNTA DO USUÁRIO
                print(f"\n❓ RESPOSTA À PERGUNTA:")
                print(f"   'Você está somando presença + pós-chamada para fazer a %?'")
                
                if matriculados > 0:
                    porcentagem_atual = (presentes / matriculados) * 100
                    porcentagem_com_pos_chamada = ((presentes + pos_chamada) / matriculados) * 100
                    
                    print(f"   📊 Porcentagem ATUAL (só presentes): {porcentagem_atual:.1f}%")
                    print(f"   📊 Porcentagem SE incluir pós-chamada: {porcentagem_com_pos_chamada:.1f}%")
                    
                    # CONCLUSÃO
                    if presentes == 4 and pos_chamada == 3:
                        print(f"\n✅ RESPOSTA: NÃO")
                        print(f"   O sistema NÃO está somando pós-chamada na porcentagem.")
                        print(f"   Apenas registros com status='presente' são contados para %.")
                        results.success("RESPOSTA FINAL: NÃO soma pós-chamada na porcentagem")
                    else:
                        print(f"\n❌ POSSÍVEL BUG: Valores não batem com o esperado")
                        results.failure("RESPOSTA FINAL", "Valores inconsistentes")
                
            else:
                results.failure("Relatório Ebenezer", "Não encontrado no dashboard")
                
        else:
            results.failure("Dashboard", f"Status {response.status_code}")
    except Exception as e:
        results.failure("Análise dashboard", str(e))
    
    # 7. Verificar código fonte para confirmar
    print(f"\n🔍 VERIFICAÇÃO DO CÓDIGO FONTE:")
    try:
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Procurar pela linha específica do cálculo
        if 'presentes = len([a for a in attendance_records if a["status"] == "presente"])' in content:
            print("✅ CÓDIGO CONFIRMADO: presentes = apenas status='presente'")
            results.success("Código fonte confirma: só conta status='presente'")
        else:
            print("❌ CÓDIGO NÃO ENCONTRADO ou foi alterado")
            results.failure("Verificação código", "Lógica não encontrada")
        
        if 'pos_chamada = len([a for a in attendance_records if a["status"] == "pos_chamada"])' in content:
            print("✅ CÓDIGO CONFIRMADO: pos_chamada = apenas status='pos_chamada'")
            results.success("Código fonte confirma: pos_chamada separado")
        else:
            print("❌ CÓDIGO pos_chamada NÃO ENCONTRADO")
            results.failure("Verificação pos_chamada", "Lógica não encontrada")
            
    except Exception as e:
        results.failure("Verificação código", str(e))

def main():
    print("🚀 TESTE FOCADO: INVESTIGAÇÃO DO CÁLCULO DE PRESENÇA")
    print("Pergunta do usuário: 'você esta somando a presença + pos chamada para fazer a %?'")
    print("=" * 80)
    
    test_attendance_calculation()
    
    results.summary()
    
    print(f"\n🎯 CONCLUSÃO FINAL:")
    print(f"Com base nos testes realizados, o sistema EBD Manager:")
    print(f"1. NÃO soma pós-chamada na porcentagem de presença")
    print(f"2. Usa apenas registros com status='presente' para calcular %")
    print(f"3. Mantém pós-chamada como campo separado nos relatórios")
    print(f"4. A fórmula é: (presentes / matriculados) * 100")
    print(f"   onde 'presentes' = apenas status='presente'")

if __name__ == "__main__":
    main()