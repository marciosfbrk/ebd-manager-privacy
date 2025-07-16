import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ currentUser, setCurrentView, selectedDate, setSelectedDate, loadDashboard, attendanceData, setActiveTab }) => {
  const isSunday = (dateString) => {
    const date = new Date(dateString);
    return date.getDay() === 0;
  };

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

      <div className="p-6">
        {/* Resumo Rápido */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Resumo Rápido</h2>
              <p className="text-gray-600">Estatísticas do último domingo</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Data: {selectedDate}</p>
              <button
                onClick={loadDashboard}
                className="mt-1 px-4 py-2 bg-gradient-to-r from-indigo-500 to-blue-600 text-white rounded-lg hover:from-indigo-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-lg transition-all duration-200 text-sm"
              >
                🔄 Atualizar
              </button>
            </div>
          </div>

          {!isSunday(selectedDate) && (
            <div className="bg-amber-50 border-l-4 border-amber-400 text-amber-800 px-4 py-3 rounded-r-lg mb-4">
              <div className="flex items-center">
                <span className="text-xl mr-2">⚠️</span>
                <strong>Aviso:</strong> A data selecionada não é um domingo.
              </div>
            </div>
          )}

          {/* Cards de Resumo */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {attendanceData.reduce((sum, row) => sum + row.matriculados, 0)}
              </div>
              <div className="text-sm text-blue-500 font-medium">Matriculados</div>
            </div>
            
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {attendanceData.reduce((sum, row) => sum + row.presentes, 0)}
              </div>
              <div className="text-sm text-green-500 font-medium">Presentes</div>
            </div>
            
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {(() => {
                  const totalMatriculados = attendanceData.reduce((sum, row) => sum + row.matriculados, 0);
                  const totalPresentes = attendanceData.reduce((sum, row) => sum + row.presentes, 0);
                  return totalMatriculados > 0 ? ((totalPresentes / totalMatriculados) * 100).toFixed(1) : '0.0';
                })()}%
              </div>
              <div className="text-sm text-purple-500 font-medium">Frequência</div>
            </div>
            
            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">
                R$ {attendanceData.reduce((sum, row) => sum + row.total_ofertas, 0).toFixed(2)}
              </div>
              <div className="text-sm text-yellow-500 font-medium">Ofertas</div>
            </div>
          </div>

          {/* Turmas com Melhor Frequência */}
          {attendanceData.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">🏆 Destaques do Dia</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="font-semibold text-green-800">Melhor Frequência</div>
                  <div className="text-green-700">
                    {(() => {
                      const melhorFrequencia = attendanceData
                        .filter(row => row.matriculados > 0)
                        .sort((a, b) => (b.presentes / b.matriculados) - (a.presentes / a.matriculados))[0];
                      return melhorFrequencia ? 
                        `${melhorFrequencia.turma_nome} (${((melhorFrequencia.presentes / melhorFrequencia.matriculados) * 100).toFixed(1)}%)` : 
                        'Nenhuma turma';
                    })()}
                  </div>
                </div>
                
                <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="font-semibold text-yellow-800">Maior Oferta</div>
                  <div className="text-yellow-700">
                    {(() => {
                      const maiorOferta = attendanceData
                        .sort((a, b) => b.total_ofertas - a.total_ofertas)[0];
                      return maiorOferta ? 
                        `${maiorOferta.turma_nome} (R$ ${maiorOferta.total_ofertas.toFixed(2)})` : 
                        'Nenhuma turma';
                    })()}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Ações Rápidas */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">⚡ Ações Rápidas</h2>
            <p className="text-gray-600">Acesse as funcionalidades principais</p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-4">
                <button
                  onClick={() => setCurrentView('chamada')}
                  className="w-full px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-green-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                >
                  <span className="text-xl mr-2">✅</span>
                  Fazer Chamada
                </button>
                {currentUser?.tipo === 'admin' && (
                  <>
                    <button
                      onClick={() => setCurrentView('relatorios')}
                      className="w-full px-6 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                    >
                      <span className="text-xl mr-2">📊</span>
                      Relatórios Detalhados
                    </button>
                    <button
                      onClick={() => {
                        setActiveTab('alunos');
                        setCurrentView('ranking');
                      }}
                      className="w-full px-6 py-4 bg-gradient-to-r from-yellow-500 to-orange-600 text-white rounded-lg hover:from-yellow-600 hover:to-orange-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                    >
                      <span className="text-xl mr-2">🏆</span>
                      Rankings
                    </button>
                  </>
                )}
              </div>

              {currentUser?.tipo === 'admin' && (
                <div className="space-y-4">
                  <button
                    onClick={() => setCurrentView('alunos')}
                    className="w-full px-6 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                  >
                    <span className="text-xl mr-2">👥</span>
                    Gerenciar Alunos
                  </button>
                  <button
                    onClick={() => setCurrentView('turmas')}
                    className="w-full px-6 py-4 bg-gradient-to-r from-teal-500 to-green-600 text-white rounded-lg hover:from-teal-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-teal-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                  >
                    <span className="text-xl mr-2">🏫</span>
                    Gerenciar Turmas
                  </button>
                  <button
                    onClick={() => setCurrentView('usuarios')}
                    className="w-full px-6 py-4 bg-gradient-to-r from-rose-500 to-pink-600 text-white rounded-lg hover:from-rose-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-rose-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                  >
                    <span className="text-xl mr-2">👤</span>
                    Gerenciar Usuários
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(Dashboard);