#!/usr/bin/env python3
"""
INVESTIGAÇÃO DO CÁLCULO DE PRESENÇA NOS RELATÓRIOS

PERGUNTA DO USUÁRIO: "você esta somando a presença + pos chamada para fazer a %?"

INVESTIGAÇÃO NECESSÁRIA:
1. Verificar endpoint de relatórios detalhados
2. Como o backend calcula o campo `presentes` em `attendanceData`
3. Se está incluindo `pos_chamada` no cálculo de `presentes`
4. Quais status são considerados como "presente"
5. Testar com dados reais da turma Ebenezer
6. Verificar fórmula: (presentes / matriculados) * 100
"""

import requests
import json
from datetime import datetime, date, timedelta
import uuid

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=')[1].strip()
                    # If it's just /api, prepend localhost
                    if backend_url == '/api':
                        return "http://localhost:8001/api"
                    elif not backend_url.endswith('/api'):
                        backend_url = backend_url + '/api'
                    return backend_url
    except:
        pass
    return "http://localhost:8001/api"

BASE_URL = get_backend_url()
print(f"🔍 INVESTIGAÇÃO DE CÁLCULO DE PRESENÇA")
print(f"Backend URL: {BASE_URL}")
print("=" * 80)

class InvestigationResults:
    def __init__(self):
        self.findings = []
        self.errors = []
        
    def add_finding(self, title, details):
        self.findings.append(f"✅ {title}: {details}")
        print(f"✅ {title}: {details}")
        
    def add_error(self, title, error):
        self.errors.append(f"❌ {title}: {error}")
        print(f"❌ {title}: {error}")
        
    def summary(self):
        print("\n" + "=" * 80)
        print("📋 RESUMO DA INVESTIGAÇÃO")
        print("=" * 80)
        for finding in self.findings:
            print(finding)
        if self.errors:
            print("\n🚨 ERROS ENCONTRADOS:")
            for error in self.errors:
                print(error)

results = InvestigationResults()

