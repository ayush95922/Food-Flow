import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axiosClient';
import LeafletMap from '../components/LeafletMap';
import ExplanationModal from '../components/ExplanationModal';
import { Utensils, Clock, MapPin, Award, CheckCircle, RefreshCw, AlertCircle, ArrowLeft } from 'lucide-react';

export default function DonationDetails() {
  const { id } = useParams();
  const [donation, setDonation] = useState(null);
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAllocation, setSelectedAllocation] = useState(null);
  const [recalculating, setRecalculating] = useState(false);

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const fetchDetails = async () => {
    try {
      const donRes = await api.get(`/donations/${id}`);
      if (donRes.data?.success) {
        setDonation(donRes.data.data);
      }
      const matchRes = await api.get(`/matching/recommendations/${id}`);
      if (matchRes.data?.success) {
        setAllocations(matchRes.data.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async (strategy = 'dynamic') => {
    setRecalculating(true);
    try {
      const res = await api.post('/matching/recalculate', {
        donationId: parseInt(id),
        strategy
      });
      if (res.data?.success) {
        setAllocations(res.data.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setRecalculating(false);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-sm text-slate-500">Loading donation details...</div>;
  }

  if (!donation) {
    return <div className="p-12 text-center text-sm text-rose-500">Donation listing not found.</div>;
  }

  const firstRec = allocations[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center space-x-2 text-xs text-slate-500">
        <Link to="/donor" className="hover:text-emerald-600 flex items-center space-x-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </Link>
        <span>/</span>
        <span className="font-semibold text-slate-700">Donation #{donation.id}</span>
      </div>

      {/* Main Details Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
              {donation.status}
            </span>
            <span className="text-xs bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-medium">
              Category: {donation.food_category}
            </span>
            {donation.ai_predicted_food && (
              <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-full font-semibold">
                AI Tagged: {donation.ai_predicted_food}
              </span>
            )}
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">{donation.food_name}</h1>
          <p className="text-sm text-slate-600 leading-relaxed">{donation.food_description || 'Surplus batch ready for immediate pickup.'}</p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-[11px] text-slate-400 font-semibold block">QUANTITY</span>
              <span className="text-base font-bold text-slate-900">{donation.quantity} {donation.quantity_unit}</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-[11px] text-slate-400 font-semibold block">STORAGE</span>
              <span className="text-base font-bold text-slate-900">{donation.storage_condition}</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-[11px] text-slate-400 font-semibold block">EST. USABLE TIME</span>
              <span className="text-base font-bold text-blue-600">~{Math.round(donation.remaining_usable_minutes)} min</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
              <span className="text-[11px] text-slate-400 font-semibold block">URGENCY SCORE</span>
              <span className="text-base font-bold text-amber-600">{(donation.urgency_score * 100).toFixed(0)}%</span>
            </div>
          </div>

          <div className="text-xs text-slate-500 pt-2 flex items-center space-x-2">
            <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
            <span>Pickup: {donation.pickup_address}</span>
          </div>
        </div>

        {/* Right side map / status */}
        <div className="space-y-4">
          <LeafletMap
            title="Pickup & Candidate Route"
            pickup={{ lat: donation.latitude, lon: donation.longitude, name: donation.pickup_address }}
            delivery={firstRec ? { lat: firstRec.recipient_address ? 22.7244 : 22.7380, lon: 75.8711, name: firstRec.recipient_organization_name } : null}
          />
        </div>
      </div>

      {/* Dynamic Multi-Factor Recommendations Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-emerald-600" />
              <h2 className="text-lg font-bold text-slate-900">Dynamic Multi-Factor Matching Recommendations</h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Ranked using SAW scoring: Demand (15%), Quantity (10%), Distance (12%), Urgency (10%), Usable Time (10%), Capacity (8%), Fairness (15%).
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleRecalculate('dynamic')}
              disabled={recalculating}
              className="text-xs font-semibold px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition flex items-center space-x-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${recalculating ? 'animate-spin' : ''}`} />
              <span>Recalculate (Dynamic)</span>
            </button>
            <button
              onClick={() => handleRecalculate('nearest')}
              disabled={recalculating}
              className="text-xs font-semibold px-3 py-1.5 bg-slate-50 text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-100 transition"
            >
              Nearest Baseline
            </button>
          </div>
        </div>

        {allocations.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            No eligible recipient matches within distance and usable-time constraints.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {allocations.map((alloc) => (
              <div
                key={alloc.id}
                className="p-5 border border-slate-200 rounded-xl hover:border-emerald-500 hover:shadow-sm transition bg-white space-y-3"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      RANK #{alloc.ranking} MATCH
                    </span>
                    <h3 className="text-base font-bold text-slate-900">{alloc.recipient_organization_name}</h3>
                    <p className="text-xs text-slate-500">Contact: {alloc.recipient_contact_person}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-extrabold text-emerald-600">
                      {(alloc.matching_score * 100).toFixed(1)}%
                    </span>
                    <p className="text-[10px] text-slate-400 font-semibold">MATCH SCORE</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center text-xs py-2 bg-slate-50 rounded-lg">
                  <div>
                    <span className="text-[10px] text-slate-400 block font-semibold">ALLOCATION</span>
                    <span className="font-bold text-slate-800">{alloc.quantity_allocated} portions</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block font-semibold">DISTANCE</span>
                    <span className="font-bold text-slate-800">{alloc.distance_km} km</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block font-semibold">PICKUP ETA</span>
                    <span className="font-bold text-slate-800">~{alloc.pickup_eta_minutes} min</span>
                  </div>
                </div>

                <div className="flex justify-between items-center pt-1">
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                    alloc.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'
                  }`}>
                    Status: {alloc.status}
                  </span>
                  <button
                    onClick={() => setSelectedAllocation(alloc)}
                    className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 hover:underline flex items-center space-x-1"
                  >
                    <span>View Matching Explanation &rarr;</span>
                  </button>
                </div>
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

