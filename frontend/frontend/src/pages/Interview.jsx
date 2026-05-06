import React, { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Mic, MicOff, Camera, CameraOff, Brain, Eye, Clock,
  ChevronRight, CheckCircle, SkipForward, AlertCircle,
  Lightbulb, Volume2, BarChart3, MessageSquare, Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useCamera, useSpeech } from '../hooks/useCamera.js'
import { interviewAPI, analyzeAPI, reportAPI } from '../utils/api.js'
import { v4 as uuidv4 } from 'uuid'

// ─── tiny components ────────────────────────────────────────────────────────
function ScoreBar({ label, value, color = '#f0a500' }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-muted">{label}</span>
        <span className="font-bold" style={{ color }}>{value}%</span>
      </div>
      <div className="score-bar">
        <div className="score-fill" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  )
}

function BandCircle({ band, size = 'md' }) {
  const color = band >= 8 ? '#00b894' : band >= 7 ? '#74b9ff' : band >= 6 ? '#f0a500' : band >= 5 ? '#fdcb6e' : '#e17055'
  const dim = size === 'lg' ? 'w-28 h-28 text-4xl' : 'w-16 h-16 text-2xl'
  return (
    <div className={`${dim} rounded-full border-4 flex flex-col items-center justify-center`}
      style={{ borderColor: color, background: `${color}15`, boxShadow: `0 0 20px ${color}30` }}>
      <span className="font-black leading-none" style={{ color }}>{band}</span>
      <span className="text-xs text-muted">/9</span>
    </div>
  )
}

function MiniMetric({ label, value, color = '#f0a500' }) {
  const safeValue = Math.max(0, Math.min(100, Math.round(value || 0)))
  return (
    <div className="space-y-1">
      <div className="flex justify-between gap-2">
        <span className="text-muted">{label}</span>
        <span className="text-white font-semibold">{safeValue}</span>
      </div>
      <div className="h-1 bg-white/10 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${safeValue}%`, background: color }} />
      </div>
    </div>
  )
}

function WaveAnim() {
  return (
    <div className="flex items-center gap-1 h-6">
      {[1, 2, 3, 4, 5].map(i => (
        <div key={i} className="wave-bar" style={{ animationDelay: `${(i - 1) * 0.1}s` }} />
      ))}
    </div>
  )
}

function fallbackQuestion(i, field, category) {
  const part = i < 2 ? 1 : i < 4 ? 2 : 3
  const focus = category || 'communication'
  const topic = field || 'your field'
  const question =
    part === 1
      ? `What role does ${focus} play in ${topic}?`
      : part === 2
        ? `Describe a situation in ${topic} where ${focus} helped you perform better.`
        : `How do you think ${focus} will change the future of ${topic}?`
  const keywords = [...new Set([topic, focus, 'example', 'impact'].filter(Boolean))]
  return {
    id: i + 1,
    question,
    part,
    field,
    category,
    keywords,
    tips: `Answer the question directly and support it with one real example from ${topic}.`,
    duration: part === 1 ? '30-45 seconds' : part === 2 ? '1-2 minutes' : '2-3 minutes',
    follow_up: ''
  }
}

