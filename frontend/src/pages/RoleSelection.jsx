import React from 'react';
import { Link } from 'react-router-dom';
import { Utensils, HeartHandshake, UserCheck, Shield } from 'lucide-react';

export default function RoleSelection() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-slate-900">Select Your Registration Role</h1>
        <p className="text-sm text-slate-500">Choose how you participate in the surplus food redistribution ecosystem.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Food Donor */}
        <Link
          to="/register/donor"
          className="bg-white p-8 rounded-2xl border-2 border-slate-200 hover:border-emerald-600 shadow-sm hover:shadow-md transition group text-left space-y-4"
        >
          <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center group-hover:scale-105 transition">
            <Utensils className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 group-hover:text-emerald-700 transition">Food Donor</h2>
            <p className="text-xs text-slate-500 mt-1">
              Restaurants, Hotels, Hostels, College Canteens, Caterers, and Individuals.
            </p>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Donate surplus prepared food with AI image recognition auto-tagging, track dynamic matching recommendations, and schedule pickups.
          </p>
          <div className="pt-2 text-xs font-semibold text-emerald-600 flex items-center space-x-1">
            <span>Register as Food Donor &rarr;</span>
          </div>
        </Link>

        {/* Food Receiver */}
        <Link
          to="/register/receiver"
          className="bg-white p-8 rounded-2xl border-2 border-slate-200 hover:border-blue-600 shadow-sm hover:shadow-md transition group text-left space-y-4"
        >
          <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center group-hover:scale-105 transition">
            <HeartHandshake className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 group-hover:text-blue-700 transition">Food Receiver (NGO / Charity)</h2>
            <p className="text-xs text-slate-500 mt-1">
              NGOs, Food Banks, Orphanages, Shelters, and Community Relief Kitchens.
            </p>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Publish daily demand requirements, receive fairness-aware donation matches with explainable scoring, and accept surplus food allocations.
          </p>
          <div className="pt-2 text-xs font-semibold text-blue-600 flex items-center space-x-1">
            <span>Register as Food Receiver &rarr;</span>
          </div>
        </Link>
      </div>

      <div className="text-center pt-4">
        <p className="text-xs text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="text-emerald-600 font-semibold hover:underline">
            Sign In here
          </Link>
        </p>
      </div>
    </div>
  );
}

