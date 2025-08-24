#!/usr/bin/env python3
"""
Sistema de importação de chamadas via planilha Excel
- Cada aba representa uma turma
- Mapeia alunos e registra presenças
- Adiciona ofertas aleatórias por turma
"""
import pandas as pd
import requests
import random
import asyncio
import json
from datetime import datetime
import sys
import os

# Configurações
API_BASE = "https://sunday-bible.preview.emergentagent.com/api"

class ImportadorChamadas:
    def __init__(self):
        self.turmas_sistema = {}
        self.alunos_sistema = {}
        self.mapeamento_turmas = {}
        
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
        return nome.strip().lower().replace("  ", " ")
    
    def mapear_turma(self, nome_aba):
        """Mapear nome da aba para turma do sistema"""
        nome_normalizado = self.normalizar_nome(nome_aba)
        
        # Mapeamentos específicos conhecidos
        mapeamentos = {
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
            'dorcas': 'dorcas (irmãs)',
            'dorcas irmas': 'dorcas (irmãs)',
            'ebenezer': 'ebenezer(obreiros)',
            'soldados de cristo': 'soldados de cristo',
            'professores': 'professores e oficiais',
            'professores e oficiais': 'professores e oficiais'
        }
        
        # Tentar mapeamento direto
        if nome_normalizado in mapeamentos:
            nome_normalizado = mapeamentos[nome_normalizado]
        
        # Procurar turma correspondente
        for turma_nome, turma_data in self.turmas_sistema.items():
            if nome_normalizado == turma_nome or nome_normalizado in turma_nome:
                return turma_data
        
        return None
    
    def processar_planilha(self, caminho_arquivo, data_chamada):
        """Processar planilha Excel com chamadas"""
        print(f"📊 Processando planilha: {caminho_arquivo}")
        print(f"📅 Data da chamada: {data_chamada}")
        
        try:
            # Ler todas as abas
            excel_data = pd.read_excel(caminho_arquivo, sheet_name=None)
            print(f"   📋 Encontradas {len(excel_data)} abas")
            
            resultados = {
                'sucesso': [],
                'erros': [],
                'estatisticas': {}
            }
            
            # Processar cada aba (turma)
            for nome_aba, df in excel_data.items():
                print(f"\n🔄 Processando aba: '{nome_aba}'")
                
                # Mapear aba para turma
                turma = self.mapear_turma(nome_aba)
                if not turma:
                    erro = f"Turma '{nome_aba}' não encontrada no sistema"
                    print(f"   ❌ {erro}")
                    resultados['erros'].append(erro)
                    continue
                
                print(f"   ✅ Turma mapeada: {turma['nome']} (ID: {turma['id']})")
                
                # Processar chamada da turma
                resultado_turma = self.processar_chamada_turma(turma, df, data_chamada)
                
                if resultado_turma['sucesso']:
                    resultados['sucesso'].append(resultado_turma)
                else:
                    resultados['erros'].extend(resultado_turma['erros'])
                
                resultados['estatisticas'][turma['nome']] = resultado_turma['stats']
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao processar planilha: {e}")
            return None
    
    def processar_chamada_turma(self, turma, df, data_chamada):
        """Processar chamada de uma turma específica"""
        turma_id = turma['id']
        turma_nome = turma['nome']
        
        resultado = {
            'sucesso': False,
            'turma': turma_nome,
            'erros': [],
            'stats': {'presentes': 0, 'ausentes': 0, 'nao_encontrados': 0}
        }
        
        # Verificar se temos alunos desta turma
        if turma_id not in self.alunos_sistema:
            resultado['erros'].append(f"Nenhum aluno encontrado para turma {turma_nome}")
            return resultado
        
        alunos_turma = self.alunos_sistema[turma_id]
        chamada_data = []
        
        print(f"   👥 Alunos na turma: {len(alunos_turma)}")
        
        # Detectar colunas da planilha
        colunas = [col.lower().strip() for col in df.columns]
        print(f"   📋 Colunas da planilha: {colunas}")
        
        # Encontrar coluna de nome
        coluna_nome = None
        for col in ['nome', 'aluno', 'nome completo', 'nome_completo']:
            if col in colunas:
                coluna_nome = df.columns[colunas.index(col)]
                break
        
        if not coluna_nome:
            resultado['erros'].append(f"Coluna de nome não encontrada na aba {turma_nome}")
            return resultado
        
        # Encontrar coluna de presença
        coluna_presenca = None
        for col in ['presente', 'presenca', 'presença', 'status', 'p', 'chamada']:
            if col in colunas:
                coluna_presenca = df.columns[colunas.index(col)]
                break
        
        # Processar cada linha da planilha
        for index, row in df.iterrows():
            try:
                nome_planilha = str(row[coluna_nome]).strip()
                if not nome_planilha or nome_planilha.lower() in ['nan', 'none', '']:
                    continue
                
                nome_normalizado = self.normalizar_nome(nome_planilha)
                
                # Encontrar aluno no sistema
                aluno_encontrado = None
                for nome_sistema, aluno_data in alunos_turma.items():
                    if (nome_normalizado == nome_sistema or 
                        nome_normalizado in nome_sistema or 
                        nome_sistema in nome_normalizado):
                        aluno_encontrado = aluno_data
                        break
                
                if not aluno_encontrado:
                    print(f"   ⚠️  Aluno '{nome_planilha}' não encontrado no sistema")
                    resultado['stats']['nao_encontrados'] += 1
                    continue
                
                # Determinar presença
                presente = True  # Padrão: presente
                if coluna_presenca:
                    valor_presenca = str(row[coluna_presenca]).lower().strip()
                    presente = valor_presenca not in ['false', 'f', 'ausente', 'falta', '0', 'não', 'nao']
                
                # Adicionar à chamada
                chamada_data.append({
                    "aluno_id": aluno_encontrado['id'],
                    "status": "presente" if presente else "ausente",
                    "oferta": 0,  # Será definida aleatoriamente por turma
                    "biblias_entregues": 0,
                    "revistas_entregues": 0
                })
                
                if presente:
                    resultado['stats']['presentes'] += 1
                else:
                    resultado['stats']['ausentes'] += 1
                
            except Exception as e:
                resultado['erros'].append(f"Erro na linha {index}: {e}")
        
        # Gerar oferta aleatória para a turma
        oferta_turma = round(random.uniform(5.00, 50.00), 2)
        
        # Distribuir oferta entre alunos presentes
        presentes = [c for c in chamada_data if c['status'] == 'presente']
        if presentes:
            oferta_por_aluno = round(oferta_turma / len(presentes), 2)
            for chamada in presentes:
                chamada['oferta'] = oferta_por_aluno
        
        print(f"   💰 Oferta gerada: R$ {oferta_turma:.2f}")
        
        # Registrar chamada no sistema
        if chamada_data:
            sucesso_api = self.registrar_chamada_api(turma_id, data_chamada, chamada_data)
            if sucesso_api:
                resultado['sucesso'] = True
                print(f"   ✅ Chamada registrada: {resultado['stats']['presentes']} presentes, {resultado['stats']['ausentes']} ausentes")
            else:
                resultado['erros'].append(f"Falha ao registrar chamada no sistema para {turma_nome}")
        else:
            resultado['erros'].append(f"Nenhum aluno válido encontrado na planilha para {turma_nome}")
        
        return resultado
    
    def registrar_chamada_api(self, turma_id, data, chamada_data):
        """Registrar chamada via API"""
        try:
            url = f"{API_BASE}/attendance/bulk/{turma_id}?data={data}"
            response = requests.post(url, json=chamada_data)
            
            if response.status_code == 200:
                return True
            else:
                print(f"   ❌ Erro API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Erro ao chamar API: {e}")
            return False
    
    def imprimir_relatorio(self, resultados):
        """Imprimir relatório final"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL DA IMPORTAÇÃO")
        print("="*60)
        
        if resultados['sucesso']:
            print(f"✅ TURMAS PROCESSADAS COM SUCESSO: {len(resultados['sucesso'])}")
            for turma_result in resultados['sucesso']:
                stats = turma_result['stats']
                print(f"   🏫 {turma_result['turma']}: {stats['presentes']} presentes, {stats['ausentes']} ausentes")
        
        if resultados['erros']:
            print(f"\n❌ ERROS ENCONTRADOS: {len(resultados['erros'])}")
            for erro in resultados['erros']:
                print(f"   • {erro}")
        
        print("\n" + "="*60)

def main():
    if len(sys.argv) < 3:
        print("Uso: python import_chamadas_planilha.py <arquivo.xlsx> <data_chamada>")
        print("Exemplo: python import_chamadas_planilha.py chamadas.xlsx 2025-08-18")
        return
    
    arquivo_planilha = sys.argv[1]
    data_chamada = sys.argv[2]
    
    if not os.path.exists(arquivo_planilha):
        print(f"❌ Arquivo não encontrado: {arquivo_planilha}")
        return
    
    # Validar formato da data
    try:
        datetime.strptime(data_chamada, '%Y-%m-%d')
    except ValueError:
        print("❌ Data deve estar no formato YYYY-MM-DD (ex: 2025-08-18)")
        return
    
    importador = ImportadorChamadas()
    
    print("🚀 IMPORTADOR DE CHAMADAS - EBD MANAGER")
    print("="*60)
    
    # Carregar dados do sistema
    if not importador.carregar_dados_sistema():
        print("❌ Falha ao carregar dados do sistema")
        return
    
    # Processar planilha
    resultados = importador.processar_planilha(arquivo_planilha, data_chamada)
    
    if resultados:
        importador.imprimir_relatorio(resultados)
    else:
        print("❌ Falha ao processar planilha")

if __name__ == "__main__":
    main()