# 🏠 EBD Manager - Setup Completo no PC Local

## 📋 O que você vai ter:
- ✅ Todos os usuários (admin@ebd.com e kell2@ebd.com)
- ✅ Todas as 11 turmas da igreja
- ✅ Todos os 242 alunos cadastrados  
- ✅ Todas as 6 revistas trimestrais
- ✅ Sistema 100% funcional

## 🛠️ Pré-requisitos (instalar nesta ordem):

### 1. Python 3.9+
- Download: https://www.python.org/downloads/
- ⚠️ **IMPORTANTE:** Marcar "Add Python to PATH" durante instalação

### 2. Node.js 18+
- Download: https://nodejs.org/
- Instala automaticamente o npm

### 3. MongoDB Community Edition
- Download: https://www.mongodb.com/try/download/community
- **OU** MongoDB Compass (interface gráfica): https://www.mongodb.com/try/download/compass

### 4. Git (se não tiver)
- Download: https://git-scm.com/download/win

## 🚀 Instalação Passo a Passo

### Passo 1: Baixar o projeto
```bash
# Escolha uma pasta (ex: C:\Projetos)
cd C:\Projetos

# Clonar o repositório
git clone [SEU_LINK_DO_GITHUB]
cd ebd-manager
```

### Passo 2: Configuração Automática
```bash
# Executar script de configuração inicial
setup_local_completo.bat
```

### Passo 3: Instalação das Dependências
```bash
# Executar instalação completa
install_completo.bat
```

### Passo 4: Iniciar o Sistema
```bash
# Iniciar todos os serviços
start_system.bat
```

## 🌐 URLs de Acesso

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **MongoDB:** mongodb://localhost:27017

## 👥 Usuários já configurados:

### 🔑 Administrador
- **Email:** admin@ebd.com
- **Senha:** 123456
- **Acesso:** Completo (todas as funcionalidades)

### 👨‍🏫 Professor
- **Email:** kell2@ebd.com
- **Senha:** 123456
- **Acesso:** Chamada e visualização

## 📊 Dados já carregados:

- ✅ **11 turmas:** Professores e Oficiais, Genesis, Primarios, etc.
- ✅ **242 alunos** distribuídos nas turmas
- ✅ **6 revistas trimestrais** com todas as lições
- ✅ **Sistema de usuários** funcionando

## 🔧 Comandos Úteis

```bash
# Iniciar sistema
start_system.bat

# Parar sistema
stop_system.bat

# Verificar status
check_system.bat

# Ver logs
type logs\backend.log
type logs\frontend.log

# Resetar dados (volta ao estado original)
reset_database.bat
```

## 🆘 Troubleshooting

### Erro: Python não encontrado
```bash
python --version
# Se não funcionar, reinstalar Python marcando "Add to PATH"
```

### Erro: Node não encontrado
```bash
node --version
npm --version
# Se não funcionar, reinstalar Node.js
```

### Erro: MongoDB não conecta
1. Verificar se MongoDB está instalado
2. Verificar se serviço está rodando
3. Usar MongoDB Compass para testar conexão

### Erro: Porta ocupada
- Frontend padrão: porta 3000
- Backend padrão: porta 8000
- Para alterar, editar os arquivos .env

### Erro: Dependências não instalam
1. Fechar todas as janelas do prompt
2. Executar como Administrador
3. Executar install_completo.bat novamente

## 📱 Recursos Disponíveis

### 🎯 Funcionalidades Principais
- Dashboard com estatísticas em tempo real
- Sistema de chamada dominical
- Gerenciamento de turmas e alunos
- Relatórios detalhados e rankings
- Sistema de revistas trimestrais
- Gerenciamento de usuários

### 📖 Revistas Trimestrais Incluídas
1. **Jovens:** "A Liberdade em Cristo"
2. **Adolescentes:** "Grandes Cartas para Nós"
3. **Pré-Adolescentes:** "Recebendo o Batismo no Espírito Santo"
4. **Juniores:** "Verdades que Jesus ensinou"
5. **Primários:** "As aventuras de um Grande Missionário"
6. **Adultos:** "A Igreja em Jerusalém"

## 🎯 Em 10 minutos você terá o sistema completo rodando!

### Próximos passos após instalação:
1. Acesse http://localhost:3000
2. Faça login com admin@ebd.com / 123456
3. Explore todas as funcionalidades
4. Teste o sistema de chamada
5. Veja os relatórios e rankings
6. Confira as revistas trimestrais

---

## 📞 Suporte
Em caso de problemas:
1. Verificar logs em `logs\`
2. Executar `check_system.bat`
3. Verificar se todos os pré-requisitos estão instalados