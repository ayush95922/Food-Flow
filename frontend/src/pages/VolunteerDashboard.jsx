import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axiosClient';
import LeafletMap from '../components/LeafletMap';
import { Navigation, CheckCircle2, Clock, MapPin, Phone, ShieldCheck, AlertCircle } from 'lucide-react';

export default function VolunteerDashboard() {
  const { user } = useAuth();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeDelivery, setActiveDelivery] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [otpInput, setOtpInput] = useState('');

  useEffect(() => {
    fetchDeliveries();
  }, []);

  const fetchDeliveries = async () => {
    try {
      const res = await api.get('/volunteer/deliveries');
      if (res.data?.success) {
        const list = res.data.data;
        setDeliveries(list);
        if (list.length > 0 && !activeDelivery) {
          setActiveDelivery(list[0]);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (deliveryId, newStatus) => {
    setUpdating(true);
    try {
      const res = await api.put(`/volunteer/deliveries/${deliveryId}/status`, {
        status: newStatus,
        otp: otpInput
      });
      if (res.data?.success) {
        setOtpInput('');
        fetchDeliveries();
      }
    } catch (err) {
      alert(err.response?.data?.message || err.message);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 flex justify-between items-center shadow-sm">
        <div>
          <span className="text-xs font-bold text-amber-600 uppercase tracking-wider">Volunteer Dispatch Console</span>
          <h1 className="text-2xl font-bold text-slate-900">Food Rescue & Delivery Assignments</h1>
          <p className="text-xs text-slate-500 mt-1">Real-time pickup coordination, deadline adherence, and route tracking.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Side: Deliveries List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
            <h2 className="text-sm font-bold text-slate-900 mb-3">Your Assigned Missions ({deliveries.length})</h2>

            {loading ? (
              <p className="text-xs text-slate-500 text-center py-6">Loading assignments...</p>
            ) : deliveries.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500 space-y-2">
                <Navigation className="w-8 h-8 text-slate-300 mx-auto" />
                <p>No active delivery assignments.</p>
                <p className="text-[11px] text-slate-400">Assignments will appear when recipients accept donations.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {deliveries.map((del) => {
                  const isSelected = activeDelivery?.id === del.id;
                  return (
                    <div
                      key={del.id}
                      onClick={() => setActiveDelivery(del)}
                      className={`p-4 rounded-xl border cursor-pointer transition text-left space-y-2 ${
                        isSelected
                          ? 'border-emerald-600 bg-emerald-50/40 ring-1 ring-emerald-600'
                          : 'border-slate-200 hover:border-slate-300 bg-white'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <h3 className="text-sm font-bold text-slate-900">{del.food_name}</h3>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          del.status === 'DELIVERED' ? 'bg-emerald-100 text-emerald-800' :
                          del.status === 'PICKED_UP' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                        }`}>
                          {del.status}
                        </span>
                      </div>

                      <p className="text-xs font-semibold text-slate-700">
                        {del.quantity} {del.quantity_unit} • {del.distance_km} km
                      </p>

                      <div className="text-[11px] text-slate-500 space-y-1 pt-1 border-t border-slate-100">
                        <p className="truncate"><strong>From:</strong> {del.donor_organization_name}</p>
                        <p className="truncate"><strong>To:</strong> {del.recipient_organization_name}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Map & Execution Card */}
        <div className="lg:col-span-2 space-y-6">
          {activeDelivery ? (
            <>
              {/* Map View */}
              <LeafletMap
                title={`Active Mission: ${activeDelivery.food_name}`}
                pickup={{
                  lat: activeDelivery.pickup_lat || 22.7533,
                  lon: activeDelivery.pickup_lon || 75.8937,
                  name: activeDelivery.pickup_address
                }}
                delivery={{
                  lat: activeDelivery.delivery_lat || 22.7244,
                  lon: activeDelivery.delivery_lon || 75.8711,
                  name: activeDelivery.delivery_address
                }}
                volunteer={{
                  lat: 22.7400,
                  lon: 75.8800,
                  name: user?.fullName || 'Volunteer'
                }}
              />

              {/* Action Controls */}
              <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
                <div className="border-b border-slate-100 pb-4 flex justify-between items-center">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Delivery Status & Progress</h3>
                    <p className="text-xs text-slate-500">Update status as you collect and deliver surplus portions.</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
                      Pickup OTP: {activeDelivery.pickup_otp || '4821'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 bg-slate-50 rounded-xl space-y-1">
                    <span className="text-[10px] font-bold text-slate-400 block uppercase">1. PICKUP AT (DONOR)</span>
                    <p className="font-bold text-slate-900 text-sm">{activeDelivery.donor_organization_name}</p>
                    <p className="text-slate-600">{activeDelivery.pickup_address}</p>
                  </div>

                  <div className="p-4 bg-slate-50 rounded-xl space-y-1">
                    <span className="text-[10px] font-bold text-slate-400 block uppercase">2. DELIVER TO (RECIPIENT)</span>
                    <p className="font-bold text-slate-900 text-sm">{activeDelivery.recipient_organization_name}</p>
                    <p className="text-slate-600">{activeDelivery.delivery_address}</p>
                    <p className="text-slate-500">Contact: {activeDelivery.recipient_contact_person}</p>
                  </div>
                </div>

                {/* Progress Buttons */}
                <div className="flex flex-wrap items-center gap-3 pt-2">
                  {activeDelivery.status === 'ASSIGNED' && (
                    <button
                      onClick={() => handleStatusUpdate(activeDelivery.id, 'PICKED_UP')}
                      disabled={updating}
                      className="px-5 py-2.5 bg-blue-600 text-white font-bold text-xs rounded-xl hover:bg-blue-700 transition flex items-center space-x-1.5 shadow-sm"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{updating ? 'Updating...' : 'Confirm Food Picked Up from Donor'}</span>
                    </button>
                  )}

                  {activeDelivery.status === 'PICKED_UP' && (
                    <button
                      onClick={() => handleStatusUpdate(activeDelivery.id, 'DELIVERED')}
                      disabled={updating}
                      className="px-5 py-2.5 bg-emerald-600 text-white font-bold text-xs rounded-xl hover:bg-emerald-700 transition flex items-center space-x-1.5 shadow-sm"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{updating ? 'Updating...' : 'Confirm Food Delivered to Charity'}</span>
                    </button>
                  )}

                  {activeDelivery.status === 'DELIVERED' && (
                    <div className="flex items-center space-x-2 text-xs text-emerald-700 font-bold bg-emerald-50 px-4 py-2 rounded-xl border border-emerald-200">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Delivery Successfully Completed & Logged!</span>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-sm shadow-sm">
              Select an assignment on the left to inspect the route and update status.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

