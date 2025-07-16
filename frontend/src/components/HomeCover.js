import React from 'react';

const HomeCover = ({ 
  isLoggedIn, 
  currentUser, 
  showLogin, 
  setShowLogin, 
  setCurrentView, 
  handleLogin,
  handleLogout 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 text-white p-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">EBD Manager</h1>
          <p className="text-indigo-200 text-lg">Ministério Belém</p>
          <p className="text-indigo-300 text-sm mt-1">Rua Managuá, 53 - Parque das Nações, Sumaré, SP</p>
          <p className="text-indigo-300 text-sm">Sistema de Gerenciamento da Escola Bíblica Dominical</p>
          <p className="text-indigo-400 text-xs mt-2">Desenvolvido por Márcio Ferreira</p>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          {/* Área de Login/Usuário */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-200">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                {isLoggedIn ? "Bem-vindo!" : "Acesso ao Sistema"}
              </h2>
              
              {isLoggedIn ? (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 font-semibold">
                      Logado como: {currentUser?.nome} ({currentUser?.tipo === 'admin' ? 'Administrador' : 'Professor'})
                    </p>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                      onClick={() => setCurrentView('dashboard')}
                      className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-lg transition-all duration-200 text-lg font-semibold"
                    >
                      🚀 Acessar Sistema
                    </button>
                    
                    <button
                      onClick={handleLogout}
                      className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 shadow-lg transition-all duration-200"
                    >
                      Sair
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-gray-600 mb-6">
                    Faça login para acessar o sistema de gerenciamento da EBD
                  </p>
                  
                  <button
                    onClick={() => setShowLogin(true)}
                    className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-lg transition-all duration-200 text-lg font-semibold"
                  >
                    🔐 Fazer Login
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Recursos do Sistema */}
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">
              📋 Recursos do Sistema
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-3xl mb-2">✅</div>
                <h4 className="font-semibold text-green-800">Chamadas</h4>
                <p className="text-sm text-green-600">Registro de presença dominical</p>
              </div>
              
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-3xl mb-2">📊</div>
                <h4 className="font-semibold text-blue-800">Relatórios</h4>
                <p className="text-sm text-blue-600">Estatísticas detalhadas</p>
              </div>
              
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-3xl mb-2">🏆</div>
                <h4 className="font-semibold text-yellow-800">Rankings</h4>
                <p className="text-sm text-yellow-600">Classificação por presença</p>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-3xl mb-2">👥</div>
                <h4 className="font-semibold text-purple-800">Alunos</h4>
                <p className="text-sm text-purple-600">Gerenciamento completo</p>
              </div>
              
              <div className="text-center p-4 bg-indigo-50 rounded-lg">
                <div className="text-3xl mb-2">🏫</div>
                <h4 className="font-semibold text-indigo-800">Turmas</h4>
                <p className="text-sm text-indigo-600">Organização por classes</p>
              </div>
              
              <div className="text-center p-4 bg-pink-50 rounded-lg">
                <div className="text-3xl mb-2">📱</div>
                <h4 className="font-semibold text-pink-800">Mobile</h4>
                <p className="text-sm text-pink-600">Acesso em qualquer dispositivo</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Login */}
      {showLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Login</h3>
            
            <form onSubmit={handleLogin}>
              <div className="mb-4">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Digite seu email"
                />
              </div>
              
              <div className="mb-6">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Senha
                </label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Digite sua senha"
                />
              </div>
              
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  Entrar
                </button>
                <button
                  type="button"
                  onClick={() => setShowLogin(false)}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default React.memo(HomeCover);