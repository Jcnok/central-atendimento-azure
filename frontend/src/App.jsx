import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginForm from './components/LoginForm';
import Signup from './pages/Signup';
import Support from './pages/Support';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Tickets from './pages/Tickets';
import Clients from './pages/Clients';
import Agent from './pages/Agent';
import Settings from './pages/Settings';
import './index.css'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div>Carregando...</div>;
  if (!user) return <Navigate to="/login" />;

  return <Layout>{children}</Layout>;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <div className="container-fluid">
      <Routes>
        <Route path="/login" element={!user ? <LoginForm /> : <Navigate to="/" />} />
        <Route path="/signup" element={!user ? <Signup /> : <Navigate to="/" />} />
        <Route path="/support" element={<Support />} />

        <Route path="/" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />

        <Route path="/tickets" element={
          <ProtectedRoute>
            <Tickets />
          </ProtectedRoute>
        } />

        <Route path="/clients" element={
          <ProtectedRoute>
            <Clients />
          </ProtectedRoute>
        } />

        <Route path="/agent" element={
          <ProtectedRoute>
            <Agent />
          </ProtectedRoute>
        } />

        <Route path="/settings" element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        } />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
