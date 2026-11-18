import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axiosClient';
import { Plus, Clock, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';

export default function DemandManagement() {
  const { user } = useAuth();
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [newDemand, setNewDemand] = useState({
    foodCategory: 'cooked_meal',
    quantityRequired: 60,
    priority: 'HIGH',
    requiredBefore: new Date(Date.now() + 18000000).toISOString().slice(0, 16),
    notes: ''
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.profileId) {
      fetchDemands();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchDemands = async () => {
    try {
      const res = await api.get(`/demands/recipient/${user.profileId}`);
      if (res.data?.success) setDemands(res.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const payload = {
        ...newDemand,
        quantityRequired: parseFloat(newDemand.quantityRequired),
        requiredBefore: new Date(newDemand.requiredBefore).toISOString()
      };
      const res = await api.post('/demands', payload);
      if (res.data?.success) {
        setShowModal(false);
        fetchDemands();
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to publish demand');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center space-x-2 text-xs text-slate-500">
        <Link to="/receiver" className="hover:text-blue-600 flex items-center space-x-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Receiver Dashboard</span>
        </Link>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-6 flex justify-between items-center shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Food Demand Requirements</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Published requirements are monitored in real-time by the Dynamic Matching engine to allocate surplus food.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 text-white font-semibold text-xs px-4 py-2 rounded-xl hover:bg-blue-700 transition flex items-center space-x-1.5 shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Add Requirement</span>
        </button>
      </div>

      {/* Demands List */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="text-sm font-bold text-slate-900">Active & Historical Food Demands</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-sm text-slate-500">Loading requirements...</div>
        ) : demands.length === 0 ? (
          <div className="p-12 text-center space-y-2">
            <Clock className="w-8 h-8 text-slate-300 mx-auto" />
            <p className="text-sm font-medium text-slate-700">No active demands registered.</p>
            <p className="text-xs text-slate-400">Click "+ Add Requirement" above to specify needed portions.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {demands.map((dem) => {
              const pct = Math.min(100, Math.round((dem.quantity_received / dem.quantity_required) * 100));
              return (
                <div key={dem.id} className="p-6 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-sm text-slate-900 capitalize">{dem.food_category?.replace('_', ' ')}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        dem.priority === 'URGENT' ? 'bg-rose-100 text-rose-800' :
                        dem.priority === 'HIGH' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                      }`}>
                        {dem.priority} Priority
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        dem.status === 'FULFILLED' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {dem.status}
                      </span>
                    </div>
                    <span className="text-xs text-slate-500">
                      Required Before: {new Date(dem.required_before).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}, {new Date(dem.required_before).toLocaleDateString()}
                    </span>
                  </div>

                  {dem.notes && <p className="text-xs text-slate-600">{dem.notes}</p>}

                  {/* Progress bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs text-slate-600 font-medium">
                      <span>Fulfilled: {dem.quantity_received} / {dem.quantity_required} portions</span>
                      <span>{pct}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          pct >= 100 ? 'bg-emerald-500' : 'bg-blue-600'
                        }`}
                        style={{ width: `${pct}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* New Demand Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-base font-bold text-slate-900">Publish New Food Requirement</h3>

            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Food Category</label>
                <select
                  value={newDemand.foodCategory}
                  onChange={(e) => setNewDemand({ ...newDemand, foodCategory: e.target.value })}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="cooked_meal">Cooked Meal (Rice, Curry, Dal)</option>
                  <option value="bakery">Bakery / Bread / Roti</option>
                  <option value="produce">Fresh Produce / Vegetables / Fruits</option>
                  <option value="dairy">Dairy Products / Milk</option>
                  <option value="any">Any Surplus Food Category</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Quantity Required (Portions)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={newDemand.quantityRequired}
                    onChange={(e) => setNewDemand({ ...newDemand, quantityRequired: e.target.value })}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Priority</label>
                  <select
                    value={newDemand.priority}
                    onChange={(e) => setNewDemand({ ...newDemand, priority: e.target.value })}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent (Immediate Need)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Required Before (Time)</label>
                <input
                  type="datetime-local"
                  required
                  value={newDemand.requiredBefore}
                  onChange={(e) => setNewDemand({ ...newDemand, requiredBefore: e.target.value })}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Notes / Beneficiary Details</label>
                <textarea
                  rows="2"
                  value={newDemand.notes}
                  onChange={(e) => setNewDemand({ ...newDemand, notes: e.target.value })}
                  placeholder="e.g. Dinner distribution for 60 homeless residents."
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-700 font-semibold hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  {submitting ? 'Publishing...' : 'Publish Requirement'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

