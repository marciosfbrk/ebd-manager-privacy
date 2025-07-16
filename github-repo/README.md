# EBD Manager 📊

> Sistema completo de gerenciamento para Escola Bíblica Dominical

## 🚀 Deploy Rápido

[![Deploy Backend](https://railway.app/button.svg)](https://railway.app/new/template)
[![Deploy Frontend](https://vercel.com/button)](https://vercel.com/new/git/external?repository-url=https://github.com/seu-usuario/ebd-manager)

## 📋 Sobre o Sistema

O **EBD Manager** é um sistema completo para gerenciamento de Escola Bíblica Dominical, desenvolvido com tecnologias modernas:

- **Frontend**: React 19 + TailwindCSS
- **Backend**: FastAPI + Python 3.9
- **Database**: MongoDB
- **Deploy**: Railway (Backend) + Vercel (Frontend)

## ✨ Funcionalidades

### 👥 Gestão de Pessoas
- ✅ Cadastro e edição de alunos
- ✅ Organização por turmas
- ✅ Transferência entre turmas
- ✅ Controle de usuários (Admin/Professor)

### 📊 Chamadas e Relatórios
- ✅ Chamadas dominicais
- ✅ Controle de presenças, faltas e visitantes
- ✅ Registro de ofertas
- ✅ Distribuição de materiais (bíblias, revistas)

### 📈 Analytics
- ✅ Dashboard com estatísticas
- ✅ Relatórios detalhados por departamento
- ✅ Rankings de presença
- ✅ Classes vencedoras

### 📱 Mobile
- ✅ Interface responsiva
- ✅ PWA (Progressive Web App)
- ✅ Funciona em qualquer dispositivo

## 🎯 Deploy em 10 minutos

### Pré-requisitos
- Conta GitHub
- Conta [Railway](https://railway.app) (gratuita)
- Conta [Vercel](https://vercel.com) (gratuita)
- Conta [MongoDB Atlas](https://cloud.mongodb.com) (gratuita)

### 📖 Guia Completo
**Consulte o arquivo [`DEPLOY_GUIDE.md`](./DEPLOY_GUIDE.md) para instruções passo a passo.**

### ⚡ Resumo Rápido

1. **Fork** este repositório
2. **MongoDB Atlas**: Criar cluster gratuito
3. **Railway**: Deploy do backend
4. **Vercel**: Deploy do frontend
5. **Migração**: Importar dados

## 🗂️ Estrutura do Projeto

```
ebd-manager/
├── backend/                # FastAPI Backend
│   ├── server.py          # Aplicação principal
│   ├── requirements.txt   # Dependências Python
│   ├── Procfile          # Configuração Railway
│   └── .env.production   # Variáveis de ambiente
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── App.js        # Componente principal
│   │   └── App.css       # Estilos
│   ├── public/           # Arquivos estáticos
│   └── package.json      # Dependências Node
├── database_export.json  # Dados de exemplo
├── migrate_data.py       # Script de migração
├── vercel.json           # Configuração Vercel
└── DEPLOY_GUIDE.md       # Guia de deploy
```

## 🎨 Screenshots

### Dashboard Principal
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Principal)

### Relatórios Detalhados
![Relatórios](https://via.placeholder.com/800x400?text=Relatórios+Detalhados)

### Rankings
![Rankings](https://via.placeholder.com/800x400?text=Rankings+de+Presença)

## 👤 Usuários Padrão

| Usuário | Email | Senha | Tipo |
|---------|-------|-------|------|
| Admin | admin@ebd.com | 123456 | Administrador |
| Professor | kell2@ebd.com | 123456 | Professor |

## 🔧 Desenvolvimento Local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 📊 Dados de Exemplo

O sistema inclui dados completos de uma igreja real:
- **11 turmas** organizadas por departamento
- **242 alunos** cadastrados
- **Estrutura completa** de classes

## 🛠️ Stack Tecnológica

### Backend
- **FastAPI**: Framework web moderno
- **Motor**: Driver MongoDB assíncrono
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validação de dados

### Frontend
- **React 19**: Biblioteca de UI
- **TailwindCSS**: Framework de CSS
- **Axios**: Cliente HTTP
- **PWA**: Aplicação web progressiva

### Database
- **MongoDB**: Banco de dados NoSQL
- **MongoDB Atlas**: Cloud database

### Deploy
- **Railway**: Backend hosting
- **Vercel**: Frontend hosting
- **GitHub Actions**: CI/CD (opcional)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

Desenvolvido com ❤️ para a comunidade da **Escola Bíblica Dominical**.

**Ministério Belém**  
Rua Managuá, 53 - Parque das Nações  
Sumaré, SP

---

## 🚀 Pronto para usar?

**[📖 Comece pelo DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)**

[![Deploy Now](https://img.shields.io/badge/Deploy-Now-blue?style=for-the-badge)](./DEPLOY_GUIDE.md)