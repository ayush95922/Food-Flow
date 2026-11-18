import React from 'react';
import { Heart, BookOpen, Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-slate-500">
          <div>
            <h4 className="font-semibold text-slate-900 mb-2">FoodFlow Academic Project</h4>
            <p className="text-xs leading-relaxed">
              Dynamic AI-Assisted Surplus Food Redistribution Under Time and Demand Uncertainty.
              A research-oriented CSE Minor Project exploring algorithmic fairness, multi-factor matching, and food waste reduction.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 mb-2 flex items-center space-x-1">
              <BookOpen className="w-4 h-4 text-emerald-600" />
              <span>Research Components</span>
            </h4>
            <ul className="text-xs space-y-1">
              <li>• Simple Additive Weighting (SAW) Multi-Factor Matching</li>
              <li>• Jain's Fairness Index & Max-Min Allocation</li>
              <li>• Thermal & Elapsed Time Usability Regression</li>
              <li>• Heuristic Route Optimization (2-Opt & Dijkstra)</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 mb-2 flex items-center space-x-1">
              <Shield className="w-4 h-4 text-emerald-600" />
              <span>Academic Integrity Notice</span>
            </h4>
            <p className="text-xs leading-relaxed">
              ML estimations are statistical estimates based on documented assumptions and do not constitute formal food-safety certification.
            </p>
          </div>
        </div>
        <div className="border-t border-slate-100 mt-6 pt-4 text-center text-xs text-slate-400 flex items-center justify-center space-x-1">
          <span>Developed with</span>
          <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" />
          <span>for B.Tech Computer Science & Engineering</span>
        </div>
      </div>
    </footer>
  );
}

