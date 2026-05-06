import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Mic, Camera, BarChart3, ChevronRight, Zap, Shield } from 'lucide-react'
import toast from 'react-hot-toast'

const FIELDS = [
  'Computer Science / IT', 'Medicine / Healthcare', 'Business / Finance',
  'Engineering', 'Law', 'Education / Teaching', 'Architecture / Design',
  'Sciences / Research', 'Arts / Media', 'Nursing', 'Pharmacy', 'Other'
]

const CATEGORIES = [
  { id: 'general', label: 'General Topics', icon: '💬', desc: 'Daily life, hobbies, family' },
  { id: 'academic', label: 'Academic & Study', icon: '🎓', desc: 'University, research, learning' },
  { id: 'work', label: 'Work & Career', icon: '💼', desc: 'Professional life, skills' },
  { id: 'technology', label: 'Technology', icon: '💻', desc: 'Digital world, AI, innovation' },
  { id: 'society', label: 'Society & Culture', icon: '🌍', desc: 'Values, traditions, issues' },
  { id: 'environment', label: 'Environment', icon: '🌿', desc: 'Climate, sustainability' },
  { id: 'health', label: 'Health & Wellbeing', icon: '❤️', desc: 'Lifestyle, medicine, fitness' },
  { id: 'travel', label: 'Travel & Places', icon: '✈️', desc: 'Tourism, culture, geography' },
]

const FEATURES = [
  { icon: Camera, color: 'text-info', bg: 'bg-info/10', title: 'Live Camera Analysis', desc: 'Real-time facial expression, eye contact & confidence scoring via Computer Vision' },
  { icon: Mic, color: 'text-danger', bg: 'bg-danger/10', title: 'Voice Recognition', desc: 'Browser-native speech-to-text. No uploads needed, instant transcription' },

  { icon: BarChart3, color: 'text-success', bg: 'bg-success/10', title: 'Official IELTS Scoring', desc: 'Band 1–9 across all 4 criteria: FC, LR, GRA & Pronunciation' },
]

