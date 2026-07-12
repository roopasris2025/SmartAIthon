import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Shield, Eye, EyeOff, Leaf, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { loginUser, registerUser } from '../services/api';
import toast from 'react-hot-toast';

const AuthPage = () => {
  const [mode, setMode] = useState('login'); // 'login' | 'signup'
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'student' });
  const [errors, setErrors] = useState({});
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
    setErrors(err => ({ ...err, [e.target.name]: '' }));
  };

  const validate = () => {
    const e = {};
    if (mode === 'signup' && !form.name.trim()) e.name = 'Name is required';
    if (!form.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) e.email = 'Invalid email address';
    if (form.password.length < 6) e.password = 'Password must be at least 6 characters';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      let res;
      if (mode === 'login') {
        // Try real API, fall back to mock
        try {
          res = await loginUser({ email: form.email, password: form.password });
          const { user, token } = res.data;
          login(user, token);
        } catch {
          // Mock auth for demo
          const mockUser = {
            id: '1', name: form.email.split('@')[0], email: form.email,
            role: form.email.toLowerCase().includes('admin') ? 'admin' : 'student',
            points: 320,
          };
          login(mockUser, 'mock-jwt-token-' + Date.now());
          toast.success(`Welcome back, ${mockUser.name}!`);
          navigate(mockUser.role === 'admin' ? '/admin' : '/dashboard');
          return;
        }
        toast.success('Login successful!');
        navigate(res.data.user.role === 'admin' ? '/admin' : '/dashboard');
      } else {
        try {
          res = await registerUser(form);
          const { user, token } = res.data;
          login(user, token);
        } catch {
          const mockUser = {
            id: Date.now().toString(), name: form.name, email: form.email, role: form.role, points: 0,
          };
          login(mockUser, 'mock-jwt-token-' + Date.now());
          toast.success(`Account created! Welcome, ${mockUser.name}!`);
          navigate(mockUser.role === 'admin' ? '/admin' : '/dashboard');
          return;
        }
        toast.success('Account created!');
        navigate(res.data.user.role === 'admin' ? '/admin' : '/dashboard');
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const inputCls = (field) =>
    `w-full bg-white/5 border rounded-xl px-4 py-3 pl-11 text-white placeholder-slate-500 text-sm focus:outline-none transition-all ${
      errors[field]
        ? 'border-rose-500/50 focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20'
        : 'border-white/10 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20'
    }`;

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden"
      style={{ background: 'radial-gradient(ellipse at 20% 50%, rgba(34,211,238,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(129,140,248,0.08) 0%, transparent 60%), #0a0f1e' }}
    >
      {/* Decorative orbs */}
      <div className="absolute top-20 left-10 w-64 h-64 rounded-full bg-cyan-500/5 blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-20 right-10 w-64 h-64 rounded-full bg-indigo-500/5 blur-3xl pointer-events-none"></div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md mx-4"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-indigo-600 shadow-2xl shadow-cyan-500/30 mb-4 float-animation">
            <Leaf className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold gradient-text">SmartWaste Campus</h1>
          <p className="text-slate-500 text-sm mt-1">Smart Waste Management System</p>
        </div>

        {/* Card */}
        <div className="glass-dark rounded-2xl border border-cyan-500/10 p-8 shadow-2xl">
          {/* Mode tabs */}
          <div className="flex rounded-xl bg-white/5 p-1 mb-6">
            {['login', 'signup'].map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setErrors({}); }}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                  mode === m
                    ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Sign Up'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence>
              {mode === 'signup' && (
                <motion.div
                  key="name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="relative mb-1">
                    <User className="absolute left-3 top-3.5 w-4 h-4 text-slate-500" />
                    <input name="name" type="text" placeholder="Full Name"
                      value={form.name} onChange={handleChange} className={inputCls('name')} />
                  </div>
                  {errors.name && <p className="text-xs text-rose-400 mt-1">{errors.name}</p>}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Email */}
            <div>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 w-4 h-4 text-slate-500" />
                <input name="email" type="email" placeholder="Email Address"
                  value={form.email} onChange={handleChange} className={inputCls('email')} />
              </div>
              {errors.email && <p className="text-xs text-rose-400 mt-1">{errors.email}</p>}
            </div>

            {/* Password */}
            <div>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 w-4 h-4 text-slate-500" />
                <input name="password" type={showPass ? 'text' : 'password'} placeholder="Password"
                  value={form.password} onChange={handleChange} className={inputCls('password')} />
                <button type="button" onClick={() => setShowPass(s => !s)}
                  className="absolute right-3 top-3.5 text-slate-500 hover:text-slate-300 transition-colors">
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-rose-400 mt-1">{errors.password}</p>}
            </div>

            {/* Role (signup only) */}
            <AnimatePresence>
              {mode === 'signup' && (
                <motion.div
                  key="role"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="relative">
                    <Shield className="absolute left-3 top-3.5 w-4 h-4 text-slate-500" />
                    <select name="role" value={form.role} onChange={handleChange}
                      className={`${inputCls('role')} appearance-none`}>
                      <option value="student">Student</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-semibold text-sm hover:opacity-90 transition-all shadow-lg hover:shadow-cyan-500/30 disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              {loading ? (
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              ) : (
                <>
                  {mode === 'login' ? 'Sign In' : 'Create Account'}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Demo hint */}
          <div className="mt-4 p-3 rounded-xl bg-cyan-500/5 border border-cyan-500/10">
            <p className="text-xs text-slate-500 text-center">
              💡 Demo: use <span className="text-cyan-400">admin@campus.edu</span> for Admin or any email for Student
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AuthPage;
