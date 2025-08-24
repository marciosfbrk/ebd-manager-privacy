# 💾 Sistema de Backup e Restore - EBD Manager

## ✅ Sistema Completo Implementado

O EBD Manager agora possui um sistema robusto de backup e restore que permite:

- **🔄 Backup automático** de todos os dados
- **📁 Download direto** pelo navegador  
- **⬆️ Restore via interface** web
- **⌨️ Scripts de linha de comando** para automação
- **📦 Compressão** para arquivos menores
- **🔍 Validação** completa dos dados

---

## 🌐 Interface Web (Mais Fácil)

### 📥 Como Fazer Backup:

1. **Faça login** como administrador (`admin@ebd.com` / `123456`)
2. **Vá ao Dashboard** (tela inicial)
3. **Role para baixo** até a seção "Ações Rápidas"
4. **Encontre "Backup & Restore"**
5. **Clique em "Gerar Backup"** ⬇️
6. **Aguarde o download** - arquivo será baixado automaticamente
7. **Nome do arquivo**: `ebd_backup_YYYYMMDD_HHMMSS.json`

### 📤 Como Fazer Restore:

1. **Faça login** como administrador
2. **Vá à seção "Backup & Restore"**
3. **Clique em "Restaurar Backup"** ⬆️
4. **Selecione o arquivo** de backup (`.json` ou `.zip`)
5. **Leia as informações** do backup mostradas
6. **⚠️ ATENÇÃO**: Todos os dados atuais serão substituídos!
7. **Digite "CONFIRMAR"** se quiser continuar
8. **Aguarde a conclusão** - sistema será recarregado automaticamente

---

## ⌨️ Scripts de Linha de Comando (Avançado)

### 📋 Comandos Disponíveis:

```bash
# Navegar para o diretório
cd /app

# Gerar backup simples
python backup_system.py backup

# Gerar backup com nome personalizado
python backup_system.py backup --file "meu_backup_especial"

# Gerar backup comprimido (menor)
python backup_system.py backup --compress

# Gerar backup com sessões incluídas
python backup_system.py backup --sessions

# Listar backups disponíveis
python backup_system.py list

# Restaurar backup (com confirmação)
python backup_system.py restore --file "/app/backups/backup.json"

# Restaurar backup forçado (sem confirmação)
python backup_system.py restore --file "/app/backups/backup.json" --force
```

### 📁 Exemplos Práticos:

```bash
# Backup diário automatizado
python backup_system.py backup --file "backup_diario_$(date +%Y%m%d)" --compress

# Backup completo antes de deploy
python backup_system.py backup --file "pre_deploy_$(date +%Y%m%d_%H%M%S)" --sessions --compress

# Restore de emergência
python backup_system.py restore --file "/app/backups/ultimo_backup.zip" --force
```

---

## 📊 Dados Inclusos no Backup

| 📋 Coleção | 📝 Descrição | 📊 Quantidade Atual |
|-------------|---------------|---------------------|
| 👤 **users** | Usuários do sistema | 3 registros |
| 🏫 **turmas** | Classes da EBD | 11 registros |
| 📚 **students** | Alunos matriculados | 244 registros |
| 📊 **attendance** | Chamadas realizadas | 0 registros |
| 📖 **revistas** | Revistas trimestrais | 6 registros |
| 🔗 **sessions** | Sessões ativas (opcional) | Variável |

### 📄 Estrutura do Arquivo de Backup:

```json
{
  "metadata": {
    "backup_timestamp": "20250821_142000",
    "backup_date": "2025-08-21T14:20:00",
    "system_version": "EBD Manager v1.0",
    "total_records": 264,
    "collections": ["users", "turmas", "students", "attendance", "revistas"]
  },
  "data": {
    "users": [...],
    "turmas": [...],
    "students": [...],
    "attendance": [...],
    "revistas": [...]
  }
}
```

---

## 🚀 Fluxo de Deploy com Backup

### 1️⃣ **Antes do Deploy:**
```bash
# Fazer backup do ambiente atual
python backup_system.py backup --file "pre_deploy_$(date +%Y%m%d_%H%M%S)" --compress

# Verificar backup criado
python backup_system.py list
```

### 2️⃣ **Após Deploy:**
```bash
# Se precisar restaurar dados
python backup_system.py restore --file "/app/backups/pre_deploy_XXXXX.zip"

# Ou via API (mais fácil)
# Use a interface web para restore
```

