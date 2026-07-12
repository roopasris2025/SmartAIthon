import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Trophy, MapPin, AlertCircle, Star, TrendingUp,
  Zap, Plus, Activity
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import StatCard from '../components/StatCard';
import { DUMMY_REPORTS } from '../utils/helpers';

const BINS = [
  { id: 1, name: 'Cafeteria Bin',  fill: 87, status: 'critical', lat: '12.9716° N', lng: '77.5946° E' },
  { id: 2, name: 'Science Block',  fill: 55, status: 'moderate', lat: '12.9720° N', lng: '77.5950° E' },
  { id: 3, name: 'Library Zone',   fill: 30, status: 'good',     lat: '12.9710° N', lng: '77.5940° E' },
  { id: 4, name: 'Sports Ground',  fill: 72, status: 'high',     lat: '12.9730° N', lng: '77.5960° E' },
];

const fillColor = (fill) => {
  if (fill >= 80) return 'from-rose-500 to-rose-600';
  if (fill >= 60) return 'from-amber-500 to-amber-600';
  if (fill >= 40) return 'from-cyan-500 to-cyan-600';
  return 'from-emerald-500 to-emerald-600';
};

const fillBorder = (fill) => {
  if (fill >= 80) return 'border-rose-500/30 bg-rose-500/5';
  if (fill >= 60) return 'border-amber-500/30 bg-amber-500/5';
  if (fill >= 40) return 'border-cyan-500/30 bg-cyan-500/5';
  return 'border-emerald-500/30 bg-emerald-500/5';
};

