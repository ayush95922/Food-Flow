import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axiosClient';
import { Utensils, Upload, Sparkles, CheckCircle2, AlertCircle, Clock, Thermometer, ShieldAlert } from 'lucide-react';

export default function CreateDonation() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    foodName: '',
    foodCategory: 'cooked_meal',
    foodDescription: '',
    quantity: 50,
    quantityUnit: 'portions',
    preparationTime: new Date(Date.now() - 3600000).toISOString().slice(0, 16),
    storageCondition: 'ROOM_TEMP',
    temperatureC: 25,
    packaging: 'covered',
    pickupAddress: user?.address || '45 Ring Road, Scheme 54, Indore',
    latitude: 22.7533,
    longitude: 75.8937,
    pickupDeadline: new Date(Date.now() + 14400000).toISOString().slice(0, 16),
    remainingUsableMinutes: 240,
    aiPredictedFood: '',
    aiConfidence: null,
    aiVerifiedByDonor: false,
    imageUrl: ''
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [usableTimeData, setUsableTimeData] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));

    // Trigger AI food recognition
    const uploadData = new FormData();
    uploadData.append('file', file);

    setAiLoading(true);
    setError('');

    try {
      const res = await api.post('/ai/recognize-food', uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.data?.success && res.data.data) {
        const ai = res.data.data;
        setAiResult(ai);
        setFormData(prev => ({
          ...prev,
          foodName: ai.food || prev.foodName,
          foodCategory: ai.category || prev.foodCategory,
          aiPredictedFood: ai.food,
          aiConfidence: ai.confidence,
          aiVerifiedByDonor: true
        }));

        // Trigger usable time estimation
        recalcUsableTime(ai.category || formData.foodCategory, formData.storageCondition, formData.temperatureC);
      }
    } catch (err) {
      console.warn('AI recognition failed', err);
    } finally {
      setAiLoading(false);
    }
  };

  const recalcUsableTime = async (category, storage, temp) => {
    try {
      const res = await api.post('/ai/estimate-usability', {
        foodCategory: category,
        storageCondition: storage.toLowerCase(),
        temperatureC: parseFloat(temp) || 25,
        elapsedMinutes: 60
      });

      if (res.data?.success && res.data.data) {
        setUsableTimeData(res.data.data);
        if (res.data.data.estimated_remaining_minutes) {
          setFormData(prev => ({
            ...prev,
            remainingUsableMinutes: res.data.data.estimated_remaining_minutes
          }));
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' || name === 'temperatureC' || name === 'latitude' || name === 'longitude'
        ? parseFloat(value) || 0
        : value
    }));

    if (name === 'storageCondition' || name === 'temperatureC' || name === 'foodCategory') {
      const cat = name === 'foodCategory' ? value : formData.foodCategory;
      const stor = name === 'storageCondition' ? value : formData.storageCondition;
      const t = name === 'temperatureC' ? value : formData.temperatureC;
      recalcUsableTime(cat, stor, t);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const payload = {
        ...formData,
        preparationTime: new Date(formData.preparationTime).toISOString(),
        pickupDeadline: new Date(formData.pickupDeadline).toISOString(),
      };

      const res = await api.post('/donations', payload);
      if (res.data?.success) {
        navigate(`/donations/${res.data.data.id}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to create donation');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">List Surplus Food Donation</h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload an image for automated AI classification and usable-time estimation.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center space-x-2 text-xs text-rose-700">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Food Photo & AI Tagging */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <h2 className="text-sm font-bold text-slate-900">1. Food Image & AI Auto-Tagging</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">Upload Surplus Food Photo</label>
              <div className="border-2 border-dashed border-slate-300 hover:border-emerald-500 rounded-2xl p-6 text-center cursor-pointer transition relative">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                {imagePreview ? (
                  <div className="space-y-2">
                    <img src={imagePreview} alt="Uploaded food" className="max-h-48 mx-auto rounded-xl object-cover shadow-sm" />
                    <p className="text-xs text-slate-500">Click to choose another photo</p>
                  </div>
                ) : (
                  <div className="space-y-2 py-4">
                    <Upload className="w-8 h-8 text-slate-400 mx-auto" />
                    <p className="text-xs font-medium text-slate-700">Drag photo or click to browse</p>
                    <p className="text-[11px] text-slate-400">Supports JPG, PNG up to 10 MB</p>
                  </div>
                )}
              </div>
            </div>

            {/* AI Prediction Feedback */}
            <div className="space-y-3">
              {aiLoading ? (
                <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center space-y-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600 mx-auto"></div>
                  <p className="text-xs font-medium text-slate-600">Analyzing image with Food Vision model...</p>
                </div>
              ) : aiResult ? (
                <div className="p-5 bg-emerald-50 border border-emerald-200 rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider">AI Classification</span>
                    <span className="text-xs font-bold bg-emerald-600 text-white px-2 py-0.5 rounded-full">
                      {(aiResult.confidence * 100).toFixed(0)}% Confidence
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900">{aiResult.food}</p>
                    <p className="text-xs text-emerald-700 font-medium">Mapped Category: {aiResult.category}</p>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Source: {aiResult.source || 'MobileNetV2 / Groq Vision'}. You may verify or edit these details below.
                  </p>
                </div>
              ) : (
                <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center text-xs text-slate-500">
                  Upload an image to see automated AI dish recognition and category matching.
                </div>
              )}

              {/* Usable Time ML Preview */}
              {usableTimeData && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-1 text-xs">
                  <div className="flex items-center space-x-1.5 font-bold text-blue-900">
                    <Clock className="w-4 h-4 text-blue-600" />
                    <span>ML Usable-Time Estimate</span>
                  </div>
                  <p className="text-slate-700">
                    Estimated Safe Window: <span className="font-bold text-blue-800">{usableTimeData.estimated_remaining_minutes} minutes</span> 
                    {' '}(~{(usableTimeData.estimated_remaining_minutes / 60).toFixed(1)} hours).
                  </p>
                  <p className="text-[10px] text-slate-500">
                    Statistical regression output; follow local food safety standards before consumption.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Step 2: Food Details */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Utensils className="w-4 h-4 text-emerald-600" />
            <h2 className="text-sm font-bold text-slate-900">2. Food Description & Quantity</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">Food Name *</label>
              <input
                type="text"
                name="foodName"
                required
                value={formData.foodName}
                onChange={handleChange}
                placeholder="e.g. Vegetable Dum Biryani, Mixed Sandwiches"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Food Category *</label>
              <select
                name="foodCategory"
                value={formData.foodCategory}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="cooked_meal">Cooked Meal (Rice, Curry, Stew)</option>
                <option value="bakery">Bakery / Bread / Roti</option>
                <option value="produce">Fresh Fruits / Produce / Salad</option>
                <option value="dairy">Dairy Products / Sweets</option>
                <option value="packaged_goods">Packaged Food</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Quantity *</label>
              <input
                type="number"
                name="quantity"
                required
                min="1"
                value={formData.quantity}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Unit</label>
              <select
                name="quantityUnit"
                value={formData.quantityUnit}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="portions">Portions / Plates</option>
                <option value="kg">Kilograms (kg)</option>
                <option value="packets">Packets</option>
                <option value="boxes">Boxes</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Storage Condition</label>
              <select
                name="storageCondition"
                value={formData.storageCondition}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="ROOM_TEMP">Room Temperature</option>
                <option value="REFRIGERATED">Refrigerated (Cold)</option>
                <option value="WARM">Warm / Thermal Container</option>
                <option value="FROZEN">Frozen</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Temp (°C)</label>
              <input
                type="number"
                name="temperatureC"
                value={formData.temperatureC}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Preparation Time *</label>
            <input
              type="datetime-local"
              name="preparationTime"
              required
              value={formData.preparationTime}
              onChange={handleChange}
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Description & Allergens</label>
            <textarea
              name="foodDescription"
              rows="2"
              value={formData.foodDescription}
              onChange={handleChange}
              placeholder="e.g. Vegetarian only, prepared for 100 pax lunch. Clean container, vegetarian spices."
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            ></textarea>
          </div>
        </div>

        {/* Step 3: Pickup Logistics */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
            <Clock className="w-4 h-4 text-emerald-600" />
            <h2 className="text-sm font-bold text-slate-900">3. Pickup Logistics & Deadlines</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Pickup Address *</label>
              <input
                type="text"
                name="pickupAddress"
                required
                value={formData.pickupAddress}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Pickup Deadline *</label>
              <input
                type="datetime-local"
                name="pickupDeadline"
                required
                value={formData.pickupDeadline}
                onChange={handleChange}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 px-6 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition shadow-lg shadow-emerald-600/20 disabled:opacity-50 text-sm"
        >
          {submitting ? 'Calculating Multi-Factor Allocations...' : 'Publish Surplus Donation & Compute Matching'}
        </button>
      </form>
    </div>
  );
}

