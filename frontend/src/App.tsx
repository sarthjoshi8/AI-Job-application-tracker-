import React from 'react';
import { useAuth } from './context/AuthContext';
import { AuthPage } from './pages/AuthPage';
import { Dashboard } from './pages/Dashboard';
import { RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-sky-400 mb-3" />
        <p className="text-xs uppercase tracking-wider font-semibold">Initializing Firebase Auth...</p>
      </div>
    );
  }

  return user ? <Dashboard /> : <AuthPage />;
};

export default App;