def investigate_attendance_calculation():
    """Investigar como o cálculo de presença está sendo feito"""
    
    print("\n🔍 ETAPA 1: VERIFICAR ENDPOINTS DISPONÍVEIS")
    print("-" * 50)
    
    # Verificar se existe endpoint de relatórios detalhados
    try:
        response = requests.get(f"{BASE_URL}/reports/detailed", params={"data": "2025-08-24"})
        if response.status_code == 200:
            results.add_finding("Endpoint /api/reports/detailed", "EXISTE e responde")
            detailed_data = response.json()
            print(f"Estrutura dos dados detalhados: {list(detailed_data.keys()) if isinstance(detailed_data, dict) else 'Lista com ' + str(len(detailed_data)) + ' itens'}")
        elif response.status_code == 404:
            results.add_finding("Endpoint /api/reports/detailed", "NÃO EXISTE - usando /api/reports/dashboard")
        else:
            results.add_error("Endpoint /api/reports/detailed", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.add_error("Endpoint /api/reports/detailed", str(e))
    
    print("\n🔍 ETAPA 2: INICIALIZAR DADOS DA IGREJA")
    print("-" * 50)
    
    # Garantir que temos dados da igreja
    try:
        response = requests.post(f"{BASE_URL}/init-church-data")
        if response.status_code == 200:
            church_data = response.json()
            results.add_finding("Dados da igreja", f"Inicializados: {church_data.get('turmas', 0)} turmas, {church_data.get('alunos', 0)} alunos")
        else:
            results.add_error("Inicialização dados igreja", f"Status {response.status_code}")
    except Exception as e:
        results.add_error("Inicialização dados igreja", str(e))
    
    print("\n🔍 ETAPA 3: ENCONTRAR TURMA EBENEZER")
    print("-" * 50)
    
    # Buscar turma Ebenezer especificamente
    ebenezer_turma = None
    try:
        response = requests.get(f"{BASE_URL}/turmas")
        if response.status_code == 200:
            turmas = response.json()
            results.add_finding("Total de turmas", f"{len(turmas)} turmas encontradas")
            
            # Procurar Ebenezer
            for turma in turmas:
                if "ebenezer" in turma['nome'].lower() or "obreiros" in turma['nome'].lower():
                    ebenezer_turma = turma
                    results.add_finding("Turma Ebenezer encontrada", f"Nome: '{turma['nome']}', ID: {turma['id']}")
                    break
            
            if not ebenezer_turma:
                results.add_error("Turma Ebenezer", "NÃO ENCONTRADA nas turmas disponíveis")
                print("Turmas disponíveis:")
                for turma in turmas[:10]:  # Mostrar primeiras 10
                    print(f"  - {turma['nome']}")
        else:
            results.add_error("Buscar turmas", f"Status {response.status_code}")
    except Exception as e:
        results.add_error("Buscar turmas", str(e))
    
    if not ebenezer_turma:
        print("❌ Não é possível continuar sem a turma Ebenezer")
        return
    
    print("\n🔍 ETAPA 4: BUSCAR ALUNOS DA TURMA EBENEZER")
    print("-" * 50)
    
    # Buscar alunos da turma Ebenezer
    ebenezer_students = []
    try:
        response = requests.get(f"{BASE_URL}/students", params={"turma_id": ebenezer_turma['id']})
        if response.status_code == 200:
            ebenezer_students = response.json()
            results.add_finding("Alunos Ebenezer", f"{len(ebenezer_students)} alunos matriculados")
            
            # Mostrar alguns nomes
            if ebenezer_students:
                print("Primeiros alunos da turma Ebenezer:")
                for student in ebenezer_students[:5]:
                    print(f"  - {student['nome_completo']}")
        else:
            results.add_error("Buscar alunos Ebenezer", f"Status {response.status_code}")
    except Exception as e:
        results.add_error("Buscar alunos Ebenezer", str(e))
    
    print("\n🔍 ETAPA 5: CRIAR DADOS DE TESTE COM DIFERENTES STATUS")
    print("-" * 50)
    
    # Criar dados de teste para investigar o cálculo
    test_date = "2025-08-24"  # Data específica da investigação
    
    if ebenezer_students and len(ebenezer_students) >= 6:
        try:
            # Criar cenário de teste:
            # - 3 alunos com status "presente"
            # - 2 alunos com status "pos_chamada" 
            # - 1 aluno com status "visitante"
            # Total: 6 registros
            
            bulk_data = []
            
            # 3 presentes
            for i in range(3):
                bulk_data.append({
                    "aluno_id": ebenezer_students[i]['id'],
                    "status": "presente",
                    "oferta": 10.0,
                    "biblias_entregues": 1,
                    "revistas_entregues": 1
                })
            
            # 2 pós-chamada
            for i in range(3, 5):
                bulk_data.append({
                    "aluno_id": ebenezer_students[i]['id'],
                    "status": "pos_chamada",
                    "oferta": 5.0,
                    "biblias_entregues": 0,
                    "revistas_entregues": 1
                })
            
            # 1 visitante (registro adicional, não é aluno matriculado)
            bulk_data.append({
                "aluno_id": str(uuid.uuid4()),  # ID fictício para visitante
                "status": "visitante",
                "oferta": 2.0,
                "biblias_entregues": 0,
                "revistas_entregues": 0
            })
            
            # Salvar dados de teste
            response = requests.post(f"{BASE_URL}/attendance/bulk/{ebenezer_turma['id']}", 
                                   params={"data": test_date, "user_tipo": "admin", "user_id": "test-admin"},
                                   json=bulk_data)
            
            if response.status_code == 200:
                results.add_finding("Dados de teste criados", f"6 registros salvos para {test_date}")
                print(f"Cenário criado:")
                print(f"  - 3 alunos com status 'presente'")
                print(f"  - 2 alunos com status 'pos_chamada'")
                print(f"  - 1 registro com status 'visitante'")
            else:
                results.add_error("Criar dados de teste", f"Status {response.status_code}: {response.text}")
                return
                
        except Exception as e:
            results.add_error("Criar dados de teste", str(e))
            return
    else:
        results.add_error("Dados de teste", "Não há alunos suficientes na turma Ebenezer")
        return
    
    print("\n🔍 ETAPA 6: VERIFICAR REGISTROS SALVOS")
    print("-" * 50)
    
    # Verificar os registros que foram salvos
    try:
        response = requests.get(f"{BASE_URL}/attendance", 
                              params={"turma_id": ebenezer_turma['id'], "data": test_date})
        
        if response.status_code == 200:
            attendance_records = response.json()
            results.add_finding("Registros salvos", f"{len(attendance_records)} registros encontrados")
            
            # Contar por status
            status_count = {}
            for record in attendance_records:
                status = record.get('status', 'unknown')
                status_count[status] = status_count.get(status, 0) + 1
            
            print("Contagem por status:")
            for status, count in status_count.items():
                print(f"  - {status}: {count}")
                results.add_finding(f"Status '{status}'", f"{count} registros")
                
        else:
            results.add_error("Verificar registros", f"Status {response.status_code}")
    except Exception as e:
        results.add_error("Verificar registros", str(e))
    
    print("\n🔍 ETAPA 7: ANALISAR CÁLCULO NO DASHBOARD")
    print("-" * 50)
    
    # Verificar como o dashboard calcula os dados
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
                results.add_finding("Relatório Ebenezer encontrado", "Dados do dashboard obtidos")
                
                # Analisar os campos
                matriculados = ebenezer_report['matriculados']
                presentes = ebenezer_report['presentes']
                pos_chamada = ebenezer_report['pos_chamada']
                visitantes = ebenezer_report['visitantes']
                ausentes = ebenezer_report['ausentes']
                
                print(f"📊 DADOS DO DASHBOARD PARA EBENEZER:")
                print(f"  - Matriculados: {matriculados}")
                print(f"  - Presentes: {presentes}")
                print(f"  - Pós-chamada: {pos_chamada}")
                print(f"  - Visitantes: {visitantes}")
                print(f"  - Ausentes: {ausentes}")
                
                results.add_finding("Matriculados", str(matriculados))
                results.add_finding("Presentes (campo)", str(presentes))
                results.add_finding("Pós-chamada (campo)", str(pos_chamada))
                results.add_finding("Visitantes (campo)", str(visitantes))
                results.add_finding("Ausentes (campo)", str(ausentes))
                
                # ANÁLISE CRÍTICA: O que está sendo contado como "presente"?
                print(f"\n🔍 ANÁLISE CRÍTICA:")
                
                # Baseado no código do backend (linha 561):
                # presentes = len([a for a in attendance_records if a["status"] == "presente"])
                expected_presentes = 3  # Apenas os com status "presente"
                expected_pos_chamada = 2  # Os com status "pos_chamada"
                expected_visitantes = 1  # Os com status "visitante"
                
                print(f"  - ESPERADO baseado no código:")
                print(f"    * Presentes (só status='presente'): {expected_presentes}")
                print(f"    * Pós-chamada (status='pos_chamada'): {expected_pos_chamada}")
                print(f"    * Visitantes (status='visitante'): {expected_visitantes}")
                
                print(f"  - OBTIDO do dashboard:")
                print(f"    * Presentes: {presentes}")
                print(f"    * Pós-chamada: {pos_chamada}")
                print(f"    * Visitantes: {visitantes}")
                
                # Verificar se os valores batem
                if presentes == expected_presentes:
                    results.add_finding("Cálculo 'presentes'", "CORRETO - só conta status='presente'")
                else:
                    results.add_error("Cálculo 'presentes'", f"INCORRETO - esperado {expected_presentes}, obtido {presentes}")
                
                if pos_chamada == expected_pos_chamada:
                    results.add_finding("Cálculo 'pos_chamada'", "CORRETO - conta status='pos_chamada'")
                else:
                    results.add_error("Cálculo 'pos_chamada'", f"INCORRETO - esperado {expected_pos_chamada}, obtido {pos_chamada}")
                
                # PERGUNTA PRINCIPAL: A porcentagem inclui pós-chamada?
                print(f"\n❓ RESPOSTA À PERGUNTA DO USUÁRIO:")
                print(f"   'Você está somando presença + pós-chamada para fazer a %?'")
                
                # Calcular porcentagem atual
                if matriculados > 0:
                    porcentagem_atual = (presentes / matriculados) * 100
                    porcentagem_com_pos_chamada = ((presentes + pos_chamada) / matriculados) * 100
                    
                    print(f"   - Porcentagem ATUAL (só presentes): {porcentagem_atual:.1f}%")
                    print(f"   - Porcentagem SE incluir pós-chamada: {porcentagem_com_pos_chamada:.1f}%")
                    
                    results.add_finding("Porcentagem atual", f"{porcentagem_atual:.1f}% (só presentes)")
                    results.add_finding("Porcentagem se incluir pós-chamada", f"{porcentagem_com_pos_chamada:.1f}%")
                    
                    if presentes == expected_presentes:
                        results.add_finding("RESPOSTA", "NÃO - pós-chamada NÃO está sendo incluída na porcentagem")
                    else:
                        results.add_error("RESPOSTA", "POSSÍVEL BUG - valores não batem com o esperado")
                
            else:
                results.add_error("Relatório Ebenezer", "Não encontrado no dashboard")
                
        else:
            results.add_error("Dashboard", f"Status {response.status_code}")
    except Exception as e:
        results.add_error("Análise dashboard", str(e))
    
    print("\n🔍 ETAPA 8: VERIFICAR CÓDIGO DO BACKEND")
    print("-" * 50)
    
    # Analisar o código do backend para confirmar a lógica
    try:
        with open('/app/backend/server.py', 'r') as f:
            backend_code = f.read()
        
        # Procurar pela linha que calcula presentes
        if 'presentes = len([a for a in attendance_records if a["status"] == "presente"])' in backend_code:
            results.add_finding("Código backend", "CONFIRMADO - só conta status='presente' para presentes")
        else:
            results.add_error("Código backend", "Lógica de cálculo não encontrada ou foi alterada")
        
        # Procurar pela linha que calcula pos_chamada
        if 'pos_chamada = len([a for a in attendance_records if a["status"] == "pos_chamada"])' in backend_code:
            results.add_finding("Código backend", "CONFIRMADO - pos_chamada é calculado separadamente")
        else:
            results.add_error("Código backend", "Cálculo de pos_chamada não encontrado")
            
    except Exception as e:
        results.add_error("Análise código", str(e))
    
    print("\n🔍 ETAPA 9: TESTAR COM DADOS REAIS DE OUTRAS TURMAS")
    print("-" * 50)
    
    # Verificar se o padrão se repete em outras turmas
    try:
        response = requests.get(f"{BASE_URL}/reports/dashboard", params={"data": test_date})
        if response.status_code == 200:
            all_reports = response.json()
            
            print("Verificando padrão em todas as turmas:")
            for report in all_reports[:5]:  # Primeiras 5 turmas
                turma_nome = report['turma_nome']
                matriculados = report['matriculados']
                presentes = report['presentes']
                pos_chamada = report['pos_chamada']
                
                if matriculados > 0:
                    porcentagem = (presentes / matriculados) * 100
                    print(f"  - {turma_nome}: {presentes}/{matriculados} = {porcentagem:.1f}% (pós-chamada: {pos_chamada})")
                    
                    if pos_chamada > 0:
                        porcentagem_com_pos = ((presentes + pos_chamada) / matriculados) * 100
                        print(f"    * Se incluir pós-chamada: {porcentagem_com_pos:.1f}%")
                        
        else:
            results.add_error("Verificar outras turmas", f"Status {response.status_code}")
    except Exception as e:
        results.add_error("Verificar outras turmas", str(e))

def main():
    """Executar investigação completa"""
    print("🚀 INICIANDO INVESTIGAÇÃO DO CÁLCULO DE PRESENÇA")
    print("Pergunta: 'Você está somando presença + pós-chamada para fazer a %?'")
    print("=" * 80)
    
    investigate_attendance_calculation()
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÕES DA INVESTIGAÇÃO")
    print("=" * 80)
    
    results.summary()
    
    print("\n📝 RECOMENDAÇÕES:")
    print("1. Se o usuário QUER que pós-chamada seja incluída na %, o código precisa ser alterado")
    print("2. Se o comportamento atual está CORRETO, documentar claramente a lógica")
    print("3. Considerar adicionar uma configuração para escolher o comportamento")

if __name__ == "__main__":
    main()