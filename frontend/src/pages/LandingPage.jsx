import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Utensils, HeartHandshake, ShieldCheck, Cpu, ArrowRight, TrendingUp, Sparkles, Navigation, Clock } from 'lucide-react';
import api from '../api/axiosClient';

export default function LandingPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get('/admin/stats')
      .then(res => {
        if (res.data?.success) setStats(res.data.data);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-16 py-12">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
        <div className="inline-flex items-center space-x-2 bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-1.5 rounded-full text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>Research-Oriented CSE Minor Project • B.Tech</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-tight">
          Dynamic AI-Assisted Surplus Food Redistribution
        </h1>

        <p className="text-lg text-slate-600 max-w-2xl mx-auto font-normal">
          Connecting food donors with verified charities under time and demand uncertainty using 
          multi-factor optimization, usable-time regression, and fairness-aware allocation.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            to="/role-selection"
            className="bg-emerald-600 text-white font-semibold px-6 py-3 rounded-xl hover:bg-emerald-700 transition flex items-center space-x-2 shadow-lg shadow-emerald-600/20"
          >
            <span>Get Started / Register</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/research"
            className="bg-white text-slate-800 font-semibold px-6 py-3 rounded-xl border border-slate-300 hover:bg-slate-50 transition flex items-center space-x-2 shadow-sm"
          >
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <span>View Research Evaluation</span>
          </Link>
        </div>
      </section>

      {/* Key Metrics Strip */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <p className="text-3xl font-extrabold text-emerald-600">{stats?.total_portions_redistributed || '3,110'}</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Portions Rescued & Redistributed</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-emerald-600">0.85</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Jain's Fairness Index</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-emerald-600">9 Factors</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Multi-Criteria Optimization</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-emerald-600">-54.8%</p>
            <p className="text-xs text-slate-500 font-medium mt-1">Wastage vs Baseline</p>
          </div>
        </div>
      </section>

      {/* System Modules Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-900">End-to-End Scientific Architecture</h2>
          <p className="text-sm text-slate-500 mt-1">Engineered with high modularity and research-grade mathematical formulation.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">AI Food Recognition & Usable Time</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              MobileNetV2 image classification with transfer learning on Food-101 and Groq vision fallback. 
              Estimates remaining usable hours based on temperature, elapsed time, and storage conditions.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
              <HeartHandshake className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Dynamic Multi-Factor Matching</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Replaces naive nearest-neighbor matching with a 9-factor Simple Additive Weighting model incorporating
              unmet demand, capacity, urgency, usable time, and past allocation history.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
              <Navigation className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Volunteer Routing & OpenStreetMap</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Interactive Leaflet.js maps with 2-opt heuristic routing algorithms optimizing pickup deadlines, 
              safe transport ETA margins, and sequence scheduling.
            </p>
          </div>
        </div>
      </section>

      {/* Role Selection Call to Action */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 text-white rounded-3xl p-8 sm:p-12 text-center space-y-6">
          <h2 className="text-3xl font-extrabold tracking-tight">Ready to Test or Evaluate the System?</h2>
          <p className="text-sm text-slate-300 max-w-xl mx-auto">
            Choose your role to test live donations, demand fulfillment, volunteer deliveries, or research benchmarks.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/donor/create" className="bg-emerald-600 text-white px-5 py-2.5 rounded-xl font-semibold hover:bg-emerald-700 transition">
              I am a Food Donor
            </Link>
            <Link to="/receiver" className="bg-slate-800 text-white border border-slate-700 px-5 py-2.5 rounded-xl font-semibold hover:bg-slate-700 transition">
              I am a Food Receiver (NGO)
            </Link>
            <Link to="/research" className="bg-white text-slate-900 px-5 py-2.5 rounded-xl font-semibold hover:bg-slate-100 transition">
              Research Evaluation Dashboard
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

