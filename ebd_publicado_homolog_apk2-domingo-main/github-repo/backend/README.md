# Configuração do Railway
# Este arquivo contém as configurações necessárias para deploy no Railway

# Variáveis de ambiente obrigatórias:
# MONGO_URL = String de conexão do MongoDB Atlas
# DB_NAME = Nome do banco de dados

# Exemplo de configuração:
# MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net/ebd_manager?retryWrites=true&w=majority
# DB_NAME=ebd_manager

# O Railway irá:
# 1. Instalar dependências do requirements.txt
# 2. Executar o comando definido no Procfile
# 3. Disponibilizar a aplicação em uma URL pública

# Porta automática:
# O Railway define automaticamente a variável PORT
# Não é necessário configurar manualmente