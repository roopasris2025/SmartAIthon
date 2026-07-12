import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3, FileText, CheckCircle, Clock, Users, Filter, Search, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import ReportTable from '../components/ReportTable';
import Modal from '../components/Modal';
import { DUMMY_REPORTS } from '../utils/helpers';
import { fetchReports, updateReport } from '../services/api';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState(DUMMY_REPORTS);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const loadReports = async () => {
    setLoading(true);
    try {
      const res = await fetchReports();
      setReports(res.data);
    } catch {
      // Use dummy data
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadReports(); }, []);

  const handleMarkCleaned = async (id) => {
    try {
      try {
        await updateReport(id, { status: 'cleaned' });
      } catch { /* demo mode */ }
      setReports(prev =>
        prev.map(r => r.id === id ? { ...r, status: 'cleaned' } : r)
      );
      toast.success('Report marked as cleaned!');
    } catch {
      toast.error('Failed to update report');
    }
  };

  const filtered = reports.filter(r => {
    const matchFilter = filter === 'all' || r.status === filter;
    const matchSearch = !search ||
      r.description.toLowerCase().includes(search.toLowerCase()) ||
      r.reporter?.toLowerCase().includes(search.toLowerCase()) ||
      r.location?.toLowerCase().includes(search.toLowerCase());
    return matchFilter && matchSearch;
  });

  const stats = {
    total:    reports.length,
    pending:  reports.filter(r => r.status === 'pending').length,
    cleaned:  reports.filter(r => r.status === 'cleaned').length,
    progress: reports.filter(r => r.status === 'in_progress').length,
  };

  return (
    <div className="min-h-screen" style={{ background: 'radial-gradient(ellipse at 60% 0%, rgba(129,140,248,0.06) 0%, transparent 60%), #0a0f1e' }}>
      <Navbar />
      <Sidebar />

      <main className="pt-20 pb-8 px-4 sm:px-6 lg:pl-72 lg:pr-8 max-w-[1400px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="mb-6 mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
        >
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-7 h-7 text-cyan-400" />
              Admin Dashboard
            </h1>
            <p className="text-slate-400 text-sm mt-1">Monitor and manage all campus waste reports</p>
          </div>
          <button onClick={loadReports}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl glass border border-white/10 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-all">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard title="Total Reports"    value={stats.total}    icon={FileText}     color="cyan"    trend="All time" />
          <StatCard title="Pending"          value={stats.pending}  icon={Clock}        color="amber"   trend="Needs action" />
          <StatCard title="In Progress"      value={stats.progress} icon={Users}        color="indigo"  trend="Being handled" />
          <StatCard title="Cleaned"          value={stats.cleaned}  icon={CheckCircle}  color="emerald" trend="Completed" />
        </div>

        {/* Filters & Search */}
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="glass-dark rounded-2xl border border-white/5 p-4 mb-4 flex flex-col sm:flex-row gap-3"
        >
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <input
              type="text" placeholder="Search reports, reporters, locations..."
              value={search} onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          {/* Filter pills */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <Filter className="w-4 h-4 text-slate-500 flex-shrink-0" />
            {['all', 'pending', 'in_progress', 'cleaned'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                  filter === f
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                }`}>
                {f.replace('_', ' ')}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        >
          <ReportTable
            reports={filtered}
            loading={loading}
            onView={setSelectedReport}
            onMarkCleaned={handleMarkCleaned}
          />
        </motion.div>

        {/* Quick Charts Row */}
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4"
        >
          {[
            { label: 'Cleaned',     pct: (stats.cleaned  / stats.total * 100) || 0, color: 'bg-emerald-500' },
            { label: 'Pending',     pct: (stats.pending  / stats.total * 100) || 0, color: 'bg-amber-500'   },
            { label: 'In Progress', pct: (stats.progress / stats.total * 100) || 0, color: 'bg-indigo-500'  },
          ].map((item) => (
            <div key={item.label} className="glass-dark rounded-2xl p-4 border border-white/5">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-slate-300">{item.label}</span>
                <span className="text-sm font-bold text-white">{item.pct.toFixed(0)}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }} animate={{ width: `${item.pct}%` }}
                  transition={{ duration: 1, ease: 'easeOut', delay: 0.5 }}
                  className={`h-full rounded-full ${item.color}`}
                />
              </div>
            </div>
          ))}
        </motion.div>
      </main>

      {/* Report detail modal */}
      <Modal report={selectedReport} onClose={() => setSelectedReport(null)} onMarkCleaned={handleMarkCleaned} />
    </div>
  );
};

export default AdminDashboard;
