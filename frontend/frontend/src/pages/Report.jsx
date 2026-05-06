import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line
} from 'recharts'
import { Download, Home, Brain, Camera, RefreshCw, ChevronDown, ChevronUp, Printer, Star } from 'lucide-react'
import toast from 'react-hot-toast'
import { reportAPI } from '../utils/api.js'

function BandMeter({ band, size = 'lg' }) {
  const getColor = b => b>=8?'#00b894':b>=7?'#74b9ff':b>=6?'#f0a500':b>=5?'#fdcb6e':'#e17055'
  const color = getColor(band)
  const pct   = (band / 9) * 100
  const dim   = size === 'lg' ? 'w-40 h-40 text-5xl' : 'w-20 h-20 text-2xl'
  return (
    <div className={`${dim} rounded-full flex flex-col items-center justify-center relative`}
      style={{
        background: `conic-gradient(${color} ${pct*3.6}deg, rgba(255,255,255,0.05) 0deg)`,
        boxShadow: `0 0 30px ${color}40`
      }}>
      <div className="absolute inset-2 rounded-full bg-surface flex flex-col items-center justify-center">
        <span className="font-black leading-none" style={{color}}>{band}</span>
        <span className="text-xs text-muted">/9.0</span>
      </div>
    </div>
  )
}

function ScoreBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-muted">{label}</span>
        <span className="font-bold" style={{color}}>{Math.round(value)}%</span>
      </div>
      <div className="score-bar">
        <div className="score-fill" style={{width:`${value}%`, background:color}} />
      </div>
    </div>
  )
}

function EmotionBadge({ emotion, pct }) {
  const map = {happy:'😊',neutral:'😐',sad:'😢',angry:'😠',surprised:'😮',fear:'😰',disgust:'🤢'}
  return (
    <div className="glass px-3 py-2 rounded-lg flex items-center gap-2 text-xs">
      <span className="text-lg">{map[emotion]||'🤔'}</span>
      <div>
        <div className="text-white capitalize font-medium">{emotion}</div>
        <div className="text-muted">{pct.toFixed(1)}%</div>
      </div>
    </div>
  )
}

