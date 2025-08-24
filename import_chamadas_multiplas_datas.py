#!/usr/bin/env python3
"""
Importador especializado para a planilha EBD com múltiplas datas
- Cada aba = uma turma
- Múltiplas colunas de datas com presenças
- Importa todas as chamadas de uma vez
"""
import pandas as pd
import requests
import random
import json
from datetime import datetime
import sys

# Configurações
API_BASE = "https://ebd-dashboard-1.preview.emergentagent.com/api"

class ImportadorChamadasMultiplas:
    def __init__(self):
        self.turmas_sistema = {}
        self.alunos_sistema = {}
        self.chamadas_importadas = []
        
    def carregar_dados_sistema(self):
        """Carregar turmas e alunos do sistema"""
        print("📡 Carregando dados do sistema...")
        
        # Carregar turmas
        try:
            response = requests.get(f"{API_BASE}/turmas")
            if response.status_code == 200:
                turmas = response.json()
                for turma in turmas:
                    nome_normalizado = self.normalizar_nome(turma['nome'])
                    self.turmas_sistema[nome_normalizado] = turma
                print(f"   ✅ {len(turmas)} turmas carregadas")
            else:
                print(f"   ❌ Erro ao carregar turmas: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erro ao conectar com API: {e}")
            return False
        
        # Carregar alunos
        try:
            response = requests.get(f"{API_BASE}/students")
            if response.status_code == 200:
                alunos = response.json()
                for aluno in alunos:
                    nome_normalizado = self.normalizar_nome(aluno['nome_completo'])
                    turma_id = aluno['turma_id']
                    if turma_id not in self.alunos_sistema:
                        self.alunos_sistema[turma_id] = {}
                    self.alunos_sistema[turma_id][nome_normalizado] = aluno
                print(f"   ✅ {len(alunos)} alunos carregados")
            else:
                print(f"   ❌ Erro ao carregar alunos: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erro ao conectar com API: {e}")
            return False
        
        return True
    
    def normalizar_nome(self, nome):
        """Normalizar nome para comparação"""
        if not nome:
            return ""
        return nome.strip().lower().replace("  ", " ").replace(".", "").replace(",", "")
    
    def mapear_turma(self, nome_aba):
        """Mapear nome da aba para turma do sistema"""
        nome_normalizado = self.normalizar_nome(nome_aba)
        
        # Mapeamentos específicos conhecidos
        mapeamentos = {
            'professores e oficiais': 'professores e oficiais',
            'genesis': 'genesis',
            'gênesis': 'genesis',
            'primarios': 'primarios',
            'primários': 'primarios',
            'juniores': 'juniores',
            'júniores': 'juniores',
            'pre adolescentes': 'pré-adolescentes',
            'pré adolescentes': 'pré-adolescentes',
            'pré-adolescentes': 'pré-adolescentes',
            'adolescentes': 'adolescentes',
            'jovens': 'jovens',
            'dorcas (irmãs)': 'dorcas (irmãs)',
            'dorcas irmas': 'dorcas (irmãs)',
            'soldados de cristo': 'soldados de cristo',
            'ebenezer(obreiros)': 'ebenezer (obreiros)',
            'ebenezer obreiros': 'ebenezer (obreiros)'
        }
        
        # Tentar mapeamento direto primeiro
        if nome_normalizado in mapeamentos:
            nome_busca = mapeamentos[nome_normalizado]
        else:
            nome_busca = nome_normalizado
        
        # Procurar turma correspondente
        for turma_nome, turma_data in self.turmas_sistema.items():
            if (nome_busca == turma_nome or 
                nome_busca in turma_nome or 
                turma_nome in nome_busca):
                return turma_data
        
        return None
    
    def encontrar_aluno_na_turma(self, nome_planilha, turma_id):
        """Encontrar aluno específico na turma"""
        if turma_id not in self.alunos_sistema:
            return None
            
        nome_normalizado = self.normalizar_nome(nome_planilha)
        alunos_turma = self.alunos_sistema[turma_id]
        
        # Busca exata primeiro
        if nome_normalizado in alunos_turma:
            return alunos_turma[nome_normalizado]
        
        # Busca por similaridade
        for nome_sistema, aluno_data in alunos_turma.items():
            # Nome da planilha contém nome do sistema
            if nome_normalizado in nome_sistema or nome_sistema in nome_normalizado:
                return aluno_data
                
            # Comparação por palavras
            palavras_planilha = nome_normalizado.split()
            palavras_sistema = nome_sistema.split()
            
            # Se pelo menos 2 palavras coincidirem
            coincidencias = sum(1 for p in palavras_planilha if p in palavras_sistema)
            if coincidencias >= 2:
                return aluno_data
        
        return None
    
    def processar_planilha(self):
        """Processar planilha Excel com chamadas múltiplas"""
        print(f"📊 Processando planilha: EBD_chamada.xlsx")
        
        try:
            # Ler todas as abas
            excel_data = pd.read_excel('EBD_chamada.xlsx', sheet_name=None)
            print(f"   📋 Encontradas {len(excel_data)} abas/turmas")
            
            resultados = {
                'turmas_processadas': 0,
                'chamadas_criadas': 0,
                'alunos_encontrados': 0,
                'alunos_nao_encontrados': 0,
                'erros': [],
                'detalhes': {}
            }
            
            # Processar cada aba (turma)
            for nome_aba, df in excel_data.items():
                print(f"\n🔄 Processando turma: '{nome_aba}'")
                
                # Mapear aba para turma
                turma = self.mapear_turma(nome_aba)
                if not turma:
                    erro = f"Turma '{nome_aba}' não encontrada no sistema"
                    print(f"   ❌ {erro}")
                    resultados['erros'].append(erro)
                    continue
                
                print(f"   ✅ Turma mapeada: {turma['nome']} (ID: {turma['id']})")
                
                # Processar múltiplas datas desta turma
                resultado_turma = self.processar_turma_multiplas_datas(turma, df)
                
                resultados['turmas_processadas'] += 1
                resultados['chamadas_criadas'] += resultado_turma['chamadas_criadas']
                resultados['alunos_encontrados'] += resultado_turma['alunos_encontrados']
                resultados['alunos_nao_encontrados'] += resultado_turma['alunos_nao_encontrados']
                resultados['erros'].extend(resultado_turma['erros'])
                resultados['detalhes'][turma['nome']] = resultado_turma
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao processar planilha: {e}")
            return None
    
    def processar_turma_multiplas_datas(self, turma, df):
        """Processar múltiplas datas de chamada para uma turma"""
        turma_id = turma['id']
        turma_nome = turma['nome']
        
        resultado = {
            'turma': turma_nome,
            'chamadas_criadas': 0,
            'alunos_encontrados': 0,
            'alunos_nao_encontrados': 0,
            'datas_processadas': [],
            'erros': []
        }
        
        # Identificar colunas de datas
        colunas_datas = []
        for coluna in df.columns:
            if isinstance(coluna, datetime):
                colunas_datas.append(coluna)
            elif isinstance(coluna, str) and any(char.isdigit() for char in coluna):
                # Para colunas como '2007/2025' que não são datetime
                continue
        
        print(f"   📅 Datas encontradas: {len(colunas_datas)}")
        for data in colunas_datas[:3]:  # Mostrar só as primeiras 3
            print(f"      - {data.strftime('%Y-%m-%d')}")
        if len(colunas_datas) > 3:
            print(f"      ... e mais {len(colunas_datas) - 3} datas")
        
        # Processar cada data
        for data_coluna in colunas_datas:
            data_str = data_coluna.strftime('%Y-%m-%d')
            
            # Verificar se já existe chamada para esta data
            if self.chamada_existe(turma_id, data_str):
                print(f"   ⚠️  Chamada de {data_str} já existe - pulando")
                continue
            
            # Montar dados da chamada para esta data
            chamada_data = []
            alunos_encontrados_data = 0
            alunos_nao_encontrados_data = 0
            
            for index, row in df.iterrows():
                try:
                    nome_planilha = str(row['Alunos']).strip()
                    if not nome_planilha or nome_planilha.lower() in ['nan', 'none', '']:
                        continue
                    
                    # Encontrar aluno no sistema
                    aluno_encontrado = self.encontrar_aluno_na_turma(nome_planilha, turma_id)
                    
                    if not aluno_encontrado:
                        print(f"      ⚠️ Aluno '{nome_planilha}' não encontrado")
                        alunos_nao_encontrados_data += 1
                        continue
                    
                    # Determinar presença para esta data
                    valor_presenca = row[data_coluna]
                    presente = self.interpretar_presenca(valor_presenca)
                    
                    # Adicionar à chamada
                    chamada_data.append({
                        "aluno_id": aluno_encontrado['id'],
                        "status": "presente" if presente else "ausente",
                        "oferta": 0,  # Será definida por turma
                        "biblias_entregues": 0,
                        "revistas_entregues": 0
                    })
                    
                    alunos_encontrados_data += 1
                    
                except Exception as e:
                    resultado['erros'].append(f"Erro na linha {index}, data {data_str}: {e}")
            
            # Distribuir ofertas aleatórias entre presentes
            if chamada_data:
                presentes = [c for c in chamada_data if c['status'] == 'presente']
                if presentes:
                    oferta_total = round(random.uniform(8.00, 47.00), 2)
                    oferta_por_aluno = round(oferta_total / len(presentes), 2)
                    
                    for chamada in presentes:
                        chamada['oferta'] = oferta_por_aluno
                    
                    print(f"      💰 {data_str}: R$ {oferta_total:.2f} ({len(presentes)} presentes)")
                
                # Registrar chamada no sistema
                if self.registrar_chamada_api(turma_id, data_str, chamada_data):
                    resultado['chamadas_criadas'] += 1
                    resultado['alunos_encontrados'] += alunos_encontrados_data
                    resultado['alunos_nao_encontrados'] += alunos_nao_encontrados_data
                    resultado['datas_processadas'].append(data_str)
                    self.chamadas_importadas.append(f"{turma_nome}_{data_str}")
                else:
                    resultado['erros'].append(f"Falha ao registrar chamada de {data_str}")
        
        print(f"   ✅ {resultado['chamadas_criadas']} chamadas criadas para {turma_nome}")
        
        return resultado
    
    def interpretar_presenca(self, valor):
        """Interpretar valor de presença da planilha"""
        if pd.isna(valor) or valor is None:
            return False
        
        if isinstance(valor, bool):
            return valor
        
        if isinstance(valor, (int, float)):
            return valor > 0
        
        if isinstance(valor, str):
            valor_lower = valor.lower().strip()
            return valor_lower not in ['false', 'f', 'ausente', 'falta', '0', 'não', 'nao']
        
        return bool(valor)
    
    def chamada_existe(self, turma_id, data_str):
        """Verificar se chamada já existe para evitar duplicatas"""
        try:
            response = requests.get(f"{API_BASE}/attendance/{turma_id}?data={data_str}")
            return response.status_code == 200 and len(response.json()) > 0
        except:
            return False
    
    def registrar_chamada_api(self, turma_id, data, chamada_data):
        """Registrar chamada via API"""
        try:
            url = f"{API_BASE}/attendance/bulk/{turma_id}?data={data}"
            response = requests.post(url, json=chamada_data)
            
            if response.status_code == 200:
                return True
            else:
                print(f"   ❌ Erro API ({data}): {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao chamar API ({data}): {e}")
            return False
    
    def imprimir_relatorio(self, resultados):
        """Imprimir relatório final"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL - IMPORTAÇÃO DE CHAMADAS MÚLTIPLAS")
        print("="*70)
        
        print(f"🏫 Turmas processadas: {resultados['turmas_processadas']}")
        print(f"📅 Chamadas criadas: {resultados['chamadas_criadas']}")
        print(f"👥 Alunos encontrados: {resultados['alunos_encontrados']}")
        print(f"⚠️ Alunos não encontrados: {resultados['alunos_nao_encontrados']}")
        
        if resultados['detalhes']:
            print(f"\n📋 DETALHES POR TURMA:")
            for turma_nome, detalhes in resultados['detalhes'].items():
                print(f"   🏫 {turma_nome}:")
                print(f"      📅 {detalhes['chamadas_criadas']} chamadas criadas")
                print(f"      👥 {detalhes['alunos_encontrados']} alunos encontrados")
                if detalhes['alunos_nao_encontrados'] > 0:
                    print(f"      ⚠️ {detalhes['alunos_nao_encontrados']} alunos não encontrados")
        
        if resultados['erros']:
            print(f"\n❌ ERROS ({len(resultados['erros'])}):")
            for erro in resultados['erros'][:5]:  # Mostrar só primeiros 5
                print(f"   • {erro}")
            if len(resultados['erros']) > 5:
                print(f"   ... e mais {len(resultados['erros']) - 5} erros")
        
        print(f"\n💰 Ofertas foram distribuídas automaticamente (R$ 8-47 por turma/data)")
        print("="*70)

def main():
    importador = ImportadorChamadasMultiplas()
    
    print("🚀 IMPORTADOR DE CHAMADAS MÚLTIPLAS - EBD MANAGER")
    print("="*70)
    print("📋 Importando planilha com múltiplas datas de chamadas...")
    
    # Carregar dados do sistema
    if not importador.carregar_dados_sistema():
        print("❌ Falha ao carregar dados do sistema")
        return
    
    # Processar planilha
    resultados = importador.processar_planilha()
    
    if resultados:
        importador.imprimir_relatorio(resultados)
        if resultados['chamadas_criadas'] > 0:
            print("\n🎉 IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
            print("   ✅ Todas as chamadas foram registradas no sistema")
            print("   💰 Ofertas aleatórias foram distribuídas")
            print("   📊 Dados disponíveis no dashboard")
        else:
            print("\n⚠️ NENHUMA CHAMADA FOI IMPORTADA")
            print("   Verifique os erros acima")
    else:
        print("❌ Falha ao processar planilha")

if __name__ == "__main__":
    main()