import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import HomePage         from './pages/HomePage';
import AuthPage         from './pages/AuthPage';
import StudentDashboard from './pages/StudentDashboard';
import ReportWaste      from './pages/ReportWaste';
import AdminDashboard   from './pages/AdminDashboard';
import MapView          from './pages/MapView';
import Leaderboard      from './pages/Leaderboard';

/** If already logged-in, skip home and go straight to dashboard */
const HomeRedirect = () => {
  const { user } = useAuth();
  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/dashboard'} replace />;
  return <HomePage />;
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        {/* Global toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3500,
            style: {
              background: 'rgba(15,23,42,0.95)',
              backdropFilter: 'blur(16px)',
              color: '#e2e8f0',
              border: '1px solid rgba(34,211,238,0.2)',
              borderRadius: '12px',
              fontSize: '13px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            },
            success: {
              iconTheme: { primary: '#10b981', secondary: '#0a0f1e' },
            },
            error: {
              iconTheme: { primary: '#f43f5e', secondary: '#0a0f1e' },
            },
          }}
        />

        <Routes>
          {/* Public */}
          <Route path="/auth" element={<AuthPage />} />

          {/* Public home */}
          <Route path="/" element={<HomeRedirect />} />

          {/* Student routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute requiredRole="student">
              <StudentDashboard />
            </ProtectedRoute>
          } />
          <Route path="/report" element={
            <ProtectedRoute>
              <ReportWaste />
            </ProtectedRoute>
          } />
          <Route path="/map" element={
            <ProtectedRoute>
              <MapView />
            </ProtectedRoute>
          } />
          <Route path="/leaderboard" element={
            <ProtectedRoute>
              <Leaderboard />
            </ProtectedRoute>
          } />

          {/* Admin routes */}
          <Route path="/admin" element={
            <ProtectedRoute requiredRole="admin">
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin/reports" element={
            <ProtectedRoute requiredRole="admin">
              <AdminDashboard />
            </ProtectedRoute>
          } />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
