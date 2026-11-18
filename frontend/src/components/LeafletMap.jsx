import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function LeafletMap({ pickup, delivery, volunteer, title }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const defaultLat = pickup?.lat || 22.7196;
    const defaultLon = pickup?.lon || 75.8577;

    const map = L.map(mapContainerRef.current).setView([defaultLat, defaultLon], 13);
    mapInstanceRef.current = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const points = [];

    // Pickup Marker (Green)
    if (pickup && pickup.lat && pickup.lon) {
      const pickupIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #059669; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 2px solid white;">P</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });
      const marker = L.marker([pickup.lat, pickup.lon], { icon: pickupIcon })
        .addTo(map)
        .bindPopup(`<b>Pickup Location (Donor)</b><br/>${pickup.name || 'Donor Address'}`);
      points.push([pickup.lat, pickup.lon]);
    }

    // Delivery Marker (Blue)
    if (delivery && delivery.lat && delivery.lon) {
      const deliveryIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #2563eb; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 2px solid white;">D</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });
      const marker = L.marker([delivery.lat, delivery.lon], { icon: deliveryIcon })
        .addTo(map)
        .bindPopup(`<b>Delivery Destination (Recipient)</b><br/>${delivery.name || 'Recipient Address'}`);
      points.push([delivery.lat, delivery.lon]);
    }

    // Volunteer Marker (Amber)
    if (volunteer && volunteer.lat && volunteer.lon) {
      const volIcon = L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: #d97706; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 11px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 2px solid white;">V</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });
      L.marker([volunteer.lat, volunteer.lon], { icon: volIcon })
        .addTo(map)
        .bindPopup(`<b>Volunteer Location</b><br/>${volunteer.name || 'Active Volunteer'}`);
      points.push([volunteer.lat, volunteer.lon]);
    }

    // Draw route line
    if (points.length >= 2) {
      const polyline = L.polyline(points, {
        color: '#059669',
        weight: 4,
        opacity: 0.8,
        dashArray: '6, 8'
      }).addTo(map);

      map.fitBounds(polyline.getBounds(), { padding: [40, 40] });
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [pickup, delivery, volunteer]);

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
      {title && (
        <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
          <span className="text-xs text-slate-500">OpenStreetMap & Haversine Heuristics</span>
        </div>
      )}
      <div ref={mapContainerRef} className="w-full h-80 min-h-[300px]"></div>
    </div>
  );
}

