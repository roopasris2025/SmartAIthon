import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MapPin, Clock, User, Tag } from 'lucide-react';
import { formatDate, getStatusColor } from '../utils/helpers';

/**
 * Report details modal
 * Props: report (object | null), onClose () => void, onMarkCleaned (id) => void
 */
const Modal = ({ report, onClose, onMarkCleaned }) => {
  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <AnimatePresence>
      {report && (
        <motion.div
          key="overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }}
          onClick={onClose}
        >
          <motion.div
            key="modal"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            className="glass-dark rounded-2xl border border-cyan-500/20 w-full max-w-lg shadow-2xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Image Header */}
            <div className="relative h-48 overflow-hidden">
              <img
                src={report.image || 'https://picsum.photos/seed/waste/600/300'}
                alt="Waste report"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0a0f1e] to-transparent"></div>
              <button
                onClick={onClose}
                className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70 transition-all"
              >
                <X className="w-4 h-4" />
              </button>
              <span className={`absolute bottom-3 left-3 px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(report.status)}`}>
                {report.status?.toUpperCase()}
              </span>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              <p className="text-white font-semibold text-lg">{report.description}</p>

              <div className="grid grid-cols-1 gap-3">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <MapPin className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <span>{report.location || 'Location not provided'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <User className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                  <span>Reported by: <span className="text-white">{report.reporter || 'Anonymous'}</span></span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  <span>{formatDate(report.createdAt)}</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                {report.status !== 'cleaned' && onMarkCleaned && (
                  <button
                    onClick={() => { onMarkCleaned(report.id); onClose(); }}
                    className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white text-sm font-semibold hover:opacity-90 transition-all shadow-lg hover:shadow-cyan-500/30"
                  >
                    ✓ Mark as Cleaned
                  </button>
                )}
                <button
                  onClick={onClose}
                  className="flex-1 py-2.5 rounded-xl glass border border-white/10 text-slate-300 text-sm font-medium hover:bg-white/5 transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Modal;
