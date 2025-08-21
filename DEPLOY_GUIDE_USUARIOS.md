# 🚀 Guia de Deploy - EBD Manager

## ✅ Sistema com Usuários Garantidos

Este sistema foi configurado para **SEMPRE** criar os usuários necessários automaticamente quando subir, evitando problemas de login no deploy.

---

## 👤 Usuários Garantidos no Deploy

### 🔐 Credenciais que SEMPRE funcionarão:

| Usuário | Email | Senha | Tipo | Descrição |
|---------|-------|-------|------|-----------|
| **Admin** | `admin@ebd.com` | `123456` | admin | Administrador do sistema |
| **Professor** | `kell@ebd.com` | `123456` | professor | Professor da EBD |

### ⚡ Criação Automática

Os usuários são criados automaticamente em **3 momentos**:

1. **🚀 Startup do Backend** - Sempre que o servidor FastAPI iniciar
2. **📊 Primeiro Acesso** - Via endpoint `/api/deploy-check` 
3. **🔧 Setup Manual** - Via endpoint `/api/setup-deploy`

---

## 🛠️ Como Verificar se está Pronto para Deploy

### Método 1: Via API
```bash
curl https://SEU-DOMINIO.com/api/deploy-check
```

**Resposta esperada:**
```json
{
  "success": true,
  "message": "Sistema pronto para deploy",
  "status": {
    "deploy_ready": true,
    "users": {
      "admin_exists": true,
      "professor_exists": true
    },
    "credentials": {
      "admin": "admin@ebd.com / 123456",
      "professor": "kell@ebd.com / 123456"
    }
  }
}
```

### Método 2: Login Direto
1. Acesse: `https://SEU-DOMINIO.com`
2. Clique em "Fazer Login"
3. Use: `admin@ebd.com` / `123456`
4. ✅ Deve funcionar imediatamente!

---

## 🔧 Se Por Algum Motivo Não Conseguir Logar

### Solução 1: Forçar Criação via API
```bash
curl -X POST https://SEU-DOMINIO.com/api/setup-deploy
```

### Solução 2: Script Manual (se tiver acesso ao servidor)
```bash
cd /app
python deploy_setup.py
```

### Solução 3: Via Código no Backend
O backend tem startup automático que cria os usuários. Se reiniciar o serviço:
```bash
# No servidor
supervisorctl restart backend
# ou
systemctl restart seu-servico-backend
```

---

## 🎯 Processo de Deploy Recomendado

### 1. **Antes do Deploy**
```bash
# No ambiente local/dev
python deploy_setup.py
# ✅ Verificar se aparece "DEPLOY SETUP FINALIZADO COM SUCESSO"
```

### 2. **Após Deploy**
```bash
# Testar imediatamente
curl https://SEU-DOMINIO.com/api/deploy-check

# Ou fazer login manual:
# URL: https://SEU-DOMINIO.com
# Email: admin@ebd.com
# Senha: 123456
```

### 3. **Se Necessário**
```bash
# Forçar criação de usuários
curl -X POST https://SEU-DOMINIO.com/api/setup-deploy
```

---

## 📊 Dados Inclusos

O sistema já vem com dados completos:

- **🏫 11 Turmas** da igreja
- **👥 242 Alunos** distribuídos nas turmas
- **📚 6 Revistas** trimestrais completas
- **👤 2 Usuários** garantidos (admin + professor)

---

## 🆘 Troubleshooting

### Problema: "Usuário ou senha inválidos"
**Soluções em ordem de prioridade:**

1. ✅ Confirme as credenciais: `admin@ebd.com` / `123456`
2. 🔄 Execute: `curl -X POST https://SEU-DOMINIO.com/api/setup-deploy`
3. 🔍 Verifique: `curl https://SEU-DOMINIO.com/api/deploy-check`
4. 🚀 Reinicie o backend se tiver acesso ao servidor

### Problema: "Erro de conexão com banco"
- Verifique se MongoDB está rodando
- Confirme variáveis de ambiente (`MONGO_URL`, `DB_NAME`)

### Problema: "Sistema sem dados"
- Execute `python deploy_setup.py` no servidor
- Isso importará todos os dados do backup automaticamente

---

## 🎉 Confirmação Final

**Sistema está pronto para produção quando:**

✅ Login `admin@ebd.com` / `123456` funciona  
✅ Dashboard mostra "242 Matriculados"  
✅ Pode navegar entre todas as telas  
✅ `/api/deploy-check` retorna `"deploy_ready": true`  

---

## 📞 Suporte

Se mesmo seguindo este guia não conseguir acessar:

1. **Verifique os logs** do backend no servidor
2. **Teste a API** de verificação: `/api/deploy-check`
3. **Execute o setup manual**: `python deploy_setup.py`

**O sistema foi projetado para NUNCA falhar no login após deploy!** 🛡️