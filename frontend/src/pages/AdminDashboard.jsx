import React, { useEffect, useState } from 'react';
import api from '../api/axiosClient';
import { ShieldCheck, Users, Utensils, HeartHandshake, CheckCircle2, XCircle, AlertTriangle, Activity } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [aiHealth, setAiHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [statsRes, usersRes, healthRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/admin/users'),
        api.get('/ai/health').catch(() => ({ data: { success: false } }))
      ]);

      if (statsRes.data?.success) setStats(statsRes.data.data);
      if (usersRes.data?.success) setUsers(usersRes.data.data);
      if (healthRes.data?.success) setAiHealth(healthRes.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleUser = async (userId) => {
    try {
      const res = await api.put(`/admin/users/${userId}/toggle-status`);
      if (res.data?.success) {
        setUsers(prev => prev.map(u => u.id === userId ? res.data.data : u));
      }
    } catch (e) {
      alert('Failed to update user status');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shadow-sm">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider">System Administration</span>
          <h1 className="text-2xl font-bold text-slate-900">Platform Control & Monitoring</h1>
          <p className="text-xs text-slate-500 mt-1">Supervise user registrations, surplus listings, and redistribution activity.</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700">
            <Activity className="w-3.5 h-3.5 text-emerald-600" />
            <span>AI Subsystem: {aiHealth?.service_online ? 'FastAPI Online' : 'Algorithmic Engine Active'}</span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Registered Donors</p>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{stats?.total_donors || 0}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Verified Charities</p>
          <p className="text-2xl font-extrabold text-blue-600 mt-1">{stats?.total_receivers || 0}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Delivered Donations</p>
          <p className="text-2xl font-extrabold text-emerald-600 mt-1">{stats?.delivered_donations || 0}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">System Fairness Index</p>
          <p className="text-2xl font-extrabold text-purple-600 mt-1">{stats?.current_fairness_index || 0.85}</p>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm space-y-4">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-sm font-bold text-slate-900">Registered Users & Role Management</h2>
          <span className="text-xs text-slate-500">{users.length} accounts</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-sm text-slate-500">Loading users...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">User</th>
                  <th className="px-6 py-3">Role</th>
                  <th className="px-6 py-3">Contact</th>
                  <th className="px-6 py-3">City / Address</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4">
                      <p className="font-bold text-slate-900">{u.fullName}</p>
                      <p className="text-slate-400">{u.email}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`font-semibold px-2 py-0.5 rounded-full text-[10px] ${
                        u.role === 'ROLE_ADMIN' ? 'bg-purple-100 text-purple-800' :
                        u.role === 'ROLE_DONOR' ? 'bg-emerald-100 text-emerald-800' :
                        u.role === 'ROLE_RECEIVER' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {u.role?.replace('ROLE_', '')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{u.phoneNumber || 'N/A'}</td>
                    <td className="px-6 py-4 text-slate-600">{u.city || u.address || 'Indore'}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        u.enabled ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
                      }`}>
                        {u.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {u.role !== 'ROLE_ADMIN' && (
                        <button
                          onClick={() => toggleUser(u.id)}
                          className="text-xs font-semibold text-slate-600 hover:text-emerald-600 underline"
                        >
                          {u.enabled ? 'Disable' : 'Enable'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

