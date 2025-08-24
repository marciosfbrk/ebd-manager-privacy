import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

// API URL - Usar variável de ambiente
const API = process.env.REACT_APP_BACKEND_URL;

function App() {
  // Funções utilitárias para cálculo de datas
  const isSunday = (dateString) => {
    const date = new Date(dateString + 'T00:00:00');
    return date.getDay() === 0;
  };

  // Função para obter o último domingo (para relatórios)
  const getLastSunday = () => {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = domingo, 1 = segunda, etc.
    
    if (dayOfWeek === 0) {
      // Se hoje é domingo, retorna hoje
      return today.toISOString().split('T')[0];
    } else {
      // Se não é domingo, retorna o domingo anterior
      const lastSunday = new Date(today);
      lastSunday.setDate(today.getDate() - dayOfWeek);
      return lastSunday.toISOString().split('T')[0];
    }
  };

  // Função para obter o próximo domingo (para chamadas)
  const getCurrentSunday = () => {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = domingo, 1 = segunda, etc.
    
    if (dayOfWeek === 0) {
      // Se hoje é domingo, retorna hoje
      return today.toISOString().split('T')[0];
    } else {
      // Se não é domingo, retorna o próximo domingo
      const nextSunday = new Date(today);
      nextSunday.setDate(today.getDate() + (7 - dayOfWeek));
      return nextSunday.toISOString().split('T')[0];
    }
  };

  const [currentView, setCurrentView] = useState('home');
  const [showApp, setShowApp] = useState(false);
  const [turmas, setTurmas] = useState([]);
  const [students, setStudents] = useState([]);
  
  // Estados para filtros de alunos
  const [searchFilter, setSearchFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState(''); // Termo atual de busca
  const [turmaFilter, setTurmaFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('todos');
  const [attendanceData, setAttendanceData] = useState([]);
  const [selectedTurma, setSelectedTurma] = useState(null);
  const [selectedDate, setSelectedDate] = useState(() => getLastSunday());
  const [loading, setLoading] = useState(false);
  
  // Estados de ranking
  const [rankingAlunos, setRankingAlunos] = useState([]);
  const [rankingProfessores, setRankingProfessores] = useState([]);
  const [rankingTurmas, setRankingTurmas] = useState([]);
  
  // Estados para backup e restore
  const [backupData, setBackupData] = useState(null);
  const [restoreLoading, setRestoreLoading] = useState(false);
  const [backupLoading, setBackupLoading] = useState(false);
  
  // Estados para logs de acesso - NOVO
  const [accessLogs, setAccessLogs] = useState([]);
  const [logStats, setLogStats] = useState({});
  const [logsLoading, setLogsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('alunos');
  
  // Estados para configurações do sistema - NOVO
  const [systemConfig, setSystemConfig] = useState({});
  const [configLoading, setConfigLoading] = useState(false);
  
  // Estados de revistas
  const [revistas, setRevistas] = useState([]);
  const [revistaAtual, setRevistaAtual] = useState(null);
  
  // Estados de autenticação
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(null);
  const [showLogin, setShowLogin] = useState(false);

  // Verificar se há sessão salva ao carregar
  useEffect(() => {
    const savedToken = localStorage.getItem('ebd_token');
    const savedUser = localStorage.getItem('ebd_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setCurrentUser(JSON.parse(savedUser));
      setIsLoggedIn(true);
      loadTurmas();
      loadStudents();
      loadDashboard();
      
      // Redirecionar para dashboard se já estiver logado
      setCurrentView('dashboard');
    }
  }, []);

  // Atualizar data automaticamente baseado na view atual
  useEffect(() => {
    if (currentView === 'chamada') {
      // Para chamadas, usar o domingo atual/próximo
      setSelectedDate(getCurrentSunday());
    } else if (currentView === 'dashboard' || currentView === 'reports') {
      // Para relatórios, usar o último domingo
      setSelectedDate(getLastSunday());
    }
  }, [currentView]);

  // Função de login
  const handleLogin = async (email, senha) => {
    try {
      const response = await axios.post(`${API}/login`, { email, senha });
      const { user_id, nome, email: userEmail, tipo, turmas_permitidas, token: userToken } = response.data;
      
      const userData = { user_id, nome, email: userEmail, tipo, turmas_permitidas };
      
      setToken(userToken);
      setCurrentUser(userData);
      setIsLoggedIn(true);
      setShowLogin(false);
      
      // Salvar no localStorage
      localStorage.setItem('ebd_token', userToken);
      localStorage.setItem('ebd_user', JSON.stringify(userData));
      
      // Carregar dados
      await loadTurmas();
      await loadStudents();
      await loadDashboard();
      
      // Redirecionar para dashboard após login bem-sucedido
      setCurrentView('dashboard');
      
      return { success: true };
    } catch (error) {
      console.error('Erro no login:', error);
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Erro ao fazer login'
      };
    }
  };

  // Função de logout
  const handleLogout = async () => {
    try {
      if (token) {
        await axios.post(`${API}/logout?token=${token}`);
      }
    } catch (error) {
      console.error('Erro no logout:', error);
    }
    
    setToken(null);
    setCurrentUser(null);
    setIsLoggedIn(false);
    setCurrentView('home');
    
    localStorage.removeItem('ebd_token');
    localStorage.removeItem('ebd_user');
  };

  // Filtrar turmas baseado nas permissões do usuário
  const getFilteredTurmas = () => {
    if (!currentUser) return turmas;
    
    if (currentUser.tipo === 'admin' || currentUser.tipo === 'moderador') {
      return turmas; // Admin e Moderador veem todas
    } else {
      // Professor vê apenas suas turmas
      return turmas.filter(turma => currentUser.turmas_permitidas.includes(turma.id));
    }
  };

  // Carregar dados iniciais
  useEffect(() => {
    loadTurmas();
    loadStudents();
    loadDashboard();
    // REMOVER loadRevistas() daqui - será carregado só quando necessário
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

  // Função para filtrar alunos (VERSÃO SIMPLES)
  const getFilteredStudents = () => {
    return students.filter(student => {
      // Filtro por nome (usa searchTerm após clicar em buscar)
      const matchesSearch = searchTerm === '' || student.nome_completo.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Filtro por turma
      const matchesTurma = turmaFilter === '' || student.turma_id === turmaFilter;
      
      // Filtro por status (ativo/inativo)
      const matchesStatus = statusFilter === 'todos' || 
                           (statusFilter === 'ativo' && student.ativo) ||
                           (statusFilter === 'inativo' && !student.ativo);
      
      return matchesSearch && matchesTurma && matchesStatus;
    });
  };

  // Função simples para executar busca
  const handleSearch = () => {
    setSearchTerm(searchFilter); // Aplica o filtro quando clica em buscar
  };

  // Limpar busca
  const handleClearSearch = () => {
    setSearchFilter('');
    setSearchTerm('');
  };

  const loadRevistas = async () => {
    try {
      const response = await axios.get(`${API}/revistas`);
      setRevistas(response.data);
    } catch (error) {
      console.error('Erro ao carregar revistas:', error);
    }
  };

  const loadRevistaByTurma = async (turmaId) => {
    try {
      const response = await axios.get(`${API}/revistas/turma/${turmaId}`);
      setRevistaAtual(response.data);
    } catch (error) {
      console.error('Erro ao carregar revista da turma:', error);
      setRevistaAtual(null);
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

  const loadRankings = async () => {
    try {
      const [alunosResponse, professoresResponse, turmasResponse] = await Promise.all([
        axios.get(`${API}/ranking/alunos`),
        axios.get(`${API}/ranking/professores-oficiais`),
        axios.get(`${API}/ranking/turmas`)
      ]);
      
      setRankingAlunos(alunosResponse.data);
      setRankingProfessores(professoresResponse.data);
      setRankingTurmas(turmasResponse.data);
    } catch (error) {
      console.error('Erro ao carregar rankings:', error);
    }
  };

  // Funções de Logs de Acesso - NOVO
  const loadAccessLogs = async () => {
    try {
      setLogsLoading(true);
      const response = await axios.get(`${API}/access-logs?limit=50`);
      setAccessLogs(response.data || []);
    } catch (error) {
      console.error('Erro ao carregar logs de acesso:', error);
      setAccessLogs([]);
    } finally {
      setLogsLoading(false);
    }
  };

  const loadAccessStats = async () => {
    try {
      const response = await axios.get(`${API}/access-logs/stats`);
      setLogStats(response.data || {});
    } catch (error) {
      console.error('Erro ao carregar estatísticas de logs:', error);
      setLogStats({});
    }
  };

  // Funções para Configurações do Sistema - NOVO
  const loadSystemConfig = async () => {
    try {
      setConfigLoading(true);
      const response = await axios.get(`${API}/system-config`);
      setSystemConfig(response.data || {});
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      setSystemConfig({});
    } finally {
      setConfigLoading(false);
    }
  };

  const updateSystemConfig = async (bloqueioAtivo, horario = "13:00") => {
    try {
      setConfigLoading(true);
      console.log("DEBUG updateConfig:", bloqueioAtivo, currentUser);
      await axios.put(`${API}/system-config?bloqueio_ativo=${bloqueioAtivo}&user_id=${currentUser.user_id || currentUser.id}&horario=${horario}`);
      await loadSystemConfig(); // Recarregar configurações
      alert('Configurações atualizadas com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar configurações:', error);
      console.error('Error details:', error.response?.data);
      alert(`Erro ao atualizar configurações: ${error.response?.data?.detail || error.message}`);
    } finally {
      setConfigLoading(false);
    }
  };

  // Funções de Backup e Restore
  const generateBackup = async () => {
    try {
      setBackupLoading(true);
      const response = await axios.get(`${API}/backup/generate`);
      
      if (response.data.success) {
        const backup = response.data.backup;
        const filename = response.data.filename;
        
        // Criar arquivo para download
        const dataStr = JSON.stringify(backup, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        // Fazer download
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert(`✅ Backup gerado com sucesso!\n\nArquivo: ${filename}\nTamanho: ${response.data.size_mb?.toFixed(2).replace('.', ',')} MB\n\nResumo:\n👥 Usuários: ${response.data.summary.users}\n🏫 Turmas: ${response.data.summary.turmas}\n📚 Alunos: ${response.data.summary.students}\n📊 Chamadas: ${response.data.summary.attendance}\n📖 Revistas: ${response.data.summary.revistas}`);
        
      } else {
        alert('❌ Erro ao gerar backup: ' + response.data.message);
      }
    } catch (error) {
      console.error('Erro ao gerar backup:', error);
      alert('❌ Erro ao gerar backup: ' + (error.response?.data?.detail || error.message));
    } finally {
      setBackupLoading(false);
    }
  };

  const handleRestoreFile = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const backupData = JSON.parse(e.target.result);
          
          // Validar estrutura do backup
          if (!backupData.data && !backupData.metadata) {
            alert('❌ Arquivo inválido: formato de backup não reconhecido');
            return;
          }
          
          // Mostrar informações do backup
          const metadata = backupData.metadata || {};
          const data = backupData.data || backupData; // Suporte a formatos antigos
          
          let confirmMessage = `📤 RESTORE DE BACKUP\n\n`;
          if (metadata.backup_date) {
            confirmMessage += `📅 Data do backup: ${new Date(metadata.backup_date).toLocaleString()}\n`;
          }
          if (metadata.total_records) {
            confirmMessage += `📊 Total de registros: ${metadata.total_records}\n`;
          }
          
          confirmMessage += `\n🔴 ATENÇÃO: Esta operação irá SUBSTITUIR todos os dados existentes!\n\n`;
          confirmMessage += `📋 Dados que serão restaurados:\n`;
          
          Object.keys(data).forEach(collection => {
            const count = data[collection]?.length || 0;
            const collectionNames = {
              users: '👤 Usuários',
              turmas: '🏫 Turmas', 
              students: '📚 Alunos',
              attendance: '📊 Chamadas',
              revistas: '📖 Revistas'
            };
            confirmMessage += `   ${collectionNames[collection] || collection}: ${count} registros\n`;
          });
          
          confirmMessage += `\n❓ Deseja continuar com o restore?`;
          
          if (window.confirm(confirmMessage)) {
            executeRestore(backupData);
          }
          
        } catch (error) {
          alert('❌ Erro ao ler arquivo: formato JSON inválido');
        }
      };
      reader.readAsText(file);
    }
    
    // Limpar input para permitir selecionar o mesmo arquivo novamente
    event.target.value = '';
  };

  const executeRestore = async (backupData) => {
    try {
      setRestoreLoading(true);
      
      const response = await axios.post(`${API}/backup/restore`, backupData);
      
      if (response.data.success) {
        const summary = response.data.restore_summary;
        let successMessage = `✅ Backup restaurado com sucesso!\n\n📊 Registros restaurados:\n`;
        
        Object.keys(summary).forEach(collection => {
          const count = summary[collection];
          const collectionNames = {
            users: '👤 Usuários',
            turmas: '🏫 Turmas',
            students: '📚 Alunos', 
            attendance: '📊 Chamadas',
            revistas: '📖 Revistas'
          };
          successMessage += `   ${collectionNames[collection] || collection}: ${count} registros\n`;
        });
        
        successMessage += `\n🔄 Total: ${response.data.total_restored} registros\n\n🔄 Recarregando sistema...`;
        
        alert(successMessage);
        
        // Recarregar dados
        await loadDashboard();
        await loadTurmas();
        await loadStudents();
        
      } else {
        alert('❌ Erro ao restaurar backup: ' + response.data.message);
      }
    } catch (error) {
      console.error('Erro ao restaurar backup:', error);
      alert('❌ Erro ao restaurar backup: ' + (error.response?.data?.detail || error.message));
    } finally {
      setRestoreLoading(false);
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
        oferta: parseFloat((att.oferta || '0').toString().replace(',', '.')) || 0,
        biblias_entregues: parseInt(att.biblias_entregues) || 0,
        revistas_entregues: parseInt(att.revistas_entregues) || 0
      }));

      const response = await axios.post(`${API}/attendance/bulk/${turmaId}?data=${date}&user_tipo=${currentUser.tipo}&user_id=${currentUser.user_id || currentUser.id}`, attendanceData);
      
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

  // Componente Dashboard
  const Dashboard = () => (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header Modernizado com Logo */}
        <div className="bg-gradient-to-r from-indigo-900 via-blue-800 to-indigo-900 text-white px-6 py-8 shadow-2xl">
          <div className="flex justify-between items-center mb-6">
            <button
              onClick={() => setCurrentView('home')}
              className="px-4 py-2 bg-white bg-opacity-20 text-white rounded-lg hover:bg-opacity-30 transition-all duration-200"
            >
              ← Início
            </button>
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg p-1">
                {/* Logo Ministério do Belém - Header */}
                <img 
                  src="/logo_belem.png" 
                  alt="Ministério do Belém" 
                  className="w-full h-full rounded-full object-cover"
                />
              </div>
              <div className="text-center">
                <h1 className="text-4xl font-bold tracking-wider">App EBD</h1>
                <div className="mt-2 text-sm text-blue-200 space-y-1">
                  <p>Presidente: <span className="font-semibold">Pr. José Felipe da Silva</span></p>
                  <p>Pastor Local: <span className="font-semibold">Pr. Henrique Ferreira Neto</span></p>
                  <p>Superintendente(EBD): <span className="font-semibold">Paulo Henrique da Silva Reis</span></p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-blue-200">
                <p>Logado como:</p>
                <p className="font-semibold text-white">{currentUser?.nome}</p>
                <p className="text-xs">({currentUser?.tipo === 'admin' ? 'Administrador' : currentUser?.tipo === 'moderador' ? 'Moderador' : 'Professor'})</p>
              </div>
              <button 
                onClick={handleLogout}
                className="mt-2 px-3 py-1 bg-red-500 bg-opacity-80 text-white rounded hover:bg-opacity-100 transition-all duration-200 text-sm"
              >
                Sair
              </button>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-blue-200 text-lg">Ministério Belém</p>
            <p className="text-blue-300 text-sm mt-1">Rua Managuá, 53 - Parque das Nações, Sumaré, SP</p>
            <p className="text-blue-300 text-sm">Sistema de Gerenciamento da Escola Bíblica Dominical</p>
            <p className="text-blue-400 text-xs mt-2">Desenvolvido por Márcio Ferreira</p>
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
                    return totalMatriculados > 0 ? ((totalPresentes / totalMatriculados) * 100).toFixed(1).replace('.', ',') : '0,0';
                  })()}%
                </div>
                <div className="text-sm text-purple-500 font-medium">Frequência</div>
              </div>
              
              <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  R$ {attendanceData.reduce((sum, row) => sum + row.total_ofertas, 0).toFixed(2).replace('.', ',')}
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
                          `${melhorFrequencia.turma_nome} (${((melhorFrequencia.presentes / melhorFrequencia.matriculados) * 100).toFixed(1).replace('.', ',')}%)` : 
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
                          `${maiorOferta.turma_nome} (R$ ${maiorOferta.total_ofertas.toFixed(2).replace('.', ',')})` : 
                          'Nenhuma turma';
                      })()}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Cards de Ações e Resumo */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Ações Rápidas */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-2xl mr-2">⚡</span>
                Ações Rápidas
              </h3>
              <div className="space-y-4">
                <button
                  onClick={() => setCurrentView('chamada')}
                  className="w-full px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-green-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                >
                  <span className="text-xl mr-2">✅</span>
                  Fazer Chamada
                </button>
                
                {(currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') && (
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
                    <button
                      onClick={() => setCurrentView('alunos')}
                      className="w-full px-6 py-4 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-lg hover:from-blue-600 hover:to-cyan-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                    >
                      <span className="text-xl mr-2">👥</span>
                      Gerenciar Alunos
                    </button>
                    <button
                      onClick={() => setCurrentView('turmas')}
                      className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                    >
                      <span className="text-xl mr-2">🏫</span>
                      Gerenciar Turmas
                    </button>
                    <button
                      onClick={() => setCurrentView('usuarios')}
                      className="w-full px-6 py-4 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-red-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                    >
                      <span className="text-xl mr-2">🔐</span>
                      Gerenciar Usuários
                    </button>
                    
                    {/* Seção de Backup e Restore - Apenas para Admin */}
                    {currentUser?.tipo === 'admin' && (
                      <div className="border-t pt-4 mt-4">
                        <h4 className="text-sm font-semibold text-gray-600 mb-3 flex items-center">
                          <span className="text-lg mr-1">💾</span>
                          Backup & Restore
                        </h4>
                        
                        <div className="space-y-2">
                          {/* Botão Gerar Backup */}
                          <button
                            onClick={generateBackup}
                            disabled={backupLoading}
                            className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-md transition-all duration-200 flex items-center justify-center font-medium disabled:opacity-50"
                          >
                            {backupLoading ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Gerando...
                              </>
                            ) : (
                              <>
                                <span className="text-lg mr-2">⬇️</span>
                                Gerar Backup
                              </>
                            )}
                          </button>
                          
                          {/* Botão Restaurar Backup */}
                          <div className="relative">
                            <input
                              type="file"
                              accept=".json,.zip"
                              onChange={handleRestoreFile}
                              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                              id="restore-file-input"
                            />
                            <button
                              disabled={restoreLoading}
                              className="w-full px-4 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 shadow-md transition-all duration-200 flex items-center justify-center font-medium disabled:opacity-50"
                            >
                              {restoreLoading ? (
                                <>
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                  Restaurando...
                                </>
                              ) : (
                                <>
                                  <span className="text-lg mr-2">⬆️</span>
                                  Restaurar Backup
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}

                {/* Botão Alterar Senha - visível para todos */}
                <button
                  onClick={() => setCurrentView('alterar-senha')}
                  className="w-full px-6 py-4 bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-lg hover:from-gray-600 hover:to-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                >
                  <span className="text-xl mr-2">🔒</span>
                  Alterar Senha
                </button>
                
                <button
                  onClick={() => setCurrentView('revistas')}
                  className="w-full px-6 py-4 bg-gradient-to-r from-teal-500 to-green-600 text-white rounded-lg hover:from-teal-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-teal-500 shadow-lg transition-all duration-200 flex items-center justify-center text-lg font-semibold"
                >
                  <span className="text-xl mr-2">📖</span>
                  Revistas Trimestrais
                </button>
                
                {currentUser?.tipo === 'professor' && (
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-700">
                      <strong>Suas turmas:</strong>
                    </p>
                    <div className="mt-2 space-y-1">
                      {getFilteredTurmas().map(turma => (
                        <span key={turma.id} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1">
                          {turma.nome}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Resumo Estatístico */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-2xl mr-2">📈</span>
                Resumo Geral
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Total de Turmas:</span>
                  <span className="text-2xl font-bold text-blue-600">{turmas.length}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Total de Alunos:</span>
                  <span className="text-2xl font-bold text-green-600">{students.length}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-emerald-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Presentes Hoje:</span>
                  <span className="text-2xl font-bold text-emerald-600">
                    {attendanceData.reduce((sum, row) => sum + row.presentes, 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                  <span className="text-gray-700 font-medium">Ofertas Hoje:</span>
                  <span className="text-xl font-bold text-yellow-600">
                    R$ {attendanceData.reduce((sum, row) => sum + row.total_ofertas, 0).toFixed(2).replace('.', ',')}
                  </span>
                </div>
              </div>
            </div>

            {/* Dicas e Informações */}
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-2xl mr-2">💡</span>
                Dicas de Uso
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <p>A chamada só pode ser feita aos domingos</p>
                </div>
                <div className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <p>Use a tela de chamada para registrar presença e ofertas</p>
                </div>
                <div className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <p>O relatório é atualizado automaticamente após salvar</p>
                </div>
                <div className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <p>Use os relatórios detalhados para ver classes vencedoras</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Componente de Login
  const LoginModal = () => {
    const [email, setEmail] = useState('');
    const [senha, setSenha] = useState('');
    const [loginLoading, setLoginLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault();
      setLoginLoading(true);
      setErrorMessage('');
      
      const result = await handleLogin(email, senha);
      
      if (!result.success) {
        setErrorMessage(result.message);
      }
      
      setLoginLoading(false);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl">
          <div className="text-center mb-6">
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-b from-orange-400 via-yellow-500 to-green-500 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl">🛡️</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800">Acesso ao Sistema</h2>
            <p className="text-gray-600 mt-2">App EBD - Ministério do Belém</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Senha</label>
              <input
                type="password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="••••••••"
                required
              />
            </div>

            {errorMessage && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                {errorMessage}
              </div>
            )}

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loginLoading}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-indigo-500 to-blue-600 text-white rounded-lg hover:from-indigo-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-400 font-semibold"
              >
                {loginLoading ? 'Entrando...' : 'Entrar'}
              </button>
              
              <button
                type="button"
                onClick={() => setShowLogin(false)}
                className="px-4 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Cancelar
              </button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            <p>Precisa de acesso? Fale com o administrador</p>
          </div>
        </div>
      </div>
    );
  };
  const HomeCover = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 flex items-center justify-center relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-black bg-opacity-20"></div>
      <div className="absolute inset-0" style={{
        backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(255,255,255,0.1) 0%, transparent 50%)'
      }}></div>
      
      <div className="relative z-10 text-center text-white max-w-4xl mx-auto px-6">
        {/* Logo Principal */}
        <div className="mb-8">
          <div className="w-32 h-32 mx-auto mb-6 bg-white rounded-full p-2 shadow-2xl">
            {/* Logo Ministério do Belém */}
            <img 
              src="/logo_belem.png" 
              alt="Ministério do Belém" 
              className="w-full h-full rounded-full object-cover"
            />
          </div>
          
          <h1 className="text-6xl font-bold mb-4 tracking-wider">
            App EBD
          </h1>
          
          <div className="text-xl text-blue-200 mb-2">
            <p>Presidente: <span className="font-semibold text-white">Pr. José Felipe da Silva</span></p>
            <p>Pastor Local: <span className="font-semibold text-white">Pr. Henrique Ferreira Neto</span></p>
            <p>Superintendente(EBD): <span className="font-semibold text-white">Paulo Henrique da Silva Reis</span></p>
          </div>
          
          <div className="text-lg text-blue-300 mt-4">
            <p className="font-semibold">Ministério Belém</p>
            <p className="text-base mt-1">Rua Managuá, 53 - Parque das Nações</p>
            <p className="text-base">Sumaré, SP, Brasil</p>
            <p className="text-base mt-2">Sistema de Gerenciamento da Escola Bíblica Dominical</p>
          </div>
        </div>

        {/* Recursos do Sistema */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="text-3xl mb-3">✅</div>
            <h3 className="font-semibold mb-2">Chamada Digital</h3>
            <p className="text-sm text-blue-200">Controle de presença rápido e eficiente</p>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="font-semibold mb-2">Relatórios</h3>
            <p className="text-sm text-blue-200">Classes vencedoras e estatísticas completas</p>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="text-3xl mb-3">👥</div>
            <h3 className="font-semibold mb-2">Gestão de Alunos</h3>
            <p className="text-sm text-blue-200">Cadastro e transferência entre turmas</p>
          </div>
          
          <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-6 border border-white border-opacity-20">
            <div className="text-3xl mb-3">💰</div>
            <h3 className="font-semibold mb-2">Controle de Ofertas</h3>
            <p className="text-sm text-blue-200">Registro de ofertas e materiais distribuídos</p>
          </div>
        </div>

        {/* Botão de Entrada */}
        <div className="space-y-4">
          {isLoggedIn ? (
            <div className="space-y-3">
              <button
                onClick={() => setCurrentView('dashboard')}
                className="px-12 py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 text-gray-900 rounded-full text-xl font-bold hover:from-yellow-400 hover:to-yellow-500 transform hover:scale-105 transition-all duration-300 shadow-2xl"
              >
                🚀 Acessar Sistema
              </button>
              
              <div className="flex items-center justify-center space-x-4 text-blue-200">
                <span>Logado como: <strong>{currentUser?.nome}</strong></span>
                <button 
                  onClick={handleLogout}
                  className="text-yellow-400 hover:text-yellow-300 underline"
                >
                  Sair
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowLogin(true)}
              className="px-12 py-4 bg-gradient-to-r from-indigo-500 to-blue-600 text-white rounded-full text-xl font-bold hover:from-indigo-400 hover:to-blue-500 transform hover:scale-105 transition-all duration-300 shadow-2xl"
            >
              🔐 Fazer Login
            </button>
          )}
          
          <p className="text-blue-300 text-sm mt-4">
            Sistema desenvolvido por Márcio Ferreira
          </p>
        </div>
      </div>
    </div>
  );
  const calcularClassesVencedoras = () => {
    if (!attendanceData || attendanceData.length === 0) return {};

    // Função para normalizar nomes (case-insensitive, trim, sem acentos)
    const normalizar = (nome) => {
      if (!nome) return '';
      return nome.toString()
        .trim()
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // remove acentos
        .replace(/[-]/g, ' '); // substitui hífens por espaços
    };

    // Whitelists dos departamentos (já normalizadas)
    const departamentos = {
      'Infantil': ['genesis', 'primarios', 'juniores'],
      'Jovens e Adolescentes': ['pre adolescentes', 'adolescentes', 'jovens'],
      'Adulto': ['soldados de cristo', 'dorcas (irmas)', 'ebenezer(obreiros)']
    };

    // Turmas a excluir sempre (normalizadas)
    const excluir = ['professores e oficiais', 'total geral', 'pos chamada', 'discipulados'];

    // Preparar dados com porcentagem de frequência
    const turmasComFrequencia = attendanceData.map(turma => ({
      ...turma,
      porcentagem_frequencia_decimal: turma.matriculados > 0 ? (turma.presentes / turma.matriculados) : 0
    }));

    const vencedores = {};

    // Para cada departamento
    Object.keys(departamentos).forEach(dept => {
      const turmasValidas = departamentos[dept];
      
      // Filtrar turmas válidas para este departamento
      const turmasDept = turmasComFrequencia.filter(turma => {
        const nomeNormalizado = normalizar(turma.turma_nome);
        
        // Excluir turmas da lista de exclusão
        if (excluir.includes(nomeNormalizado)) return false;
        
        // Incluir apenas se estiver na whitelist do departamento
        return turmasValidas.includes(nomeNormalizado);
      });

      if (turmasDept.length > 0) {
        // CLASSE VENCEDORA EM FREQUÊNCIA (maior percentual)
        const maxFrequencia = Math.max(...turmasDept.map(t => t.porcentagem_frequencia_decimal));
        const vencedorFrequencia = turmasDept.find(t => t.porcentagem_frequencia_decimal === maxFrequencia);

        // CLASSE VENCEDORA EM OFERTA (maior valor)
        const maxOferta = Math.max(...turmasDept.map(t => t.total_ofertas));
        const vencedorOferta = turmasDept.find(t => t.total_ofertas === maxOferta);

        vencedores[dept] = {
          frequencia: {
            turma_nome: vencedorFrequencia.turma_nome,
            porcentagem: Math.round(maxFrequencia * 100 * 100) / 100
          },
          oferta: {
            turma_nome: vencedorOferta.turma_nome,
            valor: Math.round(maxOferta * 100) / 100
          }
        };
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
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">Relatórios Detalhados</h1>
            <p className="text-gray-600">Relatório consolidado e classes vencedoras por departamento</p>
          </div>

          {/* Controles de Data */}
          <div className="bg-white rounded-lg shadow-lg p-4 md:p-6 mb-6">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-4 space-y-4 md:space-y-0">
              <h2 className="text-xl font-semibold text-gray-800">Relatório do Dia</h2>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
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
              <table className="w-full border-collapse border border-gray-200 text-sm">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-left">Turma</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Matric.</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Pres.</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">%</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Aus.</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Vis.</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Pós</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Ofertas</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Bíb.</th>
                    <th className="border border-gray-300 px-2 md:px-4 py-2 text-center">Rev.</th>
                  </tr>
                </thead>
                <tbody>
                  {attendanceData.map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-2 md:px-4 py-2 font-medium">{row.turma_nome}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.matriculados}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.presentes}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center font-semibold text-purple-600">
                        {row.matriculados > 0 ? ((row.presentes / row.matriculados) * 100).toFixed(1).replace('.', ',') : '0,0'}%
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.ausentes}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.visitantes}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.pos_chamada}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">R$ {row.total_ofertas.toFixed(2).replace('.', ',')}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.total_biblias}</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">{row.total_revistas}</td>
                    </tr>
                  ))}
                  {attendanceData.length > 0 && (
                    <tr className="bg-blue-50 font-semibold">
                      <td className="border border-gray-300 px-2 md:px-4 py-2">TOTAL GERAL</td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.matriculados, 0)}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.presentes, 0)}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center font-semibold text-purple-600">
                        {(() => {
                          const totalMatriculados = attendanceData.reduce((sum, row) => sum + row.matriculados, 0);
                          const totalPresentes = attendanceData.reduce((sum, row) => sum + row.presentes, 0);
                          return totalMatriculados > 0 ? ((totalPresentes / totalMatriculados) * 100).toFixed(1).replace('.', ',') : '0,0';
                        })()}%
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.ausentes, 0)}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.visitantes, 0)}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.pos_chamada, 0)}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        R$ {attendanceData.reduce((sum, row) => sum + row.total_ofertas, 0).toFixed(2).replace('.', ',')}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.total_biblias, 0)}
                      </td>
                      <td className="border border-gray-300 px-2 md:px-4 py-2 text-center">
                        {attendanceData.reduce((sum, row) => sum + row.total_revistas, 0)}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Classes Vencedoras */}
          <div className="bg-white rounded-lg shadow-lg p-4 md:p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Classes Vencedoras por Departamento</h2>
            
            <div className="space-y-6">
              {/* Departamento Infantil */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-green-700 border-b-2 border-green-200 pb-2">
                  Departamento Infantil
                </h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-semibold text-green-800 mb-2 text-sm md:text-base">
                      Classe Vencedora em Frequência do departamento Infantil
                    </h4>
                    <p className="text-green-700 text-sm md:text-base">
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
                    <h4 className="font-semibold text-green-800 mb-2 text-sm md:text-base">
                      Classe Vencedora em Oferta do departamento Infantil
                    </h4>
                    <p className="text-green-700 text-sm md:text-base">
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
              </div>

              {/* Departamento Jovens e Adolescentes */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-blue-700 border-b-2 border-blue-200 pb-2">
                  Departamento Jovens e Adolescentes
                </h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-800 mb-2 text-sm md:text-base">
                      Classe Vencedora em Frequência do departamento Jovens e Adolescentes
                    </h4>
                    <p className="text-blue-700 text-sm md:text-base">
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
                    <h4 className="font-semibold text-blue-800 mb-2 text-sm md:text-base">
                      Classe Vencedora em Oferta do departamento Jovens e Adolescentes
                    </h4>
                    <p className="text-blue-700 text-sm md:text-base">
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
              </div>

              {/* Departamento Adulto */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-purple-700 border-b-2 border-purple-200 pb-2">
                  Departamento Adulto
                </h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="font-semibold text-purple-800 mb-2 text-sm md:text-base">
                      Classe Vencedora em Frequência do departamento Adulto
                    </h4>
                    <p className="text-purple-700 text-sm md:text-base">
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
                    <h4 className="font-semibold text-purple-800 mb-2 text-sm md:text-base">
                      Classe Vencedora em Oferta do departamento Adulto
                    </h4>
                    <p className="text-purple-700 text-sm md:text-base">
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
              <h4 className="font-semibold text-gray-700 mb-2 text-sm md:text-base">Critérios de Classificação:</h4>
              <ul className="text-xs md:text-sm text-gray-600 space-y-1">
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
    
    // Estados para revista e lição atual
    const [revistaAtual, setRevistaAtual] = useState(null);
    const [licaoAtual, setLicaoAtual] = useState(null);

    useEffect(() => {
      if (selectedTurma) {
        loadTurmaData();
        loadRevistaData(); // Carregar dados da revista
      }
    }, [selectedTurma, selectedDate]);

    // Nova função para carregar dados da revista
    const loadRevistaData = async () => {
      if (!selectedTurma) {
        // Limpar estados quando não há turma selecionada
        setRevistaAtual(null);
        setLicaoAtual(null);
        return;
      }
      
      try {
        const response = await axios.get(`${API}/revistas/turma/${selectedTurma}`);
        const revista = response.data;
        
        if (revista && revista.tema) {
          setRevistaAtual(revista);
          
          // Buscar lição do dia baseada na data selecionada
          if (revista.licoes && revista.licoes.length > 0) {
            const licaoHoje = revista.licoes.find(licao => licao.data === selectedDate);
            setLicaoAtual(licaoHoje || null);
          } else {
            setLicaoAtual(null);
          }
        } else {
          setRevistaAtual(null);
          setLicaoAtual(null);
        }
      } catch (error) {
        console.error('Erro ao carregar revista:', error);
        setRevistaAtual(null);
        setLicaoAtual(null);
      }
    };

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
          // Usar parseFloat com toFixed para evitar acúmulo de imprecisões
          totalOfertas = parseFloat((totalOfertas + (att.oferta || 0)).toFixed(2));
          totalBiblias += att.biblias_entregues || 0;
          totalRevistas += att.revistas_entregues || 0;
          if (att.status === 'visitante') totalVisitantes++;
          if (att.status === 'pos_chamada') totalPosChamada++;
        });

        // Garantir precisão dos valores decimais e formato brasileiro (vírgula)
        setTurmaDataGlobal({
          ofertas_total: totalOfertas > 0 ? totalOfertas.toFixed(2).replace('.', ',') : '',
          biblias_total: totalBiblias > 0 ? totalBiblias.toString() : '',
          revistas_total: totalRevistas > 0 ? totalRevistas.toString() : '',
          visitantes_total: totalVisitantes > 0 ? totalVisitantes.toString() : '',
          pos_chamada_total: totalPosChamada > 0 ? totalPosChamada.toString() : ''
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
      // Se for campo de oferta, aceitar APENAS vírgula (padrão brasileiro)
      if (field === 'ofertas_total') {
        // Permitir apenas números e vírgula, até 2 casas decimais
        const regex = /^\d*,?\d{0,2}$/;
        if (value === '' || regex.test(value)) {
          setTurmaDataGlobal(prev => ({
            ...prev,
            [field]: value  // Manter exatamente como digitado
          }));
        }
      } else {
        setTurmaDataGlobal(prev => ({
          ...prev,
          [field]: value
        }));
      }
    };

    const handleSave = async () => {
      try {
        setLoading(true);
        
        const presentesCount = turmaAtendance.filter(att => att.presente).length;
        
        // Converter valores para números, tratando strings vazias como 0
        // Converter vírgula para ponto antes do parseFloat
        const ofertaTotal = parseFloat((turmaDataGlobal.ofertas_total || '0').replace(',', '.')) || 0;
        const bibliasTotal = parseInt(turmaDataGlobal.biblias_total) || 0;
        const revistasTotal = parseInt(turmaDataGlobal.revistas_total) || 0;
        const visitantesTotal = parseInt(turmaDataGlobal.visitantes_total) || 0;
        const posChamadaTotal = parseInt(turmaDataGlobal.pos_chamada_total) || 0;
        
        const attendanceList = turmaAtendance.map((att, index) => {
          let status = att.presente ? 'presente' : 'ausente';
          let oferta = 0;
          let biblias = 0;
          let revistas = 0;
          
          // Encontrar índice do primeiro presente
          const firstPresentIndex = turmaAtendance.findIndex(a => a.presente);
          
          // NÃO dividir ofertas automaticamente - valor total vai apenas para o primeiro presente
          if (att.presente && index === firstPresentIndex) {
            oferta = ofertaTotal; // Valor total apenas no primeiro presente
          }
          
          // Dar bíblias e revistas apenas para o primeiro aluno (para não duplicar)
          if (index === 0) {
            biblias = bibliasTotal;
            revistas = revistasTotal;
          }
          
          // CORREÇÃO: Aplicar visitantes e pós-chamada como registros adicionais
          // (sem sobrescrever seleções manuais do usuário)

          return {
            aluno_id: att.aluno_id,
            status: status,
            oferta: oferta,
            biblias_entregues: biblias,
            revistas_entregues: revistas
          };
        });
        
        // ADICIONAR registros de visitantes e pós-chamada como entradas separadas
        // (igual ao sistema de bíblias/revistas - sem afetar alunos já selecionados)
        
        // Adicionar visitantes (criar IDs únicos para registros temporários)
        for (let i = 0; i < visitantesTotal; i++) {
          attendanceList.push({
            aluno_id: `visitante_${Date.now()}_${i}`, // ID único para visitante
            status: 'visitante',
            oferta: 0,
            biblias_entregues: 0,
            revistas_entregues: 0
          });
        }
        
        // Adicionar pós-chamada (criar IDs únicos para registros temporários)
        for (let i = 0; i < posChamadaTotal; i++) {
          attendanceList.push({
            aluno_id: `pos_chamada_${Date.now()}_${i}`, // ID único para pós-chamada
            status: 'pos_chamada',
            oferta: 0,
            biblias_entregues: 0,
            revistas_entregues: 0
          });
        }

        await axios.post(`${API}/attendance/bulk/${selectedTurma}?data=${selectedDate}&user_tipo=${currentUser.tipo}&user_id=${currentUser.user_id || currentUser.id}`, attendanceList);
        
        console.log("DEBUG: Usuario logado:", currentUser.tipo, currentUser.nome);
        
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
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">Fazer Chamada</h1>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-4 md:p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Turma</label>
                <select
                  value={selectedTurma || ''}
                  onChange={(e) => setSelectedTurma(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Selecione uma turma</option>
                  {getFilteredTurmas().map(turma => (
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
                <div className="bg-blue-50 p-4 md:p-6 rounded-lg mb-6">
                  <h3 className="text-xl font-semibold text-blue-800 mb-4">Dados da Turma</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Oferta Total (R$)</label>
                      <input
                        type="text"
                        inputMode="decimal"
                        value={turmaDataGlobal.ofertas_total || ''}
                        onChange={(e) => updateTurmaData('ofertas_total', e.target.value)}
                        className="w-full px-3 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0,00"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Bíblias</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.biblias_total || ''}
                        onChange={(e) => updateTurmaData('biblias_total', e.target.value)}
                        className="w-full px-3 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Revistas</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.revistas_total || ''}
                        onChange={(e) => updateTurmaData('revistas_total', e.target.value)}
                        className="w-full px-3 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Visitantes</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.visitantes_total || ''}
                        onChange={(e) => updateTurmaData('visitantes_total', e.target.value)}
                        className="w-full px-3 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-700 mb-2">Pós-Chamada</label>
                      <input
                        type="text"
                        value={turmaDataGlobal.pos_chamada_total || ''}
                        onChange={(e) => updateTurmaData('pos_chamada_total', e.target.value)}
                        className="w-full px-3 py-3 text-lg border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="0"
                      />
                    </div>
                  </div>
                </div>

            {/* Informações da Revista e Lição Atual - NOVA SEÇÃO */}
            {selectedTurma && revistaAtual && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 md:p-6 mb-6 border-l-4 border-blue-500">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Tema da Revista */}
                  <div>
                    <div className="flex items-center mb-2">
                      <span className="text-2xl mr-2">📚</span>
                      <h3 className="text-lg font-semibold text-blue-800">Revista Trimestral</h3>
                    </div>
                    <p className="text-sm text-blue-700 leading-relaxed">
                      {revistaAtual.tema}
                    </p>
                  </div>
                  
                  {/* Lição do Dia */}
                  <div>
                    <div className="flex items-center mb-2">
                      <span className="text-2xl mr-2">🎯</span>
                      <h3 className="text-lg font-semibold text-green-800">
                        {licaoAtual ? 'Lição de Hoje' : 'Lição da Data'}
                      </h3>
                    </div>
                    {licaoAtual ? (
                      <div>
                        <p className="text-sm font-medium text-green-700 mb-1">
                          {licaoAtual.titulo}
                        </p>
                        <p className="text-xs text-green-600">
                          📅 {new Date(licaoAtual.data + 'T00:00:00').toLocaleDateString('pt-BR', {
                            weekday: 'long',
                            year: 'numeric', 
                            month: 'long',
                            day: 'numeric'
                          })}
                        </p>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-600">
                        <p>Nenhuma lição programada para esta data</p>
                        {revistaAtual.licoes && revistaAtual.licoes.length > 0 && (
                          <p className="text-xs mt-1">
                            Próxima lição: {revistaAtual.licoes[0].titulo} ({revistaAtual.licoes[0].data})
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Indicador visual de disponibilidade */}
                <div className="mt-4 pt-3 border-t border-blue-200">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-blue-600">
                      📖 Total de lições: {revistaAtual.licoes ? revistaAtual.licoes.length : 0}
                    </span>
                    {licaoAtual && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                        ✨ Lição Disponível
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Aviso se não há revista configurada */}
            {selectedTurma && !revistaAtual && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-lg">
                <div className="flex">
                  <div className="ml-3">
                    <p className="text-sm text-yellow-800">
                      <strong>📚 Atenção:</strong> Não há revista configurada para esta turma. 
                      Entre em contato com o administrador para configurar o material didático.
                    </p>
                  </div>
                </div>
              </div>
            )}

                {/* Lista de Presença Simples */}
                <div className="bg-white border rounded-lg overflow-hidden mb-6">
                  <div className="bg-gray-100 px-4 py-4 border-b">
                    <div className="mb-4">
                      <h3 className="text-xl font-semibold text-gray-800">
                        {turmas.find(t => t.id === selectedTurma)?.nome}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">Clique nos nomes para marcar presença</p>
                      <div className="flex flex-wrap gap-4 mt-2 text-sm">
                        <span className="text-green-700 font-medium">
                          Presentes: {turmaAtendance.filter(att => att.presente).length}
                        </span>
                        <span className="text-red-700 font-medium">
                          Ausentes: {turmaAtendance.filter(att => !att.presente).length}
                        </span>
                        <span className="text-blue-700 font-medium">
                          Frequência: {turmaAtendance.length > 0 
                            ? ((turmaAtendance.filter(att => att.presente).length / turmaAtendance.length) * 100).toFixed(1).replace('.', ',')
                            : '0,0'}%
                        </span>
                      </div>
                    </div>
                    
                    {/* Botão Salvar - Agora responsivo */}
                    <div className="w-full">
                      <button
                        onClick={handleSave}
                        disabled={loading}
                        className="w-full px-6 py-4 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-400 text-lg font-semibold shadow-lg"
                      >
                        {loading ? 'Salvando...' : '💾 Salvar Chamada'}
                      </button>
                    </div>
                  </div>
                  
                  <div className="p-4 md:p-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {turmaAtendance.map((att, index) => (
                        <button
                          key={index}
                          onClick={() => togglePresenca(att.aluno_id)}
                          className={`p-3 md:p-4 rounded-lg text-left transition-all duration-200 touch-manipulation ${
                            att.presente 
                              ? 'bg-green-100 border-2 border-green-500 text-green-800' 
                              : 'bg-gray-100 border-2 border-gray-300 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          <div className="flex items-center">
                            <div className={`w-4 h-4 rounded-full mr-3 flex-shrink-0 ${
                              att.presente ? 'bg-green-500' : 'bg-gray-400'
                            }`}></div>
                            <span className="font-medium text-sm md:text-base break-words">{att.nome}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Resumo */}
                <div className="p-4 md:p-6 bg-green-50 rounded-lg">
                  <h4 className="text-lg font-semibold text-green-800 mb-3">Resumo</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-xl md:text-2xl font-bold text-green-600">
                        {turmaAtendance.filter(att => att.presente).length}
                      </div>
                      <div className="text-xs md:text-sm text-green-700">Presentes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl md:text-2xl font-bold text-red-600">
                        {turmaAtendance.filter(att => !att.presente).length}
                      </div>
                      <div className="text-xs md:text-sm text-red-700">Ausentes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl md:text-2xl font-bold text-blue-600">
                        {turmaAtendance.length}
                      </div>
                      <div className="text-xs md:text-sm text-blue-700">Total</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl md:text-2xl font-bold text-purple-600">
                        {turmaAtendance.length > 0 
                          ? ((turmaAtendance.filter(att => att.presente).length / turmaAtendance.length) * 100).toFixed(1).replace('.', ',')
                          : '0,0'}%
                      </div>
                      <div className="text-xs md:text-sm text-purple-700">Frequência</div>
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
            
            {/* FILTROS DE BUSCA SIMPLES */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-medium text-gray-700 mb-3">🔍 Buscar Alunos</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                
                {/* Campo de Busca por Nome */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-600 mb-2">
                    Nome do Aluno
                  </label>
                  <input
                    id="search-students-input"
                    type="text"
                    placeholder="Digite o nome (ex: Maria, João, Ana)..."
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSearch();
                      }
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                {/* Botão Buscar */}
                <div>
                  <button
                    onClick={handleSearch}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    🔍 Buscar
                  </button>
                </div>
                
                {/* Botão Limpar */}
                <div>
                  <button
                    onClick={() => {
                      handleClearSearch();
                      setTurmaFilter('');
                      setStatusFilter('todos');
                    }}
                    className="w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    🧹 Limpar
                  </button>
                </div>
              </div>
              
              {/* Segunda linha com filtros adicionais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                
                {/* Filtro por Turma */}
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">
                    Filtrar por Turma
                  </label>
                  <select
                    value={turmaFilter}
                    onChange={(e) => setTurmaFilter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Todas as turmas</option>
                    {turmas.map(turma => (
                      <option key={turma.id} value={turma.id}>{turma.nome}</option>
                    ))}
                  </select>
                </div>
                
                {/* Filtro por Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-2">
                    Status do Aluno
                  </label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="todos">Todos</option>
                    <option value="ativo">Apenas Ativos</option>
                    <option value="inativo">Apenas Inativos</option>
                  </select>
                </div>
              </div>
              
              {/* Contador de resultados */}
              <div className="mt-4 text-sm text-gray-600">
                {searchTerm && (
                  <div className="mb-2 p-2 bg-blue-50 rounded border border-blue-200">
                    🔍 Buscando por: <strong>"{searchTerm}"</strong>
                  </div>
                )}
                <strong>{getFilteredStudents().length}</strong> de <strong>{students.length}</strong> alunos encontrados
              </div>
            </div>
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
                  {getFilteredStudents().map((student) => (
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

  // Componente Usuários
  const Usuarios = () => {
    const [usuarios, setUsuarios] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingUser, setEditingUser] = useState(null); // Novo estado para edição
    const [formData, setFormData] = useState({
      nome: '',
      email: '',
      senha: '',
      tipo: 'professor',
      turmas_permitidas: []
    });

    useEffect(() => {
      loadUsuarios();
    }, []);

    const loadUsuarios = async () => {
      try {
        const response = await axios.get(`${API}/users`);
        setUsuarios(response.data);
      } catch (error) {
        console.error('Erro ao carregar usuários:', error);
      }
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        if (editingUser) {
          // Editando usuário existente
          const updateData = {
            nome: formData.nome,
            email: formData.email,
            tipo: formData.tipo,
            turmas_permitidas: formData.turmas_permitidas
          };
          
          // Só incluir senha se foi fornecida
          if (formData.senha.trim()) {
            updateData.senha = formData.senha;
          }
          
          await axios.put(`${API}/users/${editingUser}`, updateData);
          alert('Usuário atualizado com sucesso!');
        } else {
          // Criando novo usuário
          await axios.post(`${API}/users`, formData);
          alert('Usuário criado com sucesso!');
        }
        
        await loadUsuarios();
        setShowForm(false);
        setEditingUser(null);
        setFormData({ nome: '', email: '', senha: '', tipo: 'professor', turmas_permitidas: [] });
      } catch (error) {
        console.error('Erro ao salvar usuário:', error);
        if (error.response?.data?.detail) {
          alert(`Erro: ${error.response.data.detail}`);
        } else {
          alert(`Erro ao ${editingUser ? 'atualizar' : 'criar'} usuário`);
        }
      }
    };

    const handleEdit = (usuario) => {
      setEditingUser(usuario.id);
      setFormData({
        nome: usuario.nome,
        email: usuario.email,
        senha: '', // Deixar vazio para não alterar senha obrigatoriamente
        tipo: usuario.tipo,
        turmas_permitidas: usuario.turmas_permitidas || []
      });
      setShowForm(true);
    };

    const handleDelete = async (userId) => {
      const usuario = usuarios.find(u => u.id === userId);
      const nomeUsuario = usuario ? usuario.nome : 'usuário';
      
      if (window.confirm(`Tem certeza que deseja remover ${nomeUsuario}? Esta ação não pode ser desfeita.`)) {
        try {
          console.log('Attempting to delete user with ID:', userId);
          const response = await axios.delete(`${API}/users/${userId}`);
          console.log('Delete response:', response.data);
          await loadUsuarios();
          alert(`✅ ${nomeUsuario} foi removido com sucesso!`);
        } catch (error) {
          console.error('Erro ao remover usuário:', error);
          if (error.response) {
            console.error('Response data:', error.response.data);
            console.error('Response status:', error.response.status);
            alert(`❌ Erro ao remover usuário: ${error.response.data.detail || error.response.status}`);
          } else if (error.request) {
            console.error('No response received:', error.request);
            alert('❌ Erro de conexão ao remover usuário');
          } else {
            console.error('Error setting up request:', error.message);
            alert(`❌ Erro ao remover usuário: ${error.message}`);
          }
        }
      }
    };

    const toggleTurmaPermissao = (turmaId) => {
      setFormData(prev => ({
        ...prev,
        turmas_permitidas: prev.turmas_permitidas.includes(turmaId)
          ? prev.turmas_permitidas.filter(id => id !== turmaId)
          : [...prev.turmas_permitidas, turmaId]
      }));
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
              <h1 className="text-3xl font-bold text-gray-800">Gerenciar Usuários</h1>
              <button
                onClick={() => setShowForm(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Novo Usuário
              </button>
            </div>
          </div>

          {showForm && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {editingUser ? 'Editar Usuário' : 'Novo Usuário'}
              </h2>
              <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
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
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Senha {editingUser && <span className="text-sm text-gray-500">(deixe vazio para manter atual)</span>}
                    </label>
                    <input
                      type="password"
                      value={formData.senha}
                      onChange={(e) => setFormData({...formData, senha: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required={!editingUser} // Só obrigatório para novo usuário
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
                    <select
                      value={formData.tipo}
                      onChange={(e) => setFormData({...formData, tipo: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="professor">Professor</option>
                      <option value="moderador">Moderador</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                </div>

                {formData.tipo === 'professor' && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Turmas Permitidas</label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 p-4 border rounded-lg bg-gray-50">
                      {turmas.map(turma => (
                        <label key={turma.id} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.turmas_permitidas.includes(turma.id)}
                            onChange={() => toggleTurmaPermissao(turma.id)}
                            className="mr-2"
                          />
                          <span className="text-sm">{turma.nome}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex space-x-4">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {editingUser ? 'Atualizar Usuário' : 'Criar Usuário'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingUser(null);
                      setFormData({ nome: '', email: '', senha: '', tipo: 'professor', turmas_permitidas: [] });
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
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Lista de Usuários</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left">Nome</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Email</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Tipo</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Turmas</th>
                    <th className="border border-gray-300 px-4 py-2 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {usuarios.map((usuario) => (
                    <tr key={usuario.id} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2">{usuario.nome}</td>
                      <td className="border border-gray-300 px-4 py-2">{usuario.email}</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        <span className={`px-2 py-1 rounded text-xs ${
                          usuario.tipo === 'admin' 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {usuario.tipo === 'admin' ? 'Administrador' : usuario.tipo === 'moderador' ? 'Moderador' : 'Professor'}
                        </span>
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        {usuario.tipo === 'admin' ? (
                          <span className="text-green-600 font-semibold">Todas</span>
                        ) : (
                          <span className="text-sm">
                            {usuario.turmas_permitidas.length} turma(s)
                          </span>
                        )}
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-center">
                        <div className="flex justify-center space-x-2">
                          <button
                            onClick={() => handleEdit(usuario)}
                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                          >
                            Editar
                          </button>
                          {usuario.email !== 'admin@ebd.com' && (
                            <button
                              onClick={() => handleDelete(usuario.id)}
                              className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                            >
                              Remover
                            </button>
                          )}
                        </div>
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

  // Componente Alterar Senha
  const AlterarSenha = () => {
    const [passwordData, setPasswordData] = useState({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState(''); // 'success' or 'error'

    const handleChange = (e) => {
      setPasswordData({
        ...passwordData,
        [e.target.name]: e.target.value
      });
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      setMessage('');
      setLoading(true);

      try {
        // Validações frontend
        if (passwordData.newPassword !== passwordData.confirmPassword) {
          throw new Error('Nova senha e confirmação não coincidem');
        }

        if (passwordData.newPassword.length < 6) {
          throw new Error('Nova senha deve ter pelo menos 6 caracteres');
        }

        // Chamar API
        const response = await axios.put(`${API}/users/${currentUser.user_id}/change-password`, {
          user_id: currentUser.user_id,
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword,
          confirm_password: passwordData.confirmPassword
        });

        setMessage('Senha alterada com sucesso!');
        setMessageType('success');
        setPasswordData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        });

      } catch (error) {
        setMessage(error.response?.data?.detail || error.message || 'Erro ao alterar senha');
        setMessageType('error');
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        <div className="max-w-2xl mx-auto py-8 px-4">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-800">🔒 Alterar Senha</h1>
            <p className="text-gray-600">Altere sua senha de acesso ao sistema</p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            {message && (
              <div className={`mb-6 p-4 rounded-lg ${
                messageType === 'success' 
                  ? 'bg-green-100 border border-green-400 text-green-700' 
                  : 'bg-red-100 border border-red-400 text-red-700'
              }`}>
                {message}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Senha Atual
                </label>
                <input
                  type="password"
                  name="currentPassword"
                  value={passwordData.currentPassword}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Digite sua senha atual"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nova Senha
                </label>
                <input
                  type="password"
                  name="newPassword"
                  value={passwordData.newPassword}
                  onChange={handleChange}
                  required
                  minLength={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Digite sua nova senha (mínimo 6 caracteres)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmar Nova Senha
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={passwordData.confirmPassword}
                  onChange={handleChange}
                  required
                  minLength={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Confirme sua nova senha"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setCurrentView('dashboard')}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  disabled={loading}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  disabled={loading}
                >
                  {loading ? 'Alterando...' : 'Alterar Senha'}
                </button>
              </div>
            </form>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-semibold text-blue-800 mb-2">Dicas de Segurança:</h3>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• Use pelo menos 6 caracteres</li>
                <li>• Combine letras, números e símbolos</li>
                <li>• Não use informações pessoais óbvias</li>
                <li>• Altere sua senha regularmente</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Componente Configuração de Chamadas - NOVO
  const ConfigChamadas = () => {
    const [localConfig, setLocalConfig] = useState({
      bloqueio_chamada_ativo: true,
      horario_bloqueio: "13:00"
    });

    useEffect(() => {
      if (systemConfig.bloqueio_chamada_ativo !== undefined) {
        setLocalConfig({
          bloqueio_chamada_ativo: systemConfig.bloqueio_chamada_ativo,
          horario_bloqueio: systemConfig.horario_bloqueio || "13:00"
        });
      }
    }, [systemConfig]);

    const handleSave = async () => {
      await updateSystemConfig(localConfig.bloqueio_chamada_ativo, localConfig.horario_bloqueio);
    };

    return (
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => setCurrentView('dashboard')}
            className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            ← Voltar ao Dashboard
          </button>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Configurar Chamadas</h1>
              <p className="text-gray-600">Controle quando professores podem editar chamadas</p>
            </div>

            {configLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2 text-gray-600">Carregando configurações...</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Toggle Principal */}
                <div className="border rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">Bloqueio de Edição</h3>
                      <p className="text-gray-600 text-sm mt-1">
                        Quando ativo, professores só podem editar chamadas até o horário definido
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={localConfig.bloqueio_chamada_ativo}
                        onChange={(e) => setLocalConfig({
                          ...localConfig,
                          bloqueio_chamada_ativo: e.target.checked
                        })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>

                {/* Configuração de Horário */}
                {localConfig.bloqueio_chamada_ativo && (
                  <div className="border rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Horário Limite</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Horário de Bloqueio
                        </label>
                        <input
                          type="time"
                          value={localConfig.horario_bloqueio}
                          onChange={(e) => setLocalConfig({
                            ...localConfig,
                            horario_bloqueio: e.target.value
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-blue-800 mb-2">Como funciona:</h4>
                        <p className="text-sm text-blue-700">
                          Professores podem editar chamadas até às <strong>{localConfig.horario_bloqueio}</strong> do dia que foi feita.
                          Após esse horário, apenas moderadores e administradores podem fazer alterações.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Explicação do Sistema */}
                <div className="bg-gray-50 border rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">ℹ️ Informações Importantes</h3>
                  <div className="space-y-2 text-sm text-gray-700">
                    <p><strong>• Professores:</strong> {localConfig.bloqueio_chamada_ativo ? `Podem editar chamadas até às ${localConfig.horario_bloqueio} do mesmo dia` : 'Podem editar qualquer chamada'}</p>
                    <p><strong>• Moderadores e Administradores:</strong> Sempre podem editar qualquer chamada</p>
                    <p><strong>• Objetivo:</strong> Manter integridade dos dados históricos e relatórios</p>
                  </div>
                </div>

                {/* Botões de Ação */}
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <button
                    onClick={() => setCurrentView('dashboard')}
                    className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={configLoading}
                    className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {configLoading ? 'Salvando...' : 'Salvar Configurações'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Componente Rankings
  const Rankings = () => {
    const [isLoadingRankings, setIsLoadingRankings] = useState(false);
    
    useEffect(() => {
      // Só carrega se ainda não tiver dados
      if (!rankingAlunos.ranking || !rankingProfessores.ranking || !rankingTurmas.ranking) {
        loadRankingsData();
      }
    }, []);

    const loadRankingsData = async () => {
      if (isLoadingRankings) return; // Evita múltiplas chamadas simultâneas
      
      setIsLoadingRankings(true);
      try {
        console.log('Carregando rankings...');
        const [alunosResponse, professoresResponse, turmasResponse] = await Promise.all([
          axios.get(`${API}/ranking/alunos`),
          axios.get(`${API}/ranking/professores-oficiais`),
          axios.get(`${API}/ranking/turmas`)
        ]);
        
        setRankingAlunos(alunosResponse.data);
        setRankingProfessores(professoresResponse.data);
        setRankingTurmas(turmasResponse.data);
        console.log('Rankings carregados com sucesso');
      } catch (error) {
        console.error('Erro ao carregar rankings:', error);
        alert('Erro ao carregar rankings. Tente novamente.');
      } finally {
        setIsLoadingRankings(false);
      }
    };

    const handleTabChange = (newTab) => {
      // Debounce para evitar mudanças rápidas de aba
      if (isLoadingRankings) return;
      setActiveTab(newTab);
    };

    return (
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">🏆 Rankings</h1>
            <p className="text-gray-600">Ranking de presença e desempenho</p>
          </div>

          {/* Tabs */}
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row sm:flex-wrap gap-2 sm:gap-1 bg-gray-200 p-2 sm:p-1 rounded-lg">
              <button
                onClick={() => handleTabChange('alunos')}
                disabled={isLoadingRankings}
                className={`px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  activeTab === 'alunos'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-300'
                }`}
              >
                🎓 Alunos Gerais
              </button>
              <button
                onClick={() => handleTabChange('professores')}
                disabled={isLoadingRankings}
                className={`px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  activeTab === 'professores'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-300'
                }`}
              >
                👨‍🏫 Professores e Oficiais
              </button>
              <button
                onClick={() => handleTabChange('turmas')}
                disabled={isLoadingRankings}
                className={`px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                  activeTab === 'turmas'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-300'
                }`}
              >
                🏫 Turmas
              </button>
            </div>
            
            {/* Botão de refresh */}
            <div className="mt-3 text-right">
              <button
                onClick={loadRankingsData}
                disabled={isLoadingRankings}
                className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 ml-auto"
              >
                {isLoadingRankings ? (
                  <>
                    <span className="animate-spin">⟳</span>
                    Carregando...
                  </>
                ) : (
                  <>
                    🔄 Atualizar Rankings
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Conteúdo dos Rankings */}
          <div className="bg-white rounded-lg shadow-lg p-4 md:p-6">
            {isLoadingRankings ? (
              <div className="text-center py-12">
                <div className="animate-spin text-4xl mb-4">⟳</div>
                <p className="text-gray-600">Carregando rankings...</p>
              </div>
            ) : (
              <>
                {activeTab === 'alunos' && (
                  <div>
                    <h2 className="text-lg md:text-xl font-semibold text-gray-800 mb-4">Ranking Geral de Alunos</h2>
                    <p className="text-sm md:text-base text-gray-600 mb-6">Top 50 alunos com mais presenças</p>
                    
                    {rankingAlunos.ranking && rankingAlunos.ranking.length > 0 ? (
                      <>
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse border border-gray-200 text-xs md:text-sm">
                            <thead>
                              <tr className="bg-gray-100">
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Pos.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-left">Nome</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-left">Turma</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Pres.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Dom.</th>
                              </tr>
                            </thead>
                            <tbody>
                              {rankingAlunos.ranking.map((aluno, index) => (
                                <tr key={`aluno-${aluno.aluno_id}-${index}`} className="hover:bg-gray-50">
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center font-bold">
                                    {index + 1 === 1 && '🥇'}
                                    {index + 1 === 2 && '🥈'}
                                    {index + 1 === 3 && '🥉'}
                                    {index + 1 > 3 && `${index + 1}º`}
                                  </td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 font-medium">{aluno.nome}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2">{aluno.turma}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{aluno.total_presencas}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{aluno.domingos_presentes}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <div className="mt-4 text-xs md:text-sm text-gray-600">
                          <p>Total de alunos no ranking: {rankingAlunos.total_alunos || rankingAlunos.ranking.length}</p>
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>📊 Nenhum dado de ranking disponível</p>
                        <p className="text-sm mt-2">Tente atualizar os rankings</p>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'professores' && (
                  <div>
                    <h2 className="text-lg md:text-xl font-semibold text-gray-800 mb-4">Ranking Professores e Oficiais</h2>
                    <p className="text-sm md:text-base text-gray-600 mb-6">Ranking da turma de liderança da igreja</p>
                    
                    {rankingProfessores.ranking && rankingProfessores.ranking.length > 0 ? (
                      <>
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse border border-gray-200 text-xs md:text-sm">
                            <thead>
                              <tr className="bg-gray-100">
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Pos.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-left">Nome</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Pres.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Dom.</th>
                              </tr>
                            </thead>
                            <tbody>
                              {rankingProfessores.ranking.map((professor, index) => (
                                <tr key={`prof-${professor.aluno_id}-${index}`} className="hover:bg-gray-50">
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center font-bold">
                                    {index + 1 === 1 && '🥇'}
                                    {index + 1 === 2 && '🥈'}
                                    {index + 1 === 3 && '🥉'}
                                    {index + 1 > 3 && `${index + 1}º`}
                                  </td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 font-medium">{professor.nome}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{professor.total_presencas}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{professor.domingos_presentes}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <div className="mt-4 text-xs md:text-sm text-gray-600">
                          <p>Total de membros: {rankingProfessores.total_membros || rankingProfessores.ranking.length}</p>
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>📊 Nenhum dado de ranking disponível</p>
                        <p className="text-sm mt-2">Tente atualizar os rankings</p>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'turmas' && (
                  <div>
                    <h2 className="text-lg md:text-xl font-semibold text-gray-800 mb-4">Ranking de Turmas</h2>
                    <p className="text-sm md:text-base text-gray-600 mb-6">Turmas ordenadas por frequência média</p>
                    
                    {rankingTurmas.ranking && rankingTurmas.ranking.length > 0 ? (
                      <>
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse border border-gray-200 text-xs md:text-sm">
                            <thead>
                              <tr className="bg-gray-100">
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Pos.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-left">Turma</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Matric.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Média</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Freq.</th>
                                <th className="border border-gray-300 px-2 md:px-3 py-2 text-center">Dom.</th>
                              </tr>
                            </thead>
                            <tbody>
                              {rankingTurmas.ranking.map((turma, index) => (
                                <tr key={`turma-${turma.turma_id}-${index}`} className="hover:bg-gray-50">
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center font-bold">
                                    {index + 1 === 1 && '🥇'}
                                    {index + 1 === 2 && '🥈'}
                                    {index + 1 === 3 && '🥉'}
                                    {index + 1 > 3 && `${index + 1}º`}
                                  </td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 font-medium">{turma.turma_nome}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{turma.matriculados}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{turma.media_presencas}</td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center font-semibold text-green-600">
                                    {turma.percentual_frequencia}%
                                  </td>
                                  <td className="border border-gray-300 px-2 md:px-3 py-2 text-center">{turma.domingos_com_dados}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <div className="mt-4 text-xs md:text-sm text-gray-600">
                          <p>Total de turmas: {rankingTurmas.total_turmas || rankingTurmas.ranking.length}</p>
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>📊 Nenhum dado de ranking disponível</p>
                        <p className="text-sm mt-2">Tente atualizar os rankings</p>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2 text-sm md:text-base">Como funciona o ranking:</h4>
              <ul className="text-xs md:text-sm text-blue-700 space-y-1">
                <li>• <strong>Alunos:</strong> Ordenados por total de presenças (domingos presentes)</li>
                <li>• <strong>Professores:</strong> Ranking específico da turma de liderança</li>
                <li>• <strong>Turmas:</strong> Ordenadas por percentual de frequência média</li>
                <li>• <strong>Cálculo:</strong> Baseado nos dados reais de chamada registrados</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Componente Admin Revistas - OTIMIZADO
  const AdminRevistas = () => {
    const [loadingRevistas, setLoadingRevistas] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [editingRevista, setEditingRevista] = useState(null);
    const [formData, setFormData] = useState({
      tema: '',
      turma_ids: [],
      licoes: []
    });

    useEffect(() => {
      // Carregar revistas apenas se não existirem
      if (revistas.length === 0) {
        loadRevistas();
      }
    }, []); // Array vazio - evita loop infinito

    // Inicializar lições vazias apenas quando necessário
    const initLicoes = () => {
      return Array.from({length: 13}, (_, i) => ({
        titulo: '',
        data: ''
      }));
    };

    const handleSave = async (e) => {
      e.preventDefault();
      
      if (!formData.tema || formData.turma_ids.length === 0) {
        alert('❌ Preencha o tema e selecione pelo menos uma turma');
        return;
      }

      setLoadingRevistas(true);
      
      try {
        const revistaData = {
          tema: formData.tema,
          turma_ids: formData.turma_ids,
          licoes: formData.licoes.filter(licao => licao.titulo && licao.data)
        };

        if (editingRevista) {
          await axios.put(`${API}/revistas/${editingRevista.id}`, revistaData);
          alert('✅ Revista atualizada!');
        } else {
          await axios.post(`${API}/revistas`, revistaData);
          alert('✅ Revista criada!');
        }

        await loadRevistas();
        resetForm();
      } catch (error) {
        console.error('Erro:', error);
        alert('❌ Erro ao salvar');
      } finally {
        setLoadingRevistas(false);
      }
    };

    const handleDelete = async (revistaId) => {
      if (window.confirm('Desativar esta revista?')) {
        try {
          setLoadingRevistas(true);
          await axios.delete(`${API}/revistas/${revistaId}`);
          alert('✅ Revista desativada!');
          await loadRevistas();
        } catch (error) {
          alert('❌ Erro ao desativar');
        } finally {
          setLoadingRevistas(false);
        }
      }
    };

    const handleEdit = (revista) => {
      setEditingRevista(revista);
      setFormData({
        tema: revista.tema,
        turma_ids: revista.turma_ids,
        licoes: revista.licoes
      });
      setShowForm(true);
    };

    const resetForm = () => {
      setShowForm(false);
      setEditingRevista(null);
      setFormData({
        tema: '',
        turma_ids: [],
        licoes: []
      });
    };

    const handleShowForm = () => {
      if (!showForm) {
        setFormData({
          tema: '',
          turma_ids: [],
          licoes: Array.from({length: 13}, (_, i) => ({
            titulo: '',
            data: ''
          }))
        });
      }
      setShowForm(!showForm);
    };

    return (
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-4xl mx-auto">
          {/* Header Simples */}
          <div className="flex justify-between items-center mb-6">
            <button
              onClick={() => setCurrentView('revistas')}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              ← Voltar
            </button>
            
            <button
              onClick={handleShowForm}
              disabled={loadingRevistas}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
            >
              {showForm ? '❌ Cancelar' : '➕ Nova Revista'}
            </button>
          </div>

          <h1 className="text-xl font-bold mb-6">⚙️ Administrar Revistas</h1>

          {/* Formulário Simples - só aparece quando necessário */}
          {showForm && (
            <div className="bg-white rounded-lg p-4 mb-6 border">
              <h3 className="font-bold mb-4">
                {editingRevista ? '✏️ Editar' : '➕ Nova Revista'}
              </h3>
              
              <form onSubmit={handleSave} className="space-y-4">
                {/* Tema */}
                <div>
                  <label className="block text-sm font-medium mb-1">Tema *</label>
                  <textarea
                    value={formData.tema}
                    onChange={(e) => setFormData({...formData, tema: e.target.value})}
                    required
                    rows={2}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="Tema do trimestre..."
                  />
                </div>

                {/* Turmas - Grid simples */}
                <div>
                  <label className="block text-sm font-medium mb-2">Turmas *</label>
                  <div className="grid grid-cols-2 gap-2">
                    {turmas.slice(0, 8).map(turma => (
                      <label key={turma.id} className="flex items-center text-sm">
                        <input
                          type="checkbox"
                          checked={formData.turma_ids.includes(turma.id)}
                          onChange={(e) => {
                            const newIds = e.target.checked 
                              ? [...formData.turma_ids, turma.id]
                              : formData.turma_ids.filter(id => id !== turma.id);
                            setFormData({...formData, turma_ids: newIds});
                          }}
                          className="mr-2"
                        />
                        {turma.nome}
                      </label>
                    ))}
                  </div>
                </div>

                {/* Lições - TODAS AS 13 */}
                <div>
                  <label className="block text-sm font-medium mb-2">
                    📚 Lições do Trimestre (13 lições)
                  </label>
                  <div className="text-xs text-gray-600 mb-3">
                    Complete todas as lições com títulos e datas. Use formato: 2025-07-06
                  </div>
                  
                  <div className="max-h-80 overflow-y-auto border rounded-lg p-4 bg-gray-50">
                    {formData.licoes.map((licao, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 p-3 bg-white border rounded">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            📖 Lição {index + 1} - Título *
                          </label>
                          <input
                            type="text"
                            value={licao.titulo}
                            onChange={(e) => {
                              const newLicoes = [...formData.licoes];
                              newLicoes[index].titulo = e.target.value;
                              setFormData({...formData, licoes: newLicoes});
                            }}
                            placeholder={`Título da lição ${index + 1}`}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            📅 Data da Aula *
                          </label>
                          <input
                            type="date"
                            value={licao.data}
                            onChange={(e) => {
                              const newLicoes = [...formData.licoes];
                              newLicoes[index].data = e.target.value;
                              setFormData({...formData, licoes: newLicoes});
                            }}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="text-xs text-gray-600 mt-2 p-2 bg-blue-50 rounded">
                    💡 <strong>Dica:</strong> Preencha pelo menos as primeiras lições para começar. Você pode deixar algumas vazias e completar depois editando a revista.
                  </div>
                </div>

                {/* Botões */}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={loadingRevistas}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                  >
                    {loadingRevistas ? 'Salvando...' : 'Salvar'}
                  </button>
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Lista de Revistas - Interface simplificada */}
          <div className="bg-white rounded-lg p-4">
            <h3 className="font-bold mb-4">📚 Revistas ({revistas.length})</h3>
            
            {loadingRevistas ? (
              <div className="text-center py-4">
                <div className="animate-spin text-lg mb-2">⟳</div>
                <p className="text-sm">Carregando...</p>
              </div>
            ) : revistas.length > 0 ? (
              <div className="space-y-3">
                {revistas.map(revista => {
                  const turmasNomes = turmas
                    .filter(t => revista.turma_ids.includes(t.id))
                    .map(t => t.nome)
                    .slice(0, 3)
                    .join(', ');
                  
                  return (
                    <div key={revista.id} className="border rounded p-3">
                      <div className="flex justify-between items-start">
                        <div className="flex-1 mr-4">
                          <h4 className="font-medium text-sm leading-tight mb-1">
                            {revista.tema.substring(0, 80)}
                            {revista.tema.length > 80 ? '...' : ''}
                          </h4>
                          <p className="text-xs text-gray-600">
                            {turmasNomes} • {revista.licoes.length} lições
                          </p>
                        </div>
                        <div className="flex gap-1 flex-shrink-0">
                          <button
                            onClick={() => handleEdit(revista)}
                            className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => handleDelete(revista.id)}
                            className="px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
                          >
                            Remover
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>Nenhuma revista cadastrada</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Componente Revistas
  const Revistas = () => {
    const [loadingRevistas, setLoadingRevistas] = useState(false);
    
    useEffect(() => {
      // Carregar revistas apenas uma vez quando entra na tela
      if (revistas.length === 0) {
        loadRevistas();
      }
    }, []); // Array vazio - só executa uma vez

    const RevistaCard = ({ revista }) => {
      const turmasNomes = turmas.filter(t => revista.turma_ids.includes(t.id)).map(t => t.nome);
      const today = new Date().toISOString().split('T')[0];
      const licaoHoje = revista.licoes.find(licao => licao.data === today);
      
      return (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="mb-4">
            <h3 className="text-xl font-bold text-gray-800 mb-2">📖 Revista Trimestral</h3>
            <p className="text-sm text-gray-600 mb-3">Turmas: {turmasNomes.join(', ')}</p>
            <h4 className="text-lg font-semibold text-blue-600 mb-4">{revista.tema}</h4>
          </div>

          {licaoHoje && (
            <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
              <h5 className="font-bold text-green-800 mb-1">🎯 Lição de Hoje ({today})</h5>
              <p className="text-green-700">{licaoHoje.titulo}</p>
            </div>
          )}

          <div className="mb-4">
            <h5 className="font-semibold text-gray-700 mb-3">📚 Todas as Lições do Trimestre:</h5>
            <div className="max-h-96 overflow-y-auto">
              <div className="grid gap-2">
                {revista.licoes.map((licao, index) => {
                  const licaoDate = new Date(licao.data + 'T00:00:00');
                  const isToday = licao.data === today;
                  const isPast = licao.data < today;
                  const isFuture = licao.data > today;
                  
                  return (
                    <div 
                      key={index} 
                      className={`p-3 rounded-lg border-l-4 ${
                        isToday 
                          ? 'bg-green-100 border-green-500 text-green-800' 
                          : isPast 
                            ? 'bg-gray-100 border-gray-400 text-gray-600' 
                            : 'bg-blue-50 border-blue-400 text-blue-700'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <span className="font-medium">
                            {index + 1}. {licao.titulo}
                          </span>
                          {isToday && <span className="ml-2 text-xs font-bold">← HOJE</span>}
                        </div>
                        <span className="text-sm font-medium ml-2">
                          {licaoDate.toLocaleDateString('pt-BR')}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="text-sm text-gray-500 border-t pt-3">
            <p>Total de lições: {revista.licoes.length} | Criada em: {new Date(revista.criada_em).toLocaleDateString('pt-BR')}</p>
          </div>
        </div>
      );
    };

    return (
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-4xl mx-auto">
          {/* Header fixo no topo */}
          <div className="mb-6 sticky top-0 bg-gray-50 pb-4 border-b border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 flex items-center gap-2"
              >
                ← Voltar ao Dashboard
              </button>
              
              {(currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') && (
                <button
                  onClick={() => setCurrentView('admin-revistas')}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center gap-2"
                >
                  ➕ Gerenciar Revistas
                </button>
              )}
            </div>
            
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">📖 Revistas Trimestrais</h1>
            <p className="text-gray-600">Lições e cronograma das turmas</p>
          </div>

          {/* Botão de refresh */}
          <div className="mb-6 text-right">
            <button
              onClick={() => {
                setLoadingRevistas(true);
                loadRevistas().finally(() => setLoadingRevistas(false));
              }}
              disabled={loadingRevistas}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 flex items-center gap-2 ml-auto"
            >
              {loadingRevistas ? (
                <>
                  <span className="animate-spin">⟳</span>
                  Carregando...
                </>
              ) : (
                <>
                  🔄 Atualizar Revistas
                </>
              )}
            </button>
          </div>

          {/* Lista de Revistas */}
          {loadingRevistas ? (
            <div className="text-center py-12">
              <div className="animate-spin text-4xl mb-4">⟳</div>
              <p className="text-gray-600">Carregando revistas...</p>
            </div>
          ) : revistas.length > 0 ? (
            <div>
              {revistas.map((revista) => (
                <RevistaCard key={revista.id} revista={revista} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              <div className="text-6xl mb-4">📚</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Nenhuma revista encontrada</h3>
              <p className="text-gray-500 mb-4">
                Ainda não há revistas cadastradas no sistema.
              </p>
            </div>
          )}

          {/* Informações sobre revistas */}
          <div className="mt-8 bg-blue-50 rounded-lg p-6">
            <h4 className="font-semibold text-blue-800 mb-3">ℹ️ Sobre as Revistas:</h4>
            <ul className="text-sm text-blue-700 space-y-2">
              <li>• <strong>Lição de Hoje:</strong> Destacada em verde quando há aula programada</li>
              <li>• <strong>Cronograma:</strong> 13 lições por trimestre, organizadas por data</li>
              <li>• <strong>Turmas:</strong> Cada revista pode ser compartilhada entre várias turmas</li>
              <li>• <strong>Planejamento:</strong> Professores podem se preparar vendo as próximas lições</li>
            </ul>
          </div>
        </div>
      </div>
    );
  };

  // Componente Logs de Acesso - NOVO
  const LogsAcesso = () => {
    const formatarData = (timestamp) => {
      if (!timestamp) return 'N/A';
      return new Date(timestamp).toLocaleString('pt-BR');
    };

    const formatarDuracao = (loginTime, logoutTime) => {
      if (!loginTime || !logoutTime) return 'N/A';
      const inicio = new Date(loginTime);
      const fim = new Date(logoutTime);
      const duracao = Math.round((fim - inicio) / 1000 / 60); // em minutos
      return duracao < 60 ? `${duracao}min` : `${Math.floor(duracao/60)}h${duracao%60}min`;
    };

    return (
      <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => setCurrentView('dashboard')}
              className="mb-4 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              ← Voltar ao Dashboard
            </button>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">Logs de Acesso</h1>
            <p className="text-gray-600">Histórico de acessos ao sistema</p>
          </div>

          {/* Estatísticas Rápidas */}
          {logStats && Object.keys(logStats).length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Estatísticas</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">{logStats.total_logins || 0}</div>
                  <div className="text-sm text-blue-500">Total de Logins</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">{logStats.usuarios_ativos || 0}</div>
                  <div className="text-sm text-green-500">Usuários Ativos</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">{logStats.sessoes_ativas || 0}</div>
                  <div className="text-sm text-purple-500">Sessões Ativas</div>
                </div>
              </div>
            </div>
          )}

          {/* Tabela de Logs */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">Histórico de Acesso</h2>
                <button
                  onClick={() => {
                    loadAccessLogs();
                    loadAccessStats();
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  🔄 Atualizar
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              {logsLoading ? (
                <div className="p-8 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="mt-2 text-gray-600">Carregando logs...</p>
                </div>
              ) : (
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Usuário
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Login
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Logout
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Duração
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        IP
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {accessLogs.length > 0 ? (
                      accessLogs.map((log, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div>
                                <div className="text-sm font-medium text-gray-900">{log.user_name}</div>
                                <div className="text-sm text-gray-500">ID: {log.user_id}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatarData(log.timestamp)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {log.logout_time ? formatarData(log.logout_time) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Ativo
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatarDuracao(log.timestamp, log.logout_time)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {log.ip_address || 'N/A'}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                          Nenhum log de acesso encontrado
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>

            {accessLogs.length > 0 && (
              <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
                <p className="text-sm text-gray-700">
                  Exibindo {accessLogs.length} registros mais recentes
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Renderização condicional
  const renderCurrentView = () => {
    // Se não está logado, mostrar apenas home
    if (!isLoggedIn && currentView !== 'home') {
      setCurrentView('home');
      return <HomeCover />;
    }

    switch(currentView) {
      case 'home':
        return <HomeCover />;
      case 'dashboard':
        return isLoggedIn ? <Dashboard /> : <HomeCover />;
      case 'chamada':
        return isLoggedIn ? <Chamada /> : <HomeCover />;
      case 'relatorios':
        return isLoggedIn && (currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') ? <Relatorios /> : <Dashboard />;
      case 'ranking':
        return isLoggedIn && (currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') ? <Rankings /> : <Dashboard />;
      case 'alunos':
        return isLoggedIn && (currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') ? <Alunos /> : <Dashboard />;
      case 'turmas':
        return isLoggedIn && (currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') ? <Turmas /> : <Dashboard />;
      case 'usuarios':
        return isLoggedIn && (currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') ? <Usuarios /> : <Dashboard />;
      case 'alterar-senha':
        return isLoggedIn ? <AlterarSenha /> : <HomeCover />;
      case 'revistas':
        return isLoggedIn ? <Revistas /> : <HomeCover />;
      case 'admin-revistas':
        return isLoggedIn && (currentUser?.tipo === 'admin' || currentUser?.tipo === 'moderador') ? <AdminRevistas /> : <Dashboard />;
      default:
        return <HomeCover />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {renderCurrentView()}
      {showLogin && <LoginModal />}
    </div>
  );
}

export default App;