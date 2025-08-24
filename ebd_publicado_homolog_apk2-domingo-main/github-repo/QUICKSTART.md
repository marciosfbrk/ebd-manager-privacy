## 🚀 Tutorial Rápido de Deploy

### 1. Preparar Repositório
```bash
# Clonar/Fork o repositório
git clone https://github.com/seu-usuario/ebd-manager.git
cd ebd-manager
```

### 2. MongoDB Atlas
- Criar conta gratuita
- Criar cluster M0
- Obter connection string

### 3. Railway (Backend)
- Conectar repositório GitHub
- Configurar variáveis de ambiente
- Deploy automático

### 4. Vercel (Frontend)
- Conectar repositório GitHub
- Configurar variáveis de ambiente
- Deploy automático

### 5. Migrar Dados
```bash
# Configurar MONGO_URL e executar
python migrate_data.py import
```

### 🎯 Resultado
Sistema funcionando em:
- Frontend: `https://seu-projeto.vercel.app`
- Backend: `https://seu-projeto.up.railway.app`

**Tempo total: 10-15 minutos**