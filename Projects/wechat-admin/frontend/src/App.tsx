import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Dashboard } from './components/Dashboard';
import { ParticlesBackground } from './components/ParticlesBackground';

type Page = 'login' | 'register' | 'dashboard';

const FloatingThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <button onClick={toggleTheme} className="theme-toggle-btn theme-toggle-floating">
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  );
};

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
    return <div className="loading">加载中...</div>;
  }

  const isAuthPage = currentPage === 'login' || currentPage === 'register';

  return (
    <>
      <ParticlesBackground />
      <div className="relative z-10 min-h-screen">
        {currentPage === 'login' && <Login onNavigate={navigate} />}
        {currentPage === 'register' && <Register onNavigate={navigate} />}
        {currentPage === 'dashboard' && <Dashboard onNavigate={navigate} />}
        {isAuthPage && <FloatingThemeToggle />}
      </div>
    </>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;