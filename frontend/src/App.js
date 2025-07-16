import React, { useState, useEffect, Suspense, lazy } from 'react';
import axios from 'axios';
import './App.css';
import Loading from './components/Loading';
import HomeCover from './components/HomeCover';
import Dashboard from './components/Dashboard';

// Lazy load components
const Chamada = lazy(() => import('./components/Chamada'));
const Relatorios = lazy(() => import('./components/Relatorios'));
const Rankings = lazy(() => import('./components/Rankings'));
const Alunos = lazy(() => import('./components/Alunos'));
const Turmas = lazy(() => import('./components/Turmas'));
const Usuarios = lazy(() => import('./components/Usuarios'));

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [showApp, setShowApp] = useState(false);
  const [turmas, setTurmas] = useState([]);
  const [students, setStudents] = useState([]);
  const [attendanceData, setAttendanceData] = useState([]);
  const [selectedTurma, setSelectedTurma] = useState(null);
  const [selectedDate, setSelectedDate] = useState('2025-07-13');
  const [loading, setLoading] = useState(false);
  
  // Estados de ranking
  const [rankingAlunos, setRankingAlunos] = useState([]);
  const [rankingProfessores, setRankingProfessores] = useState([]);
  const [rankingTurmas, setRankingTurmas] = useState([]);
  const [activeTab, setActiveTab] = useState('alunos');
  
  // Estados de autenticação
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(null);
  const [showLogin, setShowLogin] = useState(false);

  // Verificar login salvo
  useEffect(() => {
    const savedToken = localStorage.getItem('ebd_token');
    const savedUser = localStorage.getItem('ebd_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setCurrentUser(JSON.parse(savedUser));
      setIsLoggedIn(true);
    }
  }, []);

  // Carregar dados iniciais
  useEffect(() => {
    if (isLoggedIn) {
      loadDashboard();
    }
  }, [isLoggedIn, selectedDate]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/reports/dashboard?data=${selectedDate}`);
      setAttendanceData(response.data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
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

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const senha = formData.get('password');

    try {
      const response = await axios.post(`${API}/login`, { email, senha });
      
      if (response.data.token) {
        setToken(response.data.token);
        setCurrentUser(response.data);
        setIsLoggedIn(true);
        setShowLogin(false);
        
        // Salvar no localStorage
        localStorage.setItem('ebd_token', response.data.token);
        localStorage.setItem('ebd_user', JSON.stringify(response.data));
      }
    } catch (error) {
      alert('Login falhou: ' + (error.response?.data?.detail || 'Erro desconhecido'));
    }
  };

  const handleLogout = () => {
    setToken(null);
    setCurrentUser(null);
    setIsLoggedIn(false);
    setCurrentView('home');
    localStorage.removeItem('ebd_token');
    localStorage.removeItem('ebd_user');
  };

  // Renderização condicional
  if (!isLoggedIn && currentView !== 'home') {
    setCurrentView('home');
    return null;
  }

  // Props compartilhadas
  const sharedProps = {
    currentUser,
    setCurrentView,
    selectedDate,
    setSelectedDate,
    attendanceData,
    setAttendanceData,
    turmas,
    setTurmas,
    students,
    setStudents,
    loadDashboard,
    loadTurmas,
    loadStudents,
    loadRankings,
    rankingAlunos,
    rankingProfessores,
    rankingTurmas,
    activeTab,
    setActiveTab,
    API,
    loading,
    setLoading
  };

  const renderCurrentView = () => {
    switch(currentView) {
      case 'home':
        return (
          <HomeCover
            isLoggedIn={isLoggedIn}
            currentUser={currentUser}
            showLogin={showLogin}
            setShowLogin={setShowLogin}
            setCurrentView={setCurrentView}
            handleLogin={handleLogin}
            handleLogout={handleLogout}
          />
        );
      case 'dashboard':
        return isLoggedIn ? (
          <Dashboard
            {...sharedProps}
          />
        ) : (
          <HomeCover
            isLoggedIn={isLoggedIn}
            currentUser={currentUser}
            showLogin={showLogin}
            setShowLogin={setShowLogin}
            setCurrentView={setCurrentView}
            handleLogin={handleLogin}
            handleLogout={handleLogout}
          />
        );
      case 'chamada':
        return isLoggedIn ? (
          <Suspense fallback={<Loading message="Carregando chamada..." />}>
            <Chamada {...sharedProps} />
          </Suspense>
        ) : (
          <HomeCover
            isLoggedIn={isLoggedIn}
            currentUser={currentUser}
            showLogin={showLogin}
            setShowLogin={setShowLogin}
            setCurrentView={setCurrentView}
            handleLogin={handleLogin}
            handleLogout={handleLogout}
          />
        );
      case 'relatorios':
        return isLoggedIn && currentUser?.tipo === 'admin' ? (
          <Suspense fallback={<Loading message="Carregando relatórios..." />}>
            <Relatorios {...sharedProps} />
          </Suspense>
        ) : (
          <Dashboard {...sharedProps} />
        );
      case 'ranking':
        return isLoggedIn && currentUser?.tipo === 'admin' ? (
          <Suspense fallback={<Loading message="Carregando rankings..." />}>
            <Rankings {...sharedProps} />
          </Suspense>
        ) : (
          <Dashboard {...sharedProps} />
        );
      case 'alunos':
        return isLoggedIn && currentUser?.tipo === 'admin' ? (
          <Suspense fallback={<Loading message="Carregando alunos..." />}>
            <Alunos {...sharedProps} />
          </Suspense>
        ) : (
          <Dashboard {...sharedProps} />
        );
      case 'turmas':
        return isLoggedIn && currentUser?.tipo === 'admin' ? (
          <Suspense fallback={<Loading message="Carregando turmas..." />}>
            <Turmas {...sharedProps} />
          </Suspense>
        ) : (
          <Dashboard {...sharedProps} />
        );
      case 'usuarios':
        return isLoggedIn && currentUser?.tipo === 'admin' ? (
          <Suspense fallback={<Loading message="Carregando usuários..." />}>
            <Usuarios {...sharedProps} />
          </Suspense>
        ) : (
          <Dashboard {...sharedProps} />
        );
      default:
        return (
          <HomeCover
            isLoggedIn={isLoggedIn}
            currentUser={currentUser}
            showLogin={showLogin}
            setShowLogin={setShowLogin}
            setCurrentView={setCurrentView}
            handleLogin={handleLogin}
            handleLogout={handleLogout}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {renderCurrentView()}
    </div>
  );
}

export default App;