const StudentDashboard = () => {
  const { user } = useAuth();
  const myReports = DUMMY_REPORTS.filter((_, i) => i < 3);

  const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.1 } },
  };
  const itemVariants = {
    hidden:  { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="min-h-screen" style={{ background: 'radial-gradient(ellipse at top, rgba(34,211,238,0.05) 0%, transparent 60%), #0a0f1e' }}>
      <Navbar />

      <main className="pt-20 pb-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Hero header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="mb-8 mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold text-white">
              Hey, <span className="gradient-text">{user?.name || 'Student'}</span> 👋
            </h1>
            <p className="text-slate-400 mt-1">Your campus waste contribution at a glance</p>
          </div>
          <Link
            to="/report"
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold text-sm hover:opacity-90 transition-all shadow-lg hover:shadow-cyan-500/30 glow-pulse"
          >
            <Plus className="w-4 h-4" />
            Report Waste
          </Link>
        </motion.div>

        {/* Stats */}
        <motion.div
          variants={containerVariants} initial="hidden" animate="visible"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          {[
            { title: 'Total Points',    value: user?.points ?? 320, icon: Star,        color: 'cyan',    trend: '+50 pts this week' },
            { title: 'Reports Filed',   value: myReports.length,     icon: AlertCircle, color: 'indigo',  trend: '2 pending' },
            { title: 'Campus Rank',     value: '#3',                  icon: Trophy,      color: 'amber',   trend: 'Top 10%' },
            { title: 'Your Impact',     value: '12 kg',               icon: Zap,         color: 'emerald', trend: 'Waste cleared' },
          ].map((s, i) => (
            <motion.div key={i} variants={itemVariants}>
              <StatCard {...s} />
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Nearby bins */}
          <motion.div
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            className="lg:col-span-2 glass-dark rounded-2xl border border-white/5 p-6"
          >
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-cyan-400" />
                <h2 className="text-white font-semibold">Nearby Waste Bins</h2>
              </div>
              <Link to="/map" className="text-xs text-cyan-400 hover:underline">View Map →</Link>
            </div>

            {/* Map placeholder */}
            <div className="relative w-full h-40 rounded-xl overflow-hidden mb-4 bg-slate-800/60 border border-white/5 flex items-center justify-center">
              <div className="absolute inset-0" style={{
                backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 30px, rgba(34,211,238,0.04) 30px, rgba(34,211,238,0.04) 31px),
                  repeating-linear-gradient(90deg, transparent, transparent 30px, rgba(34,211,238,0.04) 30px, rgba(34,211,238,0.04) 31px)`
              }}></div>
              {BINS.map((bin, i) => (
                <div key={bin.id}
                  className="absolute w-3 h-3 rounded-full border-2 border-white cursor-pointer hover:scale-150 transition-transform"
                  style={{
                    left: `${15 + i * 22}%`, top: `${30 + (i % 2) * 35}%`,
                    background: bin.fill >= 80 ? '#f43f5e' : bin.fill >= 60 ? '#f59e0b' : '#22d3ee',
                    boxShadow: `0 0 8px ${bin.fill >= 80 ? '#f43f5e' : bin.fill >= 60 ? '#f59e0b' : '#22d3ee'}60`,
                  }}
                  title={bin.name}
                />
              ))}
              <p className="text-slate-500 text-xs absolute bottom-2 right-2">📍 Campus Map Preview</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {BINS.map((bin) => (
                <div key={bin.id} className={`rounded-xl p-3 border ${fillBorder(bin.fill)}`}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-white">{bin.name}</span>
                    <span className="text-xs font-bold" style={{ color: bin.fill >= 80 ? '#f43f5e' : bin.fill >= 60 ? '#f59e0b' : '#22d3ee' }}>
                      {bin.fill}%
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }} animate={{ width: `${bin.fill}%` }}
                      transition={{ duration: 1, ease: 'easeOut', delay: 0.5 }}
                      className={`h-full rounded-full bg-gradient-to-r ${fillColor(bin.fill)}`}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{bin.lat}, {bin.lng}</p>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Activity Feed */}
          <motion.div
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}
            className="glass-dark rounded-2xl border border-white/5 p-6"
          >
            <div className="flex items-center gap-2 mb-5">
              <Activity className="w-5 h-5 text-indigo-400" />
              <h2 className="text-white font-semibold">Recent Activity</h2>
            </div>
            <div className="space-y-4">
              {[
                { label: 'Report submitted',  sub: 'Cafeteria bin',    time: '2h ago',  icon: AlertCircle, color: 'text-cyan-400'   },
                { label: 'Points earned +50', sub: 'Plastic waste',    time: '1d ago',  icon: Star,        color: 'text-amber-400'  },
                { label: 'Report Cleaned!',   sub: 'Main walkway',     time: '2d ago',  icon: TrendingUp,  color: 'text-emerald-400'},
                { label: 'Report submitted',  sub: 'Sports ground',    time: '3d ago',  icon: AlertCircle, color: 'text-cyan-400'   },
                { label: 'Points earned +30', sub: 'Bio-waste hostel', time: '4d ago',  icon: Star,        color: 'text-amber-400'  },
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className={`mt-0.5 flex-shrink-0 ${item.color}`}>
                    <item.icon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white">{item.label}</p>
                    <p className="text-xs text-slate-500">{item.sub}</p>
                  </div>
                  <span className="text-xs text-slate-600 whitespace-nowrap">{item.time}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Points progress */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}
          className="mt-6 glass-dark rounded-2xl border border-white/5 p-6"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
              <h2 className="text-white font-semibold">Points Progress</h2>
            </div>
            <span className="text-sm text-cyan-400 font-semibold">{user?.points ?? 320} / 500 pts</span>
          </div>
          <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
            <motion.div
              initial={{ width: 0 }} animate={{ width: `${((user?.points ?? 320) / 500) * 100}%` }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: 0.6 }}
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-indigo-600"
              style={{ boxShadow: '0 0 12px rgba(34,211,238,0.4)' }}
            />
          </div>
          <p className="text-xs text-slate-500 mt-2">Earn {500 - (user?.points ?? 320)} more points to reach Gold rank 🥇</p>
        </motion.div>
      </main>
    </div>
  );
};

export default StudentDashboard;
