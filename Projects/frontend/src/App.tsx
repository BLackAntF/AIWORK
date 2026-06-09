import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Dashboard } from './components/Dashboard';

type Page = 'login' | 'register' | 'dashboard';

const AppContent = () => {
  const [currentPage, setCurrentPage] = useState<Page>('login');
  const { token, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && token) {
      setCurrentPage('dashboard');
    }
  }, [token, isLoading]);

  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/register') setCurrentPage('register');
      else if (path === '/dashboard') setCurrentPage('dashboard');
      else setCurrentPage('login');
    };

    handlePopState();
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    if (path === '/register') setCurrentPage('register');
    else if (path === '/dashboard') setCurrentPage('dashboard');
    else setCurrentPage('login');
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="app">
      {currentPage === 'login' && <Login onNavigate={navigate} />}
      {currentPage === 'register' && <Register onNavigate={navigate} />}
      {currentPage === 'dashboard' && <Dashboard onNavigate={navigate} />}
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;