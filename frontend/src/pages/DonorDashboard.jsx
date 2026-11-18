import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axiosClient';
import { Utensils, Plus, Clock, MapPin, CheckCircle, AlertTriangle, ChevronRight, Eye } from 'lucide-react';

export default function DonorDashboard() {
  const { user } = useAuth();
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.profileId) {
      fetchDonations();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchDonations = async () => {
    try {
      const res = await api.get(`/donations/donor/${user.profileId}`);
      if (res.data?.success) {
        setDonations(res.data.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'AVAILABLE':
        return <span className="bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full">Available</span>;
      case 'MATCHED':
        return <span className="bg-blue-100 text-blue-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full">Recipients Matched</span>;
      case 'ACCEPTED':
        return <span className="bg-purple-100 text-purple-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full">Accepted by Charity</span>;
      case 'PICKUP_ASSIGNED':
      case 'PICKED_UP':
        return <span className="bg-amber-100 text-amber-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full">Volunteer En Route</span>;
      case 'DELIVERED':
        return <span className="bg-emerald-600 text-white text-[11px] font-bold px-2.5 py-0.5 rounded-full">Delivered</span>;
      case 'CANCELLED':
        return <span className="bg-slate-200 text-slate-700 text-[11px] font-bold px-2.5 py-0.5 rounded-full">Cancelled</span>;
      default:
        return <span className="bg-slate-100 text-slate-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full">{status}</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shadow-sm">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider">Donor Control Portal</span>
          <h1 className="text-2xl font-bold text-slate-900">{user?.organizationName || 'Donor Dashboard'}</h1>
          <p className="text-xs text-slate-500 mt-1">Manage surplus food listings, AI predictions, and delivery trackings.</p>
        </div>
        <Link
          to="/donor/create"
          className="bg-emerald-600 text-white font-semibold text-sm px-4 py-2.5 rounded-xl hover:bg-emerald-700 transition flex items-center space-x-1.5 shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Food Donation</span>
        </Link>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <p className="text-xs text-slate-500 font-medium">Total Listings</p>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{donations.length}</p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <p className="text-xs text-slate-500 font-medium">Active / Matched</p>
          <p className="text-2xl font-extrabold text-blue-600 mt-1">
            {donations.filter(d => ['AVAILABLE', 'MATCHED', 'ACCEPTED', 'PICKUP_ASSIGNED'].includes(d.status)).length}
          </p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <p className="text-xs text-slate-500 font-medium">Successfully Delivered</p>
          <p className="text-2xl font-extrabold text-emerald-600 mt-1">
            {donations.filter(d => d.status === 'DELIVERED').length}
          </p>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200">
          <p className="text-xs text-slate-500 font-medium">Total Quantity Rescued</p>
          <p className="text-2xl font-extrabold text-purple-600 mt-1">
            {donations.reduce((acc, d) => acc + (d.quantity || 0), 0)} <span className="text-xs font-normal text-slate-500">portions</span>
          </p>
        </div>
      </div>

      {/* Donations List */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-base font-bold text-slate-900">Your Food Donations</h2>
          <span className="text-xs text-slate-500">{donations.length} items listed</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading donations...</div>
        ) : donations.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <Utensils className="w-10 h-10 text-slate-300 mx-auto" />
            <p className="text-sm font-medium text-slate-600">No surplus donations posted yet.</p>
            <Link
              to="/donor/create"
              className="inline-block text-xs font-semibold text-emerald-600 hover:underline"
            >
              List your first surplus food batch &rarr;
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {donations.map((d) => (
              <div key={d.id} className="p-6 hover:bg-slate-50/50 transition flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5 max-w-xl">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-base font-bold text-slate-900">{d.food_name}</h3>
                    {getStatusBadge(d.status)}
                    {d.ai_predicted_food && (
                      <span className="bg-emerald-50 text-emerald-700 text-[10px] font-semibold px-2 py-0.5 rounded border border-emerald-200">
                        AI Verified ({Math.round(d.ai_confidence * 100)}%)
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-1">{d.food_description || 'No description provided'}</p>
                  <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
                    <span className="font-semibold text-slate-800">
                      Quantity: {d.quantity} {d.quantity_unit}
                    </span>
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>Usable: ~{Math.round(d.remaining_usable_minutes)} min</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span className="truncate max-w-[200px]">{d.pickup_address}</span>
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-3 shrink-0">
                  <Link
                    to={`/donations/${d.id}`}
                    className="px-3.5 py-2 text-xs font-semibold text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-100 transition flex items-center space-x-1"
                  >
                    <Eye className="w-3.5 h-3.5 text-slate-500" />
                    <span>View Matches & Status</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

