import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, FileText, MapPin, Users, LogOut, Leaf, Route
} from 'lucide-react';

const Sidebar = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const links = [
    { to: '/admin',        icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/admin/reports',icon: FileText,        label: 'Reports'   },
    { to: '/map',          icon: MapPin,          label: 'Map View'  },
    { to: '/leaderboard',  icon: Users,           label: 'Users'     },
  ];

  return (
    <aside className="hidden lg:flex flex-col fixed left-0 top-0 h-full w-64 glass-dark border-r border-cyan-500/10 z-40 pt-16">
      {/* Brand */}
      <div className="px-6 py-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-bold text-white">SmartWaste</p>
            <p className="text-xs text-slate-500">Admin Panel</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/admin'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={`w-5 h-5 transition-all ${isActive ? 'text-cyan-400' : 'group-hover:text-white'}`} />
                {label}
                {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Logout at bottom */}
      <div className="p-4 border-t border-white/5">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-500/10 transition-all"
        >
          <LogOut className="w-5 h-5" />
          Log Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
