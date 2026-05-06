import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 60000 })

export const interviewAPI = {
  getQuestions: (field, category, num=6) =>
    api.post('/interview/questions', { field, category, num }),
  startSession: (data) => api.post('/interview/session/start', data),
  saveResponse: (sid, data) => api.post(`/interview/session/${sid}/response`, data),
  endSession: (sid) => api.post(`/interview/session/${sid}/end`),
}

export const analyzeAPI = {
  sendFrame: (session_id, frame) => api.post('/analyze/frame', { session_id, frame }),
  analyzeAnswer: (data) => api.post('/analyze/answer', data),
  transcribeAudio: (audio) => {
    const form = new FormData()
    form.append('audio', audio, 'answer.webm')
    return api.post('/transcribe/audio', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000,
    })
  },
  getCVSummary: (sid) => api.get(`/analyze/cv-summary/${sid}`),
  getBodyLanguageSummary: (sid) => api.get(`/analyze/body-language-summary/${sid}`),
  getGestureAnalysis: (sid) => api.get(`/analyze/gesture-frequency/${sid}`),
}

export const reportAPI = {
  generate: (data) => api.post('/report/generate', data),
  downloadPDF: (report) => api.post('/report/pdf', { report }, { responseType: 'blob' }),
}
