# 🎯 EBD Manager - Guia Completo de Instalação Local

## 🏆 O que você terá ao final:
- ✅ Sistema EBD Manager 100% funcional no seu PC
- ✅ Todos os logins funcionando (admin@ebd.com e kell2@ebd.com)
- ✅ 11 turmas reais da igreja carregadas
- ✅ 242 alunos já cadastrados
- ✅ 6 revistas trimestrais completas
- ✅ Dashboard, relatórios, rankings funcionando
- ✅ Sistema offline (sem internet após instalação)

---

## 📋 PASSO 1: Instalar Pré-requisitos

### 1.1 Python 3.9+ 
- **Download:** https://www.python.org/downloads/
- ⚠️ **CRÍTICO:** Marcar "Add Python to PATH" durante instalação
- **Verificar:** Abrir cmd e digitar `python --version`

### 1.2 Node.js 18+
- **Download:** https://nodejs.org/
- Instala automaticamente o npm
- **Verificar:** `node --version` e `npm --version`

### 1.3 MongoDB Community
- **Download:** https://www.mongodb.com/try/download/community
- **OU** MongoDB Compass (interface gráfica)
- **Verificar:** `mongod --version`

### 1.4 Git (se não tiver)
- **Download:** https://git-scm.com/download/win
- **Verificar:** `git --version`

---

## 🚀 PASSO 2: Baixar o Projeto

```bash
# 1. Escolher uma pasta (exemplo: C:\Projetos)
cd C:\Projetos

# 2. Clonar repositório
git clone [SEU_LINK_GITHUB]
cd ebd-manager

# 3. Verificar arquivos baixados
dir
```

**Arquivos que devem existir:**
- `setup_local_completo.bat`
- `install_completo.bat` 
- `start_system_local.bat`
- `import_data_completo.py`

---

## ⚙️ PASSO 3: Configuração Inicial

```bash
# Executar configuração inicial
setup_local_completo.bat
```

**O que este script faz:**
- ✅ Cria pastas necessárias (data, logs, backups)
- ✅ Configura arquivos .env do backend
- ✅ Configura arquivos .env do frontend
- ✅ Prepara ambiente para instalação

---

## 📦 PASSO 4: Instalação Completa

```bash
# Executar instalação automática
install_completo.bat
```

**O que este script faz:**
- ✅ Verifica Python e Node.js
- ✅ Cria ambiente virtual Python
- ✅ Instala todas as dependências Python
- ✅ Instala todas as dependências Node.js
- ✅ Inicia MongoDB local
- ✅ Importa todos os dados (usuários, turmas, alunos, revistas)

**⏳ Tempo estimado:** 5-10 minutos

---

## 🎯 PASSO 5: Iniciar o Sistema

```bash
# Iniciar todos os serviços
start_system_local.bat
```

**O que acontece:**
- ✅ Inicia MongoDB local
- ✅ Inicia Backend FastAPI (porta 8000)
- ✅ Inicia Frontend React (porta 3000)
- ✅ Abre navegador automaticamente
- ✅ Sistema pronto para uso!

---

## 🌐 PASSO 6: Acessar o Sistema

**URLs:**
- **Principal:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Backend:** http://localhost:8000

**Logins prontos:**
- **Admin:** admin@ebd.com / 123456
- **Professor:** kell2@ebd.com / 123456

---

## 📊 Dados já Carregados

### 👥 Usuários (2)
- **Márcio Ferreira** (Admin) - Acesso completo
- **Kelliane Ferreira** (Professor) - Acesso de professor

### 🏫 Turmas (11)
1. Professores e Oficiais
2. Genesis  
3. Primarios
4. Juniores
5. Pré-Adolescentes
6. Adolescentes
7. Jovens
8. Adultos Unidos
9. Dorcas (irmãs)
10. Ebenezer (Obreiros)
11. Soldados de Cristo

