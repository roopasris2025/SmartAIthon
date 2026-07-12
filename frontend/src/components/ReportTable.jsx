import { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, CheckCircle, ChevronUp, ChevronDown } from 'lucide-react';
import { formatDate, getStatusColor, truncate } from '../utils/helpers';
import { SkeletonRow } from './Loader';

/**
 * Waste Reports Table
 * Props: reports[], loading, onView(report), onMarkCleaned(id)
 */
const ReportTable = ({ reports = [], loading = false, onView, onMarkCleaned }) => {
  const [sortField, setSortField] = useState('createdAt');
  const [sortDir, setSortDir] = useState('desc');

  const toggleSort = (field) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDir('asc'); }
  };

  const sorted = [...reports].sort((a, b) => {
    const av = a[sortField] ?? '';
    const bv = b[sortField] ?? '';
    return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
  });

  const SortIcon = ({ field }) =>
    sortField === field
      ? sortDir === 'asc'
        ? <ChevronUp className="w-3 h-3 inline ml-1 text-cyan-400" />
        : <ChevronDown className="w-3 h-3 inline ml-1 text-cyan-400" />
      : null;

  return (
    <div className="glass rounded-2xl border border-white/5 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/5">
              {[
                { label: 'Preview',     field: null         },
                { label: 'Description', field: 'description'},
                { label: 'Location',    field: 'location'   },
                { label: 'Reporter',    field: 'reporter'   },
                { label: 'Status',      field: 'status'     },
                { label: 'Date',        field: 'createdAt'  },
                { label: 'Actions',     field: null         },
              ].map(({ label, field }) => (
                <th
                  key={label}
                  onClick={() => field && toggleSort(field)}
                  className={`px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap ${field ? 'cursor-pointer hover:text-slate-300 transition-colors' : ''}`}
                >
                  {label}<SortIcon field={field} />
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading
              ? Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)
              : sorted.length === 0
                ? (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-slate-500">
                      No reports found
                    </td>
                  </tr>
                )
                : sorted.map((report, idx) => (
                  <motion.tr
                    key={report.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="border-b border-white/5 hover:bg-white/2 transition-colors group"
                  >
                    {/* Image preview */}
                    <td className="px-4 py-3">
                      <img
                        src={report.image || 'https://picsum.photos/seed/w/60/40'}
                        alt="preview"
                        className="w-14 h-10 rounded-lg object-cover border border-white/10"
                      />
                    </td>
                    <td className="px-4 py-3 text-slate-300 max-w-[180px]">{truncate(report.description, 35)}</td>
                    <td className="px-4 py-3 text-slate-400 max-w-[160px]">{truncate(report.location, 30)}</td>
                    <td className="px-4 py-3 text-slate-300">{report.reporter}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusColor(report.status)}`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">{formatDate(report.createdAt)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => onView && onView(report)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10 transition-all"
                          title="View details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {report.status !== 'cleaned' && (
                          <button
                            onClick={() => onMarkCleaned && onMarkCleaned(report.id)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 transition-all"
                            title="Mark as cleaned"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </motion.tr>
                ))}
          </tbody>
        </table>
      </div>
      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/5 flex items-center justify-between">
        <p className="text-xs text-slate-500">{reports.length} total reports</p>
        <p className="text-xs text-slate-500">
          {reports.filter(r => r.status === 'cleaned').length} cleaned ·{' '}
          {reports.filter(r => r.status === 'pending').length} pending
        </p>
      </div>
    </div>
  );
};

export default ReportTable;