export default function Report() {
  const nav = useNavigate()
  const [report,    setReport]    = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [expanded,  setExpanded]  = useState(null)
  const [pdfLoading,setPdfLoading]= useState(false)

  useEffect(() => {
    const build = async () => {
      const responses = JSON.parse(localStorage.getItem('ielts_responses') || '[]')
      const cv        = JSON.parse(localStorage.getItem('ielts_cv')        || '{}')
      const name      = localStorage.getItem('ielts_name')     || 'Candidate'
      const field     = localStorage.getItem('ielts_field')    || 'General'
      const category  = localStorage.getItem('ielts_category') || 'general'
      if (!responses.length) { nav('/'); return }
      try {
        const res = await reportAPI.generate({ responses, cv, name, field, category })
        setReport(res.data.report)
      } catch (e) {
        // fallback
        const avg = key => responses.reduce((s,r)=>(s + (r.bands?.[key]||5)),0)/responses.length
        const fc=avg('fc'),lr=avg('lr'),gra=avg('gra'),p=avg('p')
        const overall = Math.round(((fc+lr+gra+p)/4)*2)/2
        setReport({
          meta:{ name, field, category,
            date: new Date().toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'}),
            time: new Date().toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit'}),
            total_questions: responses.length },
          overall:{ band:overall, label:'Competent', description:'Generally effective command', color:'#f0a500',
            fc:round1(fc), lr:round1(lr), gra:round1(gra), p:round1(p) },
          cv, ai_report:{
            summary:`${name} completed ${responses.length} IELTS speaking questions achieving an overall Band ${overall}.`,
            top_strengths:['Task completion','Communication attempt'],
            critical_improvements:['Grammar accuracy','Vocabulary range','Fluency'],
            study_plan:[
              {week:1,theme:'Grammar',daily_tasks:['Practice tenses','Grammar exercises'],resources:['Grammarly']},
              {week:2,theme:'Vocabulary',daily_tasks:['10 new words/day','Use in sentences'],resources:['Quizlet']},
              {week:3,theme:'Fluency',daily_tasks:['Speak 15 min daily','Record yourself'],resources:['IELTS.org']},
              {week:4,theme:'Mock Test',daily_tasks:['Full practice test','Review mistakes'],resources:['Cambridge IELTS']},
            ],
            target_timeline:'4–6 weeks of focused daily practice',
            field_specific_advice:`Professionals in ${field} benefit greatly from formal English. Focus on technical vocabulary.`,
            motivational_message:`Keep going, ${name}! Consistency is the key to IELTS success.`,
          },
          questions: responses.map((r,i)=>({
            num:i+1, question:r.question, answer:r.answer,
            band:r.overall_band||r.bands?.overall||5,
            bands:r.bands||{}, strengths:r.ai?.strengths||[],
            improvements:r.ai?.improvements||[],
            corrected:r.ai?.corrected_answer||'', model:r.ai?.model_answer||'',
            word_count:r.nlp?.word_count||0,
          }))
        })
      } finally { setLoading(false) }
    }
    build()
  }, [])

  const round1 = v => Math.round(v*10)/10

  const downloadPDF = async () => {
    if (!report) return
    setPdfLoading(true)
    try {
      const res = await reportAPI.downloadPDF(report)
      const url = URL.createObjectURL(new Blob([res.data],{type:'application/pdf'}))
      Object.assign(document.createElement('a'),{href:url, download:`IELTS_Report_${report.meta?.name||'report'}.pdf`}).click()
      URL.revokeObjectURL(url)
      toast.success('PDF downloaded!')
    } catch (e) {
      toast.error('PDF failed. Make sure reportlab is installed: pip install reportlab')
    } finally { setPdfLoading(false) }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-dark">
      <div className="text-center">
        <div className="relative w-24 h-24 mx-auto mb-4">
          <div className="absolute inset-0 border-4 border-gold/20 rounded-full" />
          <div className="absolute inset-0 border-4 border-transparent border-t-gold rounded-full animate-spin" />
          <Brain size={32} className="text-gold absolute inset-0 m-auto" />
        </div>
        <p className="text-muted">Generating your AI report...</p>
      </div>
    </div>
  )

  if (!report) return null
  const { meta, overall, cv, ai_report, questions } = report

  // chart data
  const radarData = [
    {subject:'Fluency',    value: overall.fc/9*100},
    {subject:'Vocabulary', value: overall.lr/9*100},
    {subject:'Grammar',    value: overall.gra/9*100},
    {subject:'Pronun.',    value: overall.p/9*100},
    {subject:'Confidence', value: cv?.avg_confidence||65},
    {subject:'Eye Contact',value: cv?.eye_contact_rate||0},
  ]

  const barData = questions.map(q=>({
    name:`Q${q.num}`,
    FC:  +(q.bands?.fc||0).toFixed(1)*10,
    LR:  +(q.bands?.lr||0).toFixed(1)*10,
    GRA: +(q.bands?.gra||0).toFixed(1)*10,
  }))

  const bandColor = overall.color || '#f0a500'

  return (
    <div className="min-h-screen bg-dark pb-20">

      {/* Sticky header */}
      <div className="sticky top-0 z-50 glass border-b border-white/5 px-4 py-3 flex items-center justify-between no-print">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-gold" />
          <span className="font-bold text-sm gold-text">IELTS Report</span>
        </div>
        <div className="flex gap-2">
          <button onClick={()=>window.print()}
            className="flex items-center gap-1.5 px-3 py-1.5 glass border border-white/10 rounded-xl text-xs text-muted hover:text-white transition-colors">
            <Printer size={13} />Print
          </button>
          <button onClick={downloadPDF} disabled={pdfLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gold/10 border border-gold/30 rounded-xl text-xs text-gold hover:bg-gold/20 transition-colors disabled:opacity-50">
            {pdfLoading ? <div className="w-3 h-3 border border-gold/30 border-t-gold rounded-full animate-spin"/> : <Download size={13} />}
            PDF
          </button>
          <button onClick={()=>nav('/')}
            className="flex items-center gap-1.5 px-3 py-1.5 glass border border-white/10 rounded-xl text-xs text-muted hover:text-white transition-colors">
            <RefreshCw size={13} />New
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">

        {/* Title */}
        <motion.div className="text-center glass rounded-3xl p-8 border border-gold/10"
          initial={{opacity:0,y:-20}} animate={{opacity:1,y:0}}>
          <h1 className="text-4xl font-black mb-2">
            <span className="gold-text">IELTS Speaking</span> Report
          </h1>
          <p className="text-muted">{meta.name} · {meta.field} · {meta.date} at {meta.time}</p>
          <p className="text-muted text-sm mt-1">{meta.total_questions} Questions Answered</p>
        </motion.div>

        {/* Band + Radar */}
        <div className="grid md:grid-cols-2 gap-6">
          <motion.div className="glass rounded-3xl p-6 flex flex-col items-center text-center"
            initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}} transition={{delay:0.1}}>
            <p className="text-xs text-muted uppercase tracking-wider mb-4">Overall IELTS Band</p>
            <BandMeter band={overall.band} size="lg" />
            <div className="mt-4">
              <p className="text-xl font-black" style={{color:bandColor}}>{overall.label}</p>
              <p className="text-sm text-muted mt-1">{overall.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-3 mt-4 w-full">
              {[['FC','Fluency & Coherence'],['LR','Lexical Resource'],['GRA','Grammar & Accuracy'],['P','Pronunciation']].map(([k,label])=>(
                <div key={k} className="glass rounded-xl p-2 text-center">
                  <div className="text-xs text-muted">{label}</div>
                  <div className="text-2xl font-black text-gold">{overall[k.toLowerCase()]||'–'}</div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div className="glass rounded-3xl p-6"
            initial={{opacity:0,x:20}} animate={{opacity:1,x:0}} transition={{delay:0.15}}>
            <p className="text-xs text-muted uppercase tracking-wider mb-2">Performance Radar</p>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="subject" tick={{fill:'#8892a4',fontSize:11}} />
                <PolarRadiusAxis angle={30} domain={[0,100]} tick={{fill:'#555',fontSize:9}} />
                <Radar name="Score" dataKey="value" stroke="#f0a500" fill="#f0a500" fillOpacity={0.15} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Per-question bar chart */}
        {barData.length > 1 && (
          <motion.div className="glass rounded-3xl p-6"
            initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:0.2}}>
            <p className="text-xs text-muted uppercase tracking-wider mb-4">Score Per Question</p>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={barData} margin={{top:4,right:10,left:-20,bottom:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="name" tick={{fill:'#8892a4',fontSize:11}} />
                <YAxis domain={[0,100]} tick={{fill:'#8892a4',fontSize:10}} />
                <Tooltip contentStyle={{background:'#16213e',border:'1px solid rgba(240,165,0,0.2)',borderRadius:'8px',color:'#fff'}} />
                <Bar dataKey="FC"  fill="#f0a500" radius={[3,3,0,0]} />
                <Bar dataKey="LR"  fill="#74b9ff" radius={[3,3,0,0]} />
                <Bar dataKey="GRA" fill="#00b894" radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-2 justify-center flex-wrap">
              {[['FC','#f0a500'],['LR','#74b9ff'],['GRA','#00b894']].map(([l,c])=>(
                <div key={l} className="flex items-center gap-1.5 text-xs text-muted">
                  <div className="w-3 h-3 rounded" style={{background:c}} />{l}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* CV Analysis */}
        <motion.div className="glass rounded-3xl p-6"
          initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:0.25}}>
          <p className="text-xs text-muted uppercase tracking-wider mb-4 flex items-center gap-2">
            <Camera size={12} className="text-info" />Computer Vision Analysis
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            {[
              {label:'Confidence',  val:`${Math.round(cv?.avg_confidence||65)}%`,  color:'text-gold'},
              {label:'Eye Contact', val:`${Math.round(cv?.eye_contact_rate||0)}%`,  color:'text-info'},
              {label:'Dominant Emotion', val:cv?.dominant_emotion||'neutral', color:'text-success'},
              {label:'Presentation', val:`${Math.round(cv?.presentation_score||65)}%`, color:'text-purple-400'},
            ].map(({label,val,color})=>(
              <div key={label} className="glass rounded-xl p-3 text-center">
                <div className={`text-xl font-black ${color} capitalize`}>{val}</div>
                <div className="text-xs text-muted mt-1">{label}</div>
              </div>
            ))}
          </div>
          {cv?.emotion_percentages && Object.keys(cv.emotion_percentages).length>0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {Object.entries(cv.emotion_percentages).sort(([,a],[,b])=>b-a).slice(0,5).map(([e,p])=>(
                <EmotionBadge key={e} emotion={e} pct={p} />
              ))}
            </div>
          )}
          {cv?.feedback?.length>0 && (
            <div className="space-y-2">
              {cv.feedback.map((f,i)=>(
                <div key={i} className={`flex items-start gap-2 p-3 rounded-xl text-sm border ${
                  f.type==='positive'?'bg-success/10 border-success/20':
                  f.type==='improve' ?'bg-danger/10 border-danger/20':
                  'bg-white/5 border-white/10'}`}>
                  <span className="mt-0.5">{f.type==='positive'?'✅':f.type==='improve'?'⚠️':'ℹ️'}</span>
                  <div>
                    <div className="text-xs font-bold text-muted mb-0.5">{f.cat}</div>
                    <p className="text-sm">{f.msg}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* AI Report */}
        {ai_report?.summary && (
          <motion.div className="glass rounded-3xl p-6"
            initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:0.3}}>
            <p className="text-xs text-muted uppercase tracking-wider mb-4 flex items-center gap-2">
              <Brain size={12} className="text-gold" />AI Assessment
            </p>
            <p className="text-sm text-muted leading-relaxed mb-4">{ai_report.summary}</p>
            {ai_report.band_interpretation && (
              <div className="glass-gold rounded-xl p-3 mb-4">
                <p className="text-xs text-gold font-semibold mb-1">What this means for {meta.field}:</p>
                <p className="text-xs text-muted">{ai_report.band_interpretation}</p>
              </div>
            )}
            {ai_report.field_specific_advice && (
              <div className="glass rounded-xl p-3 mb-4">
                <p className="text-xs text-info font-semibold mb-1">Field-Specific Advice:</p>
                <p className="text-xs text-muted">{ai_report.field_specific_advice}</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Strengths & Improvements */}
        <motion.div className="grid sm:grid-cols-2 gap-4"
          initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:0.35}}>
          <div className="glass rounded-3xl p-5">
            <h3 className="text-xs font-bold text-success uppercase mb-3">✅ Key Strengths</h3>
            <div className="space-y-2">
              {(ai_report?.top_strengths||[]).map((s,i)=>(
                <div key={i} className="flex items-start gap-2 p-2 bg-success/5 rounded-lg">
                  <span className="text-success text-xs mt-0.5">•</span>
                  <p className="text-xs text-muted">{s}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="glass rounded-3xl p-5">
            <h3 className="text-xs font-bold text-danger uppercase mb-3">⚠️ Priority Improvements</h3>
            <div className="space-y-2">
              {(ai_report?.critical_improvements||[]).map((s,i)=>(
                <div key={i} className="flex items-start gap-2 p-2 bg-danger/5 rounded-lg">
                  <span className="text-danger text-xs mt-0.5">•</span>
                  <p className="text-xs text-muted">{s}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Study Plan */}
        {ai_report?.study_plan?.length > 0 && (
          <motion.div className="glass rounded-3xl p-6"
            initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:0.4}}>
            <p className="text-xs text-muted uppercase tracking-wider mb-4 flex items-center gap-2">
              <Star size={12} className="text-gold" />4-Week AI Study Plan
            </p>
            <div className="grid sm:grid-cols-2 gap-3">
              {ai_report.study_plan.map((w,i)=>(
                <div key={i} className="glass rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-gold/10 border border-gold/20 rounded-lg flex items-center justify-center text-xs font-bold text-gold">
                      W{w.week}
                    </div>
                    <span className="text-sm font-semibold">{w.theme}</span>
                  </div>
                  <ul className="space-y-1 mb-2">
                    {(w.daily_tasks||[]).map((t,j)=>(
                      <li key={j} className="text-xs text-muted flex gap-1.5">
                        <span className="text-gold">•</span>{t}
                      </li>
                    ))}
                  </ul>
                  {w.resources?.[0] && (
                    <p className="text-xs text-info">📚 {w.resources[0]}</p>
                  )}
                </div>
              ))}
            </div>
            <div className="flex flex-wrap gap-3 mt-4 items-center">
              <span className="text-xs text-muted">Timeline: <strong className="text-white">{ai_report.target_timeline}</strong></span>
              {ai_report.recommended_score_for_goal && (
                <span className="text-xs text-muted">Target for {meta.field}: <strong className="text-gold">{ai_report.recommended_score_for_goal}</strong></span>
              )}
            </div>
            {ai_report.motivational_message && (
              <div className="mt-4 p-4 glass-gold rounded-xl">
                <p className="text-sm text-gold italic">"{ai_report.motivational_message}"</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Per-question details */}
        <motion.div className="glass rounded-3xl p-6"
          initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:0.45}}>
          <p className="text-xs text-muted uppercase tracking-wider mb-4">Question-by-Question Breakdown</p>
          <div className="space-y-2">
            {questions.map((q,i)=>(
              <div key={i} className="glass rounded-2xl overflow-hidden">
                <button className="w-full p-4 flex items-center gap-3 hover:bg-white/5 transition-colors text-left"
                  onClick={()=>setExpanded(expanded===i?null:i)}>
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-black flex-shrink-0"
                    style={{
                      background:`${q.band>=7?'#00b894':q.band>=6?'#f0a500':'#e17055'}15`,
                      color:q.band>=7?'#00b894':q.band>=6?'#f0a500':'#e17055',
                      border:`1px solid ${q.band>=7?'#00b894':q.band>=6?'#f0a500':'#e17055'}40`
                    }}>
                    {q.band}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{q.question}</p>
                    <p className="text-xs text-muted">{q.word_count} words</p>
                  </div>
                  {expanded===i?<ChevronUp size={16} className="text-muted flex-shrink-0"/>:<ChevronDown size={16} className="text-muted flex-shrink-0"/>}
                </button>

                {expanded===i && (
                  <div className="px-4 pb-4 border-t border-white/5 pt-4 space-y-3">
                    <div>
                      <p className="text-xs text-muted mb-1">Your Answer</p>
                      <p className="text-sm glass p-3 rounded-lg leading-relaxed">{q.answer}</p>
                    </div>
                    {q.corrected && q.corrected!==q.answer && (
                      <div>
                        <p className="text-xs text-success mb-1">✏️ Grammar Corrected</p>
                        <p className="text-xs text-success/80 glass p-2 rounded-lg italic">{q.corrected}</p>
                      </div>
                    )}
                    {q.model && (
                      <div>
                        <p className="text-xs text-info mb-1">🌟 Band 8+ Example</p>
                        <p className="text-xs text-info/80 glass p-2 rounded-lg italic">{q.model}</p>
                      </div>
                    )}
                    <div className="grid grid-cols-2 gap-2">
                      {q.strengths?.slice(0,2).map((s,j)=>(
                        <div key={j} className="text-xs bg-success/5 border border-success/20 rounded-lg p-2 text-success">✓ {s}</div>
                      ))}
                      {q.improvements?.slice(0,2).map((s,j)=>(
                        <div key={j} className="text-xs bg-danger/5 border border-danger/20 rounded-lg p-2 text-danger">⚠ {s}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <div className="text-center py-4">
          <p className="text-xs text-muted mb-4">
            Generated by IELTS AI Interview · Powered by local runtime NLP and computer vision analysis
          </p>
          <button onClick={()=>nav('/')}
            className="px-8 py-3 bg-gold/10 border border-gold/30 rounded-xl text-gold hover:bg-gold/20 transition-colors">
            🔄 Take Another Interview
          </button>
        </div>
      </div>
    </div>
  )
}
