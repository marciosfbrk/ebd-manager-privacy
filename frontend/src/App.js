import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [turmas, setTurmas] = useState([]);
  const [students, setStudents] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [selectedTurma, setSelectedTurma] = useState(null);
  const [selectedDate, setSelectedDate] = useState('2025-07-13');
  const [loading, setLoading] = useState(false);

  // Carregar dados iniciais
  useEffect(() => {
    loadTurmas();
    loadStudents();
    loadDashboard();
  }, []);

  const loadInitialData = async () => {
    try {
      await axios.post(`${API}/init-church-data`);
      await loadTurmas();
      await loadStudents();
      await loadDashboard();
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
    }
  };

  const loadTurmas = async () => {
    try {
      const response = await axios.get(`${API}/turmas`);
      setTurmas(response.data);
    } catch (error) {
      console.error('Erro ao carregar turmas:', error);
    }
  };

  const loadStudents = async () => {
    try {
      const response = await axios.get(`${API}/students`);
      setStudents(response.data);
    } catch (error) {
      console.error('Erro ao carregar alunos:', error);
    }
  };

  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API}/reports/dashboard?data=${selectedDate}`);
      setAttendanceData(response.data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    }
  };

  const loadAttendanceForTurma = async (turmaId, date) => {
    try {
      const response = await axios.get(`${API}/attendance?turma_id=${turmaId}&data=${date}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao carregar presença:', error);
      return [];
    }
  };

  const saveAttendance = async (turmaId, date, attendanceList) => {
    try {
      setLoading(true);
      
      // Prepare data for API
      const attendanceData = attendanceList.map(att => ({
        aluno_id: att.aluno_id,
        status: att.status,
        oferta: parseFloat(att.oferta) || 0,
        biblias_entregues: parseInt(att.biblias_entregues) || 0,
        revistas_entregues: parseInt(att.revistas_entregues) || 0
      }));

      const response = await axios.post(`${API}/attendance/bulk/${turmaId}?data=${date}`, attendanceData);
      
      await loadDashboard();
      alert('Chamada salva com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar chamada:', error);
      if (error.response?.data?.detail) {
        alert(`Erro: ${error.response.data.detail}`);
      } else {
        alert('Erro ao salvar chamada');
      }
    } finally {
      setLoading(false);
    }
  };

  const isSunday = (dateString) => {
    const date = new Date(dateString + 'T00:00:00');
    return date.getDay() === 0;
  };

  // Componente Dashboard
  const Dashboard = () => (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">EBD Manager</h1>
          <p className="text-gray-600">Sistema de Gerenciamento da Escola Bíblica Dominical</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Relatório do Dia</h2>
            <div className="flex items-center space-x-4">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={loadDashboard}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Atualizar
              </button>
            </div>
          </div>

          {!isSunday(selectedDate) && (
            <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
              <strong>Aviso:</strong> A data selecionada não é um domingo.
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-200">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-gray-300 px-4 py-2 text-left">Turma</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Matriculados</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Presentes</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Ausentes</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Visitantes</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Pós-Chamada</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Ofertas</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Bíblias</th>
                  <th className="border border-gray-300 px-4 py-2 text-center">Revistas</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="border border-gray-300 px-4 py-2 font-medium">{row.turma_nome}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.matriculados}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.presentes}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.ausentes}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.visitantes}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.pos_chamada}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">R$ {row.total_ofertas.toFixed(2)}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.total_biblias}</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">{row.total_revistas}</td>
                  </tr>
                ))}
                {attendanceData.length > 0 && (
                  <tr className="bg-blue-50 font-semibold">
                    <td className="border border-gray-300 px-4 py-2">TOTAL GERAL</td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.matriculados, 0)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.presentes, 0)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.ausentes, 0)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.visitantes, 0)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.pos_chamada, 0)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      R$ {attendanceData.reduce((sum, row) => sum + row.total_ofertas, 0).toFixed(2)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.total_biblias, 0)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2 text-center">
                      {attendanceData.reduce((sum, row) => sum + row.total_revistas, 0)}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Ações Rápidas</h3>
            <div className="space-y-3">
              <button
                onClick={() => setCurrentView('chamada')}
                className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Fazer Chamada
              </button>
              <button
                onClick={() => setCurrentView('relatorios')}
                className="w-full px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Relatórios Detalhados
              </button>
              <button
                onClick={() => setCurrentView('alunos')}
                className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Gerenciar Alunos
              </button>
              <button
                onClick={() => setCurrentView('turmas')}
                className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                Gerenciar Turmas
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Resumo</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Total de Turmas:</span>
                <span className="font-semibold">{turmas.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total de Alunos:</span>
                <span className="font-semibold">{students.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Presentes Hoje:</span>
                <span className="font-semibold text-green-600">
                  {attendanceData.reduce((sum, row) => sum + row.presentes, 0)}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Dicas</h3>
            <div className="text-sm text-gray-600 space-y-2">
              <p>• A chamada só pode ser feita aos domingos</p>
              <p>• Use a tela de chamada para registrar presença e ofertas</p>
              <p>• O relatório é atualizado automaticamente</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Função para calcular classes vencedoras usando a mesma lógica do Excel
  const calcularClassesVencedoras = () => {
    if (!attendanceData || attendanceData.length === 0) return {};

    // Preparar dados com porcentagem de frequência (como decimal 0-1)
    const turmasComFrequencia = attendanceData.map(turma => ({
      ...turma,
      porcentagem_frequencia_decimal: turma.matriculados > 0 ? (turma.presentes / turma.matriculados) : 0
    }));

    // Definir ranges como no Excel (baseado na ordem das turmas)
    const ranges = {
      'Infantil': {
        start: 0, // Primeiras turmas (equivale às linhas 5-8 do Excel)
        end: Math.min(4, turmasComFrequencia.length - 1)
      },
      'Jovens e Adolescentes': {
        start: Math.min(4, turmasComFrequencia.length),
        end: Math.min(6, turmasComFrequencia.length - 1)
      },
      'Adulto': {
        start: Math.min(6, turmasComFrequencia.length),
        end: turmasComFrequencia.length - 1
      }
    };

    const vencedores = {};

    // Para cada departamento, aplicar lógica ÍNDICE + CORRESP + MÁXIMO
    Object.keys(ranges).forEach(dept => {
      const range = ranges[dept];
      
      if (range.start <= range.end && range.start < turmasComFrequencia.length) {
        const turmasRange = turmasComFrequencia.slice(range.start, range.end + 1);
        
        if (turmasRange.length > 0) {
          // CLASSE VENCEDORA EM FREQUÊNCIA
          // Lógica: MÁXIMO(J5:J8) para encontrar maior frequência
          const maxFrequencia = Math.max(...turmasRange.map(t => t.porcentagem_frequencia_decimal));
          // ÍNDICE + CORRESP para encontrar nome da turma correspondente
          const vencedorFrequencia = turmasRange.find(t => t.porcentagem_frequencia_decimal === maxFrequencia);

          // CLASSE VENCEDORA EM OFERTA  
          // Lógica: MÁXIMO(G5:G8) para encontrar maior oferta
          const maxOferta = Math.max(...turmasRange.map(t => t.total_ofertas));
          // ÍNDICE + CORRESP para encontrar nome da turma correspondente
          const vencedorOferta = turmasRange.find(t => t.total_ofertas === maxOferta);

          vencedores[dept] = {
            frequencia: {
              turma_nome: vencedorFrequencia.turma_nome,
              porcentagem: Math.round(maxFrequencia * 100 * 100) / 100 // ARRED(*100;2)
            },
            oferta: {
              turma_nome: vencedorOferta.turma_nome,
              valor: Math.round(maxOferta * 100) / 100 // ARRED(;2)
            }
          };
        }
      }
    });

    return vencedores;
  };

  // Componente Relatórios
  const Relatorios = () => {
    const classesVencedoras = calcularClassesVencedoras();

    const formatarPorcentagem = (valor) => {
      return isNaN(valor) ? '0,00' : valor.toFixed(2).replace('.', ',');
    };

    const formatarValor = (valor) => {
      return isNaN(valor) ? '0,00' : valor.toFixed(2).replace('.', ',');
    };

    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Relatórios Detalhados</h1>
            <p className="text-gray-600">Relatório consolidado e classes vencedoras por departamento</p>
          </div>

          {/* Controles de Data */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">Relatório do Dia</h2>
              <div className="flex items-center space-x-4">
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={loadDashboard}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Atualizar
                </button>
              </div>
            </div>

            {!isSunday(selectedDate) && (
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
                <strong>Aviso:</strong> A data selecionada não é um domingo.
              </div>
            )}

            {/* Tabela de Consolidação */}
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left">Turma</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Matriculados</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Presentes</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Ausentes</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Visitantes</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Pós-Chamada</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Ofertas</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Bíblias</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Revistas</th>
                  </tr>
                </thead>
                <tbody>
                  {attendanceData.map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 font-medium">{row.turma_nome}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.matriculados}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.presentes}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.ausentes}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.visitantes}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.pos_chamada}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">R$ {row.total_ofertas.toFixed(2)}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.total_biblias}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">{row.total_revistas}</td>
                    </tr>
                  ))}
                  {attendanceData.length > 0 && (
                    <tr className="bg-blue-50 font-semibold">
                      <td className="border border-gray-300 px-4 py-2">TOTAL GERAL</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.matriculados, 0)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.presentes, 0)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.ausentes, 0)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.visitantes, 0)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.pos_chamada, 0)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        R$ {attendanceData.reduce((sum, row) => sum + row.total_ofertas, 0).toFixed(2)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.total_biblias, 0)}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.total_revistas, 0)}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Classes Vencedoras */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Classes Vencedoras por Departamento</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Departamento Infantil */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-green-700 border-b-2 border-green-200 pb-2">
                  Departamento Infantil
                </h3>
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-800 mb-2">
                    Classe Vencedora em Frequência do departamento Infantil
                  </h4>
                  <p className="text-green-700">
                    {classesVencedoras['Infantil']?.frequencia ? (
                      <>
                        Nome: <span className="font-semibold">{classesVencedoras['Infantil'].frequencia.turma_nome}</span> – 
                        Porcentagem: <span className="font-semibold">{formatarPorcentagem(classesVencedoras['Infantil'].frequencia.porcentagem)}%</span>
                      </>
                    ) : (
                      'Nenhuma turma encontrada para este departamento'
                    )}
                  </p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-800 mb-2">
                    Classe Vencedora em Oferta do departamento Infantil
                  </h4>
                  <p className="text-green-700">
                    {classesVencedoras['Infantil']?.oferta ? (
                      <>
                        Nome: <span className="font-semibold">{classesVencedoras['Infantil'].oferta.turma_nome}</span> – 
                        Máximo: <span className="font-semibold">R$ {formatarValor(classesVencedoras['Infantil'].oferta.valor)}</span>
                      </>
                    ) : (
                      'Nenhuma turma encontrada para este departamento'
                    )}
                  </p>
                </div>
              </div>

              {/* Departamento Jovens e Adolescentes */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-blue-700 border-b-2 border-blue-200 pb-2">
                  Departamento Jovens e Adolescentes
                </h3>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2">
                    Classe Vencedora em Frequência do departamento Jovens e Adolescentes
                  </h4>
                  <p className="text-blue-700">
                    {classesVencedoras['Jovens e Adolescentes']?.frequencia ? (
                      <>
                        Nome: <span className="font-semibold">{classesVencedoras['Jovens e Adolescentes'].frequencia.turma_nome}</span> – 
                        Porcentagem: <span className="font-semibold">{formatarPorcentagem(classesVencedoras['Jovens e Adolescentes'].frequencia.porcentagem)}%</span>
                      </>
                    ) : (
                      'Nenhuma turma encontrada para este departamento'
                    )}
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2">
                    Classe Vencedora em Oferta do departamento Jovens e Adolescentes
                  </h4>
                  <p className="text-blue-700">
                    {classesVencedoras['Jovens e Adolescentes']?.oferta ? (
                      <>
                        Nome: <span className="font-semibold">{classesVencedoras['Jovens e Adolescentes'].oferta.turma_nome}</span> – 
                        Máximo: <span className="font-semibold">R$ {formatarValor(classesVencedoras['Jovens e Adolescentes'].oferta.valor)}</span>
                      </>
                    ) : (
                      'Nenhuma turma encontrada para este departamento'
                    )}
                  </p>
                </div>
              </div>

              {/* Departamento Adulto */}
              <div className="space-y-4 md:col-span-2">
                <h3 className="text-lg font-medium text-purple-700 border-b-2 border-purple-200 pb-2">
                  Departamento Adulto
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="font-semibold text-purple-800 mb-2">
                      Classe Vencedora em Frequência do departamento Adulto
                    </h4>
                    <p className="text-purple-700">
                      {classesVencedoras['Adulto']?.frequencia ? (
                        <>
                          Nome: <span className="font-semibold">{classesVencedoras['Adulto'].frequencia.turma_nome}</span> – 
                          Porcentagem: <span className="font-semibold">{formatarPorcentagem(classesVencedoras['Adulto'].frequencia.porcentagem)}%</span>
                        </>
                      ) : (
                        'Nenhuma turma encontrada para este departamento'
                      )}
                    </p>
                  </div>

                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="font-semibold text-purple-800 mb-2">
                      Classe Vencedora em Oferta do departamento Adulto
                    </h4>
                    <p className="text-purple-700">
                      {classesVencedoras['Adulto']?.oferta ? (
                        <>
                          Nome: <span className="font-semibold">{classesVencedoras['Adulto'].oferta.turma_nome}</span> – 
                          Máximo: <span className="font-semibold">R$ {formatarValor(classesVencedoras['Adulto'].oferta.valor)}</span>
                        </>
                      ) : (
                        'Nenhuma turma encontrada para este departamento'
                      )}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Informações Adicionais */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-700 mb-2">Critérios de Classificação:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• <strong>Frequência:</strong> Calculada como (Presentes ÷ Matriculados) × 100, arredondada com 2 casas decimais</li>
                <li>• <strong>Oferta:</strong> Baseada no valor total de ofertas da turma, arredondada com 2 casas decimais</li>
                <li>• <strong>Departamentos:</strong> Baseados na posição das turmas (Infantil: primeiras, Jovens: intermediárias, Adulto: últimas)</li>
                <li>• <strong>Lógica Excel:</strong> Equivalente a ÍNDICE + CORRESP + MÁXIMO para encontrar vencedores</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };
  const Chamada = () => {
    const [turmaAtendance, setTurmaAtendance] = useState([]);
    const [turmaDataGlobal, setTurmaDataGlobal] = useState({
      ofertas_total: '',
      biblias_total: '',
      revistas_total: '',
      visitantes_total: '',
      pos_chamada_total: ''
    });

    useEffect(() => {
      if (selectedTurma) {
        loadTurmaData();
      }
    }, [selectedTurma, selectedDate]);

    const loadTurmaData = async () => {
      if (!selectedTurma) return;

      try {
        const studentsInTurma = students.filter(s => s.turma_id === selectedTurma);

        const existingAttendance = await loadAttendanceForTurma(selectedTurma, selectedDate);
        
        // Calcular totais existentes
        let totalOfertas = 0;
        let totalBiblias = 0;
        let totalRevistas = 0;
        let totalVisitantes = 0;
        let totalPosChamada = 0;

        const attendanceMap = {};
        existingAttendance.forEach(att => {
          attendanceMap[att.aluno_id] = att;
          totalOfertas += att.oferta || 0;
          totalBiblias += att.biblias_entregues || 0;
          totalRevistas += att.revistas_entregues || 0;
          if (att.status === 'visitante') totalVisitantes++;
          if (att.status === 'pos_chamada') totalPosChamada++;
        });

        setTurmaDataGlobal({
          ofertas_total: totalOfertas,
          biblias_total: totalBiblias,
          revistas_total: totalRevistas,
          visitantes_total: totalVisitantes,
          pos_chamada_total: totalPosChamada
        });

        const attendanceData = studentsInTurma.map(student => ({
          aluno_id: student.id,
          nome: student.nome_completo,
          presente: attendanceMap[student.id]?.status === 'presente' || false
        }));

        setTurmaAtendance(attendanceData);
      } catch (error) {
        console.error('Erro ao carregar dados da turma:', error);
      }
    };

    const togglePresenca = (alunoId) => {
      setTurmaAtendance(prev => 
        prev.map(att => 
          att.aluno_id === alunoId ? { ...att, presente: !att.presente } : att
        )
      );
    };

    const updateTurmaData = (field, value) => {
      if (value === '') {
        setTurmaDataGlobal(prev => ({
          ...prev,
          [field]: ''
        }));
      } else {
        // Substituir vírgula por ponto e arredondar para evitar problemas de precisão
        const numValue = parseFloat(value.replace(',', '.'));
        if (!isNaN(numValue)) {
          setTurmaDataGlobal(prev => ({
            ...prev,
            [field]: Math.round(numValue * 100) / 100  // Arredonda para 2 casas decimais
          }));
        }
      }
    };

    const handleSave = async () => {
      try {
        setLoading(true);
        
        const presentesCount = turmaAtendance.filter(att => att.presente).length;
        
        // Converter valores para números, tratando strings vazias como 0
        const ofertaTotal = parseFloat(turmaDataGlobal.ofertas_total) || 0;
        const bibliasTotal = parseInt(turmaDataGlobal.biblias_total) || 0;
        const revistasTotal = parseInt(turmaDataGlobal.revistas_total) || 0;
        const visitantesTotal = parseInt(turmaDataGlobal.visitantes_total) || 0;
        const posChamadaTotal = parseInt(turmaDataGlobal.pos_chamada_total) || 0;
        
        const attendanceList = turmaAtendance.map((att, index) => {
          let status = att.presente ? 'presente' : 'ausente';
          let oferta = 0;
          let biblias = 0;
          let revistas = 0;
          
          // Distribuir ofertas igualmente entre os presentes
          if (att.presente && presentesCount > 0) {
            oferta = Math.round((ofertaTotal / presentesCount) * 100) / 100;
          }
          
          // Dar bíblias e revistas apenas para o primeiro aluno (para não duplicar)
          if (index === 0) {
            biblias = bibliasTotal;
            revistas = revistasTotal;
          }
          
          // Aplicar visitantes e pós-chamada aos primeiros da lista
          if (index < visitantesTotal) {
            status = 'visitante';
          } else if (index < visitantesTotal + posChamadaTotal) {
            status = 'pos_chamada';
          }

          return {
            aluno_id: att.aluno_id,
            status: status,
            oferta: oferta,
            biblias_entregues: biblias,
            revistas_entregues: revistas
          };
        });

        await axios.post(`${API}/attendance/bulk/${selectedTurma}?data=${selectedDate}`, attendanceList);
        
        await loadDashboard();
        alert('Chamada salva com sucesso!');
      } catch (error) {
        console.error('Erro ao salvar chamada:', error);
        if (error.response?.data?.detail) {
          alert(`Erro: ${error.response.data.detail}`);
        } else {
          alert('Erro ao salvar chamada');
        }
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Fazer Chamada</h1>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Turma</label>
                <select
                  value={selectedTurma || ''}
                  onChange={(e) => setSelectedTurma(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Selecione uma turma</option>
                  {turmas.map(turma => (
                    <option key={turma.id} value={turma.id}>{turma.nome}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Data</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {!isSunday(selectedDate) && (
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
                <strong>Aviso:</strong> A data selecionada não é um domingo.
              </div>
            )}

            {selectedTurma && (
              <div>
                {/* Campos Globais da Turma */}
                <div className="bg-blue-50 p-6 rounded-lg mb-6">
                  <h3 className="text-xl font-semibold text-blue-800 mb-4">Dados da Turma</h3>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Oferta Total (R$)</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.ofertas_total || ''}
                        onChange={(e) => updateTurmaData('ofertas_total', e.target.value)}
                        className="w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Bíblias</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.biblias_total || ''}
                        onChange={(e) => updateTurmaData('biblias_total', e.target.value)}
                        className="w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Revistas</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.revistas_total || ''}
                        onChange={(e) => updateTurmaData('revistas_total', e.target.value)}
                        className="w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Visitantes</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.visitantes_total || ''}
                        onChange={(e) => updateTurmaData('visitantes_total', e.target.value)}
                        className="w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Pós-Chamada</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.pos_chamada_total || ''}
                        onChange={(e) => updateTurmaData('pos_chamada_total', e.target.value)}
                        className="w-full px-4 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                  </div>
                </div>

                {/* Lista de Presença Simples */}
                <div className="bg-white border rounded-lg overflow-hidden mb-6">
                  <div className="bg-gray-100 px-6 py-4 border-b flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-800">
                        {turmas.find(t => t.id === selectedTurma)?.nome}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">Clique nos nomes para marcar presença</p>
                      <div className="flex space-x-6 mt-2 text-sm">
                        <span className="text-green-700 font-medium">
                          Presentes: {turmaAtendance.filter(att => att.presente).length}
                        </span>
                        <span className="text-red-700 font-medium">
                          Ausentes: {turmaAtendance.filter(att => !att.presente).length}
                        </span>
                        <span className="text-blue-700 font-medium">
                          Frequência: {turmaAtendance.length > 0 
                            ? ((turmaAtendance.filter(att => att.presente).length / turmaAtendance.length) * 100).toFixed(1)
                            : 0}%
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={handleSave}
                      disabled={loading}
                      className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-400 text-lg font-semibold"
                    >
                      {loading ? 'Salvando...' : 'Salvar Chamada'}
                    </button>
                  </div>
                  
                  <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {turmaAtendance.map((att, index) => (
                        <button
                          key={index}
                          onClick={() => togglePresenca(att.aluno_id)}
                          className={`p-4 rounded-lg text-left transition-all duration-200 ${
                            att.presente 
                              ? 'bg-green-100 border-2 border-green-500 text-green-800' 
                              : 'bg-gray-100 border-2 border-gray-300 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          <div className="flex items-center">
                            <div className={`w-4 h-4 rounded-full mr-3 ${
                              att.presente ? 'bg-green-500' : 'bg-gray-400'
                            }`}></div>
                            <span className="font-medium">{att.nome}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Resumo */}
                <div className="p-6 bg-green-50 rounded-lg">
                  <h4 className="text-lg font-semibold text-green-800 mb-3">Resumo</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {turmaAtendance.filter(att => att.presente).length}
                      </div>
                      <div className="text-sm text-green-700">Presentes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">
                        {turmaAtendance.filter(att => !att.presente).length}
                      </div>
                      <div className="text-sm text-red-700">Ausentes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {turmaAtendance.length}
                      </div>
                      <div className="text-sm text-blue-700">Total</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {turmaAtendance.length > 0 
                          ? ((turmaAtendance.filter(att => att.presente).length / turmaAtendance.length) * 100).toFixed(1)
                          : 0}%
                      </div>
                      <div className="text-sm text-purple-700">Frequência</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Componente Alunos
  const Alunos = () => {
    const [showForm, setShowForm] = useState(false);
    const [editingStudent, setEditingStudent] = useState(null);
    const [showTransferForm, setShowTransferForm] = useState(false);
    const [transferringStudent, setTransferringStudent] = useState(null);
    const [formData, setFormData] = useState({
      nome_completo: '',
      data_nascimento: '',
      contato: '',
      turma_id: ''
    });
    const [transferData, setTransferData] = useState({
      nova_turma_id: ''
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        if (editingStudent) {
          await axios.put(`${API}/students/${editingStudent.id}`, formData);
        } else {
          await axios.post(`${API}/students`, formData);
        }
        await loadStudents();
        setShowForm(false);
        setEditingStudent(null);
        setFormData({ nome_completo: '', data_nascimento: '', contato: '', turma_id: '' });
        alert('Aluno salvo com sucesso!');
      } catch (error) {
        console.error('Erro ao salvar aluno:', error);
        if (error.response?.data?.detail) {
          alert(`Erro: ${error.response.data.detail}`);
        } else {
          alert('Erro ao salvar aluno');
        }
      }
    };

    const handleTransferSubmit = async (e) => {
      e.preventDefault();
      try {
        await axios.post(`${API}/students/${transferringStudent.id}/transfer`, transferData);
        await loadStudents();
        setShowTransferForm(false);
        setTransferringStudent(null);
        setTransferData({ nova_turma_id: '' });
        alert('Aluno transferido com sucesso!');
      } catch (error) {
        console.error('Erro ao transferir aluno:', error);
        if (error.response?.data?.detail) {
          alert(`Erro: ${error.response.data.detail}`);
        } else {
          alert('Erro ao transferir aluno');
        }
      }
    };

    const handleEdit = (student) => {
      setEditingStudent(student);
      setFormData({
        nome_completo: student.nome_completo,
        data_nascimento: student.data_nascimento,
        contato: student.contato,
        turma_id: student.turma_id
      });
      setShowForm(true);
    };

    const handleTransfer = (student) => {
      setTransferringStudent(student);
      setTransferData({ nova_turma_id: '' });
      setShowTransferForm(true);
    };

    const handleDelete = async (studentId) => {
      if (window.confirm('Tem certeza que deseja remover este aluno?')) {
        try {
          await axios.delete(`${API}/students/${studentId}`);
          await loadStudents();
          alert('Aluno removido com sucesso!');
        } catch (error) {
          console.error('Erro ao remover aluno:', error);
          if (error.response?.data?.detail) {
            alert(`Erro: ${error.response.data.detail}`);
          } else {
            alert('Erro ao remover aluno');
          }
        }
      }
    };

    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <div className="flex justify-between items-center">
              <h1 className="text-3xl font-bold text-gray-800">Gerenciar Alunos</h1>
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Novo Aluno
              </button>
            </div>
          </div>

          {showForm && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {editingStudent ? 'Editar Aluno' : 'Novo Aluno'}
              </h2>
              <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nome Completo</label>
                  <input
                    type="text"
                    value={formData.nome_completo}
                    onChange={(e) => setFormData({...formData, nome_completo: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Data de Nascimento</label>
                  <input
                    type="date"
                    value={formData.data_nascimento}
                    onChange={(e) => setFormData({...formData, data_nascimento: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contato</label>
                  <input
                    type="text"
                    value={formData.contato}
                    onChange={(e) => setFormData({...formData, contato: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Turma</label>
                  <select
                    value={formData.turma_id}
                    onChange={(e) => setFormData({...formData, turma_id: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Selecione uma turma</option>
                    {turmas.map(turma => (
                      <option key={turma.id} value={turma.id}>{turma.nome}</option>
                    ))}
                  </select>
                </div>
                <div className="md:col-span-2 flex space-x-4">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {editingStudent ? 'Atualizar' : 'Criar'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingStudent(null);
                      setFormData({ nome_completo: '', data_nascimento: '', contato: '', turma_id: '' });
                    }}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          )}

          {showTransferForm && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Transferir Aluno: {transferringStudent?.nome_completo}
              </h2>
              <form onSubmit={handleTransferSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nova Turma</label>
                  <select
                    value={transferData.nova_turma_id}
                    onChange={(e) => setTransferData({nova_turma_id: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Selecione a nova turma</option>
                    {turmas.filter(t => t.id !== transferringStudent?.turma_id).map(turma => (
                      <option key={turma.id} value={turma.id}>{turma.nome}</option>
                    ))}
                  </select>
                </div>
                <div className="flex space-x-4">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500"
                  >
                    Transferir
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowTransferForm(false);
                      setTransferringStudent(null);
                      setTransferData({ nova_turma_id: '' });
                    }}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Lista de Alunos</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left">Nome</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Data Nascimento</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Contato</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Turma</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr key={student.id} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2">{student.nome_completo}</td>
                      <td className="border border-gray-300 px-4 py-2">{student.data_nascimento}</td>
                      <td className="border border-gray-300 px-4 py-2">{student.contato}</td>
                      <td className="border border-gray-300 px-4 py-2">
                        {turmas.find(t => t.id === student.turma_id)?.nome || 'N/A'}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        <button
                          onClick={() => handleEdit(student)}
                          className="mr-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleTransfer(student)}
                          className="mr-2 px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600"
                        >
                          Transferir
                        </button>
                        <button
                          onClick={() => handleDelete(student.id)}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Remover
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Componente Turmas
  const Turmas = () => {
    const [showForm, setShowForm] = useState(false);
    const [editingTurma, setEditingTurma] = useState(null);
    const [formData, setFormData] = useState({
      nome: '',
      descricao: ''
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        if (editingTurma) {
          await axios.put(`${API}/turmas/${editingTurma.id}`, formData);
        } else {
          await axios.post(`${API}/turmas`, formData);
        }
        await loadTurmas();
        setShowForm(false);
        setEditingTurma(null);
        setFormData({ nome: '', descricao: '' });
        alert('Turma salva com sucesso!');
      } catch (error) {
        console.error('Erro ao salvar turma:', error);
        if (error.response?.data?.detail) {
          alert(`Erro: ${error.response.data.detail}`);
        } else {
          alert('Erro ao salvar turma');
        }
      }
    };

    const handleEdit = (turma) => {
      setEditingTurma(turma);
      setFormData({
        nome: turma.nome,
        descricao: turma.descricao || ''
      });
      setShowForm(true);
    };

    const handleDelete = async (turmaId) => {
      if (window.confirm('Tem certeza que deseja remover esta turma?')) {
        try {
          await axios.delete(`${API}/turmas/${turmaId}`);
          await loadTurmas();
          alert('Turma removida com sucesso!');
        } catch (error) {
          console.error('Erro ao remover turma:', error);
          if (error.response?.data?.detail) {
            alert(`Erro: ${error.response.data.detail}`);
          } else {
            alert('Erro ao remover turma');
          }
        }
      }
    };

    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <div className="flex justify-between items-center">
              <h1 className="text-3xl font-bold text-gray-800">Gerenciar Turmas</h1>
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Nova Turma
              </button>
            </div>
          </div>

          {showForm && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {editingTurma ? 'Editar Turma' : 'Nova Turma'}
              </h2>
              <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nome</label>
                  <input
                    type="text"
                    value={formData.nome}
                    onChange={(e) => setFormData({...formData, nome: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
                  <input
                    type="text"
                    value={formData.descricao}
                    onChange={(e) => setFormData({...formData, descricao: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="md:col-span-2 flex space-x-4">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {editingTurma ? 'Atualizar' : 'Criar'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingTurma(null);
                      setFormData({ nome: '', descricao: '' });
                    }}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Lista de Turmas</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left">Nome</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Descrição</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Alunos</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {turmas.map((turma) => (
                    <tr key={turma.id} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 font-medium">{turma.nome}</td>
                      <td className="border border-gray-300 px-4 py-2">{turma.descricao || 'N/A'}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {students.filter(s => s.turma_id === turma.id).length}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        <button
                          onClick={() => handleEdit(turma)}
                          className="mr-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(turma.id)}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                          Remover
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Renderização condicional
  const renderCurrentView = () => {
    switch(currentView) {
      case 'chamada':
        return <Chamada />;
      case 'relatorios':
        return <Relatorios />;
      case 'alunos':
        return <Alunos />;
      case 'turmas':
        return <Turmas />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {renderCurrentView()}
    </div>
  );
}

export default App;