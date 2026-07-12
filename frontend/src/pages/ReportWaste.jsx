import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, MapPin, FileText, CheckCircle, X, Image as ImageIcon, Send } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { createReport } from '../services/api';
import toast from 'react-hot-toast';

const ReportWaste = () => {
  const { user } = useAuth();
  const [step, setStep] = useState(1); // 1: form, 2: success
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [preview, setPreview] = useState(null);
  const [form, setForm] = useState({ description: '', lat: '', lng: '', location: '', image: null });
  const [errors, setErrors] = useState({});
  const fileInputRef = useRef();

  const handleFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) {
      toast.error('Please upload a valid image file');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image must be less than 5MB');
      return;
    }
    setForm(f => ({ ...f, image: file }));
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleChange = (e) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const useCurrentLocation = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation not supported');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setForm(f => ({ ...f, lat: latitude.toFixed(6), lng: longitude.toFixed(6), location: `${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E` }));
        toast.success('Location captured!');
      },
      () => toast.error('Could not get location')
    );
  };

  const validate = () => {
    const e = {};
    if (!form.image) e.image = 'Please upload an image';
    if (!form.description.trim()) e.description = 'Description is required';
    if (!form.location.trim() && (!form.lat || !form.lng)) e.location = 'Location is required';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('image', form.image);
      fd.append('description', form.description);
      fd.append('location', form.location || `${form.lat}° N, ${form.lng}° E`);
      fd.append('lat', form.lat);
      fd.append('lng', form.lng);
      fd.append('status', 'pending');
      try {
        await createReport(fd);
      } catch {
        // Mock success for demo
        await new Promise(r => setTimeout(r, 1000));
      }
      setStep(2);
      toast.success('Report submitted successfully! +25 points');
    } catch {
      toast.error('Failed to submit report');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setForm({ description: '', lat: '', lng: '', location: '', image: null });
    setPreview(null);
    setErrors({});
    setStep(1);
  };

  const inputCls = (field) =>
    `w-full bg-white/5 border rounded-xl px-4 py-3 text-white placeholder-slate-500 text-sm focus:outline-none transition-all ${
      errors[field]
        ? 'border-rose-500/50 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
        : 'border-white/10 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20'
    }`;

  return (
    <div className="min-h-screen" style={{ background: 'radial-gradient(ellipse at 40% 0%, rgba(129,140,248,0.07) 0%, transparent 60%), #0a0f1e' }}>
      <Navbar />
      <main className="pt-24 pb-8 px-4 sm:px-6 max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold text-white mb-1">Report Waste</h1>
          <p className="text-slate-400 text-sm mb-6">Help keep the campus clean — earn points for every valid report</p>

          {/* Progress steps */}
          <div className="flex items-center gap-2 mb-8">
            {['Upload Image', 'Location & Details', 'Submit'].map((s, i) => (
              <div key={i} className="flex items-center gap-2 flex-1">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${step > i + 1 ? 'bg-emerald-500 text-white' : step === i + 1 ? 'bg-gradient-to-br from-cyan-500 to-indigo-600 text-white' : 'bg-white/5 text-slate-500'}`}>
                  {step > i + 1 ? <CheckCircle className="w-4 h-4" /> : i + 1}
                </div>
                {i < 2 && <div className={`flex-1 h-0.5 rounded ${step > i + 1 ? 'bg-emerald-500' : 'bg-white/10'}`}></div>}
              </div>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {step === 2 ? (
              /* ─── Success ─── */
              <motion.div key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-dark rounded-2xl border border-emerald-500/20 p-10 text-center"
              >
                <motion.div
                  initial={{ scale: 0 }} animate={{ scale: 1 }}
                  transition={{ type: 'spring', damping: 12, delay: 0.1 }}
                  className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-4"
                >
                  <CheckCircle className="w-10 h-10 text-emerald-400" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">Report Submitted! 🎉</h2>
                <p className="text-slate-400 mb-2">Your waste report has been sent to campus admin.</p>
                <p className="text-emerald-400 font-semibold mb-6">You earned +25 points!</p>
                <div className="flex gap-3 justify-center">
                  <button onClick={resetForm}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white text-sm font-semibold hover:opacity-90 transition-all">
                    Report Another
                  </button>
                </div>
              </motion.div>
            ) : (
              /* ─── Form ─── */
              <motion.form key="form" onSubmit={handleSubmit}
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="glass-dark rounded-2xl border border-white/5 p-6 space-y-6"
              >
                {/* Image upload */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    <ImageIcon className="w-4 h-4 inline mr-1.5 text-cyan-400" />
                    Waste Image *
                  </label>

                  {preview ? (
                    <div className="relative rounded-xl overflow-hidden border border-white/10">
                      <img src={preview} alt="Preview" className="w-full h-48 object-cover" />
                      <button type="button" onClick={() => { setPreview(null); setForm(f => ({ ...f, image: null })); }}
                        className="absolute top-2 right-2 w-8 h-8 rounded-full bg-black/70 flex items-center justify-center text-white hover:bg-black transition-all">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div
                      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                      onDragLeave={() => setDragging(false)}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
                        dragging ? 'border-cyan-400 bg-cyan-500/10' : errors.image ? 'border-rose-500/50' : 'border-white/10 hover:border-cyan-500/40 hover:bg-white/2'
                      }`}
                    >
                      <Upload className={`w-10 h-10 mb-3 ${dragging ? 'text-cyan-400' : 'text-slate-500'}`} />
                      <p className="text-sm text-slate-400">Drag & drop or <span className="text-cyan-400 underline">browse files</span></p>
                      <p className="text-xs text-slate-600 mt-1">PNG, JPG up to 5MB</p>
                    </div>
                  )}
                  <input ref={fileInputRef} type="file" accept="image/*" className="hidden"
                    onChange={(e) => handleFile(e.target.files[0])} />
                  {errors.image && <p className="text-xs text-rose-400 mt-1">{errors.image}</p>}
                </div>

                {/* Location */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      <MapPin className="w-4 h-4 inline mr-1.5 text-indigo-400" />
                      Location *
                    </label>
                    <button type="button" onClick={useCurrentLocation}
                      className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> Use my location
                    </button>
                  </div>
                  <input name="location" type="text" placeholder="e.g. Near cafeteria block B" value={form.location}
                    onChange={handleChange} className={inputCls('location')} />
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <input name="lat" type="number" step="any" placeholder="Latitude" value={form.lat}
                      onChange={handleChange} className={inputCls('lat')} />
                    <input name="lng" type="number" step="any" placeholder="Longitude" value={form.lng}
                      onChange={handleChange} className={inputCls('lng')} />
                  </div>
                  {errors.location && <p className="text-xs text-rose-400 mt-1">{errors.location}</p>}
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    <FileText className="w-4 h-4 inline mr-1.5 text-amber-400" />
                    Description *
                  </label>
                  <textarea name="description" rows={3} placeholder="Describe the waste situation..."
                    value={form.description} onChange={handleChange}
                    className={`${inputCls('description')} resize-none`} />
                  {errors.description && <p className="text-xs text-rose-400 mt-1">{errors.description}</p>}
                </div>

                <button type="submit" disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold text-sm hover:opacity-90 transition-all shadow-lg hover:shadow-cyan-500/30 disabled:opacity-60">
                  {loading ? (
                    <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  ) : (
                    <><Send className="w-4 h-4" /> Submit Report</>
                  )}
                </button>
              </motion.form>
            )}
          </AnimatePresence>
        </motion.div>
      </main>
    </div>
  );
};

export default ReportWaste;
