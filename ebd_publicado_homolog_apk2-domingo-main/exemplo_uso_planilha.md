# 📋 Como Usar o Importador de Chamadas

## 📂 Formato da Planilha Esperado

### 📊 Estrutura:
- **Cada aba = uma turma**
- **Nome da aba** deve corresponder ao nome da turma no sistema

### 🏫 Abas Esperadas (baseado nas turmas do sistema):
```
- Genesis (ou Gênesis)
- Primarios (ou Primários)  
- Juniores (ou Júniores)
- Pré-Adolescentes
- Adolescentes
- Jovens
- Dorcas (ou "Dorcas Irmãs")
- Ebenezer (ou "Ebenezer Obreiros")
- Soldados de Cristo
- Professores (ou "Professores e Oficiais")
```

### 📋 Colunas em cada aba:
| Nome | Presente | (Opcional: outras colunas) |
|------|----------|---------------------------|
| João da Silva | TRUE | |
| Maria Santos | FALSE | |
| Pedro Oliveira | TRUE | |

**Colunas aceitas:**
- **Nome**: "Nome", "Aluno", "Nome Completo"
- **Presença**: "Presente", "Presença", "Status", "P", "Chamada"

**Valores de Presença:**
- ✅ **Presente**: TRUE, true, 1, presente, sim, s
- ❌ **Ausente**: FALSE, false, 0, ausente, não, nao, falta

## 🚀 Como Usar

### 1️⃣ **Preparar Planilha:**
- Salvar como `.xlsx`
- Uma aba por turma
- Colunas Nome + Presente mínimas

### 2️⃣ **Executar Importação:**
```bash
# Upload da planilha para /app/
# Depois executar:
python import_chamadas_planilha.py chamadas.xlsx 2025-08-18
```

### 3️⃣ **Resultado:**
- ✅ Chamadas registradas no sistema
- 💰 Ofertas aleatórias (R$ 5-50) por turma
- 📊 Relatório de importação

## ⚙️ Funcionalidades Automáticas

### 🔍 **Mapeamento Inteligente:**
- Normaliza nomes para comparação
- Encontra alunos por similaridade
- Mapeia abas para turmas do sistema

### 💰 **Ofertas Automáticas:**
- R$ 5,00 a R$ 50,00 por turma
- Distribuída entre alunos presentes
- Valores realistas

### 📊 **Relatório Completo:**
- Quantos alunos por turma
- Presentes vs ausentes
- Erros e avisos
- Alunos não encontrados

## 🛡️ **Segurança:**
- **NÃO altera** dados existentes
- **APENAS adiciona** chamadas novas
- **Preserva** todos os alunos e turmas
- **Valida** antes de importar

## 📝 **Exemplo de Saída:**
```
📊 RELATÓRIO FINAL DA IMPORTAÇÃO
============================================================
✅ TURMAS PROCESSADAS COM SUCESSO: 8
   🏫 Genesis: 10 presentes, 3 ausentes
   🏫 Primarios: 12 presentes, 4 ausentes
   🏫 Juniores: 8 presentes, 4 ausentes
   🏫 Jovens: 18 presentes, 5 ausentes
   💰 Total ofertas: R$ 287,50
============================================================
```