export default function Home() {
  const nav = useNavigate()
  const [name, setName] = useState('')
  const [field, setField] = useState('')
  const [customField, setCustom] = useState('')
  const [category, setCategory] = useState('general')
  const [numQ, setNumQ] = useState(6)
  const [loading, setLoading] = useState(false)

  const start = () => {
    const finalName = name.trim()
    const finalField = field === 'Other' ? customField.trim() : field
    if (!finalName) return toast.error('Please enter your name')
    if (!finalField) return toast.error('Please select your field of study/work')
    setLoading(true)
    localStorage.setItem('ielts_name', finalName)
    localStorage.setItem('ielts_field', finalField)
    localStorage.setItem('ielts_category', category)
    localStorage.setItem('ielts_numq', String(numQ))
    setTimeout(() => nav('/interview'), 300)
  }

  return (
    <div className="min-h-screen gradient-bg relative overflow-hidden">
      {/* Background orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-gold opacity-[0.04] blur-3xl animate-pulse-slow" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-info opacity-[0.04] blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-success opacity-[0.03] blur-3xl animate-pulse-slow" style={{ animationDelay: '4s' }} />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 py-12">

        {/* Hero */}
        <motion.div className="text-center mb-16"
          initial={{ opacity: 0, y: -30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-gold to-amber-600 flex items-center justify-center shadow-lg animate-float">
                <Brain size={40} className="text-white" />
              </div>
              <span className="absolute -top-2 -right-2 w-6 h-6 bg-success rounded-full flex items-center justify-center">
                <Zap size={12} className="text-white" />
              </span>
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-black mb-4 leading-tight">
            <span className="gold-text">IELTS</span>{' '}
            <span className="text-white">AI Interview</span>
          </h1>
          <p className="text-lg md:text-xl text-muted max-w-2xl mx-auto leading-relaxed">
            Practice IELTS Speaking with <span className="text-info font-semibold">real-time CV analysis</span>,{' '}
            <span className="text-success font-semibold">AI feedback</span>, and{' '}
            <span className="text-gold font-semibold">official band scoring</span>
          </p>

          <div className="flex flex-wrap justify-center gap-3 mt-6">
            {[['🆓', '100% Free AI'], ['🎥', 'Live Camera'], ['🎤', 'Voice Input'], ['📊', 'Band 1–9'], ['📄', 'PDF Report']].map(([icon, label]) => (
              <span key={label} className="glass px-4 py-1.5 rounded-full text-sm text-muted flex items-center gap-1.5">
                <span>{icon}</span>{label}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-16"
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.6 }}>
          {FEATURES.map(f => (
            <div key={f.title} className="glass rounded-2xl p-5 hover:scale-105 transition-transform duration-300">
              <div className={`w-10 h-10 ${f.bg} rounded-xl flex items-center justify-center mb-3`}>
                <f.icon size={20} className={f.color} />
              </div>
              <h3 className="font-bold text-sm mb-1 text-white">{f.title}</h3>
              <p className="text-xs text-muted leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </motion.div>

        {/* Setup Card */}
        <motion.div className="max-w-2xl mx-auto glass rounded-3xl p-8 border border-gold/10"
          initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4, duration: 0.5 }}>

          <h2 className="text-2xl font-bold text-center mb-8">
            🎯 Setup Your Interview
          </h2>

          {/* Name */}
          <div className="mb-5">
            <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">Your Full Name</label>
            <input
              type="text" value={name} onChange={e => setName(e.target.value)}
              placeholder="e.g. Abdul Wassay"
              onKeyDown={e => e.key === 'Enter' && start()}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-muted focus:outline-none focus:border-gold transition-colors"
            />
          </div>

          {/* Field */}
          <div className="mb-5">
            <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">Your Field of Study / Work</label>
            <select
              value={field} onChange={e => setField(e.target.value)}
              className="w-full bg-surface border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-gold transition-colors appearance-none"
            >
              <option value="">-- Select your field --</option>
              {FIELDS.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
            {field === 'Other' && (
              <input
                type="text" value={customField} onChange={e => setCustom(e.target.value)}
                placeholder="Type your field..."
                className="w-full mt-2 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-muted focus:outline-none focus:border-gold transition-colors"
              />
            )}
          </div>

          {/* Category */}
          <div className="mb-5">
            <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">Interview Topic Category</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {CATEGORIES.map(c => (
                <button key={c.id} onClick={() => setCategory(c.id)}
                  className={`p-3 rounded-xl border text-left transition-all duration-200 ${category === c.id ? 'border-gold bg-gold/10 text-gold' : 'border-white/10 hover:border-white/20 text-muted hover:text-white'}`}>
                  <div className="text-lg mb-1">{c.icon}</div>
                  <div className="text-xs font-semibold leading-tight">{c.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Number of questions */}
          <div className="mb-8">
            <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">
              Number of Questions: <span className="text-gold">{numQ}</span>
            </label>
            <input type="range" min="3" max="10" value={numQ} onChange={e => setNumQ(Number(e.target.value))}
              className="w-full accent-gold" />
            <div className="flex justify-between text-xs text-muted mt-1">
              <span>3 (Quick)</span><span>6 (Standard)</span><span>10 (Full)</span>
            </div>
          </div>

          {/* Start Button */}
          <button onClick={start} disabled={loading}
            className="w-full py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 bg-gradient-to-r from-gold to-amber-500 text-black hover:opacity-90 hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg">
            {loading
              ? <><div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />Preparing...</>
              : <><Zap size={20} />Begin AI Interview<ChevronRight size={20} /></>
            }
          </button>

          <div className="flex items-center justify-center gap-2 mt-4 text-xs text-muted">
            <Shield size={12} />
            <span>Camera & mic requested on next page. All data stays local.</span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
