import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axiosClient';
import ExplanationModal from '../components/ExplanationModal';
import { HeartHandshake, Plus, CheckCircle, XCircle, Award, Clock, MapPin, AlertCircle } from 'lucide-react';

export default function ReceiverDashboard() {
  const { user } = useAuth();
  const [allocations, setAllocations] = useState([]);
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAllocation, setSelectedAllocation] = useState(null);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    if (user?.profileId) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [user]);

  const loadData = async () => {
    try {
      const [allocRes, demRes] = await Promise.all([
        api.get(`/matching/recipient/${user.profileId}`),
        api.get(`/demands/recipient/${user.profileId}`)
      ]);
      if (allocRes.data?.success) setAllocations(allocRes.data.data);
      if (demRes.data?.success) setDemands(demRes.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (allocId) => {
    try {
      const res = await api.post(`/matching/accept/${allocId}`);
      if (res.data?.success) {
        setActionMessage('Surplus food allocation accepted! Volunteer pickup has been scheduled.');
        loadData();
      }
    } catch (err) {
      alert(err.response?.data?.message || err.message);
    }
  };

  const handleReject = async (allocId) => {
    try {
      const res = await api.post(`/matching/reject/${allocId}`);
      if (res.data?.success) {
        setActionMessage('Allocation declined. The matching engine will reassign to another recipient.');
        loadData();
      }
    } catch (err) {
      alert(err.response?.data?.message || err.message);
    }
  };

  const totalDemand = demands.reduce((acc, d) => acc + (d.quantity_required || 0), 0);
  const receivedDemand = demands.reduce((acc, d) => acc + (d.quantity_received || 0), 0);
  const unmetDemand = Math.max(0, totalDemand - receivedDemand);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shadow-sm">
        <div>
          <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">Receiver Organization Portal</span>
          <h1 className="text-2xl font-bold text-slate-900">{user?.organizationName || 'Recipient Dashboard'}</h1>
          <p className="text-xs text-slate-500 mt-1">Manage food demands and review fairness-aware multi-factor allocations.</p>
        </div>
        <Link
          to="/receiver/demands"
          className="bg-blue-600 text-white font-semibold text-sm px-4 py-2.5 rounded-xl hover:bg-blue-700 transition flex items-center space-x-1.5 shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Publish Food Demand</span>
        </Link>
      </div>

      {actionMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-2 text-xs text-emerald-800">
          <CheckCircle className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Demand & Capacity Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Active Unmet Demand</p>
          <p className="text-2xl font-extrabold text-blue-600 mt-1">{unmetDemand} <span className="text-xs font-normal text-slate-500">portions</span></p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Total Portions Received</p>
          <p className="text-2xl font-extrabold text-emerald-600 mt-1">{receivedDemand} <span className="text-xs font-normal text-slate-500">portions</span></p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Pending Matches To Review</p>
          <p className="text-2xl font-extrabold text-amber-600 mt-1">
            {allocations.filter(a => a.status === 'PROPOSED').length}
          </p>
        </div>
      </div>

      {/* Recommended Allocations */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm space-y-4 p-6">
        <div className="border-b border-slate-100 pb-3 flex justify-between items-center">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recommended Surplus Food Allocations</h2>
            <p className="text-xs text-slate-500 mt-0.5">Matched specifically for your organization based on demand, distance, and fairness.</p>
          </div>
          <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full">
            {allocations.length} Allocations
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading recommendations...</div>
        ) : allocations.length === 0 ? (
          <div className="p-10 text-center space-y-2">
            <HeartHandshake className="w-10 h-10 text-slate-300 mx-auto" />
            <p className="text-sm font-medium text-slate-700">No surplus food allocations currently assigned.</p>
            <p className="text-xs text-slate-400">Make sure you have active demands published.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {allocations.map((alloc) => (
              <div
                key={alloc.id}
                className="p-5 border border-slate-200 rounded-xl hover:border-blue-400 transition bg-white flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-2 max-w-xl">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      RANK #{alloc.ranking} MATCH
                    </span>
                    <h3 className="text-base font-bold text-slate-900">{alloc.food_name}</h3>
                    <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
                      {alloc.food_category}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      alloc.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' :
                      alloc.status === 'REJECTED' ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {alloc.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-600">
                    <div>
                      <span className="text-[10px] text-slate-400 block font-semibold">QUANTITY</span>
                      <span className="font-bold text-slate-900">{alloc.quantity_allocated} portions</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block font-semibold">MATCH SCORE</span>
                      <span className="font-bold text-emerald-600">{(alloc.matching_score * 100).toFixed(1)}%</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block font-semibold">DISTANCE</span>
                      <span className="font-bold text-slate-900">{alloc.distance_km} km</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block font-semibold">DELIVERY ETA</span>
                      <span className="font-bold text-slate-900">~{alloc.delivery_eta_minutes} min</span>
                    </div>
                  </div>

                  <button
                    onClick={() => setSelectedAllocation(alloc)}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline pt-1 inline-flex items-center space-x-1"
                  >
                    <Award className="w-3.5 h-3.5 text-blue-500" />
                    <span>Why was this donation recommended for us? &rarr;</span>
                  </button>
                </div>

                {alloc.status === 'PROPOSED' && (
                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={() => handleAccept(alloc.id)}
                      className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition shadow-sm flex items-center space-x-1"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>Accept Donation</span>
                    </button>
                    <button
                      onClick={() => handleReject(alloc.id)}
                      className="px-3 py-2 bg-slate-100 text-slate-600 rounded-lg text-xs font-semibold hover:bg-slate-200 transition flex items-center space-x-1"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Decline</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <ExplanationModal
        isOpen={!!selectedAllocation}
        onClose={() => setSelectedAllocation(null)}
        allocation={selectedAllocation}
      />
    </div>
  );
}

