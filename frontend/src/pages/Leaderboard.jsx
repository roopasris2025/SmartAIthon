import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Star, Medal, TrendingUp, RefreshCw, Crown } from 'lucide-react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { DUMMY_LEADERBOARD } from '../utils/helpers';
import { fetchLeaderboard } from '../services/api';

const RANK_STYLES = [
  { border: 'border-amber-400/40',   bg: 'from-amber-500/15 to-amber-600/5',   text: 'text-amber-400',   icon: Crown },
  { border: 'border-slate-400/40',   bg: 'from-slate-500/15 to-slate-600/5',   text: 'text-slate-300',   icon: Medal },
  { border: 'border-orange-400/40',  bg: 'from-orange-500/15 to-orange-600/5', text: 'text-orange-400',  icon: Medal },
];

const avatarColors = [
  'from-cyan-500 to-indigo-600',
  'from-rose-500 to-pink-600',
  'from-emerald-500 to-teal-600',
  'from-amber-500 to-orange-600',
  'from-violet-500 to-purple-600',
  'from-sky-500 to-blue-600',
  'from-fuchsia-500 to-pink-600',
  'from-lime-500 to-green-600',
];

const Leaderboard = () => {
  const { user } = useAuth();
  const [list, setList]       = useState(DUMMY_LEADERBOARD);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod]   = useState('all'); // 'all' | 'week' | 'month'

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const res = await fetchLeaderboard();
      if (res.data?.length) setList(res.data);
    } catch {
      // dummy data
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadLeaderboard(); }, []);

  // Simulate different periods with multipliers (demo)
  const displayList = [...list]
    .map(u => ({
      ...u,
      displayPoints: period === 'week'
        ? Math.floor(u.points * 0.2)
        : period === 'month'
          ? Math.floor(u.points * 0.6)
          : u.points,
    }))
    .sort((a, b) => b.displayPoints - a.displayPoints);

  const topThree = displayList.slice(0, 3);
  const rest     = displayList.slice(3);

  const myRank = displayList.findIndex(u => u.email === user?.email) + 1;

  return (
    <div className="min-h-screen" style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(251,191,36,0.06) 0%, transparent 60%), #0a0f1e' }}>
      <Navbar />

      <main className="pt-24 pb-10 px-4 sm:px-6 max-w-3xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -15 }} animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-2xl shadow-amber-500/30 mb-4">
            <Trophy className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Campus Leaderboard</h1>
          <p className="text-slate-400 text-sm mt-1">Top contributors to campus cleanliness</p>

          {/* Period filter */}
          <div className="inline-flex bg-white/5 rounded-xl p-1 mt-4">
            {['all', 'month', 'week'].map(p => (
              <button key={p} onClick={() => setPeriod(p)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-all ${
                  period === p
                    ? 'bg-gradient-to-r from-amber-500 to-orange-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}>
                {p === 'all' ? 'All Time' : `This ${p.charAt(0).toUpperCase() + p.slice(1)}`}
              </button>
            ))}
          </div>
        </motion.div>

        {/* My rank banner */}
        {myRank > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="glass-dark rounded-2xl border border-cyan-500/20 p-4 mb-6 flex items-center gap-3"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
              #{myRank}
            </div>
            <div>
              <p className="text-white text-sm font-semibold">Your Rank</p>
              <p className="text-slate-400 text-xs">{user?.name} · {displayList[myRank - 1]?.displayPoints ?? user?.points ?? 0} pts</p>
            </div>
            <div className="ml-auto">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
            </div>
          </motion.div>
        )}

        {/* Podium — top 3 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="flex items-end justify-center gap-3 mb-8"
        >
          {/* 2nd */}
          {topThree[1] && (
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${avatarColors[1]} flex items-center justify-center text-white font-bold text-lg border-2 border-slate-400/50 shadow-xl`}>
                {topThree[1].avatar}
              </div>
              <p className="text-xs text-white font-medium mt-2 text-center max-w-[80px] truncate">{topThree[1].name.split(' ')[0]}</p>
              <p className="text-xs text-slate-400">{topThree[1].displayPoints} pts</p>
              <div className="w-16 h-16 glass-dark rounded-t-xl border border-slate-400/20 flex items-center justify-center mt-2">
                <span className="text-slate-300 font-bold text-xl">2</span>
              </div>
            </div>
          )}

          {/* 1st */}
          {topThree[0] && (
            <div className="flex flex-col items-center">
              <Crown className="w-6 h-6 text-amber-400 mb-1 float-animation" />
              <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${avatarColors[0]} flex items-center justify-center text-white font-bold text-2xl border-2 border-amber-400/60 shadow-2xl shadow-amber-500/30`}>
                {topThree[0].avatar}
              </div>
              <p className="text-sm text-white font-semibold mt-2 text-center max-w-[90px] truncate">{topThree[0].name.split(' ')[0]}</p>
              <p className="text-sm text-amber-400 font-bold">{topThree[0].displayPoints} pts</p>
              <div className="w-20 h-24 bg-gradient-to-b from-amber-500/20 to-amber-600/5 rounded-t-xl border border-amber-400/20 flex items-center justify-center mt-2">
                <span className="text-amber-400 font-bold text-2xl">1</span>
              </div>
            </div>
          )}

          {/* 3rd */}
          {topThree[2] && (
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${avatarColors[2]} flex items-center justify-center text-white font-bold text-lg border-2 border-orange-400/50 shadow-xl`}>
                {topThree[2].avatar}
              </div>
              <p className="text-xs text-white font-medium mt-2 text-center max-w-[80px] truncate">{topThree[2].name.split(' ')[0]}</p>
              <p className="text-xs text-orange-400">{topThree[2].displayPoints} pts</p>
              <div className="w-16 h-12 glass-dark rounded-t-xl border border-orange-400/20 flex items-center justify-center mt-2">
                <span className="text-orange-400 font-bold text-xl">3</span>
              </div>
            </div>
          )}
        </motion.div>

        {/* Full list */}
        <div className="glass-dark rounded-2xl border border-white/5 overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
            <p className="text-sm font-semibold text-white">All Rankings</p>
            <button onClick={loadLeaderboard}
              className="text-slate-500 hover:text-white transition-colors">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div>
            {displayList.map((student, idx) => {
              const rank = idx + 1;
              const isMe = student.email === user?.email;
              const rs   = RANK_STYLES[idx] || null;
              const maxPts = displayList[0]?.displayPoints || 1;

              return (
                <motion.div
                  key={student.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  className={`flex items-center gap-4 px-5 py-3 border-b border-white/5 last:border-0 transition-all ${
                    isMe ? 'bg-cyan-500/5 border-l-2 border-l-cyan-500' : 'hover:bg-white/2'
                  }`}
                >
                  {/* Rank */}
                  <div className={`w-8 text-center font-bold text-sm flex-shrink-0 ${
                    rank === 1 ? 'text-amber-400' : rank === 2 ? 'text-slate-300' : rank === 3 ? 'text-orange-400' : 'text-slate-600'
                  }`}>
                    {rank <= 3 ? (rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉') : `#${rank}`}
                  </div>

                  {/* Avatar */}
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${avatarColors[idx % avatarColors.length]} flex items-center justify-center text-white font-bold text-sm flex-shrink-0 ${
                    isMe ? 'ring-2 ring-cyan-400' : ''
                  }`}>
                    {student.avatar}
                  </div>

                  {/* Name & bar */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm font-medium truncate ${isMe ? 'text-cyan-400' : 'text-white'}`}>
                        {student.name}
                        {isMe && <span className="ml-1 text-xs">(You)</span>}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${(student.displayPoints / maxPts) * 100}%` }}
                          transition={{ duration: 1, ease: 'easeOut', delay: idx * 0.04 + 0.3 }}
                          className={`h-full rounded-full bg-gradient-to-r ${avatarColors[idx % avatarColors.length]}`}
                        />
                      </div>
                      <span className="text-xs text-slate-500 flex-shrink-0">{student.reports} reports</span>
                    </div>
                  </div>

                  {/* Points */}
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <Star className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-sm font-bold text-white">{student.displayPoints}</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Leaderboard;
