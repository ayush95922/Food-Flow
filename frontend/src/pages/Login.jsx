import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, AlertCircle, Key, UserCheck } from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(email, password);
      redirectByRole(user.role);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  const redirectByRole = (role) => {
    switch (role) {
      case 'ROLE_DONOR':
        navigate('/donor');
        break;
      case 'ROLE_RECEIVER':
        navigate('/receiver');
        break;
      case 'ROLE_VOLUNTEER':
        navigate('/volunteer');
        break;
      case 'ROLE_ADMIN':
        navigate('/admin');
        break;
      default:
        navigate('/');
    }
  };

  const setDemoCredentials = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 space-y-6">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-6">
        <div className="text-center space-y-1">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto mb-3">
            <LogIn className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Sign In to FoodFlow</h1>
          <p className="text-xs text-slate-500">Access your role dashboard and redistribution activity.</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center space-x-2 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@domain.com"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition shadow-sm disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Login Buttons for Evaluators */}
        <div className="border-t border-slate-100 pt-5 space-y-2">
          <div className="flex items-center space-x-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <Key className="w-3.5 h-3.5" />
            <span>Quick Demo Accounts (1-Click Fill)</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => setDemoCredentials('donor@greenhotel.com', 'donor123')}
              className="p-2 border border-slate-200 rounded-lg hover:border-emerald-500 hover:bg-emerald-50 text-slate-700 text-left transition"
            >
              <span className="font-semibold block text-emerald-800">Food Donor</span>
              <span className="text-[10px] text-slate-400">Grand Palace Hotel</span>
            </button>
            <button
              type="button"
              onClick={() => setDemoCredentials('receiver@hopeorphanage.org', 'receiver123')}
              className="p-2 border border-slate-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 text-slate-700 text-left transition"
            >
              <span className="font-semibold block text-blue-800">Food Receiver</span>
              <span className="text-[10px] text-slate-400">Hope Orphanage</span>
            </button>
            <button
              type="button"
              onClick={() => setDemoCredentials('volunteer@foodflow.org', 'volunteer123')}
              className="p-2 border border-slate-200 rounded-lg hover:border-amber-500 hover:bg-amber-50 text-slate-700 text-left transition"
            >
              <span className="font-semibold block text-amber-800">Volunteer</span>
              <span className="text-[10px] text-slate-400">Rahul Verma</span>
            </button>
            <button
              type="button"
              onClick={() => setDemoCredentials('admin@foodflow.org', 'admin123')}
              className="p-2 border border-slate-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 text-slate-700 text-left transition"
            >
              <span className="font-semibold block text-purple-800">Administrator</span>
              <span className="text-[10px] text-slate-400">Full System Control</span>
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 pt-2">
          Don't have an account?{' '}
          <Link to="/role-selection" className="text-emerald-600 font-semibold hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}

