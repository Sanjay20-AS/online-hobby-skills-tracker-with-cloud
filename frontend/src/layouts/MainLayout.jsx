import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts';

export function MainLayout({ children }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const navItems = [
    { path: '/dashboard', label: '📊 Dashboard' },
    { path: '/hobbies', label: '🎨 My Hobbies' },
    { path: '/skills', label: '⭐ Skills' },
    { path: '/goals', label: '🎯 Goals' },
    { path: '/sessions', label: '⏱️ Sessions' },
    { path: '/milestones', label: '🏆 Milestones' },
    { path: '/community', label: '👥 Community' },
    { path: '/search', label: '🔍 Search' },
    { path: '/profile', label: '👤 Profile' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile header */}
      <div className="lg:hidden bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="flex items-center justify-between p-4">
          <h1 className="text-xl font-bold text-gray-900">Hobby Tracker</h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-700"
          >
            ☰
          </button>
        </div>
      </div>

      <div className="flex h-screen">
        {/* Sidebar */}
        <aside
          className={`fixed lg:static left-0 top-0 h-full w-64 bg-white border-r border-gray-200 p-6 overflow-y-auto z-30 transition-all ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          }`}
        >
          <div className="hidden lg:block mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Hobby Tracker</h1>
            <p className="text-sm text-gray-600 mt-1">Track your hobbies & skills</p>
          </div>

          <nav className="space-y-2 mb-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="border-t border-gray-200 pt-4">
            <div className="mb-4">
              <p className="text-sm text-gray-600">Signed in as</p>
              <p className="text-sm font-semibold text-gray-900 truncate">
                {user?.email || 'User'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto lg:p-8 p-4">
          {children}
        </main>
      </div>
    </div>
  );
}
