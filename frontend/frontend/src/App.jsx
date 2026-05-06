import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Home from './pages/Home.jsx'
import Interview from './pages/Interview.jsx'
import Report from './pages/Report.jsx'

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/interview" element={<Interview />} />
        <Route path="/report" element={<Report />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background:'#16213e', color:'#fff', border:'1px solid rgba(240,165,0,0.3)', borderRadius:'12px' },
          success: { iconTheme: { primary:'#00b894', secondary:'#fff' } },
          error:   { iconTheme: { primary:'#e17055', secondary:'#fff' } },
        }}
      />
    </>
  )
}
