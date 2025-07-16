import React from 'react';

const Usuarios = ({ setCurrentView }) => {
  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => setCurrentView('dashboard')}
            className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            ← Voltar ao Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-800">Gerenciar Usuários</h1>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <p className="text-gray-600">Carregando usuários...</p>
        </div>
      </div>
    </div>
  );
};

export default Usuarios;