### 3️⃣ **Migração de Servidor:**
1. **No servidor antigo**: Faça backup via interface web ou comando
2. **Baixe o arquivo** de backup
3. **No servidor novo**: Faça deploy normal
4. **Restaure o backup** via interface web
5. **✅ Migração concluída!**

---

## 🔄 Automação de Backups

### 📅 Backup Automático Diário (Cron):

```bash
# Adicionar ao crontab (crontab -e)
0 2 * * * cd /app && python backup_system.py backup --file "auto_$(date +\%Y\%m\%d)" --compress > /var/log/backup.log 2>&1

# Backup semanal (domingos às 3h)
0 3 * * 0 cd /app && python backup_system.py backup --file "weekly_$(date +\%Y\%m\%d)" --sessions --compress
```

### 🧹 Limpeza Automática de Backups Antigos:

```bash
# Manter apenas últimos 7 backups
find /app/backups -name "*.zip" -mtime +7 -delete

# Manter apenas últimos 30 backups JSON
find /app/backups -name "*.json" -mtime +30 -delete
```

---

## 📱 APIs Disponíveis

### 🔗 Endpoints do Sistema:

| 🌐 Endpoint | 📝 Descrição | 🔧 Método |
|-------------|---------------|-----------|
| `/api/backup/generate` | Gera backup completo | GET |
| `/api/backup/restore` | Restaura dados de backup | POST |
| `/api/backup/download/{filename}` | Download direto de backup | GET |
| `/api/deploy-check` | Verifica status do sistema | GET |

### 📋 Exemplo de Uso da API:

```bash
# Gerar backup via API
curl "https://SEU-DOMINIO.com/api/backup/generate" > backup.json

# Verificar sistema
curl "https://SEU-DOMINIO.com/api/deploy-check" | jq .
```

---

## ⚠️ Avisos Importantes

### 🔴 **Restore Substitui TODOS os Dados:**
- O restore **apaga** todos os dados existentes
- **Não é possível desfazer** a operação
- **Sempre faça backup** antes de restore
- **Confirme duas vezes** antes de continuar

### 🔐 **Segurança:**
- Backups contêm dados sensíveis (senhas hasheadas)
- **Armazene em local seguro**
- **Não compartilhe** arquivos de backup
- **Criptografe** se necessário para transporte

### 📏 **Tamanhos Típicos:**
- **Backup JSON**: 200-500 KB (dependendo dos dados)
- **Backup ZIP**: 20-50 KB (comprimido)
- **Com sessões**: +10-20% no tamanho

---

## 🆘 Troubleshooting

### ❌ **Erro: "Formato de backup inválido"**
- Verifique se o arquivo não está corrompido
- Confirme se é um backup válido do EBD Manager
- Tente usar backup mais recente

### ❌ **Erro: "Conexão com MongoDB"**
- Verifique se MongoDB está rodando
- Confirme variáveis de ambiente (`MONGO_URL`)
- Reinicie o backend se necessário

### ❌ **Download não funciona**
- Use navegador atualizado
- Verifique bloqueadores de popup
- Tente via linha de comando como alternativa

### ❌ **Backup muito grande**
- Use `--compress` para compactar
- Remova sessões antigas do banco
- Considere backup seletivo por coleção

---

## 🎯 Casos de Uso Recomendados

### 🔄 **Backup Regular:**
- **Diário**: Via interface web após atividades importantes
- **Semanal**: Via cron com compressão
- **Antes de mudanças**: Sempre antes de alterações críticas

### 🚀 **Deploy/Migração:**
- **Backup completo** do ambiente de produção
- **Restore imediato** no novo servidor
- **Validação** de dados após migração

### 🔧 **Desenvolvimento:**
- **Backup de dados de teste** para outros desenvolvedores
- **Reset** do ambiente de desenvolvimento
- **Sincronização** entre ambientes

---

## ✅ Verificação Final

**Sistema está pronto quando:**

✅ Interface web mostra botões "Gerar Backup" e "Restaurar Backup"  
✅ `python backup_system.py list` funciona sem erro  
✅ Backup via web faz download automaticamente  
✅ API `/api/backup/generate` retorna JSON válido  
✅ Restore via web carrega arquivo e mostra confirmação  

**🎉 Sistema de Backup Totalmente Funcional!**

---

## 📞 Suporte

Se encontrar problemas:

1. **Verifique logs** do backend: `/var/log/supervisor/backend.err.log`
2. **Teste API** diretamente: `curl /api/backup/generate`
3. **Use linha de comando** como alternativa
4. **Reinicie serviços** se necessário: `supervisorctl restart all`

**O sistema foi projetado para ser à prova de falhas na migração de dados! 🛡️**