import { motion } from 'framer-motion';

/**
 * Full-page centered loader spinner
 */
const Loader = ({ message = 'Loading...' }) => (
  <div className="fixed inset-0 flex flex-col items-center justify-center bg-[#0a0f1e] z-50">
    <div className="relative">
      <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin"></div>
      <div className="absolute inset-0 w-16 h-16 rounded-full border-4 border-indigo-500/10 border-b-indigo-400 animate-spin"
        style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
    </div>
    <p className="mt-4 text-slate-400 text-sm animate-pulse">{message}</p>
  </div>
);

/**
 * Inline skeleton loader (for cards, table rows etc.)
 */
export const SkeletonCard = () => (
  <div className="glass rounded-2xl p-6 border border-white/5">
    <div className="shimmer h-4 w-24 rounded mb-4"></div>
    <div className="shimmer h-8 w-16 rounded mb-2"></div>
    <div className="shimmer h-3 w-32 rounded"></div>
  </div>
);

export const SkeletonRow = () => (
  <tr>
    {[1,2,3,4,5].map(i => (
      <td key={i} className="px-4 py-3">
        <div className="shimmer h-4 rounded w-full"></div>
      </td>
    ))}
  </tr>
);

export default Loader;