// ────────────────────────────────────────────────────────────────────────────
export default function Interview() {
  const nav = useNavigate()
  const sidRef = useRef(uuidv4())

  // user config
  const name = localStorage.getItem('ielts_name') || 'Candidate'
  const field = localStorage.getItem('ielts_field') || 'General'
  const category = localStorage.getItem('ielts_category') || 'general'
  const numQ = parseInt(localStorage.getItem('ielts_numq') || '6')

  // state
  const [phase, setPhase] = useState('loading') // loading|setup|question|recording|analyzing|feedback|done
  const [questions, setQuestions] = useState([])
  const [qIdx, setQIdx] = useState(0)
  const [responses, setResponses] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [timer, setTimer] = useState(0)
  const [bodyLanguageSummary, setBodyLanguageSummary] = useState(null)
  const timerRef = useRef(null)

  const cam = useCamera(sidRef.current)
  const speech = useSpeech()

  // ── init ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!name) { nav('/'); return }
    const init = async () => {
      try {
        await interviewAPI.startSession({
          session_id: sidRef.current, candidate: name, field, category
        })
        const res = await interviewAPI.getQuestions(field, category, numQ)
        setQuestions(res.data.questions || [])
        setPhase('setup')
      } catch (e) {
        toast.error('Failed to load questions. Check backend.')
        // fallback questions
        setQuestions(Array.from({ length: numQ }, (_, i) => fallbackQuestion(i, field, category)))
        setPhase('setup')
      }
    }
    init()
  }, [])

  // ── timer ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (phase === 'recording') {
      timerRef.current = setInterval(() => setTimer(t => t + 1), 1000)
    } else {
      clearInterval(timerRef.current)
      if (phase !== 'recording') setTimer(0)
    }
    return () => clearInterval(timerRef.current)
  }, [phase])

  const fmt = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

  // ── handlers ──────────────────────────────────────────────────────────────
  const startInterview = async () => {
    await cam.start()
    setPhase('question')
  }

  const startRecording = async () => {
    speech.reset()
    const started = await speech.start()
    if (started) setPhase('recording')
  }

  const stopAndAnalyze = async () => {
    setPhase('analyzing')
    const answer = (await speech.stop()).trim()
    if (!answer || answer.split(' ').length < 3) {
      toast.error('No speech detected! Please try again.')
      setPhase('question')
      return
    }
    try {
      const q = questions[qIdx]
      const res = await analyzeAPI.analyzeAnswer({
        question: q.question,
        answer,
        field,
        part: q.part,
        keywords: q.keywords || [],
        session_id: sidRef.current,
      })
      const data = res.data
      setAnalysis(data)
      const resp = { ...data, question: q.question, answer }
      setResponses(p => [...p, resp])
      await interviewAPI.saveResponse(sidRef.current, resp)
      setPhase('feedback')
    } catch (e) {
      toast.error('Analysis failed: ' + (e.response?.data?.error || e.message))
      setPhase('question')
    }
  }

  const next = () => {
    speech.reset()
    setAnalysis(null)
    if (qIdx + 1 >= questions.length) finish()
    else { setQIdx(p => p + 1); setPhase('question') }
  }

  const finish = async () => {
    cam.stop()
    await interviewAPI.endSession(sidRef.current)
    try {
      const cvRes = await analyzeAPI.getCVSummary(sidRef.current)
      localStorage.setItem('ielts_cv', JSON.stringify(cvRes.data.cv || {}))
    } catch (e) { localStorage.setItem('ielts_cv', '{}') }

    // Fetch body language summary
    try {
      const blRes = await fetch(`/api/analyze/body-language-summary/${sidRef.current}`)
      const blData = await blRes.json()
      if (blData.success) {
        setBodyLanguageSummary(blData.body_language_summary)
        localStorage.setItem('ielts_body_language', JSON.stringify(blData.body_language_summary))
      }
    } catch (e) {
      console.error('Failed to fetch body language summary:', e)
      localStorage.setItem('ielts_body_language', JSON.stringify({}))
    }

    localStorage.setItem('ielts_responses', JSON.stringify(responses))
    nav('/report')
  }

  const q = questions[qIdx]
  const prog = questions.length ? (qIdx / questions.length) * 100 : 0

  // ─── render ───────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen flex flex-col bg-dark">

      {/* Top bar */}
      <div className="glass border-b border-white/5 px-4 py-3 flex items-center justify-between no-print sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-gold" />
          <span className="font-bold text-sm gold-text">IELTS AI</span>
          <span className="text-muted text-xs hidden sm:inline">· {field}</span>
        </div>
        <div className="flex items-center gap-4">
          {questions.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted">Q{Math.min(qIdx + 1, questions.length)}/{questions.length}</span>
              <div className="w-24 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <motion.div className="h-full bg-gold rounded-full" animate={{ width: `${prog}%` }} />
              </div>
            </div>
          )}
          {phase === 'recording' && (
            <div className="flex items-center gap-1.5 text-danger text-xs">
              <div className="w-2 h-2 bg-danger rounded-full animate-pulse" />
              <Clock size={12} />{fmt(timer)}
            </div>
          )}
          <span className="text-xs text-muted hidden sm:inline">{name}</span>
        </div>
      </div>

      {/* Main layout */}
      <div className="flex-1 overflow-y-auto flex flex-col p-4 md:p-6 gap-6 w-full max-w-7xl mx-auto">

        <div className={`flex flex-col ${phase !== 'feedback' ? 'lg:flex-row' : ''} gap-6 w-full`}>

          {/* ── LEFT: Camera & CV ─────────────────────────────────────────── */}
          <div className="flex-1 flex flex-col gap-5">

            {/* Camera Viewport */}
            <div className="camera-container relative rounded-3xl overflow-hidden bg-black/80 border border-white/10 w-full aspect-video max-h-[65vh] shadow-[0_0_50px_rgba(0,0,0,0.5)] flex-shrink-0">
              <canvas ref={cam.canvasRef} className="hidden" />
              {cam.active ? (
                <video
                  ref={cam.videoRef}
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
                  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted/50"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><line x1="2" y1="2" x2="22" y2="22"></line></svg>
                  <p className="text-sm text-muted text-center px-4">
                    {cam.error || 'Camera will activate during the interview'}
                  </p>
                </div>
              )}

              {/* Recording badge overlay */}
              {phase === 'recording' && (
                <div className="absolute top-6 left-6 flex items-center gap-2 bg-danger/90 px-4 py-2 rounded-full text-sm text-white font-bold shadow-lg shadow-danger/20">
                  <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse" /> REC
                </div>
              )}
            </div>

            {/* Controls & Status Row */}
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex gap-3">
                <div className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border ${cam.active ? 'bg-success/10 border-success/20 text-success' : 'bg-white/5 border-white/10 text-muted'}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg>
                  {cam.active ? 'Camera On' : 'Camera Off'}
                </div>
                <div className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold border ${speech.recording ? 'bg-danger/10 border-danger/20 text-danger' : 'bg-white/5 border-white/10 text-muted'}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={speech.recording ? 'animate-pulse' : ''}><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
                  {speech.recording ? 'Recording' : 'Mic Off'}
                </div>
              </div>

              {cam.error && (
                <div className="flex items-center gap-2 px-4 py-2.5 bg-danger/10 border border-danger/20 rounded-xl text-sm text-danger font-medium">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                  {cam.error}
                </div>
              )}
            </div>

            {/* Live CV Feedback */}
            {cam.liveData && cam.active && (
              <div className="glass rounded-2xl p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 border-t border-white/5">
                <div className="flex flex-col justify-center gap-1.5">
                  <div className="flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={cam.liveData.eye_contact ? 'text-success' : 'text-muted'}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    <span className="capitalize text-white font-semibold">
                      {cam.liveData.face_detected === false ? 'Face not centered' : cam.liveData.emotion}
                    </span>
                  </div>
                  <span className={`text-sm ${cam.liveData.eye_contact ? 'text-success' : 'text-danger'}`}>
                    {cam.liveData.eye_contact ? 'Good eye contact' : 'Look at camera'}
                  </span>
                  {cam.liveData.guidance && (
                    <div className="text-xs text-gold/90 font-semibold leading-tight mt-1 bg-gold/10 px-2 py-1 rounded">
                      {cam.liveData.guidance}
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-3 justify-center">
                  <MiniMetric label="Presence" value={cam.liveData.confidence_score} color="#00b894" />
                  <MiniMetric label="Framing" value={cam.liveData.frame_quality?.framing_score} color="#74b9ff" />
                </div>
                <div className="flex flex-col gap-3 justify-center">
                  <MiniMetric label="Posture" value={cam.liveData.posture?.posture_score} color="#a29bfe" />
                  <MiniMetric label="Stability" value={cam.liveData.movement?.stability_score} color="#f0a500" />
                </div>
                <div className="flex flex-col justify-center gap-2 text-xs">
                  <div className="glass rounded-lg px-3 py-2.5 flex justify-between items-center border border-white/5">
                    <span className="text-muted">Head:</span>
                    <span className="text-white capitalize font-semibold">{cam.liveData.head_position?.head_position || 'unknown'}</span>
                  </div>
                  <div className="glass rounded-lg px-3 py-2.5 flex justify-between items-center border border-white/5">
                    <span className="text-muted">Dress:</span>
                    <span className="text-white capitalize font-semibold">{cam.liveData.presentation?.dress_assessment || 'estimating'}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ── RIGHT: Interaction (Setup, Question, Recording) ─────────── */}
          {phase !== 'feedback' && (
            <div className="lg:w-[400px] xl:w-[480px] flex flex-col gap-5 flex-shrink-0">

              {/* Examiner Tip */}
              {q && (
                <div className="glass rounded-2xl p-5 flex flex-col gap-3 border-l-4 border-l-gold shadow-lg shadow-gold/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-gold font-bold">
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5"></path><path d="M9 18h6"></path><path d="M10 22h4"></path></svg>
                      Examiner Tip
                    </div>
                    <span className="glass-gold px-2 py-1 rounded-md text-[10px] font-bold text-gold tracking-wide">PART {q.part}</span>
                  </div>
                  <p className="text-sm text-muted/90 leading-relaxed">{q.tips}</p>
                </div>
              )}

              {/* Interaction Panel */}
              <div className="flex-1 glass rounded-3xl p-6 flex flex-col justify-center items-center border border-white/5 shadow-2xl relative overflow-hidden min-h-[400px]">
                <AnimatePresence mode="wait">
                  {/* LOADING */}
                  {phase === 'loading' && (
                    <motion.div key="loading" className="w-full h-full flex items-center justify-center"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="text-center">
                        <Loader2 size={48} className="text-gold animate-spin mx-auto mb-4" />
                        <p className="text-muted">Generating your personalized questions...</p>
                      </div>
                    </motion.div>
                  )}

                  {/* SETUP */}
                  {phase === 'setup' && (
                    <motion.div key="setup" className="w-full h-full flex items-center justify-center"
                      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                      <div className="text-center max-w-md w-full">
                        <div className="w-24 h-24 bg-gold/10 border-2 border-gold/20 rounded-full flex items-center justify-center mx-auto mb-6 animate-float">
                          <Brain size={44} className="text-gold" />
                        </div>
                        <h2 className="text-3xl font-black mb-3">
                          Ready, <span className="gold-text">{name}</span>?
                        </h2>
                        <p className="text-muted mb-2 text-sm">
                          <strong className="text-white">{questions.length}</strong> questions · Field:{' '}
                          <strong className="text-gold">{field}</strong>
                        </p>
                        <p className="text-muted text-sm mb-8">
                          The AI will analyze your grammar, vocabulary, fluency & confidence live.
                        </p>

                        <div className="grid grid-cols-3 gap-3 mb-8">
                          {[['🎥', 'Camera Analysis'], ['🎤', 'Voice Scoring'], ['🤖', 'AI Feedback']].map(([icon, label]) => (
                            <div key={label} className="glass rounded-xl p-3 text-center">
                              <div className="text-2xl mb-1">{icon}</div>
                              <div className="text-xs text-muted">{label}</div>
                            </div>
                          ))}
                        </div>

                        {/* Browser tip */}
                        <div className="glass rounded-xl p-3 mb-6 text-xs text-muted text-left">
                          <p className="font-semibold text-white mb-1">⚠️ Before you start:</p>
                          <ul className="space-y-1">
                            <li>• Use <strong className="text-gold">Google Chrome</strong> for best microphone support</li>
                            <li>• Click <strong>"Allow"</strong> when browser asks for camera & mic</li>
                            <li>• Sit in a <strong>well-lit</strong> area facing camera</li>
                          </ul>
                        </div>

                        <button onClick={startInterview}
                          className="w-full py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 bg-gradient-to-r from-gold to-amber-500 text-black hover:opacity-90 hover:scale-[1.02] transition-all shadow-lg">
                          <Camera size={20} />Start Interview
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {/* QUESTION */}
                  {phase === 'question' && q && (
                    <motion.div key={`q-${qIdx}`} className="w-full h-full flex flex-col justify-center"
                      initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}>

                      <div className="flex items-center gap-2 mb-4 flex-wrap">
                        <span className="text-xs text-muted">Question {qIdx + 1} of {questions.length}</span>
                        <span className="glass-gold px-2 py-0.5 rounded-full text-xs text-gold">Part {q.part}</span>
                        <span className="glass px-2 py-0.5 rounded-full text-xs text-muted capitalize">{category}</span>
                        <span className="glass px-2 py-0.5 rounded-full text-xs text-muted">{q.duration}</span>
                      </div>

                      {/* Question card */}
                      <div className="glass rounded-2xl p-6 p-6 mb-6 border border-white/5">
                        <p className="text-xl md:text-2xl leading-relaxed font-medium text-white">
                          "{q.question}"
                        </p>
                        {q.follow_up && (
                          <p className="text-sm text-muted mt-3 italic">Follow-up: {q.follow_up}</p>
                        )}
                      </div>

                      {/* Keywords */}
                      {q.keywords?.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-6">
                          <span className="text-xs text-muted">Key topics:</span>
                          {q.keywords.map(k => (
                            <span key={k} className="glass px-2 py-0.5 rounded text-xs text-info">{k}</span>
                          ))}
                        </div>
                      )}

                      {/* Speech error */}
                      {speech.error && (
                        <div className="flex items-start gap-2 p-3 bg-danger/10 border border-danger/20 rounded-xl text-sm text-danger mb-4">
                          <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
                          {speech.error}
                        </div>
                      )}

                      <div className="flex gap-3">
                        <button onClick={startRecording}
                          className="flex-1 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 bg-gradient-to-r from-danger to-rose-500 text-white hover:opacity-90 hover:scale-[1.02] transition-all">
                          <Mic size={20} />Start Recording
                        </button>
                        {qIdx > 0 && (
                          <button onClick={next}
                            className="py-4 px-5 glass border border-white/10 text-muted hover:text-white rounded-2xl flex items-center gap-2 transition-colors">
                            <SkipForward size={16} />Skip
                          </button>
                        )}
                      </div>
                    </motion.div>
                  )}

                  {/* RECORDING */}
                  {phase === 'recording' && q && (
                    <motion.div key="recording" className="w-full h-full flex flex-col justify-center items-center text-center"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>

                      <div className="w-28 h-28 bg-danger/10 border-2 border-danger rounded-full flex items-center justify-center mb-4 recording-ring">
                        <Mic size={44} className="text-danger" />
                      </div>
                      <WaveAnim />
                      <p className="text-muted text-sm mt-3 mb-2">Speak your answer clearly...</p>
                      <p className="text-xs text-muted mb-8 max-w-sm">"{q.question}"</p>

                      <div className="glass rounded-xl p-4 mb-6 max-w-md w-full text-left min-h-20">
                        <p className="text-sm leading-relaxed text-white">
                          {speech.transcript || <span className="text-muted italic">Your words will appear here...</span>}
                          <span className="text-muted italic">{speech.interim}</span>
                        </p>
                      </div>

                      <button onClick={stopAndAnalyze}
                        className="py-4 px-10 rounded-2xl font-bold flex items-center gap-2 bg-gradient-to-r from-gold to-amber-500 text-black hover:opacity-90 hover:scale-[1.02] transition-all">
                        <CheckCircle size={20} />Done — Analyze My Answer
                      </button>
                    </motion.div>
                  )}

                  {/* ANALYZING */}
                  {phase === 'analyzing' && (
                    <motion.div key="analyzing" className="w-full h-full flex items-center justify-center"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="text-center">
                        <div className="relative w-24 h-24 mx-auto mb-6">
                          <div className="absolute inset-0 border-4 border-gold/20 rounded-full" />
                          <div className="absolute inset-0 border-4 border-transparent border-t-gold rounded-full animate-spin" />
                          <Brain size={32} className="text-gold absolute inset-0 m-auto" />
                        </div>
                        <h3 className="text-xl font-bold mb-3">AI Analyzing Your Answer...</h3>
                        <div className="space-y-1.5 text-sm text-muted">
                          {['📝 Checking grammar & vocabulary', '🎯 Calculating IELTS band scores', '🤖 Generating personalized feedback', '💡 Creating model answer'].map(t => (
                            <p key={t}>{t}</p>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}


                </AnimatePresence>
              </div>
            </div>
          )}
        </div>

        {/* ── BOTTOM: Feedback Phase ────────────────────────────────────── */}
        {phase === 'feedback' && (
          <div className="w-full flex flex-col pt-4">
            <AnimatePresence mode="wait">
              {/* FEEDBACK */}
              {phase === 'feedback' && analysis && (
                <motion.div key="feedback" className="space-y-6 w-full mx-auto animate-slide-up">

                  {/* Band score header */}
                  <div className="glass rounded-2xl p-5 flex flex-col sm:flex-row items-center gap-5 border border-gold/10">
                    <BandCircle band={analysis.overall_band || analysis.bands?.overall || 5} size="lg" />
                    <div className="text-center sm:text-left flex-1">
                      <div className="text-2xl font-black text-white mb-1">
                        Band {analysis.overall_band || analysis.bands?.overall || 5}
                        <span className="text-muted font-normal text-base ml-2">— {analysis.band_label || analysis.bands?.label}</span>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3">
                        {[['FC', 'Fluency'], ['LR', 'Vocabulary'], ['GRA', 'Grammar'], ['P', 'Pronun.']].map(([k, label]) => (
                          <div key={k} className="glass rounded-lg p-2 text-center">
                            <div className="text-xs text-muted">{label}</div>
                            <div className="text-lg font-bold text-gold">{analysis.bands?.[k.toLowerCase()] || '–'}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Score bars */}
                  <div className="glass rounded-2xl p-5">
                    <h3 className="text-xs font-bold text-muted uppercase tracking-wider mb-3">Score Breakdown</h3>
                    <div className="space-y-3">
                      <ScoreBar label="Grammar" value={analysis.nlp?.grammar_score || 0} color="#00b894" />
                      <ScoreBar label="Vocabulary" value={analysis.nlp?.vocab_score || 0} color="#74b9ff" />
                      <ScoreBar label="Fluency" value={analysis.nlp?.fluency_score || 0} color="#f0a500" />
                      <ScoreBar label="Confidence (CV)" value={analysis.cv_snapshot?.avg_confidence || analysis.body_language?.confidence_score || 65} color="#a29bfe" />
                    </div>
                  </div>

                  {/* Body Language Feedback */}
                  {analysis.body_language && (
                    <div className="glass rounded-2xl p-5 border border-purple-400/20">
                      <h3 className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                        👁️ Body Language & Presentation
                      </h3>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                        {[
                          { label: 'Posture', val: analysis.body_language.posture?.posture_score || 70, color: '#a29bfe' },
                          { label: 'Confidence', val: analysis.body_language.confidence?.confidence_score || 70, color: '#00b894' },
                          { label: 'Eye Contact', val: analysis.body_language.gaze?.eye_contact_score || 60, color: '#74b9ff' },
                          { label: 'Head Position', val: analysis.body_language.head_position?.head_score || 70, color: '#f0a500' },
                          { label: 'Movement', val: analysis.body_language.movement?.stability_score || 60, color: '#55efc4' },
                          { label: 'Framing', val: analysis.body_language.frame_quality?.framing_score || 60, color: '#81ecec' },
                          { label: 'Lighting', val: analysis.body_language.frame_quality?.lighting_score || 60, color: '#ffeaa7' },
                          { label: 'Presentation', val: analysis.body_language.presentation?.presentation_score || 60, color: '#fd79a8' },
                        ].map(({ label, val, color }) => (
                          <div key={label} className="glass rounded-lg p-2 text-center" style={{ borderColor: color + '30', borderWidth: '1px' }}>
                            <div className="text-xs text-muted mb-1">{label}</div>
                            <div className="text-lg font-bold" style={{ color }}>{val}</div>
                          </div>
                        ))}
                      </div>
                      <div className="space-y-2">
                        {analysis.body_language.posture?.posture_quality && (
                          <div className="text-xs">
                            <span className="text-muted">Posture: </span>
                            <span className="text-purple-400 font-semibold capitalize">{analysis.body_language.posture.posture_quality}</span>
                          </div>
                        )}
                        {analysis.body_language.engagement?.engagement_level && (
                          <div className="text-xs">
                            <span className="text-muted">Engagement Level: </span>
                            <span className="text-purple-400 font-semibold capitalize">{analysis.body_language.engagement.engagement_level}</span>
                          </div>
                        )}
                        {analysis.body_language.movement?.movement_level && (
                          <div className="text-xs">
                            <span className="text-muted">Movement Control: </span>
                            <span className="text-purple-400 font-semibold capitalize">{analysis.body_language.movement.movement_level}</span>
                          </div>
                        )}
                        {analysis.body_language.presentation?.dress_assessment && (
                          <div className="text-xs">
                            <span className="text-muted">Dress / Presentation: </span>
                            <span className="text-purple-400 font-semibold capitalize">{analysis.body_language.presentation.dress_assessment}</span>
                          </div>
                        )}
                        {analysis.body_language.interviewer_signals?.length > 0 && (
                          <div className="grid sm:grid-cols-2 gap-2 pt-1">
                            {analysis.body_language.interviewer_signals.slice(0, 6).map((signal) => (
                              <div key={signal.label} className="glass rounded-lg px-2 py-1.5 text-xs flex justify-between gap-2">
                                <span className="text-muted">{signal.label}</span>
                                <span className="text-white capitalize">{signal.level}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        {analysis.body_language.guidance && (
                          <div className="text-xs mt-2 p-2 bg-purple-400/10 rounded-lg border border-purple-400/20 text-purple-300">
                            💡 {analysis.body_language.guidance}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* AI Feedback */}
                  {analysis.ai?.ai_powered && (
                    <div className="glass rounded-2xl p-5">
                      <h3 className="text-xs font-bold text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Brain size={12} className="text-gold" />AI Feedback
                        <span className="glass-gold px-2 py-0.5 rounded text-gold text-xs border border-gold/20">AI</span>
                      </h3>
                      <div className="grid sm:grid-cols-2 gap-3">
                        {[
                          { label: 'Fluency & Coherence', text: analysis.ai.fc_feedback, color: 'text-gold' },
                          { label: 'Vocabulary', text: analysis.ai.lr_feedback, color: 'text-info' },
                          { label: 'Grammar', text: analysis.ai.gra_feedback, color: 'text-success' },
                          { label: 'Pronunciation', text: analysis.ai.p_feedback, color: 'text-purple-400' },
                        ].filter(f => f.text).map(f => (
                          <div key={f.label} className="glass rounded-xl p-3">
                            <div className={`text-xs font-bold ${f.color} mb-1`}>{f.label}</div>
                            <p className="text-xs text-muted leading-relaxed">{f.text}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Strengths & Improvements */}
                  {analysis.ai?.strengths?.length > 0 && (
                    <div className="grid sm:grid-cols-2 gap-3">
                      <div className="glass rounded-2xl p-4">
                        <h4 className="text-xs font-bold text-success uppercase mb-2">✅ Strengths</h4>
                        {analysis.ai.strengths.map((s, i) => (
                          <p key={i} className="text-xs text-muted mb-1">• {s}</p>
                        ))}
                      </div>
                      <div className="glass rounded-2xl p-4">
                        <h4 className="text-xs font-bold text-danger uppercase mb-2">⚠️ Improve</h4>
                        {(analysis.ai.improvements || []).slice(0, 3).map((s, i) => (
                          <p key={i} className="text-xs text-muted mb-1">• {s}</p>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* NLP details */}
                  <div className="glass rounded-2xl p-5">
                    <h3 className="text-xs font-bold text-muted uppercase tracking-wider mb-3">NLP Details</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                      {[
                        { label: 'Words', val: analysis.nlp?.word_count || 0 },
                        { label: 'Vocab Level', val: analysis.nlp?.vocabulary_level || '–' },
                        { label: 'Fillers', val: analysis.nlp?.filler_count || 0 },
                        { label: 'Discourse Markers', val: analysis.nlp?.total_markers || 0 },
                      ].map(({ label, val }) => (
                        <div key={label} className="glass rounded-lg p-2">
                          <div className="text-xs text-muted">{label}</div>
                          <div className="text-sm font-bold text-gold capitalize">{val}</div>
                        </div>
                      ))}
                    </div>
                    {analysis.nlp?.advanced_words?.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs text-muted mb-1">Advanced words used:</p>
                        <div className="flex flex-wrap gap-1.5">
                          {analysis.nlp.advanced_words.map(w => (
                            <span key={w} className="glass-gold px-2 py-0.5 rounded text-xs text-gold">{w}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Corrected + Model answer */}
                  {analysis.ai?.corrected_answer && analysis.ai.corrected_answer !== analysis.answer && (
                    <div className="glass rounded-2xl p-4">
                      <h4 className="text-xs font-bold text-success uppercase mb-2">✏️ Grammar Corrected</h4>
                      <p className="text-sm text-success/80 italic leading-relaxed">"{analysis.ai.corrected_answer}"</p>
                    </div>
                  )}
                  {analysis.ai?.model_answer && (
                    <div className="glass rounded-2xl p-4">
                      <h4 className="text-xs font-bold text-info uppercase mb-2">🌟 Band 8+ Example Answer</h4>
                      <p className="text-sm text-info/80 italic leading-relaxed">"{analysis.ai.model_answer}"</p>
                    </div>
                  )}

                  {/* Grammar errors from AI */}
                  {analysis.ai?.grammar_errors?.length > 0 && (
                    <div className="glass rounded-2xl p-4">
                      <h4 className="text-xs font-bold text-danger uppercase mb-3">❌ Grammar Errors</h4>
                      <div className="space-y-2">
                        {analysis.ai.grammar_errors.slice(0, 4).map((e, i) => (
                          <div key={i} className="glass rounded-lg p-2 text-xs">
                            <span className="text-danger line-through mr-2">{e.error}</span>
                            <span className="text-success mr-2">→ {e.correction}</span>
                            <span className="text-muted italic">({e.rule})</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Next button */}
                  <button onClick={next}
                    className="w-full py-4 rounded-2xl font-bold flex items-center justify-center gap-2 bg-gradient-to-r from-gold to-amber-500 text-black hover:opacity-90 hover:scale-[1.02] transition-all">
                    {qIdx + 1 >= questions.length
                      ? <><BarChart3 size={20} />View Final Report</>
                      : <>Next Question <ChevronRight size={20} /></>
                    }
                  </button>
                </motion.div>
              )}


            </AnimatePresence>
          </div>
        )}

      </div>
    </div>
  )
}
