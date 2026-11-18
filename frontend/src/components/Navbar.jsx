import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Utensils, BarChart3, LogOut, User, Navigation, ShieldCheck } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-2">
              <div className="bg-emerald-600 text-white p-2 rounded-lg shadow-sm">
                <Utensils className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-xl text-slate-900 tracking-tight">FoodFlow</span>
                <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full">
                  AI-Assisted
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/research" className="flex items-center space-x-1 text-sm font-medium text-slate-600 hover:text-emerald-600 transition">
              <BarChart3 className="w-4 h-4 text-emerald-600" />
              <span>Research Evaluation</span>
            </Link>

            {user?.role === 'ROLE_DONOR' && (
              <>
                <Link to="/donor" className="text-sm font-medium text-slate-700 hover:text-emerald-600">
                  Donor Dashboard
                </Link>
                <Link to="/donor/create" className="text-sm font-medium bg-emerald-600 text-white px-3 py-1.5 rounded-md hover:bg-emerald-700 transition">
                  + Donate Food
                </Link>
              </>
            )}

            {user?.role === 'ROLE_RECEIVER' && (
              <>
                <Link to="/receiver" className="text-sm font-medium text-slate-700 hover:text-emerald-600">
                  Receiver Dashboard
                </Link>
                <Link to="/receiver/demands" className="text-sm font-medium text-slate-700 hover:text-emerald-600">
                  Manage Demands
                </Link>
              </>
            )}

            {user?.role === 'ROLE_VOLUNTEER' && (
              <Link to="/volunteer" className="flex items-center space-x-1 text-sm font-medium text-slate-700 hover:text-emerald-600">
                <Navigation className="w-4 h-4" />
                <span>Deliveries & Route</span>
              </Link>
            )}

            {user?.role === 'ROLE_ADMIN' && (
              <Link to="/admin" className="flex items-center space-x-1 text-sm font-medium text-slate-700 hover:text-emerald-600">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Admin Console</span>
              </Link>
            )}
          </nav>

          {/* User profile / Auth buttons */}
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-bold text-slate-800">{user.fullName}</p>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider">{user.role?.replace('ROLE_', '')}</p>
                </div>
                <button
                  onClick={handleLogout}
                  title="Logout"
                  className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link to="/login" className="text-sm font-medium text-slate-700 hover:text-emerald-600 px-3 py-1.5">
                  Sign In
                </Link>
                <Link
                  to="/role-selection"
                  className="text-sm font-medium bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 shadow-sm transition"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