### 👨‍🎓 Alunos (242)
- Distribuídos proporcionalmente nas 11 turmas
- Nomes, idades, telefones e endereços realistas
- Dados prontos para chamada e relatórios

### 📚 Revistas Trimestrais (6)
1. **Jovens:** "A Liberdade em Cristo" (13 lições)
2. **Adolescentes:** "Grandes Cartas para Nós" (13 lições)
3. **Pré-Adolescentes:** "Recebendo o Batismo no Espírito Santo" (13 lições)
4. **Juniores:** "Verdades que Jesus ensinou" (13 lições)
5. **Primários:** "As aventuras de um Grande Missionário" (13 lições)
6. **Adultos:** "A Igreja em Jerusalém" (13 lições)

---

## 🔧 Comandos Úteis

### Gerenciamento do Sistema
```bash
# Iniciar sistema
start_system_local.bat

# Parar sistema  
stop_system_local.bat

# Verificar status
check_system_local.bat

# Resetar dados (volta ao original)
reset_database.bat
```

### Comandos Manuais
```bash
# Ver logs
type logs\mongodb.log
type logs\backend.log
type logs\frontend.log

# Iniciar só backend
cd backend
venv\Scripts\activate.bat
python -m uvicorn server:app --reload

# Iniciar só frontend
cd frontend
npm start
```

---

## 🆘 Troubleshooting

### ❌ "Python não encontrado"
**Solução:**
1. Reinstalar Python de https://www.python.org/downloads/
2. ⚠️ **MARCAR:** "Add Python to PATH"
3. Reiniciar prompt de comando
4. Testar: `python --version`

### ❌ "Node não encontrado"  
**Solução:**
1. Reinstalar Node.js de https://nodejs.org/
2. Reiniciar prompt de comando
3. Testar: `node --version`

### ❌ "MongoDB não conecta"
**Soluções:**
1. Verificar se MongoDB está instalado
2. Verificar se pasta `data\` existe
3. Tentar: `mongod --dbpath data`
4. Usar MongoDB Compass para testar conexão

### ❌ "Porta ocupada"
**Soluções:**
- Fechar outros projetos que usam portas 3000 ou 8000
- Alterar portas nos arquivos .env se necessário
- Reiniciar computador em caso extremo

### ❌ "Dependências não instalam"
**Soluções:**
1. Executar como Administrador
2. Limpar cache: `npm cache clean --force`
3. Deletar `node_modules` e reinstalar
4. Verificar conexão com internet durante instalação

---

## 🎉 Funcionalidades Disponíveis

Após instalação, você terá acesso a:

### 📊 Dashboard
- Estatísticas em tempo real
- Gráficos de presença
- Resumo por turmas
- Dados financeiros (ofertas)

### ✅ Sistema de Chamada
- Chamada por turma
- Registro de presença
- Controle de ofertas
- Distribuição de materiais

### 👥 Gerenciamento
- Cadastro de alunos
- Gestão de turmas  
- Controle de usuários
- Permissões por tipo

### 📈 Relatórios
- Relatórios detalhados por período
- Rankings de presença
- Estatísticas por turma
- Exportação de dados

### 📖 Revistas Trimestrais
- 6 revistas completas
- Lições organizadas por data
- Fácil navegação
- Interface intuitiva

---

## 🏆 PRONTO!

Em aproximadamente 15 minutos você terá:
- ✅ Sistema completo funcionando
- ✅ Dados reais carregados
- ✅ Interface moderna e responsiva
- ✅ Funcionalidades de uma EBD real

**Acesse:** http://localhost:3000
**Login:** admin@ebd.com / 123456

---

## 📞 Suporte

Se tiver problemas:
1. Execute `check_system_local.bat` para diagnóstico
2. Verifique logs em `logs\`
3. Certifique-se que todos os pré-requisitos estão instalados
4. Tente resetar com `reset_database.bat`

**O sistema foi testado e funciona perfeitamente!** 🚀