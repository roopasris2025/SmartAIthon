import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import {
  Leaf, Recycle, MapPin, Trophy, Users, Zap, ArrowRight,
  Star, Shield, BarChart3, Globe, ChevronDown, Sparkles,
  TrendingUp, Award, Target, CheckCircle2, Play, Menu, X
} from 'lucide-react';

/* ─── tiny hook: count-up ─── */
const useCountUp = (target, duration = 2000, start = false) => {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime = null;
    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setValue(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [start, target, duration]);
  return value;
};

/* ─── floating particle ─── */
const Particle = ({ style }) => (
  <motion.div
    className="absolute rounded-full pointer-events-none"
    style={style}
    animate={{ y: [-20, 20, -20], opacity: [0.3, 0.8, 0.3] }}
    transition={{ duration: 4 + Math.random() * 4, repeat: Infinity, ease: 'easeInOut' }}
  />
);

/* ─── animated stat card ─── */
const StatCard = ({ icon: Icon, label, value, suffix = '', color }) => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  const count = useCountUp(value, 1800, inView);
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6 }}
      className="glass-dark rounded-2xl p-6 border border-white/5 hover:border-cyan-500/30 transition-all duration-300 group hover:-translate-y-1"
    >
      <div className={`inline-flex p-3 rounded-xl mb-4 ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div className="text-3xl font-black text-white">
        {count.toLocaleString()}<span className="text-cyan-400">{suffix}</span>
      </div>
      <p className="text-slate-400 text-sm mt-1">{label}</p>
    </motion.div>
  );
};

/* ─── feature card ─── */
const FeatureCard = ({ icon: Icon, title, desc, gradient, delay }) => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay }}
      className="relative glass-dark rounded-2xl p-6 border border-white/5 hover:border-cyan-400/30 group transition-all duration-300 overflow-hidden hover:-translate-y-2"
    >
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${gradient} rounded-2xl`} />
      <div className="relative z-10">
        <div className="inline-flex p-3 rounded-xl bg-white/5 border border-white/10 mb-4 group-hover:scale-110 transition-transform duration-300">
          <Icon className="w-6 h-6 text-cyan-400" />
        </div>
        <h3 className="text-white font-bold text-lg mb-2">{title}</h3>
        <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
      </div>
    </motion.div>
  );
};

/* ─── step card ─── */
const StepCard = ({ step, title, desc, delay }) => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -30 }}
      animate={inView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, delay }}
      className="flex gap-4 items-start"
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-cyan-500/20">
        {step}
      </div>
      <div>
        <h4 className="text-white font-semibold mb-1">{title}</h4>
        <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
      </div>
    </motion.div>
  );
};

