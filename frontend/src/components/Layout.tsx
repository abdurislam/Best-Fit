import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Home, PlusCircle, Shirt, Sparkles, LogOut, User } from 'lucide-react';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/closet', icon: Home, label: 'My Closet' },
    { to: '/add-item', icon: PlusCircle, label: 'Add Item' },
    { to: '/outfits', icon: Shirt, label: 'Outfits' },
    { to: '/suggestions', icon: Sparkles, label: 'Suggestions' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <nav className="fixed left-0 top-0 h-full w-64 bg-slate-800 text-white p-6 flex flex-col">
        <div className="flex items-center gap-3 mb-10">
          <span className="text-3xl">👔</span>
          <span className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-purple-400 bg-clip-text text-transparent">
            Best-Fit
          </span>
        </div>

        <ul className="flex-1 space-y-2">
          {navItems.map(({ to, icon: Icon, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-300 hover:bg-slate-700'
                  }`
                }
              >
                <Icon size={20} />
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>

        {/* User section */}
        <div className="border-t border-slate-700 pt-4 mt-4">
          <div className="flex items-center gap-3 px-4 py-2 text-gray-300">
            <User size={20} />
            <span className="truncate text-sm">{user?.displayName || user?.email}</span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-slate-700 transition-colors w-full mt-2"
          >
            <LogOut size={20} />
            <span>Sign Out</span>
          </button>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}
