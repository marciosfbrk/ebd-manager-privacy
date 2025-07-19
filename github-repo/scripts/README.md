# EBD Manager - Scripts de Automação Windows

Esta pasta contém scripts para automação no Windows:

## 📋 Scripts Disponíveis

### `install.bat`
- **Função**: Instalação completa automática
- **O que faz**:
  - Verifica Python e Node.js
  - Cria ambiente virtual Python
  - Instala dependências
  - Configura variáveis de ambiente
  - Importa dados iniciais

### `start_system.bat`  
- **Função**: Iniciar todo o sistema
- **O que faz**:
  - Inicia MongoDB local
  - Inicia Backend FastAPI
  - Inicia Frontend React
  - Abre navegador automaticamente

### `stop_system.bat`
- **Função**: Parar todo o sistema
- **O que faz**:
  - Para processos Node.js
  - Para processos Python
  - Fecha janelas do sistema
  - Mantém MongoDB rodando

### `check_system.bat`
- **Função**: Verificar status do sistema
- **O que faz**:
  - Verifica se Python/Node estão instalados
  - Verifica se serviços estão rodando
  - Mostra status de cada componente
  - Exibe logs recentes

### `setup_local.bat`
- **Função**: Configuração inicial
- **O que faz**:
  - Cria arquivos .env locais
  - Cria estrutura de pastas
  - Prepara ambiente para primeira execução

## 🚀 Ordem de Execução

1. **Primeira vez**:
   ```cmd
   setup_local.bat    # Configuração inicial
   install.bat        # Instalação completa
   start_system.bat   # Iniciar sistema
   ```

2. **Uso diário**:
   ```cmd
   start_system.bat   # Iniciar
   stop_system.bat    # Parar
   ```

3. **Verificar problemas**:
   ```cmd
   check_system.bat   # Status completo
   ```

## 🔧 Personalização

Para modificar configurações, edite:
- `backend\.env` - Configurações do backend
- `frontend\.env` - Configurações do frontend
- Scripts `.bat` - Comportamento de inicialização

## ⚠️ Troubleshooting

Se algum script não funcionar:
1. Execute como Administrador
2. Verifique se Python/Node estão no PATH
3. Execute `check_system.bat` para diagnóstico
4. Consulte logs em `logs\`

## 📞 Suporte

Em caso de problemas, execute `check_system.bat` e consulte os logs gerados.