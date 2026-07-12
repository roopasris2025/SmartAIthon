import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, X, Filter, Info, RefreshCw } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import Navbar from '../components/Navbar';
import { DUMMY_MAP_MARKERS, getStatusColor } from '../utils/helpers';
import { fetchReports } from '../services/api';
import toast from 'react-hot-toast';

// Fix Leaflet default icon paths for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const markerColors = {
  pending:     '#f59e0b',
  cleaned:     '#10b981',
  in_progress: '#22d3ee',
};

const createColoredIcon = (status) => {
  const color = markerColors[status] || '#94a3b8';
  return L.divIcon({
    html: `
      <div style="
        width: 28px; height: 28px; border-radius: 50% 50% 50% 0;
        background: ${color}; border: 3px solid white;
        transform: rotate(-45deg);
        box-shadow: 0 4px 12px ${color}80;
      "></div>`,
    className: '',
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28],
  });
};

// Component to auto-fit bounds
const FitBounds = ({ markers }) => {
  const map = useMap();
  useEffect(() => {
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers.map(m => [m.lat, m.lng]));
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [markers, map]);
  return null;
};

const MapView = () => {
  const [markers, setMarkers]     = useState(DUMMY_MAP_MARKERS);
  const [selected, setSelected]   = useState(null);
  const [filter, setFilter]       = useState('all');
  const [loading, setLoading]     = useState(false);
  const CENTER                    = [12.9716, 77.5946];

  const loadMarkers = async () => {
    setLoading(true);
    try {
      const res = await fetchReports();
      const data = res.data.map(r => ({
        id: r.id, lat: parseFloat(r.lat) || 12.9716,
        lng: parseFloat(r.lng) || 77.5946,
        title: r.description?.slice(0, 30) || 'Report',
        status: r.status, description: r.description,
      }));
      if (data.length) setMarkers(data);
    } catch {
      // use dummy data silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadMarkers(); }, []);

  const filtered = filter === 'all' ? markers : markers.filter(m => m.status === filter);

  const statusCount = (s) => markers.filter(m => m.status === s).length;

  return (
    <div className="min-h-screen" style={{ background: '#0a0f1e' }}>
      <Navbar />

      <main className="pt-16">
        {/* Top bar */}
        <div className="glass-dark border-b border-white/5 px-4 sm:px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-cyan-400" /> Campus Waste Map
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">{filtered.length} report{filtered.length !== 1 ? 's' : ''} shown</p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Legend / filter buttons */}
            {[
              { key: 'all',         label: 'All',         color: '#94a3b8' },
              { key: 'pending',     label: 'Pending',     color: '#f59e0b' },
              { key: 'in_progress', label: 'In Progress', color: '#22d3ee' },
              { key: 'cleaned',     label: 'Cleaned',     color: '#10b981' },
            ].map(({ key, label, color }) => (
              <button
                key={key}
                onClick={() => setFilter(key)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                  filter === key
                    ? 'bg-white/10 border-white/20 text-white'
                    : 'border-white/5 text-slate-500 hover:text-slate-300 hover:border-white/10'
                }`}
              >
                <span className="w-2 h-2 rounded-full" style={{ background: color }}></span>
                {label}
                {key !== 'all' && <span className="ml-0.5 opacity-60">({statusCount(key)})</span>}
              </button>
            ))}
            <button onClick={loadMarkers}
              className="p-2 rounded-lg glass border border-white/10 text-slate-400 hover:text-white transition-all">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Map + detail panel */}
        <div className="flex h-[calc(100vh-8.5rem)]">
          {/* Map */}
          <div className="flex-1 relative">
            <MapContainer
              center={CENTER}
              zoom={15}
              className="w-full h-full"
              style={{ background: '#0f172a' }}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              />
              <FitBounds markers={filtered} />

              {filtered.map((m) => (
                <Marker
                  key={m.id}
                  position={[m.lat, m.lng]}
                  icon={createColoredIcon(m.status)}
                  eventHandlers={{ click: () => setSelected(m) }}
                >
                  <Popup className="custom-popup">
                    <div className="p-1">
                      <p className="font-semibold text-sm">{m.title}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${getStatusColor(m.status)}`}>
                        {m.status}
                      </span>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>

            {/* Map overlay info */}
            <div className="absolute bottom-4 left-4 glass-dark rounded-xl border border-white/10 px-3 py-2 z-[1000] pointer-events-none">
              <p className="text-xs text-slate-400">
                🌍 Bengaluru Campus · {filtered.length} markers
              </p>
            </div>
          </div>

          {/* Side panel — report detail */}
          <AnimatePresence>
            {selected && (
              <motion.aside
                key="panel"
                initial={{ x: 320, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 320, opacity: 0 }}
                transition={{ type: 'spring', damping: 20, stiffness: 200 }}
                className="w-72 glass-dark border-l border-white/5 p-5 overflow-y-auto z-10 hidden sm:block"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-white font-semibold text-sm">Report Details</h3>
                  <button onClick={() => setSelected(null)}
                    className="text-slate-500 hover:text-white transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Description</p>
                    <p className="text-sm text-white">{selected.description}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Status</p>
                    <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${getStatusColor(selected.status)}`}>
                      {selected.status?.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Coordinates</p>
                    <p className="text-xs text-slate-300 font-mono">
                      {selected.lat.toFixed(4)}° N, {selected.lng.toFixed(4)}° E
                    </p>
                  </div>

                  <div className="pt-2 border-t border-white/5 flex items-start gap-2 text-xs text-slate-500">
                    <Info className="w-3 h-3 mt-0.5 flex-shrink-0 text-cyan-400" />
                    Click a marker on the map to view its details here
                  </div>
                </div>
              </motion.aside>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

export default MapView;
