import { motion } from 'framer-motion';

/**
 * Reusable statistics card with gradient icon and animated counter.
 * Props:
 *  - title: string
 *  - value: number | string
 *  - icon: Lucide component
 *  - color: 'cyan' | 'indigo' | 'emerald' | 'amber' | 'rose'
 *  - trend: optional string e.g. '+12% this week'
 */
const colorMap = {
  cyan:    { bg: 'from-cyan-500/20 to-cyan-600/5',   border: 'border-cyan-500/20',   icon: 'bg-cyan-500/20 text-cyan-400',    text: 'text-cyan-400'   },
  indigo:  { bg: 'from-indigo-500/20 to-indigo-600/5', border: 'border-indigo-500/20', icon: 'bg-indigo-500/20 text-indigo-400', text: 'text-indigo-400' },
  emerald: { bg: 'from-emerald-500/20 to-emerald-600/5', border: 'border-emerald-500/20', icon: 'bg-emerald-500/20 text-emerald-400', text: 'text-emerald-400' },
  amber:   { bg: 'from-amber-500/20 to-amber-600/5',  border: 'border-amber-500/20',  icon: 'bg-amber-500/20 text-amber-400',  text: 'text-amber-400'  },
  rose:    { bg: 'from-rose-500/20 to-rose-600/5',    border: 'border-rose-500/20',   icon: 'bg-rose-500/20 text-rose-400',    text: 'text-rose-400'   },
};

const StatCard = ({ title, value, icon: Icon, color = 'cyan', trend }) => {
  const c = colorMap[color] || colorMap.cyan;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={`glass rounded-2xl p-6 border ${c.border} bg-gradient-to-br ${c.bg} cursor-default`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400 mb-1">{title}</p>
          <p className={`text-3xl font-bold ${c.text}`}>{value}</p>
          {trend && <p className="text-xs text-slate-500 mt-2">{trend}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${c.icon}`}>
          {Icon && <Icon className="w-6 h-6" />}
        </div>
      </div>
    </motion.div>
  );
};

export default StatCard;
