import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, X, Info, RefreshCw, Search, Compass } from 'lucide-react';
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
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const markerColors = {
  pending: '#f59e0b',
  cleaned: '#10b981',
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
      " ></div>`,
    className: '',
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28],
  });
};

const FitBounds = ({ markers }) => {
  const map = useMap();
  useEffect(() => {
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers.map((m) => [m.lat, m.lng]));
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [markers, map]);
  return null;
};

const haversineDistance = (a, b) => {
  const toRad = (value) => (value * Math.PI) / 180;
  const R = 6371;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const sinDLat = Math.sin(dLat / 2);
  const sinDLng = Math.sin(dLng / 2);
  const h = sinDLat * sinDLat + Math.cos(lat1) * Math.cos(lat2) * sinDLng * sinDLng;
  return 2 * R * Math.asin(Math.sqrt(h));
};

const MapView = () => {
  const [markers, setMarkers] = useState(DUMMY_MAP_MARKERS);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchLocation, setSearchLocation] = useState(null);
  const [searchRadiusKm] = useState(2);
  const [googleMap, setGoogleMap] = useState(null);
  const mapContainerRef = useRef(null);
  const searchMarkerRef = useRef(null);
  const googleMarkerRefs = useRef([]);
  const googleMapsApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';
  const useGoogleMaps = Boolean(googleMapsApiKey);
  const CENTER = [12.9716, 77.5946];

  const loadMarkers = async () => {
    setLoading(true);
    try {
      const res = await fetchReports();
      const data = (res.data.reports || res.data || []).map((r) => ({
        id: r.id,
        lat: parseFloat(r.location?.lat) || 12.9716,
        lng: parseFloat(r.location?.lng) || 77.5946,
        title: r.description?.slice(0, 30) || 'Report',
        status: r.status,
        description: r.description,
        address: r.location?.address || '',
      }));
      if (data.length) setMarkers(data);
    } catch {
      // keep the local demo markers if the API is unavailable
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMarkers();
  }, []);

  useEffect(() => {
    if (!useGoogleMaps || !mapContainerRef.current || window.google?.maps) return;

    const existingScript = document.getElementById('google-maps-script');
    if (existingScript) {
      existingScript.addEventListener('load', () => {
        if (window.google?.maps) {
          const map = new window.google.maps.Map(mapContainerRef.current, {
            center: { lat: CENTER[0], lng: CENTER[1] },
            zoom: 14,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false,
          });
          setGoogleMap(map);
        }
      });
      return;
    }

    const script = document.createElement('script');
    script.id = 'google-maps-script';
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      const map = new window.google.maps.Map(mapContainerRef.current, {
        center: { lat: CENTER[0], lng: CENTER[1] },
        zoom: 14,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
      });
      setGoogleMap(map);
    };
    document.body.appendChild(script);
  }, [CENTER, googleMapsApiKey, useGoogleMaps]);

  useEffect(() => {
    if (!googleMap) return;

    googleMarkerRefs.current.forEach((marker) => marker.setMap(null));
    googleMarkerRefs.current = [];

    const infoWindow = new window.google.maps.InfoWindow();
    const visibleMarkers = filter === 'all' ? markers : markers.filter((item) => item.status === filter);
    const displayMarkers = searchLocation
      ? visibleMarkers.filter((item) => haversineDistance(searchLocation, item) <= searchRadiusKm)
      : visibleMarkers;

    displayMarkers.forEach((item) => {
      const marker = new window.google.maps.Marker({
        position: { lat: item.lat, lng: item.lng },
        map: googleMap,
        title: item.title,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 9,
          fillColor: markerColors[item.status] || '#94a3b8',
          fillOpacity: 0.95,
          strokeColor: '#ffffff',
          strokeWeight: 2,
        },
      });

      marker.addListener('click', () => {
        setSelected(item);
        infoWindow.setContent(`
          <div style="font-family: Inter, sans-serif; min-width: 180px;">
            <p style="font-weight: 700; margin: 0 0 6px;">${item.title}</p>
            <p style="margin: 0 0 4px; color: #64748b;">${item.description}</p>
            <span style="display: inline-block; padding: 2px 8px; border-radius: 999px; background: #f8fafc; color: #0f172a; font-size: 12px;">${item.status}</span>
          </div>
        `);
        infoWindow.open(googleMap, marker);
      });

      googleMarkerRefs.current.push(marker);
    });

    if (displayMarkers.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();
      displayMarkers.forEach((item) => bounds.extend({ lat: item.lat, lng: item.lng }));
      googleMap.fitBounds(bounds, 60);
    }
  }, [filter, googleMap, markers, searchLocation, searchRadiusKm]);

  useEffect(() => {
    if (!googleMap || !searchLocation) return;

    if (searchMarkerRef.current) {
      searchMarkerRef.current.setMap(null);
    }

    searchMarkerRef.current = new window.google.maps.Marker({
      position: { lat: searchLocation.lat, lng: searchLocation.lng },
      map: googleMap,
      title: 'Search area',
      icon: {
        path: window.google.maps.SymbolPath.CIRCLE,
        scale: 12,
        fillColor: '#22d3ee',
        fillOpacity: 0.95,
        strokeColor: '#ffffff',
        strokeWeight: 3,
      },
    });

    googleMap.panTo({ lat: searchLocation.lat, lng: searchLocation.lng });
    googleMap.setZoom(15);
  }, [googleMap, searchLocation]);

  const filteredMarkers = filter === 'all' ? markers : markers.filter((m) => m.status === filter);
  const displayMarkers = searchLocation
    ? filteredMarkers.filter((m) => haversineDistance(searchLocation, m) <= searchRadiusKm)
    : filteredMarkers;

  const statusCount = (s) => markers.filter((m) => m.status === s).length;

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      toast.error('Enter a campus area or landmark to search.');
      return;
    }

    setSearching(true);

    if (!useGoogleMaps || !window.google?.maps) {
      setSearching(false);
      setSearchLocation({ lat: CENTER[0], lng: CENTER[1], address: searchQuery });
      toast.success(`Showing nearby reports for ${searchQuery}`);
      return;
    }

    const geocoder = new window.google.maps.Geocoder();
    geocoder.geocode({ address: searchQuery }, (results, status) => {
      setSearching(false);
      if (status === 'OK' && results[0]) {
        const place = results[0].geometry.location;
        setSearchLocation({
          lat: place.lat(),
          lng: place.lng(),
          address: results[0].formatted_address,
        });
        toast.success(`Focused on ${results[0].formatted_address}`);
      } else {
        toast.error('No matching place found. Try a campus building or nearby street.');
      }
    });
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchLocation(null);
  };

  return (
    <div className="min-h-screen" style={{ background: '#0a0f1e' }}>
      <Navbar />

      <main className="pt-16">
        <div className="glass-dark border-b border-white/5 px-4 sm:px-6 py-4 flex flex-col gap-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-cyan-400" /> Campus Waste Map
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                {displayMarkers.length} report{displayMarkers.length !== 1 ? 's' : ''} shown
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              {[
                { key: 'all', label: 'All', color: '#94a3b8' },
                { key: 'pending', label: 'Pending', color: '#f59e0b' },
                { key: 'in_progress', label: 'In Progress', color: '#22d3ee' },
                { key: 'cleaned', label: 'Cleaned', color: '#10b981' },
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
              <button
                onClick={loadMarkers}
                className="p-2 rounded-lg glass border border-white/10 text-slate-400 hover:text-white transition-all"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search a campus area, building, or street"
                className="w-full rounded-xl border border-white/10 bg-slate-950/70 pl-10 pr-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
              />
            </div>
            <button
              type="submit"
              disabled={searching}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-sm font-semibold text-white hover:opacity-90 transition-all disabled:opacity-60"
            >
              {searching ? 'Searching...' : 'Search area'}
            </button>
            {searchLocation && (
              <button
                type="button"
                onClick={clearSearch}
                className="px-3 py-2.5 rounded-xl border border-white/10 text-sm text-slate-300 hover:text-white"
              >
                Clear
              </button>
            )}
          </form>

          <div className="rounded-xl border border-cyan-500/20 bg-slate-950/70 p-3 text-sm text-slate-300">
            <div className="flex items-center gap-2 mb-1">
              <Compass className="w-4 h-4 text-cyan-400" />
              {searchLocation ? (
                <span>
                  Showing waste reports within {searchRadiusKm} km of <span className="text-white">{searchLocation.address}</span>
                </span>
              ) : (
                <span>Search for a place to see nearby waste hotspots and their current status.</span>
              )}
            </div>
            {useGoogleMaps ? (
              <p className="text-xs text-slate-500">Google Maps is active for real place search and map navigation.</p>
            ) : (
              <p className="text-xs text-slate-500">Add a Google Maps API key to enable live place search and a full Google Maps view.</p>
            )}
          </div>
        </div>

        <div className="flex h-[calc(100vh-13rem)]">
          <div className="flex-1 relative">
            {useGoogleMaps ? (
              <div ref={mapContainerRef} className="w-full h-full" style={{ background: '#0f172a' }} />
            ) : (
              <MapContainer center={CENTER} zoom={15} className="w-full h-full" style={{ background: '#0f172a' }}>
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                />
                <FitBounds markers={displayMarkers} />

                {displayMarkers.map((m) => (
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
            )}

            <div className="absolute bottom-4 left-4 glass-dark rounded-xl border border-white/10 px-3 py-2 z-[1000] pointer-events-none">
              <p className="text-xs text-slate-400">
                🌍 {useGoogleMaps ? 'Google Maps' : 'Leaflet'} view · {displayMarkers.length} markers
              </p>
            </div>
          </div>

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
                  <button onClick={() => setSelected(null)} className="text-slate-500 hover:text-white transition-colors">
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
                    <p className="text-xs text-slate-500 mb-1">Location</p>
                    <p className="text-xs text-slate-300">{selected.address || `${selected.lat.toFixed(4)}°, ${selected.lng.toFixed(4)}°`}</p>
                  </div>
                  {searchLocation && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Distance from search area</p>
                      <p className="text-xs text-slate-300">
                        {haversineDistance(searchLocation, selected).toFixed(1)} km away
                      </p>
                    </div>
                  )}

                  <div className="pt-2 border-t border-white/5 flex items-start gap-2 text-xs text-slate-500">
                    <Info className="w-3 h-3 mt-0.5 flex-shrink-0 text-cyan-400" />
                    Search for a place to quickly find waste reports near that area.
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