/* ═══════════════════════════════════════════════════ */
const HomePage = () => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const heroRef = useRef(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMenuOpen(false);
  };

  const particles = Array.from({ length: 18 }, (_, i) => ({
    width: `${6 + Math.random() * 8}px`,
    height: `${6 + Math.random() * 8}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    background: i % 3 === 0
      ? 'rgba(34,211,238,0.4)'
      : i % 3 === 1
        ? 'rgba(129,140,248,0.4)'
        : 'rgba(16,185,129,0.4)',
  }));

  const features = [
    { icon: MapPin,    title: 'Smart Geo-Tagging',      desc: 'Pin exact waste locations on an interactive campus map with GPS precision for faster collection.', gradient: 'bg-gradient-to-br from-cyan-500/10 to-transparent', delay: 0 },
    { icon: Trophy,    title: 'Gamified Rewards',        desc: 'Earn eco-points for every report and race to the top of the campus leaderboard. Redeem rewards weekly.', gradient: 'bg-gradient-to-br from-indigo-500/10 to-transparent', delay: 0.1 },
    { icon: BarChart3, title: 'Real-Time Analytics',    desc: 'Admins get live dashboards tracking hotspots, collection rates, and sustainability KPIs at a glance.', gradient: 'bg-gradient-to-br from-emerald-500/10 to-transparent', delay: 0.2 },
    { icon: Recycle,   title: 'Smart Categorization',   desc: 'Auto-classify waste as recyclable, organic, or hazardous using AI-assisted report tagging.', gradient: 'bg-gradient-to-br from-amber-500/10 to-transparent', delay: 0.3 },
    { icon: Users,     title: 'Community Engagement',   desc: 'Collaborate with peers, follow cleanup drives, and build a greener campus together.', gradient: 'bg-gradient-to-br from-rose-500/10 to-transparent', delay: 0.4 },
    { icon: Shield,    title: 'Role-Based Access',      desc: 'Dedicated portals for students and admins with granular permissions and audit trails.', gradient: 'bg-gradient-to-br from-violet-500/10 to-transparent', delay: 0.5 },
  ];

  const steps = [
    { step: '01', title: 'Spot It',     desc: 'Notice overflowing bins or littered areas anywhere on campus.' },
    { step: '02', title: 'Report It',  desc: 'Open the app, pin the location, snap a photo, and submit in under 30 seconds.' },
    { step: '03', title: 'Track It',   desc: 'Watch your report move through "Pending → In Progress → Resolved" in real time.' },
    { step: '04', title: 'Earn It',    desc: 'Collect eco-points, unlock badges, and climb the leaderboard for every resolved issue.' },
  ];

  const testimonials = [
    { name: 'Aasha R.', role: 'Environmental Science Student', text: 'This platform made me actually care about campus waste. I reported 12 bins last month!', stars: 5 },
    { name: 'Dr. Meera K.', role: 'Campus Admin', text: 'Collection efficiency improved by 40% since we rolled this out. The heatmap is invaluable.', stars: 5 },
    { name: 'Rohan V.', role: 'Eco-Club President', text: 'The leaderboard created healthy competition. Our entire club is hooked on earning green points.', stars: 5 },
  ];

  return (
    <div className="min-h-screen overflow-x-hidden" style={{ background: '#0a0f1e' }}>

      {/* ── NAV ── */}
      <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'glass-dark shadow-2xl' : ''}`}>
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-white text-base tracking-tight">
              Smart<span className="text-cyan-400">Waste</span>
            </span>
          </div>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-8">
            {[['features','Features'], ['how-it-works','How It Works'], ['impact','Our Impact'], ['testimonials','Testimonials']].map(([id, label]) => (
              <button key={id} onClick={() => scrollTo(id)} className="text-slate-400 hover:text-white text-sm transition-colors">
                {label}
              </button>
            ))}
          </nav>

          {/* CTA buttons */}
          <div className="hidden md:flex items-center gap-3">
            <button onClick={() => navigate('/auth')}
              className="text-sm text-slate-300 hover:text-white transition-colors px-4 py-2">
              Sign In
            </button>
            <button onClick={() => navigate('/auth')}
              className="text-sm bg-gradient-to-r from-cyan-500 to-indigo-600 text-white px-5 py-2 rounded-xl font-semibold hover:opacity-90 transition-all shadow-lg shadow-cyan-500/20">
              Get Started
            </button>
          </div>

          {/* Mobile menu button */}
          <button className="md:hidden text-slate-400 hover:text-white" onClick={() => setMenuOpen(o => !o)}>
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile drawer */}
        <AnimatePresence>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden glass-dark border-t border-white/5 px-6 py-4 space-y-3"
            >
              {[['features','Features'], ['how-it-works','How It Works'], ['impact','Our Impact'], ['testimonials','Testimonials']].map(([id, label]) => (
                <button key={id} onClick={() => scrollTo(id)} className="block text-slate-300 hover:text-white text-sm py-1 w-full text-left">
                  {label}
                </button>
              ))}
              <button onClick={() => navigate('/auth')} className="w-full mt-2 text-sm bg-gradient-to-r from-cyan-500 to-indigo-600 text-white px-5 py-2.5 rounded-xl font-semibold">
                Get Started →
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* ── HERO ── */}
      <section ref={heroRef} className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 pt-16">
        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/8 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/8 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-emerald-500/4 rounded-full blur-3xl" />
          {particles.map((s, i) => <Particle key={i} style={s} />)}
        </div>

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 glass-dark border border-cyan-500/20 rounded-full px-4 py-2 mb-8"
        >
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-cyan-300 font-medium tracking-wide uppercase">
            AI-Powered Campus Sustainability Platform
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="text-5xl md:text-7xl font-black text-white leading-tight mb-6 max-w-4xl"
        >
          Turn Waste Into{' '}
          <span className="relative inline-block">
            <span className="gradient-text">Impact</span>
            <motion.span
              className="absolute -bottom-1 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.8, delay: 0.9 }}
            />
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-slate-400 text-lg md:text-xl max-w-2xl leading-relaxed mb-10"
        >
          SmartWaste Campus empowers students and administrators to report, track, and resolve
          waste issues in real time — making your campus cleaner, greener, and smarter.
        </motion.p>

        {/* CTA row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.45 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <button
            id="hero-get-started"
            onClick={() => navigate('/auth')}
            className="group flex items-center gap-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold text-base hover:opacity-90 transition-all shadow-2xl shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:-translate-y-0.5"
          >
            Start Reporting Free
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={() => scrollTo('how-it-works')}
            className="flex items-center gap-2 px-8 py-4 rounded-2xl glass-dark border border-white/10 text-white font-semibold text-base hover:border-cyan-500/30 transition-all"
          >
            <Play className="w-4 h-4 text-cyan-400" />
            See How It Works
          </button>
        </motion.div>

        {/* Trust badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="flex flex-wrap justify-center gap-6 mt-12"
        >
          {[['🏆','Campus Award 2025'],['♻️','10K+ Reports Resolved'],['🌱','100% Eco-Focused'],['⚡','Real-Time Updates']].map(([emoji, label]) => (
            <div key={label} className="flex items-center gap-2 text-slate-500 text-sm">
              <span>{emoji}</span><span>{label}</span>
            </div>
          ))}
        </motion.div>

        {/* Scroll chevron */}
        <motion.button
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.6, repeat: Infinity }}
          onClick={() => scrollTo('features')}
          className="absolute bottom-10 text-slate-600 hover:text-cyan-400 transition-colors"
        >
          <ChevronDown className="w-7 h-7" />
        </motion.button>
      </section>

      {/* ── FEATURES ── */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
              className="inline-flex items-center gap-2 glass-dark border border-cyan-500/20 rounded-full px-4 py-1.5 mb-4"
            >
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-xs text-cyan-300 font-medium uppercase tracking-widest">Platform Features</span>
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              className="text-3xl md:text-5xl font-black text-white mb-4"
            >
              Everything You Need to{' '}
              <span className="gradient-text">Go Green</span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.2 }}
              className="text-slate-400 max-w-xl mx-auto"
            >
              A complete waste-management ecosystem built for modern campuses.
            </motion.p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => <FeatureCard key={f.title} {...f} />)}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className="py-24 px-6 relative">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-0 top-1/2 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl" />
          <div className="absolute right-0 top-1/3 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl" />
        </div>
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">
          {/* Left: visual card */}
          <motion.div
            initial={{ opacity: 0, x: -40 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}
            className="relative"
          >
            <div className="glass-dark rounded-3xl border border-cyan-500/10 p-8 shadow-2xl">
              {/* Mock phone UI */}
              <div className="bg-slate-900/80 rounded-2xl p-5 border border-white/5">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-cyan-400 font-semibold">📍 Block C, Gate 2</span>
                  <span className="text-xs text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full">NEW</span>
                </div>
                <div className="w-full h-28 rounded-xl bg-gradient-to-br from-slate-800 to-slate-700 flex items-center justify-center mb-4 border border-white/5">
                  <div className="text-center">
                    <MapPin className="w-8 h-8 text-cyan-400 mx-auto mb-1" />
                    <span className="text-xs text-slate-500">Waste location pinned</span>
                  </div>
                </div>
                <div className="space-y-2">
                  {[['Waste Type','General Waste 🗑️'],['Priority','High ⚠️'],['Status','Pending Review ⏳']].map(([k,v]) => (
                    <div key={k} className="flex justify-between text-xs">
                      <span className="text-slate-500">{k}</span>
                      <span className="text-slate-300">{v}</span>
                    </div>
                  ))}
                </div>
                <button className="w-full mt-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white text-xs font-semibold">
                  Submit Report →
                </button>
              </div>
              {/* Floating badges */}
              <motion.div animate={{ y: [-4, 4, -4] }} transition={{ duration: 2.5, repeat: Infinity }}
                className="absolute -top-4 -right-4 glass-dark border border-emerald-500/30 px-3 py-1.5 rounded-xl text-xs text-emerald-300 font-semibold shadow-lg">
                +50 eco-points 🌱
              </motion.div>
              <motion.div animate={{ y: [4, -4, 4] }} transition={{ duration: 3, repeat: Infinity }}
                className="absolute -bottom-4 -left-4 glass-dark border border-indigo-500/30 px-3 py-1.5 rounded-xl text-xs text-indigo-300 font-semibold shadow-lg">
                🏆 Rank #3 Campus
              </motion.div>
            </div>
          </motion.div>

          {/* Right: steps */}
          <div>
            <motion.div
              initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
              className="inline-flex items-center gap-2 glass-dark border border-indigo-500/20 rounded-full px-4 py-1.5 mb-4"
            >
              <Target className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-xs text-indigo-300 font-medium uppercase tracking-widest">How It Works</span>
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              className="text-3xl md:text-4xl font-black text-white mb-8"
            >
              Four simple steps to a{' '}
              <span className="gradient-text">cleaner campus</span>
            </motion.h2>
            <div className="space-y-7">
              {steps.map((s, i) => <StepCard key={s.step} {...s} delay={i * 0.1} />)}
            </div>
            <motion.button
              initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: 0.5 }}
              onClick={() => navigate('/auth')}
              className="mt-10 flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold text-sm hover:opacity-90 transition-all shadow-lg"
            >
              Report Your First Waste <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </section>

      {/* ── IMPACT STATS ── */}
      <section id="impact" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
              className="inline-flex items-center gap-2 glass-dark border border-emerald-500/20 rounded-full px-4 py-1.5 mb-4"
            >
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-xs text-emerald-300 font-medium uppercase tracking-widest">Our Impact</span>
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              className="text-3xl md:text-5xl font-black text-white"
            >
              Numbers that speak for{' '}
              <span className="gradient-text">themselves</span>
            </motion.h2>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard icon={Recycle}   label="Reports Resolved"   value={12400} suffix="+"  color="bg-gradient-to-br from-cyan-500 to-cyan-700" />
            <StatCard icon={Users}     label="Active Students"    value={3200}  suffix="+"  color="bg-gradient-to-br from-indigo-500 to-indigo-700" />
            <StatCard icon={Globe}     label="Campus Coverage"    value={98}    suffix="%"  color="bg-gradient-to-br from-emerald-500 to-emerald-700" />
            <StatCard icon={Award}     label="Eco-Points Awarded" value={850}   suffix="K" color="bg-gradient-to-br from-amber-500 to-amber-700" />
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ── */}
      <section id="testimonials" className="py-24 px-6 relative">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
        </div>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              className="text-3xl md:text-5xl font-black text-white mb-4"
            >
              Loved by the{' '}
              <span className="gradient-text">campus community</span>
            </motion.h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                className="glass-dark rounded-2xl border border-white/5 p-6 hover:border-cyan-500/20 transition-all hover:-translate-y-1"
              >
                <div className="flex gap-1 mb-3">
                  {Array.from({ length: t.stars }).map((_, j) => (
                    <Star key={j} className="w-4 h-4 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-slate-300 text-sm leading-relaxed mb-4">"{t.text}"</p>
                <div className="flex items-center gap-3 mt-auto">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
                    {t.name[0]}
                  </div>
                  <div>
                    <p className="text-white text-sm font-semibold">{t.name}</p>
                    <p className="text-slate-500 text-xs">{t.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA BANNER ── */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}
            className="relative rounded-3xl overflow-hidden"
            style={{ background: 'linear-gradient(135deg, rgba(34,211,238,0.15), rgba(129,140,248,0.15)), rgba(15,23,42,0.8)', border: '1px solid rgba(34,211,238,0.2)', backdropFilter: 'blur(20px)' }}
          >
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute top-0 right-0 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl" />
              <div className="absolute bottom-0 left-0 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl" />
            </div>
            <div className="relative z-10 text-center py-16 px-8">
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-cyan-500 to-indigo-600 shadow-2xl shadow-cyan-500/30 mb-6 float-animation">
                <Leaf className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-3xl md:text-5xl font-black text-white mb-4">
                Ready to make your campus{' '}
                <span className="gradient-text">smarter?</span>
              </h2>
              <p className="text-slate-400 text-base mb-8 max-w-xl mx-auto">
                Join thousands of students and admins already turning waste reports into real campus change.
                It's free, fast, and impactful.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  id="cta-join-now"
                  onClick={() => navigate('/auth')}
                  className="group flex items-center gap-2 justify-center px-8 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold text-base hover:opacity-90 transition-all shadow-2xl shadow-cyan-500/30"
                >
                  Join Now — It's Free
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  onClick={() => navigate('/auth')}
                  className="flex items-center justify-center gap-2 px-8 py-4 rounded-2xl glass-dark border border-white/10 text-white font-semibold text-base hover:border-cyan-500/30 transition-all"
                >
                  Admin Login
                  <Shield className="w-4 h-4 text-cyan-400" />
                </button>
              </div>
              <div className="flex flex-wrap justify-center gap-6 mt-8">
                {[['✅','No credit card needed'],['✅','Instant access'],['✅','GDPR compliant']].map(([icon, label]) => (
                  <div key={label} className="flex items-center gap-2 text-slate-500 text-sm">
                    <span>{icon}</span><span>{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="border-t border-white/5 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center">
              <Leaf className="w-4 h-4 text-white" />
            </div>
            <span className="text-slate-300 font-semibold text-sm">SmartWaste Campus</span>
          </div>
          <p className="text-slate-600 text-xs text-center">
            © 2025 SmartWaste Campus. Built for a greener tomorrow. 🌍
          </p>
          <div className="flex items-center gap-4 text-slate-600 text-xs">
            <button onClick={() => navigate('/auth')} className="hover:text-slate-300 transition-colors">Login</button>
            <button onClick={() => navigate('/auth')} className="hover:text-slate-300 transition-colors">Sign Up</button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
