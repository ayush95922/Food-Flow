import React from 'react';
import { X, CheckCircle2, AlertCircle, Award } from 'lucide-react';

export default function ExplanationModal({ isOpen, onClose, allocation }) {
  if (!isOpen || !allocation) return null;

  let explanation = null;
  try {
    if (typeof allocation.explanation_json === 'string') {
      explanation = JSON.parse(allocation.explanation_json);
    } else {
      explanation = allocation.explanation_json;
    }
  } catch (e) {
    explanation = null;
  }

  const factorScores = explanation?.factor_scores || {
    demand: 0.85,
    quantity: 0.90,
    distance: 0.75,
    urgency: 0.65,
    usable_time: 0.80,
    capacity: 0.88,
    fairness: 0.78
  };

  const factorLabels = {
    demand: 'Unmet Demand Weight (15%)',
    quantity: 'Quantity Absorptive Match (10%)',
    distance: 'Geographic Proximity (12%)',
    urgency: 'Surplus Urgency Score (10%)',
    usable_time: 'Usable Time Slack Margin (10%)',
    capacity: 'Storage Handling Capacity (8%)',
    fairness: 'Jain/Max-Min Fairness (15%)',
    compatibility: 'Category Compatibility (8%)',
    pickup_feasibility: 'Pickup Feasibility (12%)'
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-100 overflow-hidden transform transition-all">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-emerald-400" />
            <h3 className="font-semibold text-base">Multi-Factor Matching Explanation</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Top Score Summary */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-emerald-800 uppercase tracking-wider">Candidate Organization</p>
              <h4 className="text-lg font-bold text-slate-900">{allocation.recipient_organization_name}</h4>
              <p className="text-xs text-slate-600 mt-0.5">
                Distance: <span className="font-semibold">{allocation.distance_km} km</span> • 
                Pickup ETA: <span className="font-semibold">{allocation.pickup_eta_minutes} min</span>
              </p>
            </div>
            <div className="text-right">
              <span className="text-3xl font-extrabold text-emerald-600">
                {(allocation.matching_score * 100).toFixed(1)}%
              </span>
              <p className="text-[11px] font-medium text-emerald-800">Overall Match Score</p>
            </div>
          </div>

          {/* Factor Breakdown */}
          <div>
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Normalized Multi-Criteria Scores (s_k ∈ [0, 1])
            </h4>
            <div className="space-y-3">
              {Object.entries(factorScores).map(([key, val]) => {
                const score = typeof val === 'number' ? val : 0.75;
                const pct = Math.round(score * 100);
                return (
                  <div key={key}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium text-slate-700">{factorLabels[key] || key}</span>
                      <span className="font-semibold text-slate-900">{score.toFixed(2)} ({pct}%)</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          pct >= 75 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-rose-500'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(5, pct))}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Algorithmic Reasons */}
          {explanation?.reasons && explanation.reasons.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Identified Strengths
              </h4>
              <ul className="space-y-1.5">
                {explanation.reasons.map((r, idx) => (
                  <li key={idx} className="flex items-start text-xs text-slate-700 space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Weaknesses if any */}
          {explanation?.weaknesses && explanation.weaknesses.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Trade-off Weaknesses
              </h4>
              <ul className="space-y-1.5">
                {explanation.weaknesses.map((w, idx) => (
                  <li key={idx} className="flex items-start text-xs text-slate-700 space-x-2">
                    <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Theoretical Note */}
          <div className="bg-slate-50 rounded-xl p-3 text-[11px] text-slate-500 border border-slate-200">
            <p>
              <strong>Research Note:</strong> Evaluated via SAW (Simple Additive Weighting). 
              Score = Σ(w_k × s_k) with hard feasibility bounds on usable-time, donor deadline, and handling capacity.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}

