import { useRef, useState, useCallback, useEffect } from 'react'
import { analyzeAPI } from '../utils/api.js'

export function useCamera(sessionId) {
  const videoRef   = useRef(null)
  const canvasRef  = useRef(null)
  const streamRef  = useRef(null)
  const intervalRef = useRef(null)
  const [active, setActive]         = useState(false)
  const [error, setError]           = useState(null)
  const [liveData, setLiveData]     = useState(null)
  const [permission, setPermission] = useState('unknown') // unknown | granted | denied

  const attachStreamToVideo = useCallback(() => {
    if (!videoRef.current || !streamRef.current) return
    if (videoRef.current.srcObject !== streamRef.current) {
      videoRef.current.srcObject = streamRef.current
    }
    const playVideo = () => videoRef.current?.play().catch((e) => console.error('[Camera Play Error]', e))
    if (videoRef.current.readyState >= 1) playVideo()
    else videoRef.current.onloadedmetadata = playVideo
  }, [])

  const start = useCallback(async () => {
    try {
      setError(null)
      const constraints = {
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30, max: 30 },
          facingMode: 'user'
        },
        audio: false
      }
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      streamRef.current = stream
      attachStreamToVideo()
      setActive(true)
      setPermission('granted')

      // Send frames every 4 seconds
      intervalRef.current = setInterval(() => captureFrame(sessionId), 4000)
    } catch (err) {
      console.error('[Camera]', err)
      setPermission('denied')
      setError(
        err.name === 'NotAllowedError' ? 'Camera permission denied. Please allow camera access in browser settings.' :
        err.name === 'NotFoundError'   ? 'No camera found. Please connect a camera.' :
        err.name === 'NotReadableError'? 'Camera is in use by another application.' :
        `Camera error: ${err.message}`
      )
    }
  }, [attachStreamToVideo, sessionId])

  const captureFrame = useCallback(async (sid) => {
    if (!videoRef.current || !canvasRef.current) return
    if (videoRef.current.readyState < 2) return

    const canvas = canvasRef.current
    const ctx    = canvas.getContext('2d')
    const sourceWidth = videoRef.current.videoWidth || 640
    const sourceHeight = videoRef.current.videoHeight || 480
    const targetWidth = sourceWidth >= 1280 ? 960 : sourceWidth
    const targetHeight = Math.round(targetWidth * (sourceHeight / sourceWidth))

    canvas.width = targetWidth
    canvas.height = targetHeight
    ctx.drawImage(videoRef.current, 0, 0, targetWidth, targetHeight)
    const b64 = canvas.toDataURL('image/jpeg', 0.88)
    try {
      const res = await analyzeAPI.sendFrame(sid, b64)
      if (res.data.success) setLiveData(res.data.result)
    } catch (e) { /* silent */ }
  }, [])

  const stop = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    if (videoRef.current) videoRef.current.srcObject = null
    streamRef.current = null
    setActive(false)
  }, [])

  useEffect(() => {
    if (active) attachStreamToVideo()
  }, [active, attachStreamToVideo])

  useEffect(() => () => stop(), [stop])

  return { videoRef, canvasRef, active, error, liveData, permission, start, stop }
}


export function useSpeech() {
  const recRef     = useRef(null)
  const mediaRecorderRef = useRef(null)
  const mediaStreamRef = useRef(null)
  const chunksRef = useRef([])
  const transcriptRef = useRef('')
  const [recording, setRecording]           = useState(false)
  const [transcript, setTranscript]         = useState('')
  const [interim, setInterim]               = useState('')
  const [error, setError]                   = useState(null)
  const [supported, setSupported]           = useState(true)

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) setSupported(false)
  }, [])

  const start = useCallback(async () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const MediaRecorderCtor = window.MediaRecorder
    if (!navigator.mediaDevices?.getUserMedia || !MediaRecorderCtor) {
      setError('Microphone recording is not supported in this browser.')
      return false
    }
    setTranscript('')
    transcriptRef.current = ''
    setInterim('')
    setError(null)
    chunksRef.current = []

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream

      const mimeType = MediaRecorderCtor.isTypeSupported?.('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'
      const mediaRecorder = new MediaRecorderCtor(stream, { mimeType })
      mediaRecorder.ondataavailable = (event) => {
        if (event.data?.size) chunksRef.current.push(event.data)
      }
      mediaRecorder.start()
      mediaRecorderRef.current = mediaRecorder
      setRecording(true)
    } catch (err) {
      setError(
        err.name === 'NotAllowedError'
          ? 'Microphone permission denied. Allow mic in browser settings.'
          : `Microphone error: ${err.message}`
      )
      return false
    }

    if (!SR) {
      setSupported(false)
      setError('Live captions are not supported here. Audio will be transcribed after recording.')
      return true
    }

    const rec = new SR()
    rec.continuous      = true
    rec.interimResults  = true
    rec.lang            = 'en-US'
    rec.maxAlternatives = 1

    rec.onstart  = () => setRecording(true)
    rec.onerror  = (e) => {
      if (e.error === 'not-allowed') setError('Microphone permission denied. Allow mic in browser settings.')
      else if (e.error === 'network') setError('Live captions are offline. Your audio will be transcribed locally after recording.')
      else if (e.error !== 'no-speech') setError(`Mic error: ${e.error}`)
    }
    rec.onend    = () => { setInterim('') }
    rec.onresult = (e) => {
      let final = '', inter = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript
        if (e.results[i].isFinal) final += t + ' '
        else inter += t
      }
      if (final) {
        setTranscript(p => {
          const next = p + final
          transcriptRef.current = next
          return next
        })
      }
      setInterim(inter)
    }

    recRef.current = rec
    try {
      rec.start()
    } catch (err) {
      setError('Live captions could not start. Audio will be transcribed after recording.')
    }
    return true
  }, [])

  const stop = useCallback(async () => {
    const stopped = new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current
      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        resolve()
        return
      }
      mediaRecorder.onstop = resolve
      mediaRecorder.stop()
    })

    try { recRef.current?.stop() } catch (e) { /* already stopped */ }
    setRecording(false)
    setInterim('')
    await stopped

    mediaStreamRef.current?.getTracks().forEach(track => track.stop())
    mediaStreamRef.current = null
    mediaRecorderRef.current = null

    const liveText = transcriptRef.current.trim()
    if (liveText) return liveText

    if (!chunksRef.current.length) return ''
    const audio = new Blob(chunksRef.current, { type: 'audio/webm' })
    try {
      const res = await analyzeAPI.transcribeAudio(audio)
      const text = (res.data.text || '').trim()
      if (text) {
        setTranscript(text)
        transcriptRef.current = text
        setError(null)
      }
      return text
    } catch (err) {
      setError(`Local transcription failed: ${err.response?.data?.error || err.message}`)
      return ''
    }
  }, [])

  useEffect(() => () => {
    try { recRef.current?.stop() } catch (e) { /* already stopped */ }
    if (mediaRecorderRef.current?.state === 'recording') mediaRecorderRef.current.stop()
    mediaStreamRef.current?.getTracks().forEach(track => track.stop())
  }, [])

  const reset = useCallback(() => {
    setTranscript('')
    transcriptRef.current = ''
    setInterim('')
    setError(null)
  }, [])

  return { recording, transcript, interim, error, supported, start, stop, reset }
}
