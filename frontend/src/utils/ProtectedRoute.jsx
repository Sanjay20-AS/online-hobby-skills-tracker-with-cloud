import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts';
import { PageLoading } from '../components';

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <PageLoading